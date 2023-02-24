"""
Start streamlit multipage app

Usage:
    # development
    streamlit run --server.runOnSave true run_app.py

    # production
    streamlit run run_app.py

    # reference
    streamlit run [script] [streamlit_args] -- [script_args]
    streamlit config show

Notes:
    Use --server.headless true to avoid opening browsers

    By default, errors will be caught and displayed but the server will stay alive.
    To actually raise the error and kill the server (e.g. to debug it post-mortem with PyCharm)
    edit `streamlit.error_util.handle_uncaught_app_exception(ex)` and add `raise ex` as first line.
"""
from streamlit_vis.example_website.main_multiapp import main

if __name__ == "__main__":
    main()
