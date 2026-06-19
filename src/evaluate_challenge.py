"""Evaluate rule-based and ML baselines on an out-of-template challenge set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from compare_algorithms import comparison_rows, write_csv as write_comparison_csv
from error_analysis import extract_errors, save_errors
from evaluate_guardrail import evaluate as evaluate_rule
from evaluate_guardrail import load_rows
from ml_baseline import NaiveBayesPromptClassifier, TfidfLogisticRegressionPromptClassifier, score_predictions


def evaluate_classifier_on_challenge(
    train_rows: list[dict[str, str]],
    challenge_rows: list[dict[str, str]],
    classifier: Any,
    algorithm: str,
) -> dict[str, Any]:
    classifier.fit(train_rows)

    examples: list[dict[str, Any]] = []
    for row in challenge_rows:
        expected = row["risk_label"].strip().lower()
        predicted = classifier.predict(row["prompt_text"])
        examples.append(
            {
                "id": row["id"],
                "language": row["language"],
                "attack_type": row["attack_type"],
                "expected": expected,
                "predicted": predicted,
                "correct": expected == predicted,
            }
        )

    return {
        "algorithm": algorithm,
        "validation": "train on prompts_extended, test on prompts_challenge",
        "summary": score_predictions(examples),
        "examples": examples,
    }


def evaluate_ml_on_challenge(train_rows: list[dict[str, str]], challenge_rows: list[dict[str, str]]) -> dict[str, Any]:
    return evaluate_classifier_on_challenge(
        train_rows,
        challenge_rows,
        NaiveBayesPromptClassifier(),
        "char_ngram_naive_bayes_challenge",
    )


def evaluate_logistic_regression_on_challenge(
    train_rows: list[dict[str, str]], challenge_rows: list[dict[str, str]]
) -> dict[str, Any]:
    return evaluate_classifier_on_challenge(
        train_rows,
        challenge_rows,
        TfidfLogisticRegressionPromptClassifier(),
        "tfidf_logistic_regression_challenge",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", default="data/prompts_extended.csv")
    parser.add_argument("--challenge", default="data/prompts_challenge.csv")
    parser.add_argument("--reports-dir", default="reports")
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    train_rows = load_rows(Path(args.train))
    challenge_rows = load_rows(Path(args.challenge))

    rule_results = evaluate_rule(challenge_rows)
    ml_results = evaluate_ml_on_challenge(train_rows, challenge_rows)
    logistic_results = evaluate_logistic_regression_on_challenge(train_rows, challenge_rows)
    algorithms = comparison_rows(rule_results, ml_results, logistic_results)

    (reports_dir / "challenge_rule_results.json").write_text(
        json.dumps(rule_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (reports_dir / "challenge_ml_results.json").write_text(
        json.dumps(ml_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (reports_dir / "challenge_logistic_results.json").write_text(
        json.dumps(logistic_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_comparison_csv(reports_dir / "challenge_algorithm_comparison.csv", algorithms)
    save_errors(extract_errors(rule_results), reports_dir / "challenge_errors.csv")
    save_errors(extract_errors(ml_results), reports_dir / "challenge_ml_errors.csv")
    save_errors(extract_errors(logistic_results), reports_dir / "challenge_logistic_errors.csv")

    print(json.dumps(algorithms, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
