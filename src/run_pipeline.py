"""Run the full KoGuard-Mini local evaluation pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dataset_summary import load_rows as load_dataset_rows
from dataset_summary import summarize
from error_analysis import extract_errors, save_errors
from evaluate_guardrail import evaluate
from evaluate_guardrail import load_rows as load_evaluation_rows
from export_assets import export_algorithm_chart, export_assets
from compare_algorithms import comparison_rows, write_csv as write_comparison_csv
from make_korean_report import build_korean_report
from make_challenge_report import build_report as build_challenge_report
from make_markdown_report import build_report
from evaluate_challenge import evaluate_ml_on_challenge
from ml_baseline import evaluate_cross_validation
from validate_dataset import validate
from export_assets import horizontal_bar_svg


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/prompts_extended.csv", help="Path to prompt CSV dataset")
    parser.add_argument("--challenge-input", default="data/prompts_challenge.csv", help="Optional challenge CSV dataset")
    parser.add_argument("--reports-dir", default="reports", help="Directory where reports will be saved")
    args = parser.parse_args()

    input_path = Path(args.input)
    challenge_path = Path(args.challenge_input)
    reports_dir = Path(args.reports_dir)

    validation = validate(input_path)
    if not validation["valid"]:
        write_json(reports_dir / "validation.json", validation)
        raise SystemExit("Dataset validation failed. See reports/validation.json.")

    dataset_summary = summarize(load_dataset_rows(input_path))
    rows = load_evaluation_rows(input_path)
    results = evaluate(rows)
    ml_results = evaluate_cross_validation(rows, k=5)
    algorithms = comparison_rows(results, ml_results)
    errors = extract_errors(results)
    ml_errors = extract_errors(ml_results)

    validation_path = reports_dir / "validation.json"
    dataset_summary_path = reports_dir / "dataset_summary.json"
    results_path = reports_dir / "results.json"
    ml_results_path = reports_dir / "ml_results.json"
    algorithm_comparison_path = reports_dir / "algorithm_comparison.csv"
    errors_path = reports_dir / "errors.csv"
    ml_errors_path = reports_dir / "ml_errors.csv"
    report_path = reports_dir / "experiment_report.md"
    korean_report_path = reports_dir / "experiment_report_ko.md"

    write_json(validation_path, validation)
    write_json(dataset_summary_path, dataset_summary)
    write_json(results_path, results)
    write_json(ml_results_path, ml_results)
    write_comparison_csv(algorithm_comparison_path, algorithms)
    save_errors(errors, errors_path)
    save_errors(ml_errors, ml_errors_path)
    export_assets(dataset_summary, results, reports_dir)
    export_algorithm_chart(algorithms, reports_dir)

    challenge_algorithms = None
    if challenge_path.exists():
        challenge_rows = load_evaluation_rows(challenge_path)
        challenge_rule_results = evaluate(challenge_rows)
        challenge_ml_results = evaluate_ml_on_challenge(rows, challenge_rows)
        challenge_algorithms = comparison_rows(challenge_rule_results, challenge_ml_results)
        write_json(reports_dir / "challenge_rule_results.json", challenge_rule_results)
        write_json(reports_dir / "challenge_ml_results.json", challenge_ml_results)
        write_comparison_csv(reports_dir / "challenge_algorithm_comparison.csv", challenge_algorithms)
        save_errors(extract_errors(challenge_rule_results), reports_dir / "challenge_errors.csv")
        save_errors(extract_errors(challenge_ml_results), reports_dir / "challenge_ml_errors.csv")
        (reports_dir / "chart_challenge_algorithm_f1.svg").write_text(
            horizontal_bar_svg(
                "Challenge Harmful F1 by Algorithm",
                {row["algorithm"]: float(row["f1_harmful"]) for row in challenge_algorithms},
            ),
            encoding="utf-8",
        )
        (reports_dir / "challenge_report.md").write_text(
            build_challenge_report(challenge_algorithms),
            encoding="utf-8",
        )

    report_path.write_text(build_report(dataset_summary, results, errors, algorithms, challenge_algorithms), encoding="utf-8")
    korean_report_path.write_text(
        build_korean_report(dataset_summary, results, errors, algorithms, challenge_algorithms),
        encoding="utf-8",
    )

    print("KoGuard-Mini pipeline complete.")
    print(f"- Validation: {validation_path}")
    print(f"- Dataset summary: {dataset_summary_path}")
    print(f"- Evaluation results: {results_path}")
    print(f"- ML results: {ml_results_path}")
    print(f"- Algorithm comparison: {algorithm_comparison_path}")
    print(f"- Error rows: {errors_path}")
    print(f"- ML error rows: {ml_errors_path}")
    print(f"- Report draft: {report_path}")
    print(f"- Korean report draft: {korean_report_path}")
    if challenge_path.exists():
        print(f"- Challenge report: {reports_dir / 'challenge_report.md'}")


if __name__ == "__main__":
    main()
