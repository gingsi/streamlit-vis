from math import ceil

import streamlit as st

from streamlit_vis.st_utils import (
    read_image_for_streamlit, logger, PERPAGE, modify_css, G_PAGENUM, G_GROUP, G_SUBSET, G_SEARCH,
    G_LOWLEVEL_ID, G_PAGE)
from streamlit_vis.website_component import WebsiteComponent


def render_overview_page(comp: WebsiteComponent):
    modify_css(["button_columns", "image_columns"])
    st.markdown("# Overview")

    # read get parameters
    pagenum = comp.get_param(G_PAGENUM, 0, int)
    perpage = PERPAGE
    group = comp.get_param(G_GROUP, "", str)
    subset = comp.get_param(G_SUBSET, "", str)
    search = comp.get_param(G_SEARCH, "", str)

    # load dataset
    meta_ll, meta_hl, keys_ll, keys_hl, _key2num_ll, _key2num_hl = comp.load_subset_for_page(
            group, subset, search)

    # render page navigation
    comp.create_nav_menu("overview")

    # compute current position
    n_pages = ceil(len(keys_hl) / perpage)
    pagenum = int(pagenum)
    perpage = int(perpage)
    start = pagenum * perpage
    end = start + perpage
    image_ids = keys_hl[start:end]
    assert pagenum >= 0, pagenum
    if len(image_ids) == 0:
        if n_pages > 0:
            logger.info(f"Page {pagenum} is out of range, returning to first page.")
            comp.set_param(G_PAGENUM, 0)
        else:
            st.markdown(f"No data found, clear search field.")
        return

    # load data for current position
    thumbnails = {key: comp.get_thumbnail_file(key) for key in image_ids}
    lowlevel_ids = {key: meta_hl[key]["lowlevel_ids"] for key in image_ids}
    lowlevel_data = {qid: meta_ll[qid]
                     for key, qids in lowlevel_ids.items()
                     for qid in qids}

    # render navigation
    cont = st.container()
    cols = cont.columns([2, 1, 1, 1, 1], gap="small")
    cols[0].write(f"Page {pagenum + 1} of {n_pages}")
    comp.create_nav_button("First", pagenum > 0, {G_PAGENUM: 0}, parent=cols[1])
    comp.create_nav_button("Prev", pagenum > 0, {G_PAGENUM: pagenum - 1}, parent=cols[2])
    comp.create_nav_button("Next", pagenum < n_pages - 1, {G_PAGENUM: pagenum + 1}, parent=cols[3])
    comp.create_nav_button("Last", pagenum < n_pages - 1, {G_PAGENUM: n_pages - 1}, parent=cols[4])

    # render images
    cont = st.tabs(["Images and questions"])[0]
    cols = cont.columns(len(image_ids), gap="small")
    for i, image_id in enumerate(image_ids):
        col = cols[i]
        col.image(read_image_for_streamlit(thumbnails[image_id]),
                  use_column_width=False)
        for lowlevel_id in lowlevel_ids[image_id]:
            q_data = lowlevel_data[lowlevel_id]
            comp.create_nav_button(
                    q_data['question'], True, {G_LOWLEVEL_ID: lowlevel_id, G_PAGE: "details"},
                    parent=col,
                    key=f"qbutton_{lowlevel_id}")
            col.markdown(f"Label: **{q_data['answer']}**")
