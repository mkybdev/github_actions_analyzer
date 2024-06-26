import pandas as pd


def preprocess(rawData: list[dict]) -> pd.DataFrame:
    all_keys: set = set()
    for i, entry in enumerate(rawData):
        if entry is None:
            assert rawData.pop(i) is None
            continue
        all_keys.update(entry.keys())
    data = pd.DataFrame(rawData)
    data = data.reindex(columns=list(all_keys))
    return data
