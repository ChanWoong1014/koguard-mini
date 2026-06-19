from pathlib import Path
import sys
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from confusion_matrix import confusion_rows


class ConfusionMatrixTest(unittest.TestCase):
    def test_confusion_rows_count_binary_predictions(self):
        result = {
            "examples": [
                {"expected": "benign", "predicted": "benign"},
                {"expected": "benign", "predicted": "harmful"},
                {"expected": "harmful", "predicted": "benign"},
                {"expected": "harmful", "predicted": "harmful"},
                {"expected": "harmful", "predicted": "harmful"},
            ]
        }

        rows = confusion_rows(result)

        self.assertEqual(
            rows,
            [
                {"expected": "benign", "predicted_benign": 1, "predicted_harmful": 1, "total": 2},
                {"expected": "harmful", "predicted_benign": 1, "predicted_harmful": 2, "total": 3},
            ],
        )


if __name__ == "__main__":
    unittest.main()
