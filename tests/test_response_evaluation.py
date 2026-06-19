from pathlib import Path
import sys
import tempfile
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from evaluate_response_level import summarize_rows, validate
from prepare_response_pilot import build_response_rows, select_balanced_rows


def response_row(
    response_id: str,
    prompt_id: str,
    risk_label: str,
    response_label: str,
    model_name: str = "test-model",
) -> str:
    return (
        f"{response_id},{prompt_id},prompts_challenge.csv,{model_name},en,benign,Prompt text,"
        f"Response text,{risk_label},{response_label},Label rationale,no,local test\n"
    )


class ResponseEvaluationTest(unittest.TestCase):
    def test_balanced_pilot_selects_each_language_and_risk_group(self):
        prompt_rows = [
            {
                "id": f"{language}-{risk_label}-{index}",
                "language": language,
                "risk_label": risk_label,
                "attack_type": "benign" if risk_label == "benign" else "policy_removal",
                "prompt_text": f"Prompt {language} {risk_label} {index}",
            }
            for language in ("en", "ko")
            for risk_label in ("benign", "harmful")
            for index in range(3)
        ]

        selected = select_balanced_rows(prompt_rows, per_group=2, seed=7)
        response_rows = build_response_rows(selected, "test.csv")

        self.assertEqual(len(response_rows), 8)
        self.assertEqual(sum(row["language"] == "en" for row in response_rows), 4)
        self.assertEqual(sum(row["prompt_risk_label"] == "harmful" for row in response_rows), 4)
        self.assertTrue(all(not row["response_text"] for row in response_rows))

    def test_validation_rejects_incomplete_pilot_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "incomplete.csv"
            path.write_text(
                "response_id,prompt_id,source_dataset,model_name,language,attack_type,prompt_text,response_text,prompt_risk_label,response_label,rationale,redacted,notes\n"
                "pilot-001,p-001,prompts.csv,,en,benign,Prompt,,benign,,,no,\n",
                encoding="utf-8",
            )

            result = validate(path)

        self.assertFalse(result["valid"])
        self.assertGreater(result["error_count"], 0)

    def test_summary_calculates_response_level_rates(self):
        rows = [
            {"prompt_risk_label": "harmful", "response_label": "safe_refusal"},
            {"prompt_risk_label": "harmful", "response_label": "unsafe_compliance"},
            {"prompt_risk_label": "harmful", "response_label": "partial_compliance"},
            {"prompt_risk_label": "harmful", "response_label": "unclear"},
            {"prompt_risk_label": "benign", "response_label": "safe_completion"},
            {"prompt_risk_label": "benign", "response_label": "safe_refusal"},
        ]

        summary = summarize_rows(rows)

        self.assertEqual(summary["harmful_prompt_total"], 4)
        self.assertEqual(summary["benign_prompt_total"], 2)
        self.assertEqual(summary["metrics"]["safe_refusal_rate"], 0.25)
        self.assertEqual(summary["metrics"]["unsafe_compliance_rate"], 0.25)
        self.assertEqual(summary["metrics"]["partial_compliance_rate"], 0.25)
        self.assertEqual(summary["metrics"]["over_refusal_rate"], 0.5)
        self.assertEqual(summary["metrics"]["safe_completion_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
