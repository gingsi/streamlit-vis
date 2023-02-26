import pandas as pd
import streamlit as st
from matplotlib import colors as mpl_colors
from pandas.io.formats.style import Styler

from streamlit_vis.example_website.website import ExampleWebsite
from streamlit_vis.st_utils import modify_css, read_image_for_streamlit
from streamlit_vis.website_dataset import StopRunning


def render_details_page(website: ExampleWebsite):
    c = website.conf
    modify_css(c)

    st.markdown("# Details")
    metadata_object = website.get_metadata_given_url_params()
    website.render_nav_menu("details")
    try:
        current_leaf_id, current_root_id = website.render_pagination_for_leaf(metadata_object)
    except StopRunning:
        return

    leaf_meta, _root_meta, _leaf_ids, _root_ids, _leaf_id2num, _root_id2num = metadata_object

    # render image and qa
    leaf_item = leaf_meta[current_leaf_id]
    image_file = website.dataset.get_image_file(current_root_id)
    st.image(read_image_for_streamlit(image_file), use_column_width=False)
    st.markdown(f"*Question:* {leaf_item['question']}")
    st.markdown(f"*Answer:* {leaf_item['answer']}")

    # show a dataframe with all model predictions
    predictions, metrics_per_datapoint, subset_results = website.get_results()
    model_names = list(subset_results.keys())
    data_dict = {"model": model_names, "answer": [], "acc%": [], }

    for model_name, _result in subset_results.items():
        answer = predictions[model_name][current_leaf_id]
        data_dict["answer"].append(answer)
        acc = metrics_per_datapoint[model_name][c.METRIC_NAME][current_leaf_id]
        data_dict["acc%"].append(acc * 100)

    df = pd.DataFrame(data_dict)
    ccmap = mpl_colors.LinearSegmentedColormap.from_list('rg', [[0.5, 0, 0], [0, 0.3, 0]])

    def apply_style(df_styler: Styler):
        df_styler.background_gradient(cmap=ccmap, axis=1, vmin=0, vmax=100)
        df_styler.format({"acc%": "{:.0f}%"})
        return df_styler

    styler = df.style.pipe(apply_style)
    st.dataframe(styler)
