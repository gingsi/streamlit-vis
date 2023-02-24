# streamlit-vis

A visualization example app for image datasets using streamlit.

The app visualizes a dummy visual question answering dataset and example model predictions.

[See the gallery for screenshots.](#gallery)

## Setup

Clone, cd into, create environment with python>=3.7 and `pip install -r requirements.txt`

Tested with `python=3.9 streamlit=1.18.1`

## Usage

Start the streamlit server:

~~~bash
streamlit run --server.runOnSave true run_app.py
~~~

This app is optimized for dark theme, activate it in the settings menu (top right).

## Features

- Supports hierarchical data: For one image there can be 1 to N questions.
- Basic filtering:
    - Dataset is divided into "train" and "val" subsets.
    - Questions are sorted into "number" and "yes/no" categories depending on their answer.
    - A search field can be used to search for specific questions.
- The **overview** page shows a grid of images and questions.
- The **details** page shows a single image-question pair and model predictions for this pair.
- The **results** page shows aggregated metrics per model and question category.
- Some CSS tricks are applied to overcome weaknesses of streamlit:
    - Image overview grid with a variable number of images per row depending on browser width.
    - `st.columns` that do not span the whole page.

## Gallery

![Overview](docs/_static/overview.png "Overview")

![Details](docs/_static/details.png "Details")

![Results](docs/_static/results.png "Results")

## Version history

- 2023-02-24: Refactor to decouple example app and library code (no backwards compatibility)
- 2023-02-21: Initial version