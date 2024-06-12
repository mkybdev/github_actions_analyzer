import unittest
import pandas as pd
from github_actions_analyzer.cooccurrence.get_probability import get_probability


class TestGetProbability(unittest.TestCase):
    def test_get_probability(self):
        test_cases = [
            # Test case 1
            {
                "df": pd.Series(
                    [["A"], ["B"], ["C"], ["C"], ["A"], ["B"], ["A"], ["A"]],
                ),
                "expected": pd.Series(
                    [0.5, 0.25, 0.25],
                    name="probability",
                    index=["A", "B", "C"],
                ),
            },
            # Test case 2
            {
                "df": pd.Series(
                    [
                        ["A", "B", "D"],
                        ["B", "C"],
                        ["C"],
                        ["C", "E"],
                        ["A", "C", "D", "E"],
                        ["B", "D", "E"],
                        ["A", "B", "C", "D"],
                        ["A", "E"],
                    ],
                ),
                "expected": pd.Series(
                    [0.5, 0.5, 0.625, 0.5, 0.5],
                    name="probability",
                    index=["A", "B", "C", "D", "E"],
                ),
            },
        ]
        for i, test_case in enumerate(test_cases):
            with self.subTest(i=i):
                result = get_probability(test_case["df"])
                pd.testing.assert_series_equal(
                    result,
                    test_case["expected"],
                    check_like=True,
                )


if __name__ == "__main__":
    unittest.main()
