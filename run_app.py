"""
Start streamlit multipage app

Usage:
    streamlit run --server.runOnSave true run_app.py

    # reference
    streamlit run [script] [streamlit_args] -- [script_args]
    streamlit config show
    # --server.headless true to avoid opening browser windows
"""
from streamlit_vis.example_website.main_multiapp import main

if __name__ == "__main__":
    main()
