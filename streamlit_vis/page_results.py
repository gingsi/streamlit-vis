import streamlit as st
import streamlit_permalink as stp

from streamlit_vis.st_utils import METRIC_NAME, modify_css, METRIC_FORMAT, G_PAGE, G_SUBSET,\
    G_GROUP, G_PAGENUM
from streamlit_vis.website_component import WebsiteComponent


def str_to_html_anchor(in_str):
    return in_str.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")


def render_results_page(comp: WebsiteComponent):
    modify_css(["button_columns"])
    st.markdown("# Results")

    # evaluation subsets
    subsets = comp.subsets
    subset_size_reference = len(subsets["all"]["subsets"]["all"])

    # metrics
    metric_names = [METRIC_NAME]

    # model results
    results = comp.results
    model_names = list(results.keys())

    st.markdown(f"Show results for models **{', '.join(model_names)}** "
                f"on groups **{', '.join(subsets.keys())}**")
    comp.create_nav_menu("results")

    show_abs = stp.checkbox("Show absolute score", key="show_absolute_score", value=True)
    show_rel = stp.checkbox("Show score relative to the 'all' set", key="show_relative_score",
                            value=True)

    # table of contents
    content_lines = ["**Table of Contents**"]
    for group_name, group_info in subsets.items():
        content_lines.append(f"[{group_info['title']}](#{str_to_html_anchor(group_name)})")
    st.markdown("\n* ".join(content_lines), unsafe_allow_html=True)

    # collect reference metrics (group_name=all subset_name=all)
    collected_metrics_ref = {}
    for model_name in model_names:
        collected_metrics_ref[model_name] = {}
        for metric_name in metric_names:
            collected_metrics_ref[model_name][metric_name] = results[
                model_name][metric_name]["all"]["all"]

    for group_name, group_info in subsets.items():
        show_abs_here = show_abs or group_name == "all" or not show_rel
        group_data = group_info["subsets"]

        # write the table
        group_desc = group_info["description"]
        group_title = group_info["title"]
        st.header(f"{group_title}", anchor=str_to_html_anchor(group_name))
        st.markdown(group_desc)
        table_html = ["<table>"]
        header_style = f" style='color: #777;'"

        # subset header
        table_html.append(f"<tr{header_style}><td>Subset</td>")
        for _metric_name in metric_names:
            for subset_name in group_data.keys():
                table_html.append(f"<td>{subset_name}</td>")
        table_html.append("</tr>")

        # subset size header
        table_html.append(f"<tr{header_style}><td>Subset size</td>")
        for _metric_name in metric_names:
            for subset_name, subset_data in group_data.items():
                subset_size = len(subset_data)
                subset_size_pct = subset_size / subset_size_reference
                table_html.append(f"<td>{subset_size:,d} "
                                  f"<b style='color: #fff;'>{subset_size_pct:.0%}</b></td>")
        table_html.append("</tr>")

        # metric header, only for multiple metrics
        if len(metric_names) > 1:
            table_html.append("<tr><td>Metric</td>")
            for metric_name in metric_names:
                table_html.append(f"<td colspan='{len(group_data)}'>"
                                  f"{metric_name}</td>")
            table_html.append("</tr>")

        # content rows (one row per model)
        for model_name in model_names:
            table_html.append(f"<tr><td>{model_name}</td>")
            for metric_name in metric_names:
                formatter = METRIC_FORMAT[metric_name]
                metric_value_ref = collected_metrics_ref[model_name][metric_name]
                for subset_name in group_data.keys():
                    metric_value = results[
                        model_name][metric_name][group_name][subset_name]
                    metric_rel_value = metric_value - metric_value_ref
                    table_html.append(f"<td>")
                    if show_abs_here:
                        table_html.append(f"{formatter.format(metric_value)}")
                    if show_rel:
                        if show_abs_here:
                            table_html.append("<br />")
                        metric_rel_fmt = formatter.format(metric_rel_value)
                        if metric_rel_value >= 0:
                            metric_str = f" <span style='color: #5b5;'>+{metric_rel_fmt}"
                        else:
                            metric_str = f" <span style='color: #f77;'>{metric_rel_fmt}"
                        table_html.append(metric_str)

                    table_html.append("</td>")
            table_html.append("</tr>")
        st.markdown("".join(table_html), unsafe_allow_html=True)
        st.write("<br />Display overview for subsets:", unsafe_allow_html=True)

        # create a grid of buttons to filter for this subset, with max 6 buttons per column
        subset_names = list(group_data.keys())
        for i, subset_name in enumerate(subset_names):
            col_i = i % 6
            if col_i == 0:
                cont = st.container()
                cols = cont.columns(6, gap="small")
            # noinspection PyUnboundLocalVariable
            comp.create_nav_button(
                    f"{subset_name}", True, {
                            G_PAGE: "overview", G_SUBSET: subset_name, G_GROUP: group_name,
                            G_PAGENUM: 0, },
                    parent=cols[col_i],
                    key=f"nav-{group_name}-{subset_name}-{i}")

        st.markdown("[Back to top](#results)", unsafe_allow_html=True)
