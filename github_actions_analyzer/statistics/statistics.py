import pandas as pd

from ..common import export_df, logger
from .utils import nest, nol


class Statistics:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def run(self):
        nol_df = nol(self.df)
        nest_df = nest(self.df)
        export_df(nol_df, "statistics", "nol", quiet=True, index=True)
        export_df(nest_df, "statistics", "nest", quiet=True, index=True)
        logger.info("\nStatistics analysis completed.")
