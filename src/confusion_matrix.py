"""Create confusion matrix tables and simple SVG charts for binary prompt classifiers."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


MATRIX_FIELDS = ["expected", "predicted_benign", "predicted_harmful", "total"]


def confusion_counts(result: dict[str, Any]) -> dict[str, dict[str, int]]:
    counts = {
        "benign": {"benign": 0, "harmful": 0},
        "harmful": {"benign": 0, "harmful": 0},
    }
    for example in result["examples"]:
        expected = example["expected"]
        predicted = example["predicted"]
        counts[expected][predicted] += 1
    return counts


def confusion_rows(result: dict[str, Any]) -> list[dict[str, int | str]]:
    counts = confusion_counts(result)
    return [
        {
            "expected": label,
            "predicted_benign": counts[label]["benign"],
            "predicted_harmful": counts[label]["harmful"],
            "total": counts[label]["benign"] + counts[label]["harmful"],
        }
        for label in ("benign", "harmful")
    ]


def write_confusion_csv(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MATRIX_FIELDS)
        writer.writeheader()
        writer.writerows(confusion_rows(result))


def confusion_svg(title: str, result: dict[str, Any]) -> str:
    counts = confusion_counts(result)
    cells = [
        ("benign", "benign", counts["benign"]["benign"]),
        ("benign", "harmful", counts["benign"]["harmful"]),
        ("harmful", "benign", counts["harmful"]["benign"]),
        ("harmful", "harmful", counts["harmful"]["harmful"]),
    ]
    max_count = max((value for _, _, value in cells), default=1)
    max_count = max(max_count, 1)

    width = 620
    height = 360
    cell = 120
    left = 220
    top = 100
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="24" y="36" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#111827">{title}</text>',
        f'<text x="{left + 35}" y="76" font-family="Arial, sans-serif" font-size="13" fill="#374151">Predicted benign</text>',
        f'<text x="{left + cell + 28}" y="76" font-family="Arial, sans-serif" font-size="13" fill="#374151">Predicted harmful</text>',
        f'<text x="40" y="{top + 70}" font-family="Arial, sans-serif" font-size="13" fill="#374151">Expected benign</text>',
        f'<text x="40" y="{top + cell + 70}" font-family="Arial, sans-serif" font-size="13" fill="#374151">Expected harmful</text>',
    ]

    for row_index, expected in enumerate(("benign", "harmful")):
        for col_index, predicted in enumerate(("benign", "harmful")):
            value = counts[expected][predicted]
            intensity = 0.18 + 0.72 * (value / max_count)
            blue = int(255 - 115 * intensity)
            green = int(255 - 80 * intensity)
            fill = f"rgb({blue},{green},255)"
            x = left + col_index * cell
            y = top + row_index * cell
            lines.extend(
                [
                    f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" stroke="#ffffff" stroke-width="2"/>',
                    f'<text x="{x + cell / 2}" y="{y + 66}" text-anchor="middle" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#111827">{value}</text>',
                ]
            )

    lines.append("</svg>")
    return "\n".join(lines)


def write_confusion_svg(path: Path, title: str, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(confusion_svg(title, result), encoding="utf-8")
