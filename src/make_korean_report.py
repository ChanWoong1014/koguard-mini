"""Create a Korean Markdown experiment report draft."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from make_markdown_report import load_errors, load_json
from make_markdown_report import algorithm_table


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


def error_table(errors: list[dict[str, str]]) -> str:
    if not errors:
        return "현재 평가에서는 오분류가 없습니다."

    lines = ["| ID | 언어 | 공격 유형 | 정답 | 예측 | 매칭 규칙 |", "|---|---|---|---|---|---|"]
    for item in errors:
        lines.append(
            "| {id} | {language} | {attack_type} | {expected} | {predicted} | {matched_patterns} |".format(
                **item
            )
        )
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
            "KoGuard-Mini는 한국어와 영어 프롬프트를 대상으로 LLM 안전성 위험 패턴을 평가해보는 미니 실험 프로젝트입니다. "
            "새로운 LLM을 학습시키는 프로젝트가 아니라, 프롬프트가 정상적인 요청인지 또는 우회/정책 제거/프롬프트 누출 같은 위험 패턴인지 "
            "분석하는 평가 파이프라인을 만드는 것이 목표입니다.",
            "## 2. 연구 질문\n\n"
            "> 단순한 규칙 기반 guardrail baseline이 한국어와 영어의 sanitized bypass-style prompt를 어느 정도 탐지할 수 있는가?",
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
            "## 4. 평가 결과\n\n" + metric_table(summary),
            "## 5. 알고리즘 비교\n\n"
            + algorithm_table(algorithms)
            + "\n\n![Harmful F1 by Algorithm](chart_algorithm_f1.svg)",
            "## 6. Challenge Set 일반화 평가\n\n"
            + algorithm_table(challenge_algorithms)
            + "\n\n![Challenge Harmful F1 by Algorithm](chart_challenge_algorithm_f1.svg)\n\n"
            "challenge set은 main extended dataset과 별도로 작성된 데이터입니다. 알고리즘이 기존 데이터 표현을 외운 것인지, 새로운 표현에도 어느 정도 대응하는지 확인하기 위해 사용합니다.",
            "## 7. 시각화\n\n"
            "![Accuracy by Language](chart_accuracy_by_language.svg)\n\n"
            "![False Allow by Attack Type](chart_false_allow_by_attack_type.svg)\n\n"
            "![Dataset by Attack Type](chart_dataset_by_attack_type.svg)",
            "## 8. 오류 분석\n\n" + error_table(errors),
            "## 9. 해석\n\n"
            "규칙 기반 baseline은 설명하기 쉽지만 표현 변화에 약합니다. 명시적인 키워드가 있는 프롬프트는 잘 잡지만, 우회 의도가 간접적으로 표현되면 놓칠 수 있습니다. "
            "문자 n-gram Naive Bayes baseline은 이 sanitized dataset에서 harmful recall을 크게 높였지만, 이것이 실제 LLM 서비스 안전성을 보장한다는 뜻은 아닙니다. "
            "이 결과는 알고리즘 비교와 한계 분석을 보여주는 학습용 실험 결과로 해석하는 것이 적절합니다.",
            "## 10. 한계\n\n"
            "- 데이터셋은 학습과 실험에는 유용하지만 연구 결론을 강하게 주장하기에는 아직 작습니다.\n"
            "- 라벨은 수작업으로 지정했습니다.\n"
            "- 규칙 기반 방식이라 표현이 조금만 바뀌어도 놓칠 수 있습니다.\n"
            "- Naive Bayes baseline은 단순한 알고리즘이라 synthetic wording에 과적합될 수 있습니다.\n"
            "- 현재는 프롬프트 자체만 평가하고, 실제 LLM 응답은 평가하지 않습니다.\n"
            "- 공개 가능한 안전한 예시 중심이라 실제 공격 데이터보다 단순합니다.",
            "## 11. 향후 개선 방향\n\n"
            "- 데이터셋을 200개 이상으로 확장합니다.\n"
            "- 실제 LLM 응답을 수집하고 safe refusal, partial compliance, unsafe compliance로 라벨링합니다.\n"
            "- logistic regression, TF-IDF classifier 등 추가 ML baseline과 비교합니다.\n"
            "- 한국어 표현 변형과 우회 표현을 더 추가합니다.",
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
