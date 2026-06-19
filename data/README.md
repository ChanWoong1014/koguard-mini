# Data

이 폴더에는 KoGuard-Mini에서 사용하는 CSV 데이터가 들어 있습니다.

## Files

- `prompts_template.csv`: 가장 작은 예시 템플릿
- `prompts_seed.csv`: 100개 seed dataset
- `prompts_extended.csv`: 600개 main dataset
- `prompts_challenge.csv`: 80개 challenge dataset
- `response_eval_template.csv`: 실제 LLM 응답 평가를 위한 라벨링 템플릿

## 공개 기준

이 저장소의 데이터는 공개 가능한 수준의 synthetic/sanitized 예시만 포함합니다.

포함하지 않는 것:

- 실제 사용자 로그
- 개인정보
- 실제 위해 절차
- 구체적인 공격 방법
- 실제 LLM 응답 데이터

## 데이터 재생성

`prompts_extended.csv`와 `prompts_challenge.csv`는 직접 수정하기보다 스크립트에서 원문을 수정한 뒤 다시 생성하는 방식을 권장합니다.

```powershell
python src\build_extended_dataset.py --output data\prompts_extended.csv
python src\build_challenge_dataset.py --output data\prompts_challenge.csv
```

## Response-Level Evaluation

`response_eval_template.csv`는 실제 평가 데이터가 아니라 템플릿입니다.

실제 LLM 응답을 수집하려면 먼저 다음 문서를 읽어야 합니다.

```text
docs/RESPONSE_LEVEL_EVALUATION_PLAN.md
```

실제 응답 데이터는 unsafe content를 포함할 수 있으므로 공개 전에 redaction과 안전 검토가 필요합니다.
