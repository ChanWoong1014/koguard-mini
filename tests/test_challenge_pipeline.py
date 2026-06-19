from pathlib import Path
import sys
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from build_challenge_dataset import make_rows
from evaluate_challenge import evaluate_logistic_regression_on_challenge, evaluate_ml_on_challenge
from evaluate_guardrail import evaluate
from ml_baseline import load_rows


class ChallengePipelineTest(unittest.TestCase):
    def test_challenge_dataset_builder_creates_80_rows(self):
        rows = make_rows()

        self.assertEqual(len(rows), 80)
        self.assertEqual(sum(1 for row in rows if row["language"] == "en"), 40)
        self.assertEqual(sum(1 for row in rows if row["language"] == "ko"), 40)
        self.assertEqual(sum(1 for row in rows if row["risk_label"] == "benign"), 40)
        self.assertEqual(sum(1 for row in rows if row["risk_label"] == "harmful"), 40)

    def test_challenge_evaluation_runs(self):
        root = Path(__file__).resolve().parents[1]
        train_rows = load_rows(root / "data" / "prompts_extended.csv")
        challenge_rows = make_rows()

        rule_result = evaluate(challenge_rows)
        ml_result = evaluate_ml_on_challenge(train_rows, challenge_rows)
        logistic_result = evaluate_logistic_regression_on_challenge(train_rows, challenge_rows)

        self.assertEqual(rule_result["summary"]["total"], 80)
        self.assertEqual(ml_result["summary"]["total"], 80)
        self.assertEqual(logistic_result["summary"]["total"], 80)
        self.assertIn("accuracy", rule_result["summary"])
        self.assertIn("accuracy", ml_result["summary"])
        self.assertIn("accuracy", logistic_result["summary"])


if __name__ == "__main__":
    unittest.main()
