"""
Start streamlit multipage app

Usage:
    # development
    streamlit run --server.runOnSave true run_app.py -- --debug

    # production
    streamlit run run_app.py

Reference:
    streamlit run [script] [streamlit_args] -- [script_args]

"""
import argparse

import streamlit as st
import streamlit_permalink as stp
from streamlit import config

from streamlit_vis import app_example, app_visualizer
from streamlit_vis.st_utils import G_APP


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--show_config", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    debug = args.debug

    if args.show_config:
        config.show_config()

    config.set_option("browser.gatherUsageStats", False)
    config.set_option("global.developmentMode", debug)  # options in top right menu
    st.set_page_config(
            page_title="Visualizer",
            page_icon="home",
            layout="wide",
            # initial_sidebar_state="collapsed",
            menu_items={
                    'Get help': 'https://help',
                    'Report a bug': "https://bug",
                    'About': "*About* page"
            }
    )

    apps = {
            "Visualizer": {"function": app_visualizer.app},
            "Example": {"function": app_example.app},
    }

    with st.sidebar:
        selected_page = stp.selectbox("App", list(apps.keys()), index=0,
                                      help="Example navigation help", url_key=G_APP)

    page = apps[selected_page]
    page["function"]()


if __name__ == "__main__":
    main()
