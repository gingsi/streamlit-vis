import os
import os.path
import pickle

import joblib
from joblib import register_store_backend
# noinspection PyProtectedMember
from joblib._store_backends import FileSystemStoreBackend


class StoreNoNumpy(FileSystemStoreBackend):
    """
    Store backend with pickle instead of numpy_pickle.
    This is alot faster for non-numpy objects (e.g. dicts).
    """
    NAME = "no_numpy"

    def load_item(self, path, verbose=1, msg=None):
        full_path = os.path.join(self.location, *path)

        if verbose > 1:
            if verbose < 10:
                print(f'{msg}...')
            else:
                print(f'{msg} from {full_path}')

        mmap_mode = (None if not hasattr(self, 'mmap_mode')
                     else self.mmap_mode)

        filename = os.path.join(full_path, 'output.pkl')
        if not self._item_exists(filename):
            raise KeyError(f"Non-existing item (may have been cleared).\n"
                           f"File {filename} does not exist")

        assert mmap_mode is None, "Standard pickle does not support mmap_mode"
        with self._open_item(filename, "rb") as fh:
            item = pickle.load(fh)
        return item


register_store_backend(StoreNoNumpy.NAME, StoreNoNumpy)


def get_joblib_memory(location="cache_joblib", verbose=1, numpy_capable=False):
    """

    Args:
        location: cache dir
        verbose: higher = more verbose
        numpy_capable: keep False unless needed, it makes loading alot slower for e.g. dicts

    Returns:
        memory: use as @memory.cache decorator for functions
    """
    backend = "local" if numpy_capable else StoreNoNumpy.NAME
    return joblib.Memory(location=location, backend=backend, verbose=verbose)
