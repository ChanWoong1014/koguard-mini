"""Compare rule-based and ML baseline summaries."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


FIELDS = [
    "algorithm",
    "total",
    "accuracy",
    "precision_harmful",
    "recall_harmful",
    "f1_harmful",
    "false_allow_rate",
    "false_refusal_rate",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def comparison_rows(rule_results: dict[str, Any], ml_results: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"algorithm": "rule_based_guardrail", **rule_results["summary"]},
        {"algorithm": ml_results["algorithm"], **ml_results["summary"]},
    ]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-results", required=True)
    parser.add_argument("--ml-results", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = comparison_rows(load_json(Path(args.rule_results)), load_json(Path(args.ml_results)))
    write_csv(Path(args.output), rows)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
