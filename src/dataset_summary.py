"""Print a compact summary of the prompt dataset."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def summarize(rows: list[dict[str, str]]) -> dict[str, Any]:
    prompt_lengths = [len(row["prompt_text"]) for row in rows]
    average_prompt_length = sum(prompt_lengths) / len(prompt_lengths) if prompt_lengths else 0.0

    return {
        "total": len(rows),
        "by_language": dict(Counter(row["language"] for row in rows)),
        "by_risk_label": dict(Counter(row["risk_label"] for row in rows)),
        "by_attack_type": dict(Counter(row["attack_type"] for row in rows)),
        "by_category": dict(Counter(row["category"] for row in rows)),
        "average_prompt_length": round(average_prompt_length, 2),
        "min_prompt_length": min(prompt_lengths) if prompt_lengths else 0,
        "max_prompt_length": max(prompt_lengths) if prompt_lengths else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to CSV prompt dataset")
    parser.add_argument("--output", help="Optional path to save JSON summary")
    args = parser.parse_args()

    summary = summarize(load_rows(Path(args.input)))
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
