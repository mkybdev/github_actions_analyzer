import pandas as pd


def depth(d):
    if isinstance(d, dict):
        return 1 + (max(map(depth, d.values())) if d else 0)
    elif isinstance(d, list):
        return 1 + (max(map(depth, d)) if d else 0)
    return 0


def count_nest(s: pd.Series) -> pd.Series:
    return s.map(lambda x: depth(x))


def nest(df: pd.DataFrame) -> list[pd.Series | pd.DataFrame]:
    max_df = df.apply(count_nest, axis=1).apply(max, axis=1)
    outlier = max_df.quantile(0.95)
    outlier_df = max_df[max_df > outlier].rename("nest_depth").to_frame()
    if not outlier_df.empty:
        outlier_df = pd.concat([outlier_df, df.loc[outlier_df.index]], axis=1)
    return [max_df.describe().rename("nest_depth"), max_df, outlier_df]


def count_nol(el, level: int = 0) -> int:
    if isinstance(el, dict):
        line_count = 0
        for key, value in el.items():
            # key itself is a line
            line_count += 1
            # recursively count the lines in the value
            line_count += count_nol(value, level + 1)
        return line_count
    elif isinstance(el, list):
        line_count = 0
        for item in el:
            # each item in the list starts a new line
            line_count += 1
            # recursively count the lines in the item
            line_count += count_nol(item, level + 1)
        return line_count
    else:
        # if data is a leaf node (scalar), it's one line
        return 1


def nol(df: pd.DataFrame) -> list[pd.Series]:
    return [
        df.apply(lambda x: x.apply(count_nol), axis=1)
        .apply(sum, axis=1)
        .describe()
        .rename("number_of_lines"),
        df.apply(lambda x: x.apply(count_nol), axis=1).apply(sum, axis=1),
    ]
