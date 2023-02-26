from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import List, Optional

import streamlit as st

from streamlit_vis.dataset_base import VisionDatasetComponent
from streamlit_vis.st_utils import PathType
from streamlit_vis.website_base import BaseWebsite


class StopRunning(Exception):
    """Signals that the website is done rendering, e.g. there is no data to show."""


@dataclass
class DatasetWebsite(BaseWebsite, metaclass=ABCMeta):
    data_dir_base: Optional[PathType] = None
    text_leaf: str = "question"
    text_root: str = "image"

    def __post_init__(self):
        super().__post_init__()
        if self.data_dir_base is None:
            self.data_dir_base = self.conf.DATA_PATH
        self.data_dir_base = Path(self.data_dir_base)

    @abstractmethod
    def setup_dataset(self, dataset_name: str, dataset_split: str):
        """Should set self.dataset to an instance of VisionDatasetComponent"""
        self.dataset: Optional[VisionDatasetComponent] = None

    @abstractmethod
    def setup_results(self):
        """
        Loads predictions and computes metrics for each prediction.
        Should set the following attributes:
            self.predictions:
                {model_name: {leaf_id: prediction}}
            self.metrics_per_datapoint:
                {model_name: {metric_name: {leaf_id: metric_value}}}
            self.subset_results:
                {model_name: {metric_name: {group_name: {subset_name: metric_aggregated_value}}}}
        """
        self.predictions, self.metrics_per_datapoint, self.subset_results = None, None, None

    def get_metadata_given_url_params(self, write_message=True):
        c = self.conf
        group = self.get_param(c.G_GROUP, "", str)
        subset = self.get_param(c.G_SUBSET, "", str)
        search = self.get_param(c.G_SEARCH, "", str)
        metadata_object, info_text = self.dataset.load_metadata_for_page(
                group, subset, {c.SEARCH_FIELD: search})
        if write_message:
            st.markdown(info_text)
        return metadata_object

    def get_current_leaf_id(self):
        return self.get_param(self.conf.G_LEAF_ID, "", str)

    def get_results(self):
        return self.predictions, self.metrics_per_datapoint, self.subset_results

    def get_subsets(self):
        return self.dataset.get_subsets()

    def render_pagination_for_leaf(self, metadata_object):
        """
        Returns:
            current_leaf_id, current_root_id
        """

        website = self
        c = self.conf
        text_leaf, text_root = self.text_leaf, self.text_root
        leaf_meta, root_meta, leaf_ids, root_ids, leaf_id2num, root_id2num = metadata_object

        # determine current leaf id
        if len(leaf_ids) == 0:
            st.markdown(f"No questions found, clear search field.")
            raise StopRunning

        current_leaf_id = website.get_current_leaf_id()
        if current_leaf_id == "":
            st.markdown(f"No question id given. Showing the first question.")
            current_leaf_id = leaf_ids[0]
        elif current_leaf_id not in leaf_meta:
            st.markdown(f"Question {current_leaf_id} not found. Showing the first question.")
            current_leaf_id = leaf_ids[0]

        leaf_num = leaf_id2num[current_leaf_id]
        leaf_item = leaf_meta[current_leaf_id]
        current_root_id = leaf_item["root_id"]
        root_num = root_id2num[current_root_id]

        # create navigation for questions
        nav_targets = []
        nav_targets.append(("First", leaf_num > 0, {c.G_LEAF_ID: leaf_ids[0]}))
        prev_id = leaf_ids[leaf_num - 1] if leaf_num > 0 else None
        nav_targets.append(("Prev", leaf_num > 0, {c.G_LEAF_ID: prev_id}))
        next_id = leaf_ids[leaf_num + 1] if leaf_num < len(leaf_ids) - 1 else None
        nav_targets.append(("Next", leaf_num < len(leaf_ids) - 1, {c.G_LEAF_ID: next_id}))
        nav_targets.append(("Last", leaf_num < len(leaf_ids) - 1, {c.G_LEAF_ID: leaf_ids[-1]}))
        cont = st.container()
        cols = cont.columns([2] + [1] * len(nav_targets), gap="small")
        cols[0].markdown(f"**{text_leaf}** {leaf_num + 1} of {len(leaf_ids)}<br />"
                         f"(id {current_leaf_id})", unsafe_allow_html=True)
        for i, nav_target in enumerate(nav_targets):
            col = cols[i + 1]
            n_text, n_enabled, n_params = nav_target
            website.render_nav_button(n_text, n_enabled, n_params, parent=col)

        # create navigation for images
        nav_targets = []
        first_image_qid, prev_image_qid = None, None
        if root_num > 0:
            first_image_qid = root_ids[0]
            first_image_qid = root_meta[first_image_qid]["leaf_ids"][0]
            prev_image_id = root_ids[root_num - 1]
            prev_image_qid = root_meta[prev_image_id]["leaf_ids"][0]
        nav_targets.append((f"First {text_root}", first_image_qid is not None,
                            {c.G_LEAF_ID: first_image_qid}))
        nav_targets.append((f"Prev {text_root}", prev_image_qid is not None,
                            {c.G_LEAF_ID: prev_image_qid}))

        next_leaf_id, last_leaf_id = None, None
        if root_num < len(root_ids) - 1:
            next_root_id = root_ids[root_num + 1]
            next_root_item = root_meta[next_root_id]
            next_leaf_id = next_root_item["leaf_ids"][0]
            last_root_id = root_ids[-1]
            last_leaf_id = root_meta[last_root_id]["leaf_ids"][0]
        nav_targets.append((
                f"Next {text_root}", next_leaf_id is not None, {c.G_LEAF_ID: next_leaf_id}))
        nav_targets.append((
                f"Last {text_root}", last_leaf_id is not None, {c.G_LEAF_ID: last_leaf_id}))

        cont = st.container()
        cols = cont.columns([2] + [1] * len(nav_targets), gap="small")
        cols[0].markdown(
                f"**{text_root}** {root_num + 1} of {len(root_ids)}<br />(id {current_root_id})",
                unsafe_allow_html=True)
        for i, nav_target in enumerate(nav_targets):
            col = cols[i + 1]
            n_text, n_enabled, n_params = nav_target
            website.render_nav_button(n_text, n_enabled, n_params, parent=col)

        return current_leaf_id, current_root_id

    def render_pagination_for_overview(self, metadata_object) -> List[str]:
        """
        Returns:
            list of root ids that are currently displayed
        """
        website = self
        c = self.conf
        _leaf_meta, _root_meta, _leaf_ids, root_ids, _leaf_id2num, _root_id2num = metadata_object

        # compute current position
        pagenum, perpage = website.get_pagination_params()
        n_pages = ceil(len(root_ids) / perpage)
        if n_pages == 0:
            st.markdown(f"No data found, clear search field.")
            raise StopRunning
        if pagenum >= n_pages:
            st.markdown(f"Page {pagenum} is out of range. Showing the first page.")
            pagenum = 0

        start = pagenum * perpage
        end = start + perpage
        current_root_ids = root_ids[start:end]
        assert n_pages > pagenum >= 0, pagenum
        assert len(current_root_ids) > 0

        # render navigation
        cont = st.container()
        cols = cont.columns([2, 1, 1, 1, 1], gap="small")
        cols[0].write(f"Page {pagenum + 1} of {n_pages}")
        website.render_nav_button(
                "First", pagenum > 0, {c.G_PAGENUM: 0}, parent=cols[1])
        website.render_nav_button(
                "Prev", pagenum > 0, {c.G_PAGENUM: pagenum - 1}, parent=cols[2])
        website.render_nav_button(
                "Next", pagenum < n_pages - 1, {c.G_PAGENUM: pagenum + 1}, parent=cols[3])
        website.render_nav_button(
                "Last", pagenum < n_pages - 1, {c.G_PAGENUM: n_pages - 1}, parent=cols[4])
        return current_root_ids
