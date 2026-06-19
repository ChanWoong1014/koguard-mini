"""Create a balanced, local-only pilot file for LLM response evaluation."""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path


RESPONSE_COLUMNS = [
    "response_id",
    "prompt_id",
    "source_dataset",
    "model_name",
    "language",
    "attack_type",
    "prompt_text",
    "response_text",
    "prompt_risk_label",
    "response_label",
    "rationale",
    "redacted",
    "notes",
]


def load_prompt_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def select_balanced_rows(rows: list[dict[str, str]], per_group: int, seed: int) -> list[dict[str, str]]:
    """Select equal counts from the four language/risk-label groups."""
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["language"], row["risk_label"])].append(row)

    required_groups = [("en", "benign"), ("en", "harmful"), ("ko", "benign"), ("ko", "harmful")]
    missing = [group for group in required_groups if len(grouped[group]) < per_group]
    if missing:
        details = ", ".join(f"{language}/{risk_label}" for language, risk_label in missing)
        raise ValueError(f"Not enough prompts for pilot groups: {details}")

    rng = random.Random(seed)
    selected: list[dict[str, str]] = []
    for group in required_groups:
        candidates = sorted(grouped[group], key=lambda row: row["id"])
        selected.extend(rng.sample(candidates, per_group))

    return selected


def build_response_rows(prompt_rows: list[dict[str, str]], source_dataset: str) -> list[dict[str, str]]:
    response_rows: list[dict[str, str]] = []
    for index, prompt in enumerate(prompt_rows, start=1):
        response_rows.append(
            {
                "response_id": f"pilot-{index:03d}",
                "prompt_id": prompt["id"],
                "source_dataset": source_dataset,
                "model_name": "",
                "language": prompt["language"],
                "attack_type": prompt["attack_type"],
                "prompt_text": prompt["prompt_text"],
                "response_text": "",
                "prompt_risk_label": prompt["risk_label"],
                "response_label": "",
                "rationale": "",
                "redacted": "no",
                "notes": "Pilot row. Add one model response and label it using the response evaluation plan.",
            }
        )
    return response_rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESPONSE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a balanced response-level evaluation pilot CSV.")
    parser.add_argument("--input", default="data/prompts_challenge.csv", help="Prompt dataset CSV")
    parser.add_argument(
        "--output",
        default="data/response_evaluations/pilot_20.csv",
        help="Local-only output CSV. This directory is ignored by Git.",
    )
    parser.add_argument("--per-group", type=int, default=5, help="Rows from each language/risk group")
    parser.add_argument("--seed", type=int, default=20260620, help="Random seed for reproducible sampling")
    args = parser.parse_args()

    if args.per_group < 1:
        raise SystemExit("--per-group must be at least 1.")

    input_path = Path(args.input)
    selected = select_balanced_rows(load_prompt_rows(input_path), args.per_group, args.seed)
    response_rows = build_response_rows(selected, input_path.name)
    output_path = Path(args.output)
    write_rows(output_path, response_rows)

    print(f"Created {len(response_rows)} pilot rows: {output_path}")
    print("This file is intentionally ignored by Git because it may contain model responses.")


if __name__ == "__main__":
    main()
