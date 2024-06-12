import json
import os
import pickle
import random

import graphviz
import yaml  # type: ignore
import yamlcore  # type: ignore
from appdirs import user_cache_dir  # type: ignore
from tqdm import tqdm  # type: ignore

from ..common import constants, logger
from ..visualizer import visualize
from .load_dump import load_dump


def load(
    root_dir: str,
    sample: int,
    name: str,
    out_dir: str,
    visual: bool,
) -> list[dict]:

    loaded_data: list[dict] = []
    skipped_files = []

    logger.info(f"\nLoading data...")

    if os.path.exists(root_dir):

        for i, (dirpath, _, filenames) in enumerate(os.walk(root_dir)):

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
        logger.info(f"Loaded {len(loaded_data)} files.")
    else:
        if sample > len(loaded_data):
            logger.error("Sample size exceeds the number of loaded files.")
        constants.IS_SAMPLED = True
        logger.info(f"Loaded {len(loaded_data)} files and sampled {sample}.")
        loaded_data = random.sample(loaded_data, sample)

    if visual:
        print("")
        if os.path.exists(os.path.join(constants.OUTPUT_PATH, "visualize")):
            for file in os.listdir(os.path.join(constants.OUTPUT_PATH, "visualize")):
                os.remove(os.path.join(constants.OUTPUT_PATH, "visualize", file))
            os.rmdir(os.path.join(constants.OUTPUT_PATH, "visualize"))
        i = 1
        for yml_data in tqdm(
            loaded_data[:30],
            desc=f"VISUALIZING {'UP TO 30' if len(loaded_data) > 30 else str(len(loaded_data))} {'SAMPLES' if constants.IS_SAMPLED else 'FILES'}",
        ):
            gv = visualize(yml_data)
            graphviz.Source(gv).render(
                outfile=os.path.join(constants.OUTPUT_PATH, f"visualize/{i}.png"),
                format="png",
                cleanup=True,
            )
            i += 1

    return loaded_data
