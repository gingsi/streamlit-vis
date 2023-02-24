import logging
import os
from pathlib import Path
from typing import Union

import numpy as np
import streamlit as st
from PIL import Image
from importlib_resources import files

import streamlit_vis
from streamlit_vis.vis_config_default import default_config

logger = logging.getLogger("streamlit_vis")
PathType = Union[Path, str]


def modify_css(conf=default_config, button_columns=True, image_columns=False):
    """See the respective CSS files for details."""
    # noinspection PyTypeChecker
    package_files = files(streamlit_vis)
    css_dir = package_files / "static"
    css_main = (css_dir / "style.css").read_text(encoding="utf-8")
    css_appends = []
    if button_columns:
        css_appends.append((css_dir / "style_button_columns.css").read_text(encoding="utf-8"))
    if image_columns:
        css_appends.append((css_dir / "style_image_columns.css").read_text(encoding="utf-8"))
    st.markdown("\n".join([
            "<style>",
            ":root {",
            f"--imagesize: {conf.THUMBNAIL_SIZE:d}px;",
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


class ColumnGridGenerator:
    def __init__(self, n_columns: int):
        self.i = 0
        self.n_columns = n_columns
        self.columns = None

    def next_column(self):
        col_i = self.i % self.n_columns
        if col_i == 0:
            cont = st.container()
            self.columns = cont.columns(self.n_columns, gap="small")
        self.i += 1
        return self.columns[col_i]

    def __iter__(self):
        return self

    def __next__(self):
        return self.next_column()


def read_image_for_streamlit(file: Union[str, Path]):
    # inefficient to load from file to array, then let streamlit convert it back.
    # it would be better to let the browser directly render given binary (e.g. jpeg) data

    # noinspection PyTypeChecker
    return np.asarray(Image.open(file).convert("RGB"))
