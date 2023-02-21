"""
Simple hierarchical data:

- Highlevel: A single image with 1 to 4 gaussian blobs drawn on the image
- Lowlevel: Few questions about the image (e.g. "How many gaussians are there?")

"""
import json
from copy import deepcopy
from pathlib import Path

from streamlit_vis.st_utils import DATA_PATH


def create_dataset_loader(dataset_name, split):
    # note no need to store this in memory since the whole website component will store it
    # and if the split changes, we need a new component anyway
    # but, we can cache it to disk
    assert dataset_name == "example_dataset"
    return DatasetLoaderExample(dataset_name, split)


class DatasetLoaderExample:
    def __init__(self, dataset_name, split):
        self.base_path = Path(DATA_PATH)
        self.dataset_name = dataset_name
        self.split = split
        self.meta_ll, self.meta_hl = self._load_metadata()
        self.subsets = self._create_subsets()

    def get_metadata(self):
        return self.meta_ll, self.meta_hl

    def get_subsets(self):
        return self.subsets

    def _load_metadata(self):
        dataset_path = self.base_path / self.dataset_name
        assert dataset_path.is_dir(), f"Path {dataset_path} not found."

        meta_lowlevel = json.load((dataset_path / f"meta_{self.split}_lowlevel.json").open(
                encoding="utf-8"))
        meta_highlevel = json.load((dataset_path / f"meta_{self.split}_highlevel.json").open(
                encoding="utf-8"))
        return meta_lowlevel, meta_highlevel

    def _create_subsets(self):
        meta_lowlevel, meta_highlevel = self.meta_ll, self.meta_hl
        # sort data into groups for analysis
        # here, classify the questions with a simple heuristic
        group_questions = {"number": [], "yesno": []}
        for lowlevel_id, lowlevel_data in meta_lowlevel.items():
            if lowlevel_data["question"].lower().startswith("how many"):
                group_questions["number"].append(lowlevel_id)
            else:
                group_questions["yesno"].append(lowlevel_id)

        # format {group_name: {"title": x, "description": y, "subsets": { subset_name:  [ids] } } }
        return {"all": {
                "title": "All",
                "description": "All questions",
                "subsets": {"all": list(meta_lowlevel.keys())}},
                "question_type": {
                        "title": "question type",
                        "description": "Group data by start of question.",
                        "subsets": group_questions}}


def filter_data_given_lowlevel_ids(lowlevel_ids, meta_lowlevel, meta_highlevel):
    new_lowlevel_ids = set(lowlevel_ids)
    new_meta_lowlevel = {}
    new_hl_keys = []
    for k, v in meta_lowlevel.items():
        if k in new_lowlevel_ids:
            new_meta_lowlevel[str(k)] = deepcopy(v)
            new_hl_keys.append(str(v["highlevel_id"]))
    new_meta_highlevel = {}
    new_hl_keys = set(new_hl_keys)
    for k, v in meta_highlevel.items():
        if str(k) in new_hl_keys:
            new_ll_ids = []
            for qid in v["lowlevel_ids"]:
                if str(qid) in new_meta_lowlevel:
                    new_ll_ids.append(str(qid))
            new_v = deepcopy(v)
            new_v["lowlevel_ids"] = new_ll_ids
            new_meta_highlevel[str(k)] = new_v
    new_sum_ll = sum(len(v['lowlevel_ids']) for v in new_meta_highlevel.values())
    assert new_sum_ll == len(new_meta_lowlevel)
    return new_meta_lowlevel, new_meta_highlevel
