import pandas as pd


def extract_elements(row) -> list:
    match row:
        # 集合
        case list() | tuple() | set():
            return list(row)
        # 辞書
        case dict():
            if row.get("type") is not None:
                return [row["type"]]
            return list(row.keys())
        # リテラル
        case _:
            return [row]


def format_df(df: pd.DataFrame, cols: list[str], index: str = "") -> pd.DataFrame:
    return (
        df[cols + ([index] if index != "" else [])]
        .dropna()
        .apply(lambda x: x.apply(extract_elements))
    )
