# KoGuard-Mini 초보자 가이드

이 문서는 프로젝트를 처음 보는 사람이 전체 흐름을 이해하기 위한 가이드입니다.

## 1. 이 프로젝트는 무엇인가

KoGuard-Mini는 LLM에 들어가기 전의 사용자 프롬프트를 보고, 그 요청이 정상적인지 또는 안전 정책 우회 가능성이 있는지 분류해보는 실험 프로젝트입니다.

PromptLouter가 “어떤 LLM으로 보낼 것인가”를 고민했다면, KoGuard-Mini는 그보다 앞단에서 “이 요청을 그대로 LLM에 보내도 되는가?”라는 질문을 다룹니다.

## 2. 전체 흐름

```text
CSV 데이터 생성
→ 데이터 검증
→ rule-based guardrail 평가
→ Naive Bayes 평가
→ TF-IDF Logistic Regression 평가
→ challenge set 평가
→ confusion matrix 생성
→ 차트와 보고서 생성
→ 단위 테스트
```

## 3. 주요 폴더

### `data/`

프롬프트 데이터가 들어 있습니다.

- `prompts_extended.csv`: 600개 main dataset
- `prompts_challenge.csv`: 80개 challenge dataset
- `response_eval_template.csv`: 실제 LLM 응답 평가용 템플릿

### `src/`

실제 코드가 들어 있습니다.

- `build_extended_dataset.py`: main dataset 생성
- `build_challenge_dataset.py`: challenge dataset 생성
- `validate_dataset.py`: 데이터 형식 검증
- `rule_guardrail.py`: 규칙 기반 분류기
- `ml_baseline.py`: Naive Bayes와 Logistic Regression
- `evaluate_guardrail.py`: rule-based 평가
- `evaluate_challenge.py`: challenge set 평가
- `confusion_matrix.py`: confusion matrix CSV/SVG 생성
- `run_pipeline.py`: 전체 파이프라인 실행

### `reports/`

실행 결과가 저장됩니다.

- `algorithm_comparison.csv`: main dataset 성능 비교
- `challenge_algorithm_comparison.csv`: challenge set 성능 비교
- `confusion_matrix_*.csv`: 알고리즘별 confusion matrix
- `chart_*.svg`: 결과 차트
- `experiment_report.md`: 실험 보고서 초안

### `tests/`

코드가 의도대로 동작하는지 확인하는 단위 테스트가 들어 있습니다.

## 4. 실행 방법

VS Code에서 `C:\koguard-mini` 폴더를 열고 PowerShell 터미널에서 실행합니다.

```powershell
.\run_windows.ps1
```

직접 단계별로 실행하려면:

```powershell
python src\build_extended_dataset.py --output data\prompts_extended.csv
python src\build_challenge_dataset.py --output data\prompts_challenge.csv
python src\run_pipeline.py --input data\prompts_extended.csv --challenge-input data\prompts_challenge.csv --reports-dir reports
python -m unittest discover tests
```

정상 실행되면 다음과 비슷한 메시지가 나옵니다.

```text
KoGuard-Mini pipeline complete.
Ran 18 tests
OK
```

## 5. 결과를 어떻게 해석하나

중요한 지표는 accuracy만이 아닙니다.

- `Harmful Recall`: 실제 harmful-style 요청 중 얼마나 잡았는가
- `False Allow Rate`: harmful-style 요청을 benign으로 통과시킨 비율
- `False Refusal Rate`: 정상 요청을 harmful로 잘못 막은 비율

안전성 평가에서는 `False Allow Rate`가 특히 중요합니다. 위험한 요청을 정상으로 통과시키는 문제이기 때문입니다.

하지만 `False Refusal Rate`도 무시하면 안 됩니다. 정상 사용자를 너무 많이 막으면 실제 서비스에서는 사용성이 나빠집니다.

## 6. 현재 결과 요약

Main dataset에서는 Naive Bayes와 TF-IDF Logistic Regression이 rule-based보다 훨씬 좋은 결과를 보였습니다.

하지만 이 결과는 synthetic/sanitized dataset 기준입니다. 즉, 실제 LLM 서비스에서 그대로 동작한다고 주장하면 안 됩니다.

정확한 해석은 다음과 같습니다.

> 단순 규칙 기반 방식은 표현 변화에 취약했고, character n-gram 기반 ML baseline은 현재 데이터셋에서 더 높은 recall을 보였다. 하지만 실제 LLM 안전성을 주장하려면 실제 응답 평가와 외부 benchmark 비교가 추가로 필요하다.

## 7. 다음 단계

실제 LLM 응답을 평가하려면 먼저 `docs/RESPONSE_LEVEL_EVALUATION_PLAN.md`를 읽어야 합니다.

그 문서에는 다음 라벨 기준이 들어 있습니다.

- `safe_refusal`
- `safe_completion`
- `partial_compliance`
- `unsafe_compliance`
- `unclear`

응답 데이터는 민감할 수 있으므로, 바로 공개 저장소에 넣기보다 로컬에서 pilot labeling을 먼저 하는 것이 안전합니다.
