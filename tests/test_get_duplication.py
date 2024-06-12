import unittest
import pandas as pd

from github_actions_analyzer.intersection.get_duplication import get_duplication


def sort_lists_in_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    sorted_df = df.copy()
    for col in sorted_df.columns:
        sorted_df[col] = sorted_df[col].apply(
            lambda x: sorted(x) if isinstance(x, list) else x
        )
    return sorted_df


class TestGetDuplication(unittest.TestCase):
    def test_get_duplication(self):
        test_cases = [
            # Test case 1
            {
                "df": pd.DataFrame(
                    {
                        "name": ["a", "b", "c", "d", "e"],
                        "A": [
                            {"a": 1, "b": 2, "c": 3},
                            {"a": 1, "b": 2},
                            {"a": 1},
                            {"a": 1, "b": 2, "c": 3},
                            {"a": 1, "b": 2, "c": 3},
                        ],
                        "B": [
                            {"a": 1},
                            {"a": 1, "b": 2},
                            {"a": 1, "b": 2, "c": 3},
                            {"a": 1, "b": 2, "c": 3},
                            {"a": 1, "c": 2, "d": 3},
                        ],
                    }
                ),
                "expected": pd.DataFrame(
                    {
                        "name": ["a", "b", "c", "d", "e"],
                        "duplication": [
                            ["a"],
                            ["a", "b"],
                            ["a"],
                            ["a", "b", "c"],
                            ["a", "c"],
                        ],
                    }
                ),
            }
        ]
        for i, test_case in enumerate(test_cases):
            with self.subTest(i=i):
                result = get_duplication(test_case["df"], ["A", "B"])
                pd.testing.assert_frame_equal(
                    sort_lists_in_dataframe(result),
                    sort_lists_in_dataframe(test_case["expected"]),
                    check_like=True,
                )


if __name__ == "__main__":
    unittest.main()
