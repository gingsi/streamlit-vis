"""
Start streamlit multipage app

Usage:
    # development
    streamlit run --server.runOnSave true run_app.py -- --debug

    # production
    streamlit run run_app.py

Reference:
    streamlit run [script] [streamlit_args] -- [script_args]

"""
from streamlit_vis.main_multiapp import main

if __name__ == "__main__":
    main()
