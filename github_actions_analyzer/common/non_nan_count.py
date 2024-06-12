import pandas as pd


def non_nan_count(df: pd.DataFrame) -> pd.DataFrame:
    non_nan_counts = df.notna().sum().reset_index()
    non_nan_counts.columns = pd.Index(["Column", "Non_NaN_Count"])
    non_nan_counts = non_nan_counts.sort_values(by="Non_NaN_Count", ascending=False)
    return non_nan_counts
