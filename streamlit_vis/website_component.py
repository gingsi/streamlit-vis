import json
import time
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any

import numpy as np
import streamlit as st

from streamlit_vis.dataset_loader import filter_data_given_lowlevel_ids, DatasetLoaderExample
from streamlit_vis.st_utils import (
    DATA_PATH, THUMBNAIL_SIZE, create_thumbnail, PAGES, G_PAGE,
    METRIC_NAME, logger)


class WebsiteComponent:
    def __init__(self, data_dir_base=DATA_PATH):
        logger.info(f"Create website component")
        self.meta_ll, self.meta_hl, self.keys_ll, self.keys_hl = None, None, None, None
        self.loaded = False
        self.data_dir_base = Path(data_dir_base)

    def on_reload(self):
        self.url_get_params = st.experimental_get_query_params()
        self.url_get_params_init = deepcopy(self.url_get_params)

    def get_param(self, name, default=None, cast=None):
        params = self.url_get_params.get(name, [default])
        assert len(params) == 1, f"Expected 1 value for get param {name}, got {len(params)}"
        param = params[0]
        if cast is not None and param is not None:
            return cast(param)
        return param

    def set_param(self, name, value):
        self.url_get_params[name] = [value]

    def set_params(self, **update_dict):
        self.url_get_params.update(update_dict)

    def clear_params(self):
        self.url_get_params = {}

    def on_close(self):
        if self.url_get_params != self.url_get_params_init:
            print(f"Get params changed, reloading website! "
                  f"Setting new params: {self.url_get_params}")
            st.experimental_set_query_params(**self.url_get_params)
            # streamlit bug: without sleep, the rerun kills the website before the set_query_params
            # reaches the browser, the url is never updated. todo report bug or find workaround
            time.sleep(.1)
            st.experimental_rerun()

    def load_dataset(self, dataset_name="example_dataset", split="train"):
        if self.loaded:
            return self.meta_ll, self.meta_hl
        self.dataset_name = dataset_name
        self.split = split
        self.dataset_loader = DatasetLoaderExample(self.dataset_name, self.split)

        logger.info(f"Reload dataset {dataset_name} split {split}")
        self.meta_ll, self.meta_hl = self.dataset_loader.get_metadata()

        self.loaded = True
        self.data_dir = self.data_dir_base / dataset_name
        self.thumbnail_dir = self.data_dir / "thumbnails"

        self.update_keys()
        self.subsets = self.dataset_loader.get_subsets()

    def load_subset(self, group_name, subset_name):
        qids = self.subsets[group_name]["subsets"][subset_name]
        new_meta, new_meta_hl = filter_data_given_lowlevel_ids(
                qids, self.meta_ll, self.meta_hl)
        return new_meta, new_meta_hl

    def load_results(self):
        # load predictions
        # format: {model_name: {lowlevel_id: prediction}}
        preds = json.load(open(self.data_dir / f"preds_{self.split}.json", encoding="utf8"))

        # compute metrics per individual prediction
        # format: {model_name: {lowlevel_id: {metric_name: metric_value}}}
        metrics_per_datapoint = {}
        for model_name, model_preds in preds.items():
            metrics_per_datapoint[model_name] = {}
            for lowlevel_id, lowlevel_data in self.meta_ll.items():
                gt_answer = lowlevel_data["answer"]
                model_answer = model_preds[lowlevel_id]
                acc = float(gt_answer == model_answer)
                metrics_per_datapoint[model_name][lowlevel_id] = {METRIC_NAME: acc}

        # compute average metrics per subset
        # note group_name "all" subset_name "all" will give the average over the whole dataset
        # format: {model_name: {metric_name: {group_name: {subset_name: metric_value}}}}
        results = {}
        for model_name, model_preds in preds.items():
            results[model_name] = {METRIC_NAME: {}}
            for group_name, group_info in self.subsets.items():
                group_results = {}
                for subset_name, subset_ll_ids in group_info["subsets"].items():
                    subset_acc = float(np.mean([metrics_per_datapoint[
                                                    model_name][qid][METRIC_NAME] for qid in
                                                subset_ll_ids]))
                    group_results[subset_name] = subset_acc
                results[model_name][METRIC_NAME][group_name] = group_results

        self.preds, self.metrics_per_datapoint, self.results = (
                preds, metrics_per_datapoint, results)

    def update_keys(self):
        self.keys_ll, self.keys_hl = list(self.meta_ll.keys()), list(self.meta_hl.keys())
        self.key2num_ll = {k: i for i, k in enumerate(self.keys_ll)}
        self.key2num_hl = {k: i for i, k in enumerate(self.keys_hl)}

    def get_thumbnail_file(self, image_id):
        if not self.loaded:
            return None
        thumb_size = THUMBNAIL_SIZE
        thumbnail_file = self.thumbnail_dir / f"{image_id}_{thumb_size}.jpg"
        if not thumbnail_file.is_file():
            image_file = self.get_image_file(image_id)
            create_thumbnail(image_file, thumbnail_file, longer_side=thumb_size)
        return thumbnail_file

    def get_image_file(self, image_id):
        return self.data_dir_base / self.meta_hl[str(image_id)]["image_file"]

    def create_nav_button(
            self, title, is_enabled: bool, state_update: Dict[str, Any], parent=None, key=None):
        parent = st if parent is None else parent
        debug_str = ""
        if parent.button(f"{title} {debug_str}", disabled=not is_enabled, key=key):
            self.set_params(**state_update)

    def create_nav_menu(self, current_page):
        # in addition to the left side select box, create a top bar with buttons
        cont = st.container()
        cols = cont.columns([3] + [1] * len(PAGES), gap="small")
        cols[0].markdown(f"**Navigate**")
        for i in range(3):
            col = cols[i + 1]
            page = PAGES[i]
            self.create_nav_button(page, current_page != page, {G_PAGE: page}, parent=col)

    def load_subset_for_page(self, group_name="", subset_name="", search=""):
        keys_hl = self.keys_hl
        meta_hl = self.meta_hl
        meta_ll = self.meta_ll
        keys_ll = self.keys_ll
        key2num = self.key2num_ll
        key2num_hl = self.key2num_hl

        output_text = []
        if group_name == "":
            output_text.append(f"Showing all questions for split *{self.split}*.")
            recompute_keys = False
        else:
            group_info = self.subsets[group_name]
            group_desc = group_info["description"]
            group_title = group_info["title"]
            output_text.append(
                    f"Filter split **{self.split}** group **{group_title}** "
                    f"subset **{subset_name}**. "
                    f"Group description: {group_desc}")
            meta_ll, meta_hl = self.load_subset(group_name, subset_name)
            recompute_keys = True
        output_text.append(f"Total {len(keys_hl)} images, {len(keys_ll)} questions.")
        st.markdown(" ".join(output_text))

        if search != "":
            search = search.lower().strip()
            qids = []
            for qid, item in meta_ll.items():
                question = item["question"]
                if search in question.lower():
                    qids.append(qid)
            new_meta, new_meta_hl = filter_data_given_lowlevel_ids(
                    qids, meta_ll, meta_hl)
            meta_ll, meta_hl = new_meta, new_meta_hl
            recompute_keys = True

        if recompute_keys:
            keys_ll, keys_hl = list(meta_ll.keys()), list(meta_hl.keys())
            key2num = {k: i for i, k in enumerate(keys_ll)}
            key2num_hl = {k: i for i, k in enumerate(keys_hl)}

        if search != "":
            st.markdown(f"Search found {len(keys_ll)} questions, search term: '{search}'")

        return meta_ll, meta_hl, keys_ll, keys_hl, key2num, key2num_hl
