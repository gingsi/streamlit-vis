import streamlit as st

from streamlit_vis.example_website.website import ExampleWebsite
from streamlit_vis.st_utils import read_image_for_streamlit, modify_css
from streamlit_vis.website_dataset import StopRunning


def render_overview_page(website: ExampleWebsite):
    c = website.conf
    modify_css(c, image_columns=True)

    st.markdown("# Overview")
    metadata_object = website.get_metadata_given_url_params()
    website.render_nav_menu("overview")

    try:
        current_root_ids = website.render_pagination_for_overview(metadata_object)
    except StopRunning:
        return

    leaf_meta, root_meta, _leaf_ids, _root_ids, _leaf_id2num, _root_id2num = metadata_object

    # render images
    thumbnails = {root_id: website.dataset.get_thumbnail_file(root_id) for root_id in
                  current_root_ids}
    cont = st.tabs(["Images and questions"])[0]
    cols = cont.columns(len(current_root_ids), gap="small")
    for i, root_id in enumerate(current_root_ids):
        col = cols[i]
        col.image(read_image_for_streamlit(thumbnails[root_id]),
                  use_column_width=False)
        leaf_ids_for_root = root_meta[root_id]["leaf_ids"]
        for leaf_id in leaf_ids_for_root:
            leaf_data = leaf_meta[leaf_id]
            website.render_nav_button(
                    leaf_data['question'], True, {c.G_LEAF_ID: leaf_id, c.G_PAGE: "details"},
                    parent=col, key=f"qbutton_{leaf_id}")
            col.markdown(f"Label: **{leaf_data['answer']}**")
