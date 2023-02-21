import logging
import os
from pathlib import Path
from typing import Union, Optional, List

import numpy as np
import streamlit as st
from PIL import Image
from importlib_resources import files

import streamlit_vis

logger = logging.getLogger("streamlit_vis")
THUMBNAIL_SIZE = 280
PERPAGE = 5
DATA_PATH = Path("data")
MODEL_NAMES = ["random", "sayyes", "oracle"]
METRIC_NAME = "acc"
METRIC_FORMAT = {"acc": "{:.0%}"}
DATASETS = {"example_dataset": ["train", "val"]}
PAGES = ["overview", "details", "results"]

# url get parameters, short parameter names to avoid getting too long urls
G_PAGENUM = "pn"
G_GROUP = "g"
G_SUBSET = "su"
G_SEARCH = "se"
G_LOWLEVEL_ID = "lli"
G_PAGE = "p"
G_APP = "a"
G_DATASET = "d"
G_SPLIT = "sp"


def modify_css(css_names: Optional[List[str]] = None):
    """
    See the CSS files for details. Uses importlib_resources (a backport from python 3.10)
    to find the files relative to this package.
    """
    # noinspection PyTypeChecker
    package_files = files(streamlit_vis)
    css_main = (package_files / "static" / "style.css").read_text(encoding="utf-8")
    css_appends = []
    if css_names is not None:
        for css_name in css_names:
            css_appends.append((package_files / "static" / f"style_{css_name}.css"
                                ).read_text(encoding="utf-8"))
    st.markdown("\n".join([
            "<style>",
            ":root {",
            f"--imagesize: {THUMBNAIL_SIZE:d}px;",
            "}",
            css_main,
            *css_appends,
            "</style>"]),
            unsafe_allow_html=True)


def create_thumbnail(input_file, output_file, longer_side: int = 200):
    input_file = Path(input_file)
    img = Image.open(input_file)
    w, h = img.width, img.height

    # resize longer side to target size
    if w > h:
        w_new = longer_side
        h_new = round(h * longer_side / w)
    else:
        h_new = longer_side
        w_new = round(w * longer_side / h)
    # noinspection PyUnresolvedReferences
    img = img.resize((w_new, h_new), Image.Resampling.LANCZOS)

    output_file = Path(output_file)
    os.makedirs(output_file.parent, exist_ok=True)
    img.save(output_file)


def read_image_for_streamlit(file: Union[str, Path]):
    # inefficient to load from file to array, then let streamlit convert it back.
    # it would be better to let the browser directly render given binary (e.g. jpeg) data

    # noinspection PyTypeChecker
    return np.asarray(Image.open(file).convert("RGB"))
