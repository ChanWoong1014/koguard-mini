"""Create a Markdown portfolio report draft from generated result files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_errors(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_table(summary: dict[str, Any]) -> str:
    rows = [
        ("Total prompts", summary["total"]),
        ("Accuracy", summary["accuracy"]),
        ("Precision for harmful prompts", summary["precision_harmful"]),
        ("Recall for harmful prompts", summary["recall_harmful"]),
        ("F1 for harmful prompts", summary["f1_harmful"]),
        ("False allow rate", summary["false_allow_rate"]),
        ("False refusal rate", summary["false_refusal_rate"]),
    ]
    lines = ["| Metric | Value |", "|---|---:|"]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    return "\n".join(lines)


def count_table(title: str, counts: dict[str, int]) -> str:
    lines = [f"### {title}", "", "| Group | Count |", "|---|---:|"]
    for key, value in counts.items():
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def grouped_result_table(title: str, grouped: dict[str, dict[str, Any]]) -> str:
    lines = [
        f"### {title}",
        "",
        "| Group | Total | Correct | Accuracy | False Allow | False Refusal |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key, value in grouped.items():
        lines.append(
            "| {key} | {total} | {correct} | {accuracy} | {false_allow_rate} | {false_refusal_rate} |".format(
                key=key,
                total=value["total"],
                correct=value["correct"],
                accuracy=value["accuracy"],
                false_allow_rate=value["false_allow_rate"],
                false_refusal_rate=value["false_refusal_rate"],
            )
        )
    return "\n".join(lines)


def error_table(errors: list[dict[str, str]]) -> str:
    if not errors:
        return "No incorrect predictions were found in the current evaluation."

    lines = [
        "| ID | Language | Attack Type | Expected | Predicted | Matched Patterns |",
        "|---|---|---|---|---|---|",
    ]
    for item in errors:
        lines.append(
            "| {id} | {language} | {attack_type} | {expected} | {predicted} | {matched_patterns} |".format(
                **item
            )
        )
    return "\n".join(lines)


def algorithm_table(rows: list[dict[str, Any]] | None) -> str:
    if not rows:
        return "Algorithm comparison was not generated."

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


def build_report(
    dataset_summary: dict[str, Any],
    results: dict[str, Any],
    errors: list[dict[str, str]],
    algorithms: list[dict[str, Any]] | None = None,
    challenge_algorithms: list[dict[str, Any]] | None = None,
) -> str:
    summary = results["summary"]
    return "\n\n".join(
        [
            "# KoGuard-Mini Portfolio Report Draft",
            "## 1. Project Summary\n\n"
            "KoGuard-Mini is a small Korean-English LLM prompt safety evaluation project. "
            "The goal is not to train a new LLM, but to build an interpretable evaluation "
            "pipeline for checking whether prompts look benign or adversarial.",
            "## 2. Research Question\n\n"
            "Can a simple rule-based guardrail detect sanitized English and Korean bypass-style prompts?",
            "## 3. Dataset Summary\n\n"
            f"- Total rows: {dataset_summary['total']}\n"
            f"- Average prompt length: {dataset_summary['average_prompt_length']}\n"
            f"- Min prompt length: {dataset_summary['min_prompt_length']}\n"
            f"- Max prompt length: {dataset_summary['max_prompt_length']}\n\n"
            + count_table("By Language", dataset_summary["by_language"])
            + "\n\n"
            + count_table("By Risk Label", dataset_summary["by_risk_label"])
            + "\n\n"
            + count_table("By Attack Type", dataset_summary["by_attack_type"]),
            "## 4. Evaluation Metrics\n\n" + metric_table(summary),
            "## 5. Algorithm Comparison\n\n"
            + algorithm_table(algorithms)
            + "\n\n![Harmful F1 by Algorithm](chart_algorithm_f1.svg)",
            "## 6. Challenge Set Generalization\n\n"
            + algorithm_table(challenge_algorithms)
            + "\n\n![Challenge Harmful F1 by Algorithm](chart_challenge_algorithm_f1.svg)\n\n"
            "The challenge set is written separately from the main extended dataset. It is used to check whether the algorithms handle new wording patterns instead of only fitting the main synthetic dataset.",
            "## 7. Visual Summary\n\n"
            "![Accuracy by Language](chart_accuracy_by_language.svg)\n\n"
            "![False Allow Rate by Attack Type](chart_false_allow_by_attack_type.svg)\n\n"
            "![Dataset Rows by Attack Type](chart_dataset_by_attack_type.svg)",
            "## 8. Grouped Results\n\n"
            + grouped_result_table("By Language", results["by_language"])
            + "\n\n"
            + grouped_result_table("By Attack Type", results["by_attack_type"]),
            "## 9. Error Analysis\n\n" + error_table(errors),
            "## 10. Interpretation\n\n"
            "The rule-based baseline is interpretable but brittle. It performs best when prompts contain explicit "
            "keywords that match the written rules, but it misses many paraphrased harmful-style prompts. "
            "The character n-gram Naive Bayes baseline improves harmful recall on this sanitized dataset, but this "
            "should not be interpreted as production-level safety. Incorrect predictions are useful because they show "
            "where simple pattern matching and simple ML both have limits.",
            "## 11. Limitations\n\n"
            "- The dataset is useful for a portfolio but still small for research.\n"
            "- Labels are manually assigned.\n"
            "- The guardrail uses simple text patterns, so it is brittle.\n"
            "- The Naive Bayes baseline is simple and may overfit synthetic wording patterns.\n"
            "- The project currently evaluates prompts only, not actual LLM responses.\n"
            "- The published dataset avoids detailed harmful instructions, so it is safer but less realistic.",
            "## 12. Next Steps\n\n"
            "- Expand the dataset beyond 200 rows with more realistic but still safe paraphrases.\n"
            "- Add more Korean paraphrases that do not use obvious keywords.\n"
            "- Add response-level labeling: safe refusal, partial compliance, unsafe compliance.\n"
            "- Compare additional ML baselines such as logistic regression or TF-IDF classifiers.\n"
            "- Convert this Markdown draft into a 6-10 page PDF portfolio report.",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-summary", required=True, help="Path to dataset summary JSON")
    parser.add_argument("--results", required=True, help="Path to evaluation result JSON")
    parser.add_argument("--errors", required=True, help="Path to error CSV")
    parser.add_argument("--output", required=True, help="Path to output Markdown report")
    args = parser.parse_args()

    report = build_report(
        dataset_summary=load_json(Path(args.dataset_summary)),
        results=load_json(Path(args.results)),
        errors=load_errors(Path(args.errors)),
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Saved report draft to {output_path}")


if __name__ == "__main__":
    main()
