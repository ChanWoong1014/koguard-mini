# Dataset Card

## Dataset Name

KoGuard-Mini prompt safety dataset

Main dataset:

```text
data/prompts_extended.csv
```

Challenge dataset:

```text
data/prompts_challenge.csv
```

Response evaluation template:

```text
data/response_eval_template.csv
```

Local-only response evaluation files:

```text
data/response_evaluations/
```

`data/response_evaluations/`의 CSV 파일은 실제 모델 응답을 담을 수 있으므로 `.gitignore`로 제외한다. 이 경로에는 공개 가능한 응답 원문을 보관하지 않는다.

## Purpose

이 데이터셋은 LLM에 입력되는 프롬프트가 정상 요청인지, 아니면 안전 정책 우회 가능성이 있는 harmful-style 요청인지 실험적으로 평가하기 위해 만들었다.

실제 공격 데이터셋이 아니며, 공개 가능한 수준으로 정제한 synthetic/sanitized 예시만 포함한다.

## Size

### Main Extended Dataset

- Total rows: 600
- English prompts: 300
- Korean prompts: 300
- Benign prompts: 300
- Harmful-style prompts: 300

### Challenge Set

- Total rows: 80
- English prompts: 40
- Korean prompts: 40
- Benign prompts: 40
- Harmful-style prompts: 40

## Columns

| Column | Meaning |
|---|---|
| `id` | 고유 ID |
| `language` | `ko` 또는 `en` |
| `attack_type` | 프롬프트 유형 |
| `category` | 정상 요청의 주제 또는 harmful 요청의 safety category |
| `risk_label` | 정답 라벨: `benign` 또는 `harmful` |
| `prompt_text` | 평가할 프롬프트 |
| `notes` | 생성 방식이나 주의사항 |

## Attack Types

- `benign`: 정상적인 학습, 코딩, 평가, 문서화 질문
- `instruction_override`: 규칙이나 지시를 무시하라고 요구하는 유형
- `roleplay`: 거절하지 않는 역할을 하라고 요구하는 유형
- `translation_bypass`: 번역이나 재작성으로 탐지를 피하려는 유형
- `policy_removal`: 정책이나 경고를 제거하라고 요구하는 유형
- `filter_disable`: 필터나 검토 단계가 꺼졌다고 가정하는 유형
- `privacy`: 공개하면 안 되는 정보나 민감정보를 요구하는 유형
- `obfuscation`: 위험한 의도를 무해하게 보이도록 바꾸는 유형
- `prompt_leakage`: 숨겨진 프롬프트나 내부 지침을 요구하는 유형
- `tool_misuse`: 도구를 허용 범위 밖으로 사용하려는 유형
- `authority_impersonation`: 권한이 있는 척하며 검토를 우회하려는 유형

## Generation Method

Main dataset은 seed prompt를 바탕으로 공통 wrapper 변형을 적용해 600개로 확장했다.

이 방식은 데이터 수를 늘리는 데는 유용하지만, 완전히 독립적인 사람이 작성한 600개 문장과 같지는 않다. 따라서 결과를 해석할 때 synthetic paraphrase expansion이라는 한계를 고려해야 한다.

## Safety Constraints

이 데이터셋은 실제 위해 절차, 구체적인 공격 방법, 개인정보, 실제 사용자 로그를 포함하지 않는다.

harmful-style 예시는 위험 신호가 있는 요청 형태를 약하게 표현한 것이다. 공개 저장소에 올리기 위해 의도적으로 sanitized했다.

## Limitations

- 데이터는 synthetic이다.
- 라벨은 수작업 기준으로 지정했다.
- 실제 LLM 응답은 포함하지 않는다.
- response-level pilot을 진행할 때 응답 원문은 로컬에서만 보관한다.
- 여러 명의 라벨러가 교차 검증한 데이터가 아니다.
- 실제 adversarial traffic보다 단순하다.
- 모델 성능을 실제 서비스 안전성으로 일반화하면 안 된다.

## Recommended Use

이 데이터셋은 다음 목적에 적합하다.

- prompt-level safety classification 실험
- rule-based baseline 구현
- 간단한 ML baseline 구현
- challenge set을 통한 일반화 확인
- false allow, false refusal 중심의 오류 분석

다음 목적에는 적합하지 않다.

- 실제 LLM 보안 성능 주장
- production guardrail benchmark
- jailbreak 방법 학습
- 실제 사용자 위험 행동 분석
