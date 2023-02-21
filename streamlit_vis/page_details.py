import pandas as pd
import streamlit as st
from matplotlib import colors as mpl_colors
from pandas.io.formats.style import Styler

from streamlit_vis.st_utils import (
    modify_css, read_image_for_streamlit, G_LOWLEVEL_ID, G_GROUP, G_SUBSET, G_SEARCH, METRIC_NAME)
from streamlit_vis.website_component import WebsiteComponent


def render_details_page(comp: WebsiteComponent):
    modify_css(["button_columns"])
    st.markdown("# Details")

    # read get parameters
    lowlevel_id = comp.get_param(G_LOWLEVEL_ID, 0, int)
    lowlevel_id = str(lowlevel_id)
    group = comp.get_param(G_GROUP, "", str)
    subset = comp.get_param(G_SUBSET, "", str)
    search = comp.get_param(G_SEARCH, "", str)

    # load dataset
    meta, meta_hl, keys, keys_hl, key2num, key2num_hl = comp.load_subset_for_page(
            group, subset, search)
    comp.create_nav_menu("details")

    # in case the data selection changes and the question is not available anymore
    # load the first existing question instead or stop
    if lowlevel_id not in meta:
        if len(keys) > 0:
            st.markdown(f"Question {lowlevel_id} not found. "
                        f"Reading the first question instead.")
            lowlevel_id = keys[0]
        else:
            st.markdown(f"No questions found, clear search field.")
            return

    item_ll = meta[lowlevel_id]
    image_id = item_ll["highlevel_id"]

    # navigate questions
    question_num = key2num[lowlevel_id]
    image_num = key2num_hl[image_id]

    nav_targets = []
    param_key = G_LOWLEVEL_ID
    nav_targets.append(("First", question_num > 0, {param_key: keys[0]}))
    prev_id = keys[question_num - 1] if question_num > 0 else None
    nav_targets.append(("Prev", question_num > 0, {param_key: prev_id}))
    next_id = keys[question_num + 1] if question_num < len(keys) - 1 else None
    nav_targets.append(("Next", question_num < len(keys) - 1, {param_key: next_id}))
    nav_targets.append(("Last", question_num < len(keys) - 1, {param_key: keys[-1]}))
    cont = st.container()
    cols = cont.columns([2] + [1] * len(nav_targets), gap="small")
    cols[0].markdown(f"**Question** {question_num + 1} of {len(keys)}<br />(id {lowlevel_id})",
                     unsafe_allow_html=True)
    for i, nav_target in enumerate(nav_targets):
        col = cols[i + 1]
        n_text, n_enabled, n_params = nav_target
        comp.create_nav_button(n_text, n_enabled, n_params, parent=col)

    # navigate images
    nav_targets = []
    first_image_qid, prev_image_qid = None, None
    if image_num > 0:
        first_image_qid = keys_hl[0]
        first_image_qid = meta_hl[first_image_qid]["lowlevel_ids"][0]
        prev_image_id = keys_hl[image_num - 1]
        prev_image_qid = meta_hl[prev_image_id]["lowlevel_ids"][0]

    next_image_qid, last_image_qid = None, None
    if image_num < len(keys_hl) - 1:
        next_image_id = keys_hl[image_num + 1]
        next_meta_hl = meta_hl[next_image_id]
        next_image_qid = next_meta_hl["lowlevel_ids"][0]
        last_image_id = keys_hl[-1]
        last_image_qid = meta_hl[last_image_id]["lowlevel_ids"][0]

    nav_targets.append(("First image", first_image_qid is not None,
                        {param_key: first_image_qid}))
    nav_targets.append(("Prev image", prev_image_qid is not None,
                        {param_key: prev_image_qid}))
    nav_targets.append(("Next image", next_image_qid is not None,
                        {param_key: next_image_qid}))
    nav_targets.append(("Last image", last_image_qid is not None,
                        {param_key: last_image_qid}))

    cont = st.container()
    cols = cont.columns([2] + [1] * len(nav_targets), gap="small")
    cols[0].markdown(f"**Image** {image_num + 1} of {len(keys_hl)}<br />(id {image_id})",
                     unsafe_allow_html=True)
    for i, nav_target in enumerate(nav_targets):
        col = cols[i + 1]
        n_text, n_enabled, n_params = nav_target
        comp.create_nav_button(n_text, n_enabled, n_params, parent=col)

    # load and render image
    image_file = comp.get_image_file(image_id)
    st.image(read_image_for_streamlit(image_file), use_column_width=False)

    st.markdown(f"*Question:* {item_ll['question']}")
    st.markdown(f"*Answer:* {item_ll['answer']}")

    preds, metrics_per_datapoint, results, = comp.preds, comp.metrics_per_datapoint, comp.results
    model_names = list(results.keys())
    data_dict = {
            "model": model_names, "answer": [], "acc%": []
    }
    for model_name, result in results.items():
        answer = preds[model_name][lowlevel_id]
        data_dict["answer"].append(answer)
        acc = metrics_per_datapoint[model_name][lowlevel_id][METRIC_NAME]
        data_dict["acc%"].append(acc * 100)
    df = pd.DataFrame(data_dict)

    ccmap = mpl_colors.LinearSegmentedColormap.from_list('rg', [[0.5, 0, 0], [0, 0.3, 0]])

    def apply_style(df_styler: Styler):
        df_styler.background_gradient(cmap=ccmap, axis=1, vmin=0, vmax=100)
        df_styler.format({"acc%": "{:.0f}%"})
        return df_styler

    styler = df.style.pipe(apply_style)
    st.dataframe(styler)
