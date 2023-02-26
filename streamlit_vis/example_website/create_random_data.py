"""
Script used to create the dummy data.
"""
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

from streamlit_vis.example_website.config import ExampleWebsiteConfig as conf
from streamlit_vis.st_utils import logger


def create_question(q, a, chance=0.5):
    """Create a question."""
    if np.random.uniform() < chance:
        return {"question": q, "answer": a}
    return None


def create_gaussian_data(base_path=conf.DATA_PATH):
    """Create random data for testing."""
    model_names = conf.MODEL_NAMES
    base_path = Path(base_path)
    dataset_name = "example_dataset"
    dataset_path = base_path / dataset_name

    split_sizes = {"train": 7, "val": 3}
    n_total_leaf, n_total_root = 0, 0
    n_max_gauss = 5
    scale = 30
    n_pixels = 1000
    default_chance = 0.5
    for split_name, split_size in split_sizes.items():
        meta_leaf, meta_root = {}, {}

        for _n_img in range(split_size):
            h = np.random.randint(400, 600)
            w = np.random.randint(400, 600)
            img = np.random.uniform(0, 0.3, size=(h, w, 3))
            root_id = f"{n_total_root}"
            n_gauss = np.random.randint(1, n_max_gauss)
            for _n_g in range(n_gauss):
                border = min(w, h) // 10
                x = np.random.uniform(border, w - border)
                y = np.random.uniform(border, h - border)
                mean = np.array([x, y])
                cov = np.random.uniform(-scale, scale, size=(2, 2))
                cov = np.dot(cov, cov.T)
                samples = np.random.multivariate_normal(mean, cov, size=n_pixels
                                                        ).round().astype(int)
                colors = np.random.uniform(0.0, 1.0, size=(n_pixels, 3))
                for n_p, (x, y) in enumerate(samples):
                    if 0 <= x < w and 0 <= y < h:
                        img[y, x, :] = colors[n_p, :]

                # draw a cross to denote the mean
                mean_radius = 20
                mx, my = int(mean[0]), int(mean[1])
                img[my - mean_radius:my + mean_radius, mx, :] = 1.0
                img[my, mx - mean_radius:mx + mean_radius, :] = 1.0

            image_file_rel = Path(dataset_name) / "images" / f"{split_name}_{root_id}.png"
            image_file = base_path / image_file_rel
            meta_root[root_id] = {
                    "leaf_ids": [],
                    "width": w,
                    "height": h,
                    "image_file": image_file_rel.as_posix(),
                    "n_gaussians": n_gauss,
            }
            n_total_root += 1
            img = (img * 255).astype(np.uint8)
            img = Image.fromarray(img)
            os.makedirs(image_file.parent, exist_ok=True)
            img.save(image_file)

            # create questions for the gaussians
            def _create_question(q, a, chance=default_chance):
                # pylint: disable=cell-var-from-loop
                nonlocal n_total_leaf
                if np.random.uniform() < chance:
                    meta_leaf[f"{n_total_leaf}"] = {
                            "question": q, "answer": a, "root_id": f"{root_id}"}
                    meta_root[root_id]["leaf_ids"].append(f"{n_total_leaf}")
                    n_total_leaf += 1

            randint = np.random.randint(2, n_max_gauss - 1)
            bool_map = {True: "yes", False: "no"}
            _create_question(f"Are there more than {randint} gaussians?",
                             bool_map[n_gauss > randint])
            _create_question(f"Are there less than {randint} gaussians?",
                             bool_map[n_gauss < randint])
            _create_question(f"Is there an even number of gaussians?", bool_map[n_gauss % 2 == 0])
            chance_here = default_chance
            if len(meta_root[root_id]["leaf_ids"]) == 0:
                chance_here = 1.0
            _create_question("How many gaussians are there?", str(n_gauss), chance=chance_here)

        json.dump(meta_leaf, (base_path / dataset_name / f"meta_{split_name}_leaf.json"
                              ).open("w", encoding="utf-8"), indent=2)
        json.dump(meta_root, (base_path / dataset_name / f"meta_{split_name}_root.json"
                              ).open("w", encoding="utf-8"), indent=2)

        # create some results
        random_answer_set = ["yes", "no", "1", "2", "3", "4"]
        preds = {}
        for model_name in model_names:
            preds[model_name] = {}
            for leaf_id, item in meta_leaf.items():
                if model_name == "random":
                    preds[model_name][leaf_id] = str(np.random.choice(random_answer_set))
                elif model_name == "sayyes":
                    preds[model_name][leaf_id] = "yes"
                elif model_name == "oracle":
                    preds[model_name][leaf_id] = item["answer"]
                else:
                    raise ValueError(f"Unknown model name: {model_name}")

        json.dump(preds, (dataset_path / f"preds_{split_name}.json").open(
                "w", encoding="utf-8"), indent=2)

    logger.info(f"Created dataset in path: {base_path}")


def main():
    create_gaussian_data()


if __name__ == "__main__":
    main()
