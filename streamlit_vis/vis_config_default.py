from dataclasses import dataclass
from pathlib import Path


@dataclass
class WebsiteConfig:
    DATA_PATH = Path("data")
    PERPAGE = 20
    THUMBNAIL_SIZE = 280
    PAGES = ["overview", "details", "results"]
    BUTTON_COLUMNS = 6
    SEARCH_FIELD = "question"
    # url get parameters, short parameter names to avoid getting too long urls
    G_PAGENUM = "pn"
    G_GROUP = "g"
    G_SUBSET = "su"
    G_SEARCH = "se"
    G_LEAF_ID = "leaf"
    G_PAGE = "p"
    G_APP = "a"
    G_DATASET = "d"
    G_SPLIT = "sp"


default_config = WebsiteConfig()
