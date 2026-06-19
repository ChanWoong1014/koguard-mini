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
- `response_evaluations/`: 실제 모델 응답을 로컬에서만 보관하는 폴더. GitHub에 올라가지 않음

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
- `prepare_response_pilot.py`: challenge set에서 20개 파일럿을 균형 있게 뽑음
- `evaluate_response_level.py`: 응답 라벨 CSV의 형식을 검사하고 안전성 지표를 계산
- `collect_openai_responses.py`: OpenAI API로 한 모델의 실제 응답을 로컬 CSV에 수집

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

### 20개 파일럿을 만드는 순서

1. PowerShell에서 아래 명령을 실행합니다.

```powershell
python src\prepare_response_pilot.py --input data\prompts_challenge.csv --output data\response_evaluations\pilot_20.csv
```

2. `data/response_evaluations/pilot_20.csv`를 VS Code로 엽니다. 이 파일은 4개 그룹(한국어/영어 x benign/harmful)에서 각각 5개씩 뽑은 20개 행입니다.
3. 한 모델에서 각 프롬프트를 같은 조건으로 실행합니다. `model_name`, `response_text`, `response_label`, `rationale`을 채웁니다.
4. 아래 명령으로 빈 칸이나 잘못된 라벨이 없는지 검사하고, 지표 JSON을 만듭니다.

```powershell
python src\evaluate_response_level.py --input data\response_evaluations\pilot_20.csv --output reports\response_pilot_metrics.json
```

여기서 중요한 점은 `response_evaluations` 폴더의 원문 CSV는 GitHub에 올라가지 않는다는 것입니다. `reports/response_pilot_metrics.json`에는 응답 원문이 없고 숫자와 라벨 집계만 들어갑니다.

### OpenAI API 자동 수집은 언제 하는가

자동 수집은 비용이 발생하므로, 파일럿 CSV와 라벨 기준을 먼저 이해한 뒤에 합니다. 실제 키는 프로젝트의 `.env` 파일에만 둡니다. `.env`는 GitHub에 올라가지 않습니다.

```text
OPENAI_API_KEY=your_real_key_here
```

먼저 API 호출 없이 개수만 확인합니다.

```powershell
python src\collect_openai_responses.py --input data\response_evaluations\pilot_20.csv --output data\response_evaluations\openai_pilot_20.csv --model YOUR_MODEL_ID --max-requests 20 --dry-run
```

`Requests planned: 20`을 확인한 다음에만 아래 명령을 실행합니다.

```powershell
python src\collect_openai_responses.py --input data\response_evaluations\pilot_20.csv --output data\response_evaluations\openai_pilot_20.csv --model YOUR_MODEL_ID --max-requests 20 --confirm-model-calls
```

이 스크립트는 `--max-requests`와 `--confirm-model-calls`가 모두 없으면 실제 API를 호출하지 않도록 만들었습니다. 수집 후에는 `openai_pilot_20.csv`에서 `response_label`과 `rationale`을 직접 채워야 합니다.
