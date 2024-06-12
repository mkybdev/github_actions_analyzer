from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns  # type: ignore
from sklearn.cluster import KMeans  # type: ignore
from sklearn.decomposition import PCA  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.manifold import TSNE  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore

from ..common import export_image, logger


def get_pca_loadings(X_tfidf: pd.DataFrame, X: pd.DataFrame):
    # データの標準化
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(X_tfidf)

    target = PCA(n_components=2)  # 2つの主成分を取得
    principalComponents = target.fit_transform(data_scaled)
    loadings = target.components_.T * np.sqrt(target.explained_variance_)

    # 主成分の負荷量とデータフレームを作成
    loadings_df = pd.DataFrame(loadings, columns=["PC1", "PC2"], index=X_tfidf.columns)

    # # サンプリング（データセットが大きい場合のため）
    # sample_size = 500  # サンプルサイズを適宜調整
    # indices = np.random.choice(principalComponents.shape[0], sample_size, replace=False)
    # sampled_data = principalComponents[indices]

    # 負荷量が0.5以上の要素のみを抽出
    filtered_loadings_df = loadings_df[
        (abs(loadings_df["PC1"]) > 0.5) | (abs(loadings_df["PC2"]) > 0.5)
    ]

    for value_to_search in filtered_loadings_df.copy().index:
        # 特定の値を含む行を抽出する関数
        def contains_value(row, value):
            columns_with_value = []
            for col in row.index:
                if isinstance(row[col], list) and value in row[col]:
                    columns_with_value.append(col)
            return columns_with_value

    # データフレーム全体を検索して行と含まれていたカラムを抽出します
    results = X.apply(lambda row: contains_value(row, value_to_search), axis=1)
    matching_rows = X[results.apply(len) > 0]
    columns_with_value = results[results.apply(len) > 0]

    if len(matching_rows) == 0:
        filtered_loadings_df = filtered_loadings_df.rename(
            index={value_to_search: f"{value_to_search} (?)"}
        )
    else:
        filtered_loadings_df = filtered_loadings_df.rename(
            index={
                value_to_search: f"{value_to_search} ({set([columns_with_value[matching_rows.index[i]][0] for i in range(len(matching_rows.index))])})"
            }
        )

    # ヒートマップの作成
    fig = plt.figure()
    sns.heatmap(filtered_loadings_df, annot=False, cmap="coolwarm", fmt=".2f")
    plt.title(f"Heatmap of PCA Loadings (with |PC1| and |PC2| > 0.5)")
    plt.xlabel("Principal Components")
    plt.ylabel("Variables")
    plt.tight_layout()
    export_image(
        fig,
        f"PCA Loadings",
        f"clustering/kmeans/pca",
        quiet=True,
    )


def kmeans(
    X: pd.DataFrame, X_tfidf: pd.DataFrame, y: pd.Series, num_clusters: int = 5
) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    columns = X.columns.values
    # KMeansを用いたクラスタリング
    try:
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        kmeans.fit(X_tfidf)
    except:
        logger.error(
            "An error occurred while running KMeans. Maybe the dataset is too small."
        )

    pca(X, X_tfidf, kmeans)
    tsne(X, X_tfidf, kmeans)

    res = []

    # クラスタラベルを元のデータフレームXに追加
    X["cluster"] = kmeans.labels_
    X.insert(0, "name", y)

    # クラスタごとにデータをグループ化
    for cluster_num in range(num_clusters):
        cluster_data = X[X["cluster"] == cluster_num]
        cluster_feature: dict[str, list] = dict()
        for column in columns:
            # すべてのリストを一つのリストに結合し、出現頻度をカウント
            all_items = []
            for items in cluster_data[column]:
                if isinstance(items, list):  # カラムのデータがリスト型であることを確認
                    all_items += items
                else:
                    all_items += []  # リスト型でない場合は空のリストを追加
            item_counts = Counter(all_items)
            # 出現回数が多い上位5項目を取得（適宜調整可能）
            top_items = item_counts.most_common(5)
            cluster_feature[column] = top_items
        rows = []
        for key, values in cluster_feature.items():
            for value in values:
                rows.append([value[0], key, value[1]])
        rows.sort(key=lambda x: x[2], reverse=True)
        res.append(
            (cluster_data, pd.DataFrame(rows, columns=["item", "field", "count"]))
        )

    return res


def pca(X: pd.DataFrame, X_tfidf: pd.DataFrame, kmeans: KMeans):
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_tfidf)
    fig = plt.figure()
    plt.scatter(
        X_pca[:, 0],
        X_pca[:, 1],
        c=kmeans.labels_,
        cmap="viridis",
        marker="o",
        edgecolor="k",
        s=50,
        alpha=0.6,
    )
    plt.colorbar()
    plt.title("PCA - Cluster Visualization")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.grid()
    export_image(fig, "PCA", "clustering/kmeans/pca", quiet=True)
    get_pca_loadings(X_tfidf, X)


def tsne(X: pd.DataFrame, X_tfidf: pd.DataFrame, kmeans: KMeans):
    tsne = TSNE(
        n_components=2, random_state=42, perplexity=min(30, X_tfidf.shape[0] - 1)
    )
    X_tsne = tsne.fit_transform(X_tfidf)
    fig = plt.figure()
    plt.scatter(
        X_tsne[:, 0],
        X_tsne[:, 1],
        c=kmeans.labels_,
        cmap="viridis",
        marker="o",
        edgecolor="k",
        s=50,
        alpha=0.6,
    )
    plt.colorbar()
    plt.title("t-SNE - Cluster Visualization")
    plt.xlabel("t-SNE Feature 1")
    plt.ylabel("t-SNE Feature 2")
    plt.grid()
    export_image(fig, "t-SNE", "clustering/kmeans/tsne", quiet=True)


def vectorize(df: pd.DataFrame) -> pd.DataFrame:
    # データフレームXのリストを文字列に変換
    X_transformed = df.map(lambda x: " ".join(x))

    # 各カラムごとにTF-IDFベクトルを計算
    vectorizer = TfidfVectorizer()
    X_tfidf = pd.DataFrame()
    for column in X_transformed.columns:
        tfidf_matrix = vectorizer.fit_transform(X_transformed[column])
        df_tfidf = pd.DataFrame(
            tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out()  # type: ignore
        )
        X_tfidf = pd.concat([X_tfidf, df_tfidf], axis=1)

    return X_tfidf
