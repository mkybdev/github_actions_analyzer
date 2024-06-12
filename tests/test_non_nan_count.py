import unittest
import pandas as pd
from github_actions_analyzer.common.non_nan_count import non_nan_count


class TestNonNanCount(unittest.TestCase):
    def test_non_nan_count(self):
        test_cases = [
            # Test case 1
            {
                "df": pd.DataFrame(
                    {
                        "A": [1, 2, 3, 4, 5],
                        "B": [1.1, 2.2, 3.3, 4.4, 5.5],
                        "C": ["a", "b", "c", "d", "e"],
                        "D": [True, False, True, False, True],
                    }
                ),
                "expected": pd.DataFrame(
                    {"Column": ["A", "B", "C", "D"], "Non_NaN_Count": [5, 5, 5, 5]}
                ),
            },
            # Test case 2
            {
                "df": pd.DataFrame(
                    {
                        "A": [1, 2, 3, 4, 5],
                        "B": [1.1, 2.2, 3.3, 4.4, 5.5],
                        "C": ["a", "b", "c", "d", None],
                        "D": [True, False, True, False, True],
                    }
                ),
                "expected": pd.DataFrame(
                    {"Column": ["A", "B", "C", "D"], "Non_NaN_Count": [5, 5, 4, 5]}
                ),
            },
            # Test case 3
            {
                "df": pd.DataFrame(
                    {
                        "A": [1, 2, 3, 4, 5],
                        "B": [1.1, 2.2, 3.3, 4.4, 5.5],
                        "C": ["a", "b", "c", "d", None],
                        "D": [True, False, True, False, None],
                    }
                ),
                "expected": pd.DataFrame(
                    {"Column": ["A", "B", "C", "D"], "Non_NaN_Count": [5, 5, 4, 4]}
                ),
            },
        ]
        for i, test_case in enumerate(test_cases):
            with self.subTest(i=i):
                result = non_nan_count(test_case["df"])
                pd.testing.assert_frame_equal(
                    result, test_case["expected"], check_like=True
                )


if __name__ == "__main__":
    unittest.main()
