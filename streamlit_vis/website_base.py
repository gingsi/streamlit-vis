from abc import ABCMeta
from dataclasses import dataclass
from typing import Dict, Any

import streamlit as st

from streamlit_vis.navigation_base import BrowserComponent
from streamlit_vis.st_utils import logger, ColumnGridGenerator
from streamlit_vis.vis_config_default import WebsiteConfig


@dataclass
class BaseWebsite(metaclass=ABCMeta):
    conf: WebsiteConfig

    def __post_init__(self):
        logger.info(f"Create website component type {type(self).__name__}")
        self.browser = BrowserComponent()
        self.get_param = self.browser.get_param
        self.set_param = self.browser.set_param
        self.set_params = self.browser.set_params

    def on_reload(self):
        """Must be called whenever the site is reloaded, to read the new url get params."""
        self.browser.on_reload()

    def on_complete(self):
        """Must be called after the site is rendered. If the get params have changed, the site
        will be reloaded."""
        self.browser.on_complete()

    def reset_page(self):
        self.browser.clear_params()

    def get_pagination_params(self):
        pagenum = self.get_param(self.conf.G_PAGENUM, 0, int)
        perpage = self.conf.PERPAGE
        return pagenum, perpage

    def render_nav_button(
            self, title, is_enabled: bool, state_update: Dict[str, Any], parent=None, key=None):
        """Create a button that updates the url get params using "state_update" when clicked."""
        parent = st if parent is None else parent
        debug_str = ""
        if parent.button(f"{title} {debug_str}", disabled=not is_enabled, key=key):
            self.set_params(**state_update)

    def render_nav_menu(self, current_page):
        # instead of the left side select box, create a top bar with buttons
        c = self.conf
        pages = c.PAGES
        n_pages = len(pages)
        n_columns = c.BUTTON_COLUMNS

        def _create_button(k, target_page, parent):
            self.render_nav_button(
                    target_page, current_page != target_page, {c.G_PAGE: target_page},
                    parent=parent, key=f"button_{target_page}_{k}")

        cont = st.container()
        if n_pages <= n_columns - 1:
            # fits into one row, add label and right align the buttons
            cols = cont.columns([n_columns - n_pages] + [1] * n_pages, gap="small")
            cols[0].markdown(f"**Navigate**")
            for i, page in enumerate(pages):
                col = cols[i + 1]
                _create_button(i, page, col)
        else:
            # does not fit into one row, put buttons into a left aligned grid without label
            grid = ColumnGridGenerator(n_columns)
            for i, page in enumerate(pages):
                col = grid.next_column()
                _create_button(i, page, col)
