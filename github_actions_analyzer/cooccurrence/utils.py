import os
import re
from collections import Counter

import matplotlib.pyplot as plt  # type: ignore
import networkx as nx  # type: ignore
import pandas as pd
import seaborn as sns  # type: ignore
from tqdm import tqdm  # type: ignore

from ..common import constants, export_image, logger


def get_conditional_probability(
    df: pd.DataFrame, probabilities: dict[str, pd.Series], cols: list[str]
) -> dict[str, pd.DataFrame]:

    cache_dir = (
        os.path.join(constants.DUMP_PATH, "conditional_probabilities")
        if constants.DUMP_PATH
        else None
    )
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
    cached_files = os.listdir(cache_dir) if cache_dir else []

    # conditional_probabilities = pd.DataFrame()
    conditional_probabilities = dict()

    # 条件付き共起確率を計算する
    probs = {col: probabilities[col] for col in cols}

    # 条件付き共起確率を計算する関数
    def calculate_conditional_probabilities(base_column: str, target_column: str):
        conditional_probs = {}
        total_rows = len(df)

        for base_item in probs[base_column].index:
            base_rows = df[df[base_column].apply(lambda x: base_item in x)]
            base_count = len(base_rows)

            if base_count > 0:
                co_occurrence_counts = Counter(
                    [item for sublist in base_rows[target_column] for item in sublist]
                )
                conditional_probs[base_item] = {
                    k: v / total_rows for k, v in co_occurrence_counts.items()
                }

        return pd.DataFrame(conditional_probs).fillna(0)

    # 各データフレームをフラット化
    def flatten(df: pd.DataFrame, combination: str):
        flat_df = df.unstack().reset_index()
        flat_df.columns = pd.Index(["Base", "Target", "Probability"])
        flat_df.loc[:, ["Combination"]] = combination
        flat_df = flat_df.sort_values(by="Probability", ascending=False)
        return flat_df

    # 各カラムの組み合わせに対して条件付き共起確率を計算
    for base_column in tqdm(
        cols, desc="COOCCURRENCE: CALCULATING CONDITIONAL PROBABILITY", leave=False
    ):
        for target_column in cols:
            if base_column != target_column:
                combination = f"{base_column} -> {target_column}"
                cond_prob_df = pd.DataFrame()
                if not constants.IS_SAMPLED and f"{combination}.csv" in cached_files:
                    cond_prob_df = pd.read_csv(
                        f"{cache_dir}/{combination}.csv",
                        dtype={
                            "Base": str,
                            "Target": str,
                            "Probability": float,
                            "Combination": str,
                        },
                    )
                else:
                    cond_prob_df = flatten(
                        calculate_conditional_probabilities(base_column, target_column),
                        combination,
                    )
                    if cache_dir:
                        cond_prob_df.to_csv(f"{cache_dir}/{combination}.csv")
                # conditional_probabilities = pd.concat(
                #     [conditional_probabilities, cond_prob_df],
                #     ignore_index=True,
                # )
                conditional_probabilities[combination] = cond_prob_df

    return conditional_probabilities


def get_probability(series: pd.Series) -> pd.Series:
    if all(isinstance(item, list) for item in series):
        # リストの全要素をフラットにする
        all_keywords = [item for sublist in series for item in sublist]

        # フラットにしたリストをSeriesに変換
        flat_keywords = pd.Series(all_keywords)

        # 各要素の出現回数をカウント
        value_counts = flat_keywords.value_counts()

        # 全要素数を取得
        total_count = len(series)

        # 各要素の出現確率を計算
        probabilities = value_counts / total_count
        keywords_prob = probabilities.rename("probability")
        return keywords_prob
    else:
        logger.error("Each element of series must be a list.")
        return pd.Series()


def convert_format(input_string):
    # 正規表現を使って "X -> Y" 形式を "P(Y | X)" 形式に変換
    pattern = re.compile(r"(\w+)\s*->\s*(\w+)")
    match = pattern.match(input_string)

    if match:
        x = match.group(1)
        y = match.group(2)
        return f"P({y} | {x})"
    else:
        return input_string


def make_heatmap(flatten_conditional_probabilities: dict[str, pd.DataFrame]):

    skipped_list_empty = []
    skipped_list_failed = []

    for key in tqdm(
        flatten_conditional_probabilities.keys(), desc="MAKING COOCCURRENCE HEATMAP"
    ):
        # 結果をピボットテーブルに変換
        pivot_table = (
            flatten_conditional_probabilities[key]
            .head(500)
            .pivot(index="Base", columns="Target", values="Probability")
        )
        if pivot_table.empty:
            skipped_list_empty.append(key)
            continue
        # ヒートマップを描画
        try:
            fig = plt.figure()
            sns.heatmap(pivot_table, annot=False, fmt=".2f", cmap="YlGnBu")
            plt.title(convert_format(key))
            plt.xlabel("Target")
            plt.ylabel("Base")
            plt.tight_layout()
            export_image(fig, key, "cooccurrence/heatmap", quiet=True)
        except:
            skipped_list_failed.append(key)
            continue

    if skipped_list_empty:
        logger.info(f"Combinations {skipped_list_empty} was skipped: Empty data.")
    if skipped_list_failed:
        logger.info(
            f"Combinations {skipped_list_failed} was skipped: Failed to make heatmap."
        )


def make_network(flatten_conditional_probabilities):

    skipped_list_empty = []
    skipped_list_failed = []

    keys = flatten_conditional_probabilities.keys()

    for key in tqdm(keys, desc="MAKING COOCCURRENCE NETWORK"):
        if flatten_conditional_probabilities[key].empty:
            skipped_list_empty.append(key)
            continue
        try:
            # ネットワーク図の描画
            fig = plt.figure()
            G = nx.DiGraph()

            # ノードとエッジを追加
            for _, row in flatten_conditional_probabilities[key].head(200).iterrows():
                G.add_edge(row["Base"], row["Target"], weight=row["Probability"])

            # ノードのサイズを調整するための辞書を作成
            node_sizes = {
                node: sum([d["weight"] for _, _, d in G.edges(node, data=True)]) * 3000
                for node in G.nodes()
            }

            # エッジの幅を調整するためのリストを作成
            edge_widths = [d["weight"] * 10 for _, _, d in G.edges(data=True)]

            # ポジションを設定
            pos = nx.spring_layout(G, k=0.15, iterations=20)

            nx.draw(
                G,
                pos,
                with_labels=True,
                node_size=[node_sizes[node] for node in G.nodes()],
                width=edge_widths,
                edge_color="blue",
                node_color="lightblue",
                font_size=18,
                font_weight="normal",
            )
            plt.title(key)
            export_image(fig, key, "cooccurrence/network", quiet=True)
        except:
            skipped_list_failed.append(key)
            continue

    if skipped_list_empty:
        logger.info(f"Combinations {skipped_list_empty} was skipped: Empty data.")
    if skipped_list_failed:
        logger.info(
            f"Combinations {skipped_list_failed} was skipped: Failed to make network."
        )
