import pandas as pd
from tqdm import tqdm  # type: ignore

from ..common import export_df, format_df, logger
from .utils import get_conditional_probability  # type: ignore
from .utils import get_probability, make_heatmap, make_network


class Cooccurrence:
    def __init__(self, df: pd.DataFrame, cols: list[str]):
        if not set(cols).issubset(df.columns):
            logger.error(f"All columns: {cols} must be in the input data.")
        self.df = df
        self.cols = cols
        self.formatted_df = format_df(df, cols)

    def conditional_probability(self) -> dict[str, pd.DataFrame]:
        return get_conditional_probability(
            self.formatted_df,
            {
                str(name): get_probability(series)
                for name, series in self.formatted_df.items()
            },
            self.cols,
        )

    def run(self):
        print()
        conditional_probabilities = self.conditional_probability()
        for key, value in tqdm(
            conditional_probabilities.items(), desc="RUNNING COOCCURRENCE ANALYSIS"
        ):
            export_df(
                value, "cooccurrence/conditional_probability", f"{key}", quiet=True
            )
        print()
        make_heatmap(conditional_probabilities)
        print()
        make_network(conditional_probabilities)
