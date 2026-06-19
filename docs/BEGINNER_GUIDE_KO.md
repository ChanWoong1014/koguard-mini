# KoGuard-Mini 초보자 가이드

이 문서는 프로젝트를 처음 보는 사람이 파일 역할과 실행 흐름을 이해하기 위한 가이드입니다.

## 1. 이 프로젝트의 목표

이 프로젝트는 새로운 LLM을 만드는 프로젝트가 아닙니다.

목표는 다음과 같습니다.

> 한국어/영어 프롬프트가 정상 요청인지, 아니면 LLM 안전 정책을 우회하려는 위험 패턴인지 평가하는 작은 파이프라인 만들기

즉, 핵심은 모델 학습이 아니라 데이터 구성, 평가 기준, baseline 구현, 오류 분석입니다.

## 2. 꼭 알아야 할 용어

### LLM

ChatGPT 같은 대형 언어 모델입니다.

### Prompt

사용자가 LLM에게 입력하는 질문이나 명령입니다.

### Guardrail

위험하거나 부적절한 입력/출력을 막기 위한 안전장치입니다.

### Benign

정상적이고 안전한 요청입니다.

### Harmful-style

실제 유해한 방법을 자세히 담지는 않지만, 안전 정책 우회나 프롬프트 누출처럼 위험한 의도를 가진 형태의 요청입니다.

### False Allow

위험한 요청인데 시스템이 통과시킨 경우입니다. 안전성 평가에서는 이 값이 중요합니다.

### False Refusal

정상 요청인데 시스템이 잘못 막은 경우입니다. 이 값이 높으면 사용성이 나빠집니다.

## 3. 중요한 파일

### `data/prompts_seed.csv`

프로젝트의 핵심 데이터셋입니다.

기본 seed 파일은 100개 행이고, 확장 파일은 200개 행입니다.

- `data/prompts_seed.csv`: 100개
- `data/prompts_extended.csv`: 200개
- `data/prompts_challenge.csv`: 80개 일반화 테스트용 데이터

### `src/rule_guardrail.py`

규칙 기반 baseline입니다.

예를 들어 "규칙 무시", "우회", "프롬프트 공개", "필터 비활성화" 같은 표현이 있으면 위험하다고 판단합니다.

### `src/validate_dataset.py`

CSV 데이터셋이 올바른 형식인지 검사합니다.

중복 ID, 빈 프롬프트, 잘못된 라벨 같은 문제를 잡습니다.

### `src/run_pipeline.py`

전체 실행을 한 번에 처리하는 파일입니다.

이 파일 하나를 실행하면 데이터 검증, 평가, 오류 분석, 차트 생성, 보고서 생성이 모두 진행됩니다.

### `reports/portfolio_report_ko.md`

한국어 보고서 초안입니다.

대학원 지원용으로 다듬을 때 가장 먼저 봐야 할 파일입니다.

## 4. 실행 방법

VS Code에서 `C:\koguard-mini` 폴더를 엽니다.

터미널을 열고 아래 명령을 실행합니다.

```powershell
python src\build_extended_dataset.py --output data\prompts_extended.csv
python src\build_challenge_dataset.py --output data\prompts_challenge.csv
python src\run_pipeline.py --input data\prompts_extended.csv --challenge-input data\prompts_challenge.csv --reports-dir reports
```

또는:

```powershell
.\run_windows.ps1
```

## 5. 실행 후 생기는 파일

### `reports/validation.json`

데이터셋 형식 검증 결과입니다.

### `reports/dataset_summary.json`

언어별, 라벨별, 공격 유형별 데이터 개수입니다.

### `reports/results.json`

전체 평가 결과입니다.

### `reports/errors.csv`

틀린 예측만 모은 파일입니다.

### `reports/portfolio_report_ko.md`

한국어 보고서 초안입니다.

### `reports/*.svg`

결과를 시각화한 차트입니다.

## 6. 지금 결과를 어떻게 해석해야 하나

현재 결과는 rule-based baseline과 ML baseline을 비교하고, 별도의 challenge set으로 일반화 성능도 확인합니다.

하지만 이 결과를 과장하면 안 됩니다.

데이터가 실제 공격 데이터가 아니라 안전하게 만든 sanitized seed dataset이기 때문입니다.

좋은 표현:

> 200개 규모의 한국어/영어 프롬프트 안전성 평가용 dataset을 만들고, 규칙 기반 guardrail과 문자 n-gram Naive Bayes baseline을 비교하여 데이터 검증, 성능 평가, 오류 분석, 차트 생성, 보고서 자동 생성을 수행했다.

나쁜 표현:

> 실제 LLM 보안 문제를 완전히 해결했다.

## 7. 다음 개선 방향

1. 데이터셋을 300개 이상으로 확장합니다.
2. 실제 LLM 응답을 수집하고 응답 안전성을 라벨링합니다.
3. 규칙 기반 baseline과 간단한 ML classifier를 비교합니다.
4. 보고서를 PDF 형태로 정리합니다.
