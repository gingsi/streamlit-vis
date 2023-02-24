import streamlit as st
import streamlit_permalink as stp

from streamlit_vis.example_website.config import ExampleWebsiteConfig as conf
from streamlit_vis.example_website.page_details import render_details_page
from streamlit_vis.example_website.page_overview import render_overview_page
from streamlit_vis.example_website.page_results import render_results_page
from streamlit_vis.example_website.website import ExampleWebsite
from streamlit_vis.st_utils import logger


def app():
    logger.info("---------- App restart")
    pages = {
            conf.PAGES[0]: render_overview_page,
            conf.PAGES[1]: render_details_page,
            conf.PAGES[2]: render_results_page,
    }

    with st.sidebar:
        page = stp.selectbox("Page", list(pages.keys()), index=0, help="", url_key=conf.G_PAGE)
        datasets = conf.DATASETS.keys()
        dataset_name = stp.selectbox("Dataset", datasets, index=0, url_key=conf.G_DATASET)
        splits = conf.DATASETS[dataset_name]
        dataset_split = stp.selectbox(
                "Split", splits, index=0, url_key=conf.G_SPLIT)
        _search = stp.text_input("Search for question", "", url_key=conf.G_SEARCH)

    ds_state_key = f"dataloader_{dataset_name}_{dataset_split}"
    website_component = st.session_state.get(ds_state_key, None)
    if website_component is None:
        # first time setup
        website_component = ExampleWebsite(conf())
        website_component.on_reload()
        website_component.setup_dataset(dataset_name, dataset_split)
        website_component.setup_results()
        logger.info("Initialization complete")
        st.session_state[ds_state_key] = website_component
    else:
        website_component.on_reload()

    with st.sidebar:
        if st.button("Reset page"):
            website_component.reset_page()

    pages[page](website_component)
    website_component.on_complete()
