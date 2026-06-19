"""Extract incorrect predictions from an evaluation result JSON file."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def load_result(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_errors(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in result["examples"] if not item["correct"]]


def save_errors(errors: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "language", "attack_type", "expected", "predicted", "matched_patterns", "fold"]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in errors:
            writer.writerow(
                {
                    "id": item["id"],
                    "language": item["language"],
                    "attack_type": item["attack_type"],
                    "expected": item["expected"],
                    "predicted": item["predicted"],
                    "matched_patterns": ";".join(item.get("matched_patterns", [])),
                    "fold": item.get("fold", ""),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to evaluation JSON file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    result = load_result(Path(args.input))
    errors = extract_errors(result)
    save_errors(errors, Path(args.output))

    print(f"Saved {len(errors)} error rows to {args.output}")


if __name__ == "__main__":
    main()
