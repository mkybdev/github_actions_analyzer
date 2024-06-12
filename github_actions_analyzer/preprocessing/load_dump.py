import os
import pickle

from appdirs import user_cache_dir  # type: ignore

from ..common import constants, logger


def load_dump(name: str) -> list[dict]:

    cache_dir = os.path.join(user_cache_dir("github_actions_analyzer", "gaa"), name)
    constants.DUMP_PATH = cache_dir
    cache_file_path = os.path.join(cache_dir, "data.pkl")

    if os.path.exists(cache_file_path):
        with open(cache_file_path, "rb") as cache_file:
            loaded_data = pickle.load(cache_file)
            logger.info("Loaded data from cache.")
        return loaded_data
    else:
        return []
