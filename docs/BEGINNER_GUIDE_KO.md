# KoGuard-Mini 초보자 가이드

이 문서는 프로젝트를 처음 보는 사람이 전체 흐름을 이해하기 위한 가이드입니다.

## 1. 왜 이 프로젝트를 만들었나

이 프로젝트는 PromptLouter를 진행하면서 생긴 궁금증에서 출발했습니다.

PromptLouter에서는 사용자의 요청을 어떤 LLM으로 보낼지, 비용과 성능을 어떻게 조절할지에 초점이 있었습니다. KoGuard-Mini에서는 그보다 앞단의 문제를 봅니다.

> LLM에 요청을 보내기 전에, 사용자의 프롬프트 자체가 안전한 요청인지 위험 신호가 있는 요청인지 평가할 수 있을까?

즉, 이 프로젝트는 LLM 응답을 직접 평가하는 프로젝트가 아니라 **프롬프트 수준의 안전성/안정성 평가 실험**입니다.

## 2. 꼭 알아야 할 용어

### LLM

ChatGPT 같은 대형 언어 모델입니다.

### Prompt

사용자가 LLM에게 입력하는 질문이나 명령입니다.

### Guardrail

위험하거나 부적절한 입력/출력을 막기 위한 안전장치입니다.

### Benign

정상 요청입니다.

### Harmful-style

실제 유해한 절차를 담지는 않지만, 안전 정책 우회나 프롬프트 누출처럼 위험 신호가 있는 요청 형태입니다.

### False Allow

위험한 요청인데 시스템이 통과시킨 경우입니다. 안전성 평가에서 특히 중요합니다.

### False Refusal

정상 요청인데 시스템이 잘못 막은 경우입니다.

## 3. 중요한 파일

### `data/prompts_extended.csv`

200개 main 데이터셋입니다.

- 영어 100개
- 한국어 100개
- benign 100개
- harmful-style 100개

### `data/prompts_challenge.csv`

80개 challenge 데이터셋입니다.

main dataset과 다른 표현으로 작성해서 알고리즘이 새로운 표현에도 대응하는지 확인합니다.

### `src/rule_guardrail.py`

정규표현식 기반 rule-based baseline입니다.

사람이 정한 위험 표현을 기준으로 탐지합니다.

### `src/ml_baseline.py`

character n-gram Naive Bayes baseline입니다.

문장을 짧은 문자 조각으로 나누고, 어떤 조각이 benign 또는 harmful-style에 자주 나오는지 학습합니다.

### `src/run_pipeline.py`

전체 실행 파일입니다.

데이터 검증, rule-based 평가, ML 평가, challenge 평가, 오류 분석, 차트 생성, 보고서 생성을 한 번에 실행합니다.

## 4. 실행 방법

VS Code에서 `C:\koguard-mini` 폴더를 열고 PowerShell 터미널에서 실행합니다.

```powershell
.\run_windows.ps1
```

직접 실행하려면:

```powershell
python src\build_extended_dataset.py --output data\prompts_extended.csv
python src\build_challenge_dataset.py --output data\prompts_challenge.csv
python src\run_pipeline.py --input data\prompts_extended.csv --challenge-input data\prompts_challenge.csv --reports-dir reports
python -m unittest discover tests
```

정상 실행되면 다음과 비슷한 메시지가 나옵니다.

```text
KoGuard-Mini pipeline complete.
Ran 15 tests
OK
```

## 5. 결과를 어디서 보나

- `reports/algorithm_comparison.csv`: main dataset 알고리즘 비교
- `reports/challenge_algorithm_comparison.csv`: challenge set 알고리즘 비교
- `reports/errors.csv`: rule-based 오분류
- `reports/ml_errors.csv`: ML baseline 오분류
- `reports/challenge_report.md`: challenge set 결과 요약
- `reports/experiment_report_ko.md`: 전체 실험 보고서 초안

## 6. 결과를 어떻게 해석하나

현재 결과는 rule-based 방식과 Naive Bayes 방식의 차이를 보여줍니다.

rule-based 방식은 설명하기 쉽지만, 표현이 바뀌면 많이 놓칩니다. challenge set에서 성능이 크게 떨어지는 것이 그 예시입니다.

Naive Bayes는 현재 데이터셋에서 훨씬 좋은 성능을 보입니다. 하지만 데이터가 synthetic이므로 실제 서비스에서도 그대로 잘 된다고 말하면 안 됩니다.

## 7. 좋은 설명과 나쁜 설명

좋은 설명:

> PromptLouter를 진행하면서 LLM 라우팅뿐 아니라 입력 프롬프트의 안전성 평가도 궁금해졌다. 그래서 한국어/영어 프롬프트 데이터셋을 만들고, rule-based guardrail과 character n-gram Naive Bayes를 비교하여 프롬프트 수준의 위험 신호 탐지 실험을 진행했다.

나쁜 설명:

> 실제 LLM 보안 문제를 해결했다.

이 프로젝트는 학습/실험 프로젝트이지 실제 서비스용 보안 시스템이 아닙니다.
