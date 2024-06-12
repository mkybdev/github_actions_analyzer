import unittest
import pandas as pd
from github_actions_analyzer.intersection.get_frequency import get_frequency
from github_actions_analyzer.intersection.get_duplication import get_duplication


class TestGetFrequency(unittest.TestCase):
    def test_get_frequency(self):
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
                        "Element": ["a", "b", "c"],
                        "Frequency": [5, 2, 2],
                        "Dict_Key_Count_A": [5, 4, 3],
                        "Dict_Key_Count_B": [5, 3, 3],
                    }
                ),
            }
        ]
        for i, test_case in enumerate(test_cases):
            with self.subTest(i=i):
                result = get_frequency(
                    test_case["df"],
                    get_duplication(test_case["df"], ["A", "B"]),
                    ["A", "B"],
                )
                pd.testing.assert_frame_equal(
                    result, test_case["expected"], check_like=True
                )


if __name__ == "__main__":
    unittest.main()
