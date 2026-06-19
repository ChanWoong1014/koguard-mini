"""Create a short Markdown report for challenge-set evaluation."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def table(rows: list[dict[str, str]]) -> str:
    lines = [
        "| Algorithm | Accuracy | Harmful Precision | Harmful Recall | Harmful F1 | False Allow | False Refusal |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {algorithm} | {accuracy} | {precision_harmful} | {recall_harmful} | {f1_harmful} | {false_allow_rate} | {false_refusal_rate} |".format(
                **row
            )
        )
    return "\n".join(lines)


def build_report(rows: list[dict[str, str]]) -> str:
    return "\n\n".join(
        [
            "# Challenge Set Evaluation",
            "## Purpose\n\n"
            "The challenge set contains prompts that were written separately from the main extended dataset. "
            "It is used to check whether each baseline generalizes to new wording patterns.",
            "## Results\n\n" + table(rows),
            "## Interpretation\n\n"
            "If a model performs much worse on the challenge set than on cross-validation, that suggests it may be "
            "overfitting the wording patterns in the main synthetic dataset. This is important because real user prompts "
            "will not follow the exact wording used in the training data.",
            "## Limitations\n\n"
            "- The challenge set is still synthetic.\n"
            "- It is smaller than the main dataset.\n"
            "- It tests prompt-level classification only, not actual LLM responses.\n"
            "- It should be treated as a portfolio-level generalization check, not a production benchmark.",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", default="reports/challenge_algorithm_comparison.csv")
    parser.add_argument("--output", default="reports/challenge_report.md")
    args = parser.parse_args()

    report = build_report(load_rows(Path(args.comparison)))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(f"Saved challenge report to {output}")


if __name__ == "__main__":
    main()
