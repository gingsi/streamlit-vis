from collections import defaultdict
from copy import deepcopy

from streamlit_vis.joblib_ext import get_joblib_memory

mem = get_joblib_memory(verbose=0)


def filter_data_given_leaf_ids(
        leaf_ids, leaf_meta, root_meta):
    """
    Args:
        leaf_ids: ids to filter for
        leaf_meta: {leaf_id: {"root_id": root_id, key1: value1, ...}}
        root_meta: {root_id: {key1: value1, ...}}

    Returns:
        updated metadata with only the entries that are related to leaf_ids
    """
    new_leaf_ids = set(leaf_ids)
    new_meta_leaf = {}
    tree = defaultdict(list)
    for low_id, low_item in leaf_meta.items():
        low_id = str(low_id)
        if low_id in new_leaf_ids:
            new_meta_leaf[str(low_id)] = deepcopy(low_item)
            root_id = str(low_item["root_id"])
            tree[root_id].append(str(low_id))

    new_meta_root = {}
    for root_id, root_leaf_ids in tree.items():
        new_meta_root[root_id] = deepcopy(root_meta[root_id])
        new_meta_root[root_id]["leaf_ids"] = root_leaf_ids

    # # check consistency of the data (might be slow for big datasets)
    # new_sum_ll = sum(len(v['leaf_ids']) for v in new_meta_root.values())
    # assert new_sum_ll == len(new_meta_leaf)

    return new_meta_leaf, new_meta_root


@mem.cache(ignore=["*", "**"])
def filter_data_given_leaf_ids_cached(
        _cache_key: str, *args, **kwargs):
    return filter_data_given_leaf_ids(*args, **kwargs)
