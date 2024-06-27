import os
import re

import graphviz
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

from ..common import constants, export_df, export_image, logger
from ..visualizer import visualize
from .utils import nest, nol


class Statistics:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def pie_chart(self, data: pd.Series, name: str, title: str):
        fig, ax = plt.subplots()
        data = data.groupby(data).size().sort_index(ascending=False)
        ax.pie(data, labels=data.index, autopct="%1.1f%%", startangle=90)
        ax.set_title(title)
        export_image(fig, name, "statistics", quiet=True)

    def histogram(
        self,
        data: pd.Series,
        name: str,
        xlabel: str,
        ylabel: str,
        title: str,
        log: bool = False,
    ):
        fig, ax = plt.subplots()
        ax.hist(data, bins=(np.arange(data.max() + 1) + 0.5) if data.max() < 20 else 20)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if log:
            ax.set_yscale("log")
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        ax.set_title(title)
        export_image(fig, name, "statistics", quiet=True)

    def run(self):
        stat_nol, data_nol, outliner_nol = nol(self.df)
        stat_nest, data_nest, outlier_nest = nest(self.df)
        export_df(stat_nol, "statistics", "nol", quiet=True, index=True)
        export_df(stat_nest, "statistics", "nest", quiet=True, index=True)
        for outlier, name, col in zip(
            [outliner_nol, outlier_nest],
            ["outlier_nol", "outlier_nest"],
            ["number_of_lines", "nest_depth"],
        ):
            if not outlier.empty:
                outlier = outlier.join(
                    pd.DataFrame(
                        (data_nest if col == "number_of_lines" else data_nol).loc[
                            outlier.index
                        ],
                        columns=[
                            (
                                "nest_depth"
                                if col == "number_of_lines"
                                else "number_of_lines"
                            )
                        ],
                    ),
                    how="outer",
                )
                export_df(outlier, "statistics", name, quiet=True, index=True)
                # outlier_path = os.path.join(constants.OUTPUT_PATH, "statistics", name)
                # if os.path.exists(outlier_path):
                #     for file in os.listdir(outlier_path):
                #         os.remove(os.path.join(outlier_path, file))
                # i = 1
                # err = 0
                # for index, row in tqdm(
                #     outlier.iterrows(), desc="VISUALIZING OUTLIERS OF " + col
                # ):
                #     yml_data = row.drop([col]).dropna().to_dict()
                #     gv = visualize(yml_data, str(i))
                #     try:
                #         s = graphviz.Source(
                #             gv,
                #             directory=outlier_path,
                #             format="png",
                #         )
                #         s.render(cleanup=True, quiet=True)
                #     except Exception as e:
                #         # print(e)
                #         err += 1
                #         continue
                #     i += 1
                #     os.rename(
                #         os.path.join(outlier_path, "Source.gv.png"),
                #         os.path.join(
                #             outlier_path,
                #             str(index) + ".png",
                #         ),
                #     )
                #     print(os.path.join(outlier_path, "Source.gv"))
                #     if os.path.exists(os.path.join(outlier_path, "Source.gv")):
                #         print("test")
                #         try:
                #             os.remove(os.path.join(outlier_path, "Source.gv"))
                #         except Exception as e:
                #             print(e)
                #     if os.path.exists(os.path.join(outlier_path, "Source.gv.png")):
                #         print("test")
                #         try:
                #             os.remove(os.path.join(outlier_path, "Source.gv.png"))
                #         except Exception as e:
                #             print(e)
                # if err > 0:
                #     logger.info(f"Skipped {err} files, failed to visualize.")
        self.histogram(
            data_nol,
            "nol",
            "Number of Lines",
            "Frequency",
            f"Number of Lines of Workflow Files (N = {len(data_nol)})",
            log=True,
        )
        self.histogram(
            data_nest,
            "nest",
            "Maximum Nesting Depth",
            "Frequency",
            f"Maximum Nesting Depth of YAML (N = {len(data_nest)})",
            log=True,
        )

        logger.info("\nStatistics analysis completed.")
