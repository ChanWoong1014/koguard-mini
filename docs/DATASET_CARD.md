# 데이터셋 카드

## 데이터셋 이름

Main dataset:

```text
data/prompts_extended.csv
```

Challenge dataset:

```text
data/prompts_challenge.csv
```

## 목적

이 데이터셋은 LLM에 입력되는 프롬프트가 정상 요청인지, 아니면 안전 정책 우회 가능성이 있는 harmful-style 요청인지 실험적으로 평가하기 위해 만들었습니다.

이 데이터셋은 실제 공격 데이터셋이 아닙니다. 공개 가능한 수준의 synthetic/sanitized 예시만 포함합니다.

## 크기

### Main Extended Dataset

- 총 200개
- 영어 100개
- 한국어 100개
- benign 100개
- harmful-style 100개

### Challenge Set

- 총 80개
- 영어 40개
- 한국어 40개
- benign 40개
- harmful-style 40개

## 컬럼

| Column | Meaning |
|---|---|
| `id` | 고유 ID |
| `language` | `ko` 또는 `en` |
| `attack_type` | 프롬프트 유형 |
| `category` | 큰 범주 |
| `risk_label` | 정답 라벨: `benign` 또는 `harmful` |
| `prompt_text` | 평가할 프롬프트 |
| `notes` | 생성 메모 |

## Attack Type

- `benign`: 정상적인 학습, 코딩, 평가, 문서화 질문
- `instruction_override`: 규칙이나 지침을 무시하라고 요구하는 유형
- `roleplay`: 거절하지 않는 역할을 하라고 요구하는 유형
- `translation_bypass`: 번역이나 재작성으로 탐지를 피하려는 유형
- `policy_removal`: 정책이나 경고를 제거하라고 요구하는 유형
- `filter_disable`: 필터나 검토 단계가 꺼졌다고 가정하는 유형
- `privacy`: 공개되면 안 되는 정보나 민감정보를 요구하는 유형
- `obfuscation`: 위험한 의도를 무해하게 보이도록 바꾸려는 유형
- `prompt_leakage`: 숨겨진 프롬프트나 내부 지침을 요구하는 유형
- `tool_misuse`: 도구를 허용 범위 밖으로 사용하려는 유형
- `authority_impersonation`: 권한이 있는 척하며 검사를 우회하려는 유형

## 안전 제약

이 데이터셋은 실제 유해한 절차나 구체적인 공격 방법을 포함하지 않습니다.

harmful-style 예시는 위험 신호가 있는 요청 형태를 약하게 표현한 것입니다. 따라서 공개 저장소에 올리기에는 비교적 안전하지만, 실제 adversarial traffic보다 단순합니다.

## 한계

- 데이터는 synthetic입니다.
- 라벨은 수작업으로 지정했습니다.
- 실제 LLM 응답을 평가하지 않습니다.
- 여러 명의 라벨러가 교차 검증한 데이터가 아닙니다.
- 실제 서비스 성능을 주장하기 위한 benchmark가 아닙니다.

## 권장 사용

이 데이터셋은 다음을 보여주기 위한 학습/실험용 데이터입니다.

- 한국어/영어 프롬프트 평가
- rule-based baseline 구현
- 간단한 ML baseline 구현
- challenge set을 통한 일반화 테스트
- false allow, false refusal 중심의 오류 분석
