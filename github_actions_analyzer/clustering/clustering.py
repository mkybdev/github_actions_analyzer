import pandas as pd
from tqdm import tqdm  # type: ignore

from ..common import export_df, format_df, logger  # type: ignore
from .utils import kmeans as km
from .utils import vectorize


class Clustering:
    def __init__(self, df: pd.DataFrame, cols: list[str]):
        if not set(cols).issubset(df.columns):
            logger.error(f"All columns: {cols} must be in the input data.")
        self.df = format_df(df, cols, index="name")
        self.cols = cols
        self.X = self.df[cols]
        self.X_tfidf = vectorize(self.X)
        self.y = self.df["name"]

    def kmeans(self) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
        return km(self.X, self.X_tfidf, self.y)

    def run(self):
        print()
        kmeans_list = self.kmeans()
        for i, (kmeans_df, kmeans_info_df) in tqdm(
            enumerate(kmeans_list), desc="RUNNING CLUSTERING ANALYSIS"
        ):
            export_df(kmeans_df, "clustering/kmeans/cluster", str(i), quiet=True)
            export_df(kmeans_info_df, "clustering/kmeans/info", f"{i}_info", quiet=True)
