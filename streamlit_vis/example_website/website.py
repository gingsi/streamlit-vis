import json
from dataclasses import dataclass

import numpy as np

from streamlit_vis.example_website.config import ExampleWebsiteConfig
from streamlit_vis.example_website.dataset_component import GaussDatasetComponent
from streamlit_vis.website_dataset import DatasetWebsite


@dataclass
class ExampleWebsite(DatasetWebsite):

    # noinspection PyTypeChecker
    def __post_init__(self):
        super().__post_init__()

        # update type hints, this does nothing at runtime.
        self.conf: ExampleWebsiteConfig = self.conf

    def setup_dataset(self, dataset_name: str = "example_dataset", dataset_split: str = "train"):
        self.dataset: GaussDatasetComponent = GaussDatasetComponent(
                dataset_name, dataset_split, self.data_dir_base, self.conf.THUMBNAIL_SIZE)
        self.dataset.preload_everything()

    def setup_results(self):
        c = self.conf
        dataset_dir = self.dataset.dataset_dir
        split = self.dataset.split
        leaf_meta, _root_meta = self.dataset.get_metadata()
        subsets = self.dataset.get_subsets()

        # load predictions
        predictions = json.load(open(dataset_dir / f"preds_{split}.json", encoding="utf8"))

        # compute metrics per individual prediction
        metrics_per_datapoint = {}
        for model_name, model_preds in predictions.items():
            metrics_per_datapoint[model_name] = {c.METRIC_NAME: {}}
            for leaf_id, leaf_data in leaf_meta.items():
                gt_answer = leaf_data["answer"]
                model_answer = model_preds[leaf_id]
                acc = float(gt_answer == model_answer)
                metrics_per_datapoint[model_name][c.METRIC_NAME][leaf_id] = acc

        # compute average metrics per subset
        # note group_name "all" subset_name "all" will give the average over the whole dataset
        subset_results = {}
        for model_name, model_preds in predictions.items():
            subset_results[model_name] = {c.METRIC_NAME: {}}
            for group_name, group_info in subsets.items():
                group_results = {}
                for subset_name, subset_ll_ids in group_info["subsets"].items():
                    subset_acc = float(np.mean([
                            metrics_per_datapoint[model_name][c.METRIC_NAME][qid]
                            for qid in subset_ll_ids]))
                    group_results[subset_name] = subset_acc
                subset_results[model_name][c.METRIC_NAME][group_name] = group_results

        self.predictions, self.metrics_per_datapoint, self.subset_results = (
                predictions, metrics_per_datapoint, subset_results)
