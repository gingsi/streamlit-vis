from streamlit import config

config.set_option("browser.gatherUsageStats", False)
config.set_option("global.developmentMode", True)  # options in top right menu
port = config.get_option("browser.serverPort")
print(f"  Local URL: http://localhost:{port}")
print()

import streamlit as st
import streamlit_permalink as stp

from streamlit_vis.example_website import app_visualizer, app_example
from streamlit_vis.example_website.config import ExampleWebsiteConfig as conf

from streamlit.error_util import handle_uncaught_app_exception

# to activate hard errors (i.e. the server actually crashing on exceptions)
# add `raise ex` as first line to this function
_ = handle_uncaught_app_exception


def main():
    st.set_page_config(page_title="Visualizer", page_icon="home", layout="wide",
                       menu_items={'Get help': 'https://a', 'Report a bug': "https://b",
                                   'About': "*About* page"})
    apps = {"Visualizer": {"function": app_visualizer.app},
            "Example": {"function": app_example.app}, }
    with st.sidebar:
        selected_page = stp.selectbox("App", list(apps.keys()), index=0,
                                      help="Example navigation help", url_key=conf.G_APP)
    page = apps[selected_page]
    page["function"]()


if __name__ == "__main__":
    main()
