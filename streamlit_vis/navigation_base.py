import time
from copy import deepcopy

import streamlit as st

from streamlit_vis.st_utils import logger


class BrowserComponent:
    """Handles the browser navigation with url get params."""

    def on_reload(self):
        self.url_get_params = st.experimental_get_query_params()
        self.url_get_params_init = deepcopy(self.url_get_params)

    def on_complete(self):
        if self.url_get_params != self.url_get_params_init:
            logger.info(f"Get params changed, reloading website! "
                        f"Setting new params: {self.url_get_params}")
            st.experimental_set_query_params(**self.url_get_params)
            # streamlit bug: without sleep, the rerun kills the website before the set_query_params
            # reaches the browser, the url is never updated. todo report bug or find workaround
            time.sleep(.1)
            st.experimental_rerun()

    def get_param(self, name, default=None, cast=None):
        params = self.url_get_params.get(name, [default])
        if len(params) > 1:
            logger.warning("Expected 1 value for get param {name}, got {len(params)}")
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
