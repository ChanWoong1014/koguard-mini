# Data

이 폴더에는 KoGuard-Mini에서 사용하는 CSV 데이터셋이 들어 있습니다.

## 파일

- `prompts_template.csv`: 가장 작은 예시 템플릿
- `prompts_seed.csv`: 100개 seed 데이터셋
- `prompts_extended.csv`: 200개 main 데이터셋
- `prompts_challenge.csv`: 80개 challenge 데이터셋

## 공개 기준

이 저장소의 데이터는 공개 가능한 수준의 synthetic/sanitized 예시만 포함합니다.

실제 유해한 절차, 구체적인 공격 방법, 개인정보, 실제 사용자 로그는 포함하지 않습니다.

## 데이터 수정 방법

`prompts_extended.csv`와 `prompts_challenge.csv`는 직접 수정하기보다 아래 스크립트에서 원문을 수정한 뒤 다시 생성하는 방식을 권장합니다.

```powershell
python src\build_extended_dataset.py --output data\prompts_extended.csv
python src\build_challenge_dataset.py --output data\prompts_challenge.csv
```
