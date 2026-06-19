"""Export CSV tables and SVG charts for the portfolio report."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def grouped_rows(grouped: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group, values in grouped.items():
        rows.append(
            {
                "group": group,
                "total": values["total"],
                "correct": values["correct"],
                "accuracy": values["accuracy"],
                "false_allow_rate": values["false_allow_rate"],
                "false_refusal_rate": values["false_refusal_rate"],
            }
        )
    return rows


def horizontal_bar_svg(title: str, values: dict[str, float], width: int = 920) -> str:
    label_width = 250
    chart_width = width - label_width - 120
    bar_height = 24
    gap = 10
    top = 56
    row_height = bar_height + gap
    height = top + len(values) * row_height + 40
    max_value = max(values.values()) if values else 1.0
    max_value = max(max_value, 0.001)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="24" y="32" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#111827">{title}</text>',
    ]

    for index, (label, value) in enumerate(values.items()):
        y = top + index * row_height
        bar_width = int((value / max_value) * chart_width)
        value_label = f"{value:.2f}" if isinstance(value, float) else str(value)
        lines.extend(
            [
                f'<text x="24" y="{y + 17}" font-family="Arial, sans-serif" font-size="13" fill="#374151">{label}</text>',
                f'<rect x="{label_width}" y="{y}" width="{chart_width}" height="{bar_height}" rx="4" fill="#e5e7eb"/>',
                f'<rect x="{label_width}" y="{y}" width="{bar_width}" height="{bar_height}" rx="4" fill="#2563eb"/>',
                f'<text x="{label_width + chart_width + 16}" y="{y + 17}" font-family="Arial, sans-serif" font-size="13" fill="#111827">{value_label}</text>',
            ]
        )

    lines.append("</svg>")
    return "\n".join(lines)


def count_svg(title: str, counts: dict[str, int], width: int = 920) -> str:
    return horizontal_bar_svg(title, {key: float(value) for key, value in counts.items()}, width=width)


def export_assets(dataset_summary: dict[str, Any], results: dict[str, Any], reports_dir: Path) -> dict[str, str]:
    reports_dir.mkdir(parents=True, exist_ok=True)

    language_rows = grouped_rows(results["by_language"])
    attack_rows = grouped_rows(results["by_attack_type"])

    write_csv(
        reports_dir / "metrics_by_language.csv",
        language_rows,
        ["group", "total", "correct", "accuracy", "false_allow_rate", "false_refusal_rate"],
    )
    write_csv(
        reports_dir / "metrics_by_attack_type.csv",
        attack_rows,
        ["group", "total", "correct", "accuracy", "false_allow_rate", "false_refusal_rate"],
    )

    (reports_dir / "chart_accuracy_by_language.svg").write_text(
        horizontal_bar_svg(
            "Accuracy by Language",
            {group: values["accuracy"] for group, values in results["by_language"].items()},
        ),
        encoding="utf-8",
    )
    (reports_dir / "chart_false_allow_by_attack_type.svg").write_text(
        horizontal_bar_svg(
            "False Allow Rate by Attack Type",
            {group: values["false_allow_rate"] for group, values in results["by_attack_type"].items()},
        ),
        encoding="utf-8",
    )
    (reports_dir / "chart_dataset_by_attack_type.svg").write_text(
        count_svg("Dataset Rows by Attack Type", dataset_summary["by_attack_type"]),
        encoding="utf-8",
    )

    return {
        "metrics_by_language": str(reports_dir / "metrics_by_language.csv"),
        "metrics_by_attack_type": str(reports_dir / "metrics_by_attack_type.csv"),
        "chart_accuracy_by_language": str(reports_dir / "chart_accuracy_by_language.svg"),
        "chart_false_allow_by_attack_type": str(reports_dir / "chart_false_allow_by_attack_type.svg"),
        "chart_dataset_by_attack_type": str(reports_dir / "chart_dataset_by_attack_type.svg"),
    }


def export_algorithm_chart(comparison_rows: list[dict[str, Any]], reports_dir: Path) -> str:
    values = {row["algorithm"]: float(row["f1_harmful"]) for row in comparison_rows}
    path = reports_dir / "chart_algorithm_f1.svg"
    path.write_text(horizontal_bar_svg("Harmful F1 by Algorithm", values), encoding="utf-8")
    return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-summary", default="reports/dataset_summary.json")
    parser.add_argument("--results", default="reports/results.json")
    parser.add_argument("--reports-dir", default="reports")
    args = parser.parse_args()

    outputs = export_assets(
        dataset_summary=load_json(Path(args.dataset_summary)),
        results=load_json(Path(args.results)),
        reports_dir=Path(args.reports_dir),
    )
    print(json.dumps(outputs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
