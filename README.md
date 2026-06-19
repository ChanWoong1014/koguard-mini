# KoGuard-Mini

KoGuard-Mini는 한국어/영어 LLM 프롬프트가 정상 요청인지, 아니면 안전 정책 우회 가능성이 있는 요청인지 실험적으로 평가해보는 작은 프로젝트입니다.

이 프로젝트는 이전에 진행한 PromptLouter 프로젝트에서 출발했습니다. PromptLouter에서는 입력을 어떤 LLM으로 보낼지, 비용과 성능을 어떻게 조절할지에 관심이 있었다면, KoGuard-Mini에서는 한 단계 앞의 질문을 다룹니다.

> LLM에 입력되기 전, 사용자의 프롬프트 자체가 안전한 요청인지 위험 신호가 있는 요청인지 간단히 평가할 수 있을까?

중요한 점은 이 프로젝트가 실제 서비스용 보안 시스템이 아니라는 것입니다. 목표는 LLM 안전성 문제를 직접 이해하기 위해 데이터셋을 만들고, 기준 알고리즘을 구현하고, 결과를 해석해보는 것입니다.

## 현재 구성

- 확장 데이터셋: `data/prompts_extended.csv`
- challenge 데이터셋: `data/prompts_challenge.csv`
- 규칙 기반 baseline: `src/rule_guardrail.py`
- ML baseline: `src/ml_baseline.py`
- 전체 실행 파이프라인: `src/run_pipeline.py`
- 결과 보고서: `reports/experiment_report_ko.md`

## 데이터셋

### `prompts_extended.csv`

- 총 200개
- 영어 100개
- 한국어 100개
- benign 100개
- harmful-style 100개

### `prompts_challenge.csv`

- 총 80개
- 영어 40개
- 한국어 40개
- benign 40개
- harmful-style 40개

`harmful-style`은 실제 유해한 방법을 자세히 담은 문장이 아닙니다. 공개 가능한 수준의 sanitized 예시로, 안전 정책 우회, 프롬프트 누출, 민감정보 요구, 도구 오용처럼 위험 신호가 있는 요청 형태를 약하게 표현한 것입니다.

## 비교한 방법

### 1. Rule-based Guardrail

정규표현식 기반 규칙으로 위험 표현을 탐지합니다.

장점:

- 이해하기 쉽습니다.
- 왜 탐지했는지 설명하기 쉽습니다.
- 학습 데이터가 없어도 동작합니다.

단점:

- 사람이 미리 쓴 표현만 잘 잡습니다.
- 표현이 조금만 바뀌어도 놓칠 수 있습니다.
- 정상적인 안전성 설명 요청을 과하게 막을 수 있습니다.

### 2. Character N-Gram Naive Bayes

문장을 짧은 문자 조각으로 나누고, 어떤 패턴이 benign 또는 harmful-style에 자주 나타나는지 통계적으로 학습합니다.

장점:

- 사람이 직접 규칙으로 쓰지 않은 표현도 어느 정도 학습할 수 있습니다.
- 영어와 한국어 모두에 적용할 수 있습니다.
- 외부 라이브러리 없이 실행됩니다.

단점:

- 문장의 의미를 깊게 이해하는 모델은 아닙니다.
- synthetic 데이터셋의 표현 패턴에 과적합될 수 있습니다.
- 실제 LLM 응답 안전성을 직접 평가하지는 않습니다.

## 현재 결과

### Main Extended Dataset

| Algorithm | Accuracy | Harmful Recall | False Allow Rate | False Refusal Rate |
|---|---:|---:|---:|---:|
| Rule-based guardrail | 0.79 | 0.58 | 0.42 | 0.0 |
| Character n-gram Naive Bayes | 0.99 | 1.0 | 0.0 | 0.02 |

### Challenge Set

| Algorithm | Accuracy | Harmful Recall | False Allow Rate | False Refusal Rate |
|---|---:|---:|---:|---:|
| Rule-based guardrail | 0.4875 | 0.075 | 0.925 | 0.1 |
| Character n-gram Naive Bayes | 0.9875 | 1.0 | 0.0 | 0.025 |

해석하면, rule-based 방식은 설명 가능하지만 표현 변화에 매우 약했습니다. 반면 Naive Bayes는 현재 synthetic 데이터셋과 challenge set에서 훨씬 높은 recall을 보였습니다. 다만 이 결과를 실제 서비스 성능으로 일반화하면 안 됩니다.

## 실행 방법

Windows PowerShell에서:

```powershell
cd C:\koguard-mini
.\run_windows.ps1
```

직접 실행하려면:

```powershell
python src\build_extended_dataset.py --output data\prompts_extended.csv
python src\build_challenge_dataset.py --output data\prompts_challenge.csv
python src\run_pipeline.py --input data\prompts_extended.csv --challenge-input data\prompts_challenge.csv --reports-dir reports
python -m unittest discover tests
```

정상 실행되면 다음과 비슷한 결과가 나옵니다.

```text
KoGuard-Mini pipeline complete.
Ran 15 tests
OK
```

## 주요 결과 파일

- `reports/algorithm_comparison.csv`: main dataset에서 알고리즘 비교
- `reports/challenge_algorithm_comparison.csv`: challenge set에서 알고리즘 비교
- `reports/errors.csv`: rule-based 오분류 사례
- `reports/ml_errors.csv`: ML baseline 오분류 사례
- `reports/challenge_report.md`: challenge set 결과 요약
- `reports/experiment_report_ko.md`: 전체 실험 보고서 초안
- `reports/*.svg`: 결과 시각화 차트

## 프로젝트의 한계

- 데이터셋은 직접 만든 synthetic/sanitized 데이터입니다.
- 실제 사용자 로그나 실제 jailbreak benchmark가 아닙니다.
- 실제 LLM 응답을 수집해서 평가하지 않았습니다.
- 라벨링을 여러 사람이 교차 검증하지 않았습니다.
- Naive Bayes 성능이 높아도 실제 환경에서 그대로 동작한다고 볼 수 없습니다.

## 다음 개선 방향

- 실제 LLM 응답을 수집하고 safe refusal, partial compliance, unsafe compliance로 라벨링하기
- 공개 benchmark 일부를 안전하게 redaction해서 비교하기
- TF-IDF, Logistic Regression 같은 추가 baseline 구현하기
- 한국어 우회 표현을 더 다양하게 확장하기
- 데이터 라벨링 기준 문서화하기
