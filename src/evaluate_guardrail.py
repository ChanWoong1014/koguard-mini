"""Evaluate the rule-based guardrail on a CSV prompt dataset."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from rule_guardrail import classify_prompt


def safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def evaluate(rows: list[dict[str, str]]) -> dict[str, Any]:
    examples: list[dict[str, Any]] = []
    total = len(rows)
    correct = 0
    true_harmful = 0
    true_benign = 0
    predicted_harmful = 0
    false_allow = 0
    false_refusal = 0

    by_language: dict[str, dict[str, int]] = {}
    by_attack_type: dict[str, dict[str, int]] = {}

    for row in rows:
        expected = row["risk_label"].strip().lower()
        decision = classify_prompt(row["prompt_text"])
        predicted = decision.label
        is_correct = expected == predicted

        correct += int(is_correct)
        true_harmful += int(expected == "harmful")
        true_benign += int(expected == "benign")
        predicted_harmful += int(predicted == "harmful")
        false_allow += int(expected == "harmful" and predicted == "benign")
        false_refusal += int(expected == "benign" and predicted == "harmful")

        language = row.get("language", "unknown")
        attack_type = row.get("attack_type", "unknown")
        for group, key in ((by_language, language), (by_attack_type, attack_type)):
            group.setdefault(key, {"total": 0, "correct": 0, "false_allow": 0, "false_refusal": 0})
            group[key]["total"] += 1
            group[key]["correct"] += int(is_correct)
            group[key]["false_allow"] += int(expected == "harmful" and predicted == "benign")
            group[key]["false_refusal"] += int(expected == "benign" and predicted == "harmful")

        examples.append(
            {
                "id": row["id"],
                "language": language,
                "attack_type": attack_type,
                "expected": expected,
                "predicted": predicted,
                "correct": is_correct,
                "matched_patterns": decision.matched_patterns,
            }
        )

    precision = safe_divide(correct_harmful_predictions(examples), predicted_harmful)
    recall = safe_divide(correct_harmful_predictions(examples), true_harmful)
    f1 = safe_divide(2 * precision * recall, precision + recall)

    return {
        "summary": {
            "total": total,
            "accuracy": round(safe_divide(correct, total), 4),
            "precision_harmful": round(precision, 4),
            "recall_harmful": round(recall, 4),
            "f1_harmful": round(f1, 4),
            "false_allow_rate": round(safe_divide(false_allow, true_harmful), 4),
            "false_refusal_rate": round(safe_divide(false_refusal, true_benign), 4),
        },
        "by_language": add_rates(by_language),
        "by_attack_type": add_rates(by_attack_type),
        "examples": examples,
    }


def correct_harmful_predictions(examples: list[dict[str, Any]]) -> int:
    return sum(1 for item in examples if item["expected"] == "harmful" and item["predicted"] == "harmful")


def add_rates(grouped: dict[str, dict[str, int]]) -> dict[str, dict[str, float | int]]:
    output: dict[str, dict[str, float | int]] = {}
    for key, values in grouped.items():
        total = values["total"]
        output[key] = {
            **values,
            "accuracy": round(safe_divide(values["correct"], total), 4),
            "false_allow_rate": round(safe_divide(values["false_allow"], total), 4),
            "false_refusal_rate": round(safe_divide(values["false_refusal"], total), 4),
        }
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to CSV prompt dataset")
    parser.add_argument("--output", required=True, help="Path to output JSON report")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = evaluate(load_rows(input_path))
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
