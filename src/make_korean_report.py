"""Create a Korean Markdown experiment report draft."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from make_markdown_report import algorithm_table, load_errors, load_json


def table_from_counts(counts: dict[str, int]) -> str:
    lines = ["| 항목 | 개수 |", "|---|---:|"]
    lines.extend(f"| {key} | {value} |" for key, value in counts.items())
    return "\n".join(lines)


def metric_table(summary: dict[str, Any]) -> str:
    rows = [
        ("전체 프롬프트 수", summary["total"]),
        ("정확도", summary["accuracy"]),
        ("harmful precision", summary["precision_harmful"]),
        ("harmful recall", summary["recall_harmful"]),
        ("harmful F1", summary["f1_harmful"]),
        ("False allow rate", summary["false_allow_rate"]),
        ("False refusal rate", summary["false_refusal_rate"]),
    ]
    lines = ["| 지표 | 값 |", "|---|---:|"]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    return "\n".join(lines)


def error_table(errors: list[dict[str, str]], limit: int = 30) -> str:
    if not errors:
        return "현재 평가에서는 오분류가 발견되지 않았습니다."

    lines = ["| ID | 언어 | 공격 유형 | 정답 | 예측 | 매칭 규칙 |", "|---|---|---|---|---|---|"]
    for item in errors[:limit]:
        lines.append(
            "| {id} | {language} | {attack_type} | {expected} | {predicted} | {matched_patterns} |".format(
                **item
            )
        )
    if len(errors) > limit:
        lines.append(f"| ... | ... | ... | ... | ... | 전체 {len(errors)}개 중 {limit}개만 표시 |")
    return "\n".join(lines)


def build_korean_report(
    dataset_summary: dict[str, Any],
    results: dict[str, Any],
    errors: list[dict[str, str]],
    algorithms: list[dict[str, Any]] | None = None,
    challenge_algorithms: list[dict[str, Any]] | None = None,
) -> str:
    summary = results["summary"]
    return "\n\n".join(
        [
            "# KoGuard-Mini 한국어 실험 보고서 초안",
            "## 1. 프로젝트 개요\n\n"
            "KoGuard-Mini는 한국어와 영어 프롬프트를 대상으로 LLM 안전성 위험 신호를 평가해보는 미니 실험 프로젝트입니다. "
            "새로운 LLM을 학습시키는 프로젝트가 아니라, 사용자의 입력 프롬프트가 정상 요청인지 또는 안전 정책 우회 가능성이 있는 요청인지 "
            "분류하는 평가 파이프라인을 만드는 것이 목표입니다.",
            "## 2. 연구 질문\n\n"
            "> rule-based guardrail, character n-gram Naive Bayes, TF-IDF Logistic Regression은 한국어/영어 harmful-style prompt를 어느 정도 구분할 수 있는가?\n\n"
            "특히 accuracy만 보지 않고 harmful recall, false allow rate, false refusal rate를 함께 확인합니다.",
            "## 3. 데이터셋 구성\n\n"
            f"- 전체 데이터 수: {dataset_summary['total']}\n"
            f"- 평균 프롬프트 길이: {dataset_summary['average_prompt_length']}\n"
            f"- 최소 길이: {dataset_summary['min_prompt_length']}\n"
            f"- 최대 길이: {dataset_summary['max_prompt_length']}\n\n"
            "### 언어별 분포\n\n"
            + table_from_counts(dataset_summary["by_language"])
            + "\n\n### 라벨별 분포\n\n"
            + table_from_counts(dataset_summary["by_risk_label"])
            + "\n\n### 공격 유형별 분포\n\n"
            + table_from_counts(dataset_summary["by_attack_type"]),
            "## 4. Rule-Based Guardrail 평가 결과\n\n" + metric_table(summary),
            "## 5. 알고리즘 비교\n\n"
            + algorithm_table(algorithms)
            + "\n\n![Harmful F1 by Algorithm](chart_algorithm_f1.svg)",
            "## 6. Challenge Set 일반화 평가\n\n"
            + algorithm_table(challenge_algorithms)
            + "\n\n![Challenge Harmful F1 by Algorithm](chart_challenge_algorithm_f1.svg)\n\n"
            "challenge set은 main dataset과 별도로 작성한 데이터입니다. 모델이 기존 표현을 외운 것인지, 새로운 표현에도 어느 정도 대응하는지 확인하기 위해 사용합니다.",
            "## 7. Confusion Matrix\n\n"
            "![TF-IDF Logistic Regression Confusion Matrix](chart_confusion_matrix_logistic.svg)\n\n"
            "confusion matrix를 보면 harmful을 benign으로 통과시킨 경우와 benign을 harmful로 잘못 막은 경우를 직접 확인할 수 있습니다.",
            "## 8. 오류 분석\n\n" + error_table(errors),
            "## 9. 해석\n\n"
            "Rule-based baseline은 설명하기 쉽지만 표현 변화에 약합니다. main dataset에서도 harmful recall이 0.58이고, challenge set에서는 0.075까지 떨어졌습니다. "
            "즉 새로운 표현이 들어오면 위험 요청을 놓칠 가능성이 큽니다.\n\n"
            "Character n-gram Naive Bayes와 TF-IDF Logistic Regression은 현재 synthetic/sanitized dataset에서 훨씬 좋은 결과를 보였습니다. "
            "하지만 이것이 실제 LLM 서비스 안전성을 보장한다는 뜻은 아닙니다. 모델이 실제 의도를 깊게 이해했다기보다는, 데이터셋에 반복적으로 나타난 표현 패턴을 학습했을 가능성이 있습니다.",
            "## 10. 한계\n\n"
            "- 데이터셋은 직접 만든 synthetic/sanitized 데이터입니다.\n"
            "- 실제 사용자 로그나 공개 jailbreak benchmark가 아닙니다.\n"
            "- 실제 LLM 응답 안전성은 아직 평가하지 않았습니다.\n"
            "- 라벨은 수작업 기준으로 지정했습니다.\n"
            "- Naive Bayes와 Logistic Regression은 데이터 작성 스타일에 과적합될 수 있습니다.\n"
            "- 현재 결과는 연구 결론이라기보다 학습과 실험 결과로 해석해야 합니다.",
            "## 11. 다음 개선 방향\n\n"
            "- 실제 LLM 응답을 수집하고 response-level label을 부여합니다.\n"
            "- `safe_refusal`, `partial_compliance`, `unsafe_compliance` 기준을 사용합니다.\n"
            "- 공개 benchmark를 안전하게 redaction한 뒤 비교합니다.\n"
            "- 여러 명의 라벨러가 같은 기준으로 판단하는지 확인합니다.",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-summary", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--errors", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    report = build_korean_report(
        dataset_summary=load_json(Path(args.dataset_summary)),
        results=load_json(Path(args.results)),
        errors=load_errors(Path(args.errors)),
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Saved Korean report draft to {output_path}")


if __name__ == "__main__":
    main()
