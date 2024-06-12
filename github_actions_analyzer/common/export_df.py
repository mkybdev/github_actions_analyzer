import os

import pandas as pd

from . import constants  # type: ignore
from . import logger  # type: ignore


def export_df(
    df: pd.DataFrame | pd.Series,
    dir: str,
    name: str,
    quiet: bool = False,
    index: bool = False,
):
    dir_path = os.path.join(constants.OUTPUT_PATH, dir)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, name + ".csv")

    with open(file_path, "w") as file:
        df.to_csv(file, index=index)
        if not quiet:
            logger.info(f"Exported output: {file_path}")
