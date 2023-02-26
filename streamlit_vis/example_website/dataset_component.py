"""
Simple hierarchical data:

- Root level: A single image with 1 to 4 gaussian blobs drawn on the image
- Leaf level: Few questions about the image (e.g. "How many gaussians are there?")

"""
import json
from dataclasses import dataclass

from streamlit_vis.dataset_base import VisionDatasetComponent


@dataclass
class GaussDatasetComponent(VisionDatasetComponent):
    def _load_metadata(self):
        dataset_path = self.dataset_dir
        assert dataset_path.is_dir(), f"Path {dataset_path} not found."

        meta_leaf = json.load((dataset_path / f"meta_{self.split}_leaf.json").open(
                encoding="utf-8"))
        meta_root = json.load((dataset_path / f"meta_{self.split}_root.json").open(
                encoding="utf-8"))
        return meta_leaf, meta_root

    def _load_subsets(self):
        meta_leaf, _meta_root = self.get_metadata()

        # sort data into groups for analysis
        # here, classify the questions with a simple heuristic
        group_questions = {"number": [], "yesno": []}
        for leaf_id, leaf_data in meta_leaf.items():
            if leaf_data["question"].lower().startswith("how many"):
                group_questions["number"].append(leaf_id)
            else:
                group_questions["yesno"].append(leaf_id)

        # format {group_name: {"title": x, "description": y, "subsets": { subset_name:  [ids] } } }
        subsets = {"all": {
                "title": "All",
                "description": "All questions",
                "subsets": {"all": list(meta_leaf.keys())}},
                "question_type": {
                        "title": "question type",
                        "description": "Group data by start of question.",
                        "subsets": group_questions}}
        return subsets
