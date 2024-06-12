import json
import os
import pickle
import random

import yaml  # type: ignore
import yamlcore  # type: ignore
from appdirs import user_cache_dir  # type: ignore
from tqdm import tqdm  # type: ignore

from ..common import constants, logger
from .load_dump import load_dump


def load(
    root_dir: str,
    sample: int,
    name: str,
    out_dir: str,
) -> list[dict]:

    loaded_data: list[dict] = []
    skipped_files = []

    print("")

    if os.path.exists(root_dir):

        for dirpath, _, filenames in tqdm(os.walk(root_dir), desc="LOADING DATA"):

            if any(filename.endswith(".yml") for filename in filenames):
                for filename in filenames:
                    if filename.endswith(".yml"):
                        yml_path = os.path.join(dirpath, filename)
                        with open(yml_path, "r", encoding="utf-8") as f:
                            try:
                                yml_data = yaml.load(f, Loader=yamlcore.CoreLoader)
                                loaded_data.append(yml_data)
                            except:
                                skipped_files.append(yml_path)

        if skipped_files:
            logger.info(f"Skipped loading {len(skipped_files)} files: {skipped_files}")

        if name == "":
            logger.info("Dump name not provided. Continuing without dumping.")

        else:
            cache_dir = os.path.join(
                user_cache_dir("github_actions_analyzer", "gaa"), name
            )
            os.makedirs(cache_dir, exist_ok=True)
            constants.DUMP_PATH = cache_dir

            cache_file_path = os.path.join(cache_dir, "data.pkl")

            with open(cache_file_path, "wb") as cache_file:
                pickle.dump(loaded_data, cache_file)
                logger.info("Loaded data and saved to cache.")

    else:
        loaded_data = load_dump(root_dir)
        if loaded_data == []:
            logger.error("No such directory or dumped dataset.")
        else:
            try:
                os.rmdir(constants.OUTPUT_PATH)
            except:
                pass
            constants.OUTPUT_PATH = os.path.join(out_dir, root_dir)

    if sample < 0:
        logger.info(f"Loaded {len(loaded_data)} packages.")
        return loaded_data
    else:
        if sample > len(loaded_data):
            logger.error("Sample size exceeds the number of loaded packages.")
        constants.IS_SAMPLED = True
        logger.info(
            f"Sampling {sample} packages from {len(loaded_data)} loaded packages."
        )
        return random.sample(loaded_data, sample)
