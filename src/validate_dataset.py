"""Validate the KoGuard-Mini CSV dataset before evaluation."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = ["id", "language", "attack_type", "category", "risk_label", "prompt_text", "notes"]
ALLOWED_LANGUAGES = {"ko", "en"}
ALLOWED_RISK_LABELS = {"benign", "harmful"}


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def validate(path: Path) -> dict[str, Any]:
    columns, rows = load_rows(path)
    issues: list[dict[str, Any]] = []

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in columns]
    for column in missing_columns:
        issues.append({"level": "error", "type": "missing_column", "message": f"Missing column: {column}"})

    id_counts = Counter(row.get("id", "").strip() for row in rows)
    prompt_counts = Counter(row.get("prompt_text", "").strip() for row in rows)

    for row_number, row in enumerate(rows, start=2):
        row_id = row.get("id", "").strip()
        language = row.get("language", "").strip()
        risk_label = row.get("risk_label", "").strip()
        prompt_text = row.get("prompt_text", "").strip()

        if not row_id:
            issues.append({"level": "error", "type": "missing_id", "row": row_number})
        if row_id and id_counts[row_id] > 1:
            issues.append({"level": "error", "type": "duplicate_id", "row": row_number, "id": row_id})
        if language not in ALLOWED_LANGUAGES:
            issues.append(
                {"level": "error", "type": "invalid_language", "row": row_number, "id": row_id, "value": language}
            )
        if risk_label not in ALLOWED_RISK_LABELS:
            issues.append(
                {"level": "error", "type": "invalid_risk_label", "row": row_number, "id": row_id, "value": risk_label}
            )
        if not prompt_text:
            issues.append({"level": "error", "type": "empty_prompt", "row": row_number, "id": row_id})
        if prompt_text and prompt_counts[prompt_text] > 1:
            issues.append({"level": "warning", "type": "duplicate_prompt", "row": row_number, "id": row_id})

    errors = [issue for issue in issues if issue["level"] == "error"]
    warnings = [issue for issue in issues if issue["level"] == "warning"]

    return {
        "valid": not errors,
        "row_count": len(rows),
        "column_count": len(columns),
        "missing_columns": missing_columns,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to CSV prompt dataset")
    parser.add_argument("--output", help="Optional path to save JSON validation report")
    args = parser.parse_args()

    result = validate(Path(args.input))
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
