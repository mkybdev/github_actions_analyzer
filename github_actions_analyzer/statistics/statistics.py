import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import graphviz
import re

from ..common import export_df, export_image, logger, constants
from .utils import nest, nol
from ..visualizer import visualize


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
        nol_res = nol(self.df)
        stat_nest, data_nest, outlier_nest = nest(self.df)
        export_df(nol_res[0], "statistics", "nol", quiet=True, index=True)
        export_df(stat_nest, "statistics", "nest", quiet=True, index=True)
        if not outlier_nest.empty:
            export_df(
                outlier_nest, "statistics", "outlier_nest", quiet=True, index=True
            )
            nest_path = os.path.join(
                constants.OUTPUT_PATH, "statistics", "outlier_nest"
            )
            if os.path.exists(nest_path):
                for file in os.listdir(nest_path):
                    os.remove(os.path.join(nest_path, file))
            i = 1
            err = 0
            for _, row in outlier_nest.iterrows():
                yml_data = row.drop(['nest_depth']).dropna().to_dict()
                gv = visualize(yml_data, str(i))
                try:
                    s = graphviz.Source(
                        gv,
                        directory=nest_path,
                        format="png",
                    )
                    s.render(cleanup=True, quiet=True)
                except Exception as e:
                    err += 1
                    continue
                if i == 30:
                    break
                i += 1
            for file in os.listdir(nest_path):
                if re.match(r"Source.gv\.\d+\.png", file):
                    os.rename(
                        os.path.join(nest_path, file),
                        os.path.join(
                            nest_path,
                            file.split(".")[2] + ".png",
                        ),
                    )
                elif re.match(r"Source.gv.png", file):
                    os.rename(
                        os.path.join(nest_path, file),
                        os.path.join(nest_path, "1.png"),
                    )
            if err > 0:
                logger.info(f"Skipped {err} files, failed to visualize.")
        self.histogram(
            nol_res[1],
            "nol",
            "Number of Lines",
            "Frequency",
            f"Number of Lines of Workflow Files (N = {len(nol_res[1])})",
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
