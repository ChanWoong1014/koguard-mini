# 알고리즘 설명

KoGuard-Mini는 세 가지 baseline을 비교한다.

1. Rule-based guardrail
2. Character n-gram Naive Bayes
3. TF-IDF Logistic Regression

여기서 baseline은 “가장 먼저 비교 기준으로 삼는 단순한 방법”이라는 뜻이다. 복잡한 LLM을 새로 학습시키기 전에, 간단한 방법으로도 어느 정도 되는지 확인하는 것이 목적이다.

## 1. Rule-Based Guardrail

Rule-based 방식은 사람이 직접 만든 규칙으로 프롬프트를 분류한다.

예를 들어 다음과 같은 위험 신호를 찾는다.

- 이전 지시를 무시하라는 표현
- 안전 정책을 제거하라는 표현
- 숨겨진 시스템 프롬프트를 보여달라는 표현
- 민감 정보를 요구하는 표현
- 도구를 허용 범위 밖으로 사용하려는 표현

장점:

- 구현이 쉽다.
- 어떤 규칙 때문에 탐지됐는지 설명하기 쉽다.
- 학습 데이터가 없어도 동작한다.

단점:

- 사람이 미리 쓴 표현만 잘 잡는다.
- 표현이 조금만 바뀌면 놓칠 수 있다.
- 문맥을 깊게 이해하지 못한다.

이 프로젝트 결과에서도 rule-based 방식은 main dataset에서 harmful recall 0.58, challenge set에서 harmful recall 0.075로 떨어졌다. 특히 challenge set false allow rate 0.925는 새로운 표현에 매우 취약하다는 뜻이다.

## 2. Character N-Gram Naive Bayes

Naive Bayes는 간단한 확률 기반 분류기다.

이 프로젝트에서는 단어가 아니라 character n-gram을 feature로 사용한다. character n-gram은 문장을 짧은 문자 조각으로 나눈 것이다.

예를 들어 `safety`라는 단어를 3글자 조각으로 보면 다음과 비슷하다.

```text
saf, afe, fet, ety
```

이 방식을 쓰는 이유는 한국어와 영어가 섞여 있어도 비교적 단순하게 처리할 수 있기 때문이다.

장점:

- 구현이 가볍다.
- 한국어/영어 혼합 데이터에 적용하기 쉽다.
- 규칙에 없는 표현도 데이터에서 반복되면 학습할 수 있다.

단점:

- 문장의 의미를 진짜로 이해하는 것은 아니다.
- synthetic 데이터의 표현 패턴에 과적합될 수 있다.
- 데이터 작성 방식이 바뀌면 성능이 크게 달라질 수 있다.

## 3. TF-IDF Logistic Regression

Logistic Regression은 이진 분류에 자주 쓰이는 선형 모델이다. 여기서는 `benign`과 `harmful` 중 하나로 분류한다.

전체 흐름은 다음과 같다.

1. 프롬프트를 character n-gram으로 나눈다.
2. 각 n-gram에 TF-IDF 가중치를 계산한다.
3. Logistic Regression이 각 feature의 가중치를 학습한다.
4. harmful일 확률이 threshold 이상이면 harmful로 분류한다.

### TF-IDF란?

TF-IDF는 어떤 feature가 한 문장 안에서는 자주 나오지만 전체 문서에서는 너무 흔하지 않을 때 더 높은 값을 주는 방식이다.

간단히 말하면:

- 자주 나오는 feature는 중요할 수 있다.
- 하지만 모든 문장에 흔하게 나오는 feature는 구분력이 낮다.
- 그래서 “그 문장에서는 중요하지만 전체에서는 너무 흔하지 않은 패턴”을 더 크게 본다.

### Threshold가 중요한 이유

Logistic Regression은 내부적으로 harmful일 확률에 가까운 점수를 만든다.

이 점수가 기준값보다 크면 harmful, 작으면 benign으로 본다.

이 기준값을 threshold라고 한다.

- threshold가 낮으면 harmful을 많이 잡지만 정상 요청도 과하게 막을 수 있다.
- threshold가 높으면 정상 요청은 덜 막지만 위험 요청을 놓칠 수 있다.

현재 프로젝트에서는 기본 threshold를 `0.9`로 두었다. 초기 threshold `0.5`에서는 harmful recall은 높았지만 false refusal이 너무 커서 정상 요청을 많이 막았다. 그래서 main dataset의 점수 분포를 확인한 뒤 더 보수적인 기준을 적용했다.

## 4. Confusion Matrix

Confusion matrix는 분류 결과를 네 가지로 나눠 보여준다.

- True Negative: benign을 benign으로 맞춤
- False Positive: benign을 harmful로 잘못 막음
- False Negative: harmful을 benign으로 통과시킴
- True Positive: harmful을 harmful로 맞춤

이 프로젝트에서는 특히 False Negative가 중요하다. harmful-style 요청을 benign으로 통과시키는 경우이기 때문이다. 보고서에서는 이것을 false allow라고 부른다.

## 5. 결과 해석 기준

현재 결과만 보면 Naive Bayes와 Logistic Regression이 rule-based보다 훨씬 좋아 보인다.

하지만 이 결론은 조심해야 한다.

이 데이터셋은 실제 사용자 로그가 아니라 직접 만든 synthetic/sanitized 데이터다. 따라서 모델이 실제 위험 의도를 깊게 이해했다기보다, 작성된 데이터의 반복 패턴을 잘 학습했을 수 있다.

정확한 해석은 다음 정도가 적절하다.

> 단순 규칙 기반 방식은 표현 변화에 취약했고, character n-gram 기반 ML baseline은 현재 synthetic 데이터셋에서 더 높은 recall을 보였다. 하지만 실제 LLM 안전성을 주장하려면 외부 benchmark, 실제 응답 평가, 라벨링 기준 검증이 추가로 필요하다.
