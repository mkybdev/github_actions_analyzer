import pandas as pd
from tqdm import tqdm  # type: ignore

from ..common import export_df, logger
from .utils import get_duplication, get_frequency


class Intersection:
    def __init__(self, df: pd.DataFrame, cols: list[str]):
        if not set(cols).issubset(df.columns):
            logger.error(f"All columns: {cols} must be in the input data.")
        self.df = df
        self.cols = cols
        self.dup = None

    def duplication(self):
        self.dup = get_duplication(self.df, self.cols)
        return self.dup

    def frequency(self):
        return get_frequency(
            self.df,
            get_duplication(self.df, self.cols) if self.dup is None else self.dup,
            self.cols,
        )

    def run(self):
        print()
        for i in tqdm(range(2), desc="RUNNING INTERSECTION ANALYSIS"):
            if i == 0:
                export_df(self.duplication(), "intersection", "duplication", quiet=True)
            else:
                export_df(self.frequency(), "intersection", "frequency", quiet=True)
