from dataclasses import dataclass

from streamlit_vis.vis_config_default import WebsiteConfig


@dataclass
class ExampleWebsiteConfig(WebsiteConfig):
    # overwrite old constants
    PERPAGE = 5
    # set new ones
    MODEL_NAMES = ["random", "sayyes", "oracle"]
    METRIC_NAME = "acc"
    METRIC_FORMAT = {"acc": "{:.0%}"}
    DATASETS = {"example_dataset": ["train", "val"]}
