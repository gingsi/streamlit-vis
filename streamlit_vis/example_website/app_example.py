import streamlit as st

from streamlit_vis.st_utils import modify_css


def app():
    modify_css()
    st.markdown("# Example second app")
    st.markdown("Markdown text")


if __name__ == "__main__":
    app()
