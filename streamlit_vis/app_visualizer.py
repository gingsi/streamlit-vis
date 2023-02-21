import streamlit as st
import streamlit_permalink as stp

from streamlit_vis.page_details import render_details_page
from streamlit_vis.page_overview import render_overview_page
from streamlit_vis.page_results import render_results_page
from streamlit_vis.st_utils import (
    DATASETS, G_SEARCH, G_SPLIT, G_DATASET, G_PAGE, PAGES, logger)
from streamlit_vis.website_component import WebsiteComponent


def app():
    logger.info("---------- App restart")
    pages = {
            PAGES[0]: render_overview_page,
            PAGES[1]: render_details_page,
            PAGES[2]: render_results_page,
    }

    with st.sidebar:
        page = stp.selectbox("Page", list(pages.keys()), index=0, help="", url_key=G_PAGE)
        datasets = DATASETS.keys()
        dataset_name = stp.selectbox("Dataset", datasets, index=0, url_key=G_DATASET)
        splits = DATASETS[dataset_name]
        dataset_split = stp.selectbox(
                "Split", splits, index=0, url_key=G_SPLIT)
        _search = stp.text_input("Search for question", "", url_key=G_SEARCH)

    # only load the website component if it doesnt exist in memory yet
    ds_state_key = f"dataloader_{dataset_name}_{dataset_split}"
    website_component = st.session_state.get(ds_state_key, None)
    if website_component is None:
        website_component = WebsiteComponent()
        website_component.load_dataset(dataset_name, dataset_split)
        website_component.load_results()
        logger.info("Initialization complete")
        st.session_state[ds_state_key] = website_component

    website_component.on_reload()

    with st.sidebar:
        if st.button("Reset page"):
            website_component.clear_params()

    pages[page](website_component)
    website_component.on_close()
