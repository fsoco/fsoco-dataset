from pathlib import Path
import pickle
from typing import Any

from .logger import Logger

MAGIC_STRING = "FSOCO_SIMILARITY_SCORER"
CACHE_VERSION = 0


class Cache:
    def __init__(self, read_only: bool = False):
        self.read_only = read_only
        self._data = {"TYPE": MAGIC_STRING, "VERSION": CACHE_VERSION}

    def load_from_file(self, cache_file: Path):
        with open(str(cache_file), "rb") as f:
            data = pickle.load(f)
            if data["TYPE"] == MAGIC_STRING and data["VERSION"] == CACHE_VERSION:
                self._data = data
                return True
            else:
                Logger.log_error("Cache File has wrong type or version!")
                return False

    def store_to_file(self, cache_file: Path):
        if not self.read_only:
            with open(str(cache_file), "wb") as f:
                pickle.dump(self._data, f)
        else:
            raise RuntimeError("Cache is read only!")

    def add_cache_item(self, module: str, key: str, data: Any):
        if module not in self._data.keys():
            self._data[module] = {}

        self._data[module][key] = data

    def get_cache_item(self, module: str, key: str, default_value: Any = None):
        return self._data.get(module, {}).get(key, default_value)
