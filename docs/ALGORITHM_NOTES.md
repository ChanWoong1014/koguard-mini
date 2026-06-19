# 알고리즘 설명

이 프로젝트는 두 가지 baseline을 비교합니다.

## 1. Rule-Based Guardrail

파일:

```text
src/rule_guardrail.py
```

정규표현식으로 위험 신호를 찾는 방식입니다.

예를 들어 다음과 비슷한 표현을 찾습니다.

- 규칙 무시
- 가드레일 우회
- 숨겨진 시스템 프롬프트 공개
- 필터 비활성화
- 민감정보 제공
- 정책 제거

### 장점

- 이해하기 쉽습니다.
- 어떤 규칙 때문에 탐지됐는지 설명할 수 있습니다.
- 학습 데이터 없이도 동작합니다.
- 작은 실험의 기준선으로 적합합니다.

### 단점

- 사람이 미리 적은 표현만 잘 잡습니다.
- 표현이 바뀌면 쉽게 놓칩니다.
- 한국어 문장 순서가 바뀌면 탐지가 약해질 수 있습니다.
- 정상적인 안전성 설명 요청도 위험하게 볼 수 있습니다.

## 2. Character N-Gram Naive Bayes

파일:

```text
src/ml_baseline.py
```

문장을 짧은 문자 조각으로 나누고, 어떤 조각이 benign 또는 harmful-style 문장에서 자주 나타나는지 학습하는 방식입니다.

예를 들어 "ignore safety rules"라는 문장은 `ign`, `safe`, `rule` 같은 문자 조각으로 나뉩니다. 한국어도 같은 방식으로 처리할 수 있기 때문에 형태소 분석기 없이 간단히 실험할 수 있습니다.

현재 구현은 5-fold stratified cross-validation을 사용합니다.

### 장점

- 사람이 규칙으로 직접 쓰지 않은 표현도 일부 학습할 수 있습니다.
- 영어와 한국어 모두에 적용할 수 있습니다.
- 외부 라이브러리 없이 순수 Python으로 동작합니다.
- rule-based 방식과 비교하기 좋습니다.

### 단점

- 의미를 깊게 이해하는 모델은 아닙니다.
- synthetic 데이터의 표현 패턴을 외울 수 있습니다.
- 실제 LLM 응답을 평가하지 않습니다.
- 실제 서비스용 안전 모델이라고 보기에는 부족합니다.

## 3. Challenge Set

파일:

```text
data/prompts_challenge.csv
```

challenge set은 main extended dataset과 따로 작성한 데이터입니다.

목적은 다음 질문을 확인하는 것입니다.

> 알고리즘이 기존 데이터 표현을 외운 것인가, 아니면 새로운 표현에도 어느 정도 대응하는가?

challenge set에는 다음 유형이 들어 있습니다.

- 안전성 설명을 요청하지만 `bypass`, `hidden prompt` 같은 단어가 들어간 정상 요청
- 직접적인 키워드가 적은 harmful-style 요청
- 한국어/영어 표현 변형

현재 결과에서는 rule-based 방식이 challenge set에서 크게 약해졌습니다. 반면 Naive Bayes는 더 안정적으로 동작했지만, synthetic 데이터셋이라는 한계는 여전히 있습니다.

## 4. 이 프로젝트에서 말할 수 있는 것

적절한 설명:

> PromptLouter를 진행하며 LLM 라우팅뿐 아니라 입력 프롬프트의 안전성 평가도 궁금해졌다. 그래서 한국어/영어 프롬프트 데이터셋을 만들고, rule-based guardrail과 character n-gram Naive Bayes를 비교하여 프롬프트 수준의 위험 신호 탐지 실험을 진행했다.

피해야 할 설명:

> 이 시스템은 LLM 안전 문제를 해결한다.

그 표현은 과장입니다.
