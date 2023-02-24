from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import joblib

from streamlit_vis.data_utils import filter_data_given_leaf_ids_cached
from streamlit_vis.st_utils import logger, PathType, create_thumbnail


@dataclass
class VisionDatasetComponent(metaclass=ABCMeta):
    """
    Component for a hierarchical vision dataset.
    """
    name: str
    split: str
    dataroot_dir: PathType
    thumbnail_size: int

    def __post_init__(self):
        logger.info(f"Reload dataset {self}")
        self.dataroot_dir = Path(self.dataroot_dir)
        self.dataset_dir = self.dataroot_dir / self.name
        self.leaf_meta, self.root_meta, self.subsets = None, None, None
        self.thumbnail_dir = self.dataroot_dir / self.name / "thumbnails"

    def preload_everything(self):
        """Use in case we do not want to lazy load, but load everything at once"""
        self.get_metadata()
        self.get_subsets()

    def get_metadata(self):
        if self.leaf_meta is None or self.root_meta is None:
            self.leaf_meta, self.root_meta = self._load_metadata()
            self._update_keys()
        return self.leaf_meta, self.root_meta

    def get_subsets(self):
        if self.subsets is None:
            self.subsets = self._load_subsets()
        return self.subsets

    def get_metadata_for_subset(self, group_name, subset_name):
        leaf_ids = self.subsets[group_name]["subsets"][subset_name]
        cache_key = joblib.hash((self.name, self.split, group_name, subset_name))
        new_leaf_meta, new_root_meta = filter_data_given_leaf_ids_cached(
                cache_key, leaf_ids, self.leaf_meta, self.root_meta)
        return new_leaf_meta, new_root_meta

    def _update_keys(self):
        """Set the metadata keys given the metadata"""
        self.leaf_keys, self.root_keys = list(self.leaf_meta.keys()), list(self.root_meta.keys())
        self.leaf_key2num = {k: i for i, k in enumerate(self.leaf_keys)}
        self.root_key2num = {k: i for i, k in enumerate(self.root_keys)}

    @abstractmethod
    def _load_metadata(self):
        """Set self.leaf_meta and self.root_meta from disk
        leaf_meta: {leaf_id: {"root_id": root_id, key1: value1, ...}}
        root_meta: {root_id: {key1: value1, ...}}
        """

    @abstractmethod
    def _load_subsets(self):
        """Set self.subsets given metadata.
        subsets: {group_name: {"title": x, "description": y, "subsets": { subset_name:  [ids] } } }
        e.g. subsets["question_type"]["subsets"]["number"] -> leaf_ids with question type number
        """

    def get_image_file(self, image_id):
        return self.dataroot_dir / self.root_meta[str(image_id)]["image_file"]

    def get_thumbnail_file(self, image_id):
        thumb_size = self.thumbnail_size
        thumbnail_file = self.thumbnail_dir / f"{image_id}_{thumb_size}.jpg"
        if not thumbnail_file.is_file():
            image_file = self.get_image_file(image_id)
            create_thumbnail(image_file, thumbnail_file, longer_side=thumb_size)
        return thumbnail_file

    def load_metadata_for_page(
            self, group_name="", subset_name="", search_leaf: Optional[Dict[str, str]] = None):
        root_keys = self.root_keys
        root_meta = self.root_meta
        leaf_meta = self.leaf_meta
        leaf_keys = self.leaf_keys
        leaf_key2num = self.leaf_key2num
        root_key2num = self.root_key2num
        name = self.name
        split = self.split
        subsets = self.subsets

        output_text = []
        if group_name == "":
            output_text.append(f"Showing all questions for split *{split}*.")
            recompute_keys = False
        else:
            group_info = subsets[group_name]
            group_desc = group_info["description"]
            group_title = group_info["title"]
            output_text.append(
                    f"Filter split **{split}** group **{group_title}** "
                    f"subset **{subset_name}**. "
                    f"Group description: {group_desc}")
            leaf_meta, root_meta = self.get_metadata_for_subset(group_name, subset_name)
            recompute_keys = True
        output_text.append(f"Total {len(root_meta)} images, {len(leaf_meta)} questions.")

        if search_leaf is not None:
            assert len(search_leaf) == 1, "Only one search field supported"
            search_field, search_value = list(search_leaf.items())[0]
            search_value = search_value.lower().strip()
            if search_value != "":
                leaf_ids = []
                for leaf_id, leaf_item in leaf_meta.items():
                    compare_value = leaf_item[search_field]
                    if search_value in compare_value.lower():
                        leaf_ids.append(leaf_id)

                cache_key = joblib.hash((
                        name, split, group_name, subset_name, search_field, search_value))
                new_meta, new_meta_hl = filter_data_given_leaf_ids_cached(
                        cache_key, leaf_ids, leaf_meta, root_meta)
                leaf_meta, root_meta = new_meta, new_meta_hl
                output_text.append(
                        f"Search for {search_field}={search_value} found {len(leaf_meta)} items.")
                recompute_keys = True

        if recompute_keys:
            leaf_keys, root_keys = list(leaf_meta.keys()), list(root_meta.keys())
            leaf_key2num = {k: i for i, k in enumerate(leaf_keys)}
            root_key2num = {k: i for i, k in enumerate(root_keys)}

        info_text = " ".join(output_text)
        return (leaf_meta, root_meta, leaf_keys, root_keys, leaf_key2num, root_key2num), info_text
