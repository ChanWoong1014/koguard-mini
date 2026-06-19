# KoGuard-Mini

한국어/영어 LLM 프롬프트 안전성 평가 미니 프로젝트입니다.

이 프로젝트는 새로운 LLM을 학습시키는 프로젝트가 아닙니다. 대신 사용자의 프롬프트가 정상 요청인지, 아니면 안전 정책 우회나 프롬프트 누출 같은 위험 패턴인지 평가하는 간단한 파이프라인을 만듭니다.

## 현재 구성

- 기본 데이터셋: `data/prompts_seed.csv`
- 확장 데이터셋: `data/prompts_extended.csv`
- 일반화 테스트 데이터셋: `data/prompts_challenge.csv`
- 확장 데이터 수: 200개
- challenge 데이터 수: 80개
- 언어: 영어 100개, 한국어 100개
- 라벨: benign 100개, harmful-style 100개
- baseline: 규칙 기반 guardrail, 문자 n-gram Naive Bayes
- 결과 보고서: `reports/portfolio_report_ko.md`

## 실행

PowerShell에서 프로젝트 폴더로 이동한 뒤 실행합니다.

```powershell
python src\build_extended_dataset.py --output data\prompts_extended.csv
python src\build_challenge_dataset.py --output data\prompts_challenge.csv
python src\run_pipeline.py --input data\prompts_extended.csv --challenge-input data\prompts_challenge.csv --reports-dir reports
```

또는 Windows 실행 스크립트를 사용할 수 있습니다.

```powershell
.\run_windows.ps1
```

## 주요 결과물

- `docs/BEGINNER_GUIDE_KO.md`: 초보자용 한국어 설명
- `docs/DATASET_CARD.md`: 데이터셋 설명 문서
- `reports/validation.json`: 데이터 검증 결과
- `reports/dataset_summary.json`: 데이터셋 요약
- `reports/results.json`: 평가 결과
- `reports/ml_results.json`: Naive Bayes 평가 결과
- `reports/algorithm_comparison.csv`: 알고리즘 비교 결과
- `reports/challenge_algorithm_comparison.csv`: challenge set 일반화 비교 결과
- `reports/challenge_report.md`: challenge set 보고서
- `reports/errors.csv`: 오분류 케이스
- `reports/ml_errors.csv`: ML baseline 오분류 케이스
- `reports/portfolio_report.md`: 영어 보고서 초안
- `reports/portfolio_report_ko.md`: 한국어 보고서 초안
- `reports/*.svg`: 시각화 차트

## 포트폴리오에서 강조할 점

이 프로젝트는 "LLM 안전 시스템을 완성했다"는 프로젝트가 아닙니다.

더 현실적인 설명은 다음과 같습니다.

> 한국어/영어 LLM 프롬프트 안전성 평가용 200개 확장 dataset과 80개 challenge set을 만들고, 규칙 기반 guardrail과 문자 n-gram Naive Bayes baseline을 비교한 뒤, 데이터 검증, 성능 평가, 일반화 테스트, 오류 분석, 차트 생성, 보고서 자동 생성을 수행했다.

이 표현이 더 정직하고 대학원 지원용으로도 방어하기 좋습니다.
