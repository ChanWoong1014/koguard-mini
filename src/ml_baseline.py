"""Small no-dependency ML baselines for prompt classification."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


LABELS = ["benign", "harmful"]


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def char_ngrams(text: str, min_n: int = 3, max_n: int = 5) -> list[str]:
    normalized = f"  {' '.join(text.lower().strip().split())}  "
    features: list[str] = []
    for n in range(min_n, max_n + 1):
        if len(normalized) >= n:
            features.extend(normalized[index : index + n] for index in range(len(normalized) - n + 1))
    return features


class NaiveBayesPromptClassifier:
    def __init__(self, alpha: float = 1.0) -> None:
        self.alpha = alpha
        self.label_counts: Counter[str] = Counter()
        self.feature_counts: dict[str, Counter[str]] = {label: Counter() for label in LABELS}
        self.total_features: Counter[str] = Counter()
        self.vocabulary: set[str] = set()

    def fit(self, rows: list[dict[str, str]]) -> None:
        for row in rows:
            label = row["risk_label"].strip().lower()
            self.label_counts[label] += 1
            features = char_ngrams(row["prompt_text"])
            self.feature_counts[label].update(features)
            self.total_features[label] += len(features)
            self.vocabulary.update(features)

    def predict(self, text: str) -> str:
        scores = self.predict_log_proba(text)
        return max(scores, key=scores.get)

    def predict_log_proba(self, text: str) -> dict[str, float]:
        features = char_ngrams(text)
        total_rows = sum(self.label_counts.values())
        vocab_size = max(len(self.vocabulary), 1)
        scores: dict[str, float] = {}

        for label in LABELS:
            prior = (self.label_counts[label] + self.alpha) / (total_rows + self.alpha * len(LABELS))
            score = math.log(prior)
            denominator = self.total_features[label] + self.alpha * vocab_size

            for feature in features:
                numerator = self.feature_counts[label][feature] + self.alpha
                score += math.log(numerator / denominator)

            scores[label] = score

        return scores


def term_frequencies(features: list[str]) -> dict[str, float]:
    counts = Counter(features)
    total = max(len(features), 1)
    return {feature: count / total for feature, count in counts.items()}


def sigmoid(value: float) -> float:
    if value >= 35:
        return 1.0
    if value <= -35:
        return 0.0
    return 1 / (1 + math.exp(-value))


class TfidfLogisticRegressionPromptClassifier:
    """A compact binary logistic regression baseline using char n-gram TF-IDF features."""

    def __init__(
        self,
        epochs: int = 80,
        learning_rate: float = 0.7,
        l2: float = 0.0005,
        threshold: float = 0.9,
    ) -> None:
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.l2 = l2
        self.threshold = threshold
        self.idf: dict[str, float] = {}
        self.weights: dict[str, float] = defaultdict(float)
        self.bias = 0.0

    def fit(self, rows: list[dict[str, str]]) -> None:
        self.idf = self._build_idf(rows)
        self.weights = defaultdict(float)
        self.bias = 0.0

        examples = [
            (1 if row["risk_label"].strip().lower() == "harmful" else 0, self._transform(row["prompt_text"]))
            for row in sorted(rows, key=lambda item: item["id"])
        ]

        for _ in range(self.epochs):
            for label, features in examples:
                prediction = sigmoid(self.bias + self._dot(features))
                error = prediction - label
                self.bias -= self.learning_rate * error

                for feature, value in features.items():
                    weight = self.weights[feature]
                    gradient = error * value + self.l2 * weight
                    self.weights[feature] = weight - self.learning_rate * gradient

    def predict(self, text: str) -> str:
        return "harmful" if self.predict_probability(text) >= self.threshold else "benign"

    def predict_probability(self, text: str) -> float:
        return sigmoid(self.bias + self._dot(self._transform(text)))

    def _build_idf(self, rows: list[dict[str, str]]) -> dict[str, float]:
        doc_frequency: Counter[str] = Counter()
        for row in rows:
            doc_frequency.update(set(char_ngrams(row["prompt_text"])))

        document_count = max(len(rows), 1)
        return {
            feature: math.log((1 + document_count) / (1 + frequency)) + 1
            for feature, frequency in doc_frequency.items()
        }

    def _transform(self, text: str) -> dict[str, float]:
        tf = term_frequencies(char_ngrams(text))
        return {feature: value * self.idf.get(feature, 0.0) for feature, value in tf.items()}

    def _dot(self, features: dict[str, float]) -> float:
        return sum(self.weights.get(feature, 0.0) * value for feature, value in features.items())


def stratified_folds(rows: list[dict[str, str]], k: int = 5) -> list[list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["risk_label"].strip().lower()].append(row)

    folds: list[list[dict[str, str]]] = [[] for _ in range(k)]
    for label_rows in grouped.values():
        for index, row in enumerate(sorted(label_rows, key=lambda item: item["id"])):
            folds[index % k].append(row)

    return folds


def safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def score_predictions(examples: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(examples)
    correct = sum(1 for item in examples if item["correct"])
    true_harmful = sum(1 for item in examples if item["expected"] == "harmful")
    true_benign = sum(1 for item in examples if item["expected"] == "benign")
    predicted_harmful = sum(1 for item in examples if item["predicted"] == "harmful")
    harmful_correct = sum(
        1 for item in examples if item["expected"] == "harmful" and item["predicted"] == "harmful"
    )
    false_allow = sum(1 for item in examples if item["expected"] == "harmful" and item["predicted"] == "benign")
    false_refusal = sum(1 for item in examples if item["expected"] == "benign" and item["predicted"] == "harmful")

    precision = safe_divide(harmful_correct, predicted_harmful)
    recall = safe_divide(harmful_correct, true_harmful)
    f1 = safe_divide(2 * precision * recall, precision + recall)

    return {
        "total": total,
        "accuracy": round(safe_divide(correct, total), 4),
        "precision_harmful": round(precision, 4),
        "recall_harmful": round(recall, 4),
        "f1_harmful": round(f1, 4),
        "false_allow_rate": round(safe_divide(false_allow, true_harmful), 4),
        "false_refusal_rate": round(safe_divide(false_refusal, true_benign), 4),
    }


def evaluate_cross_validation_with_classifier(
    rows: list[dict[str, str]],
    classifier_factory: Callable[[], Any],
    algorithm: str,
    k: int = 5,
) -> dict[str, Any]:
    folds = stratified_folds(rows, k=k)
    examples: list[dict[str, Any]] = []

    for fold_index, test_rows in enumerate(folds):
        train_rows = [row for index, fold in enumerate(folds) if index != fold_index for row in fold]
        classifier = classifier_factory()
        classifier.fit(train_rows)

        for row in test_rows:
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
                    "fold": fold_index + 1,
                }
            )

    return {
        "algorithm": algorithm,
        "validation": f"{k}-fold stratified cross-validation",
        "summary": score_predictions(examples),
        "examples": sorted(examples, key=lambda item: item["id"]),
    }


def evaluate_cross_validation(rows: list[dict[str, str]], k: int = 5) -> dict[str, Any]:
    return evaluate_cross_validation_with_classifier(
        rows=rows,
        classifier_factory=NaiveBayesPromptClassifier,
        algorithm="char_ngram_naive_bayes",
        k=k,
    )


def evaluate_logistic_regression_cross_validation(rows: list[dict[str, str]], k: int = 5) -> dict[str, Any]:
    return evaluate_cross_validation_with_classifier(
        rows=rows,
        classifier_factory=TfidfLogisticRegressionPromptClassifier,
        algorithm="tfidf_logistic_regression",
        k=k,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to prompt CSV dataset")
    parser.add_argument("--output", required=True, help="Path to output JSON report")
    parser.add_argument("--folds", type=int, default=5, help="Number of stratified folds")
    parser.add_argument(
        "--algorithm",
        choices=["naive_bayes", "logistic_regression"],
        default="naive_bayes",
        help="ML baseline to evaluate",
    )
    args = parser.parse_args()

    rows = load_rows(Path(args.input))
    if args.algorithm == "logistic_regression":
        result = evaluate_logistic_regression_cross_validation(rows, k=args.folds)
    else:
        result = evaluate_cross_validation(rows, k=args.folds)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
