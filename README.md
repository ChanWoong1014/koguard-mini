# KoGuard-Mini

Korean-English LLM safety evaluation mini project for graduate lab application.

## 1. Project Goal

KoGuard-Mini is a small portfolio project for evaluating whether LLM prompts are likely to be unsafe, adversarial, or benign. The project is designed for a student-level research portfolio, not for claiming production-grade safety.

The main research question is:

> Do Korean and English prompts show different risk patterns when users try to bypass LLM safety behavior?

This project focuses on evaluation and analysis, not on creating harmful content.

## 2. Why This Fits DAMI Lab

DAMI Lab studies Data Analysis & Machine Intelligence, including Trustworthy AI. This project connects to:

- Robustness: checking whether LLM safety behavior changes under prompt variation.
- Privacy & Security: identifying prompts that try to bypass normal model behavior.
- Interpretability: explaining why a simple guardrail flags a prompt.
- AI Applications: building a practical evaluation pipeline that could be reused for LLM services.

## 3. Expected Final Output

The final submission package should include:

- GitHub repository with this code.
- Short PDF report, about 6 to 10 pages.
- Dataset description.
- Evaluation table.
- Error analysis examples.
- Clear limitation section.
- Korean report draft for application writing.
- SVG charts for quick visual inspection.

## 4. Folder Structure

```text
koguard-mini/
  data/
    prompts_template.csv       # Safe template dataset
    prompts_seed.csv           # Current 100-row safe seed dataset
    prompts_extended.csv       # Current 200-row safe extended dataset
    prompts_challenge.csv      # Current 80-row out-of-template challenge dataset
  docs/
    BEGINNER_GUIDE.md          # Step-by-step beginner guide
    BEGINNER_GUIDE_KO.md       # Korean beginner guide
    ALGORITHM_NOTES.md         # Rule-based vs ML baseline explanation
    DATASET_CARD.md            # Dataset construction and safety notes
    REPORT_OUTLINE.md          # Portfolio report outline
  reports/
    results.json               # Generated after evaluation
  src/
    rule_guardrail.py          # Simple rule-based baseline
    evaluate_guardrail.py      # Evaluation script
    dataset_summary.py         # Dataset summary script
    error_analysis.py          # Incorrect-prediction extraction script
  tests/
    test_rule_guardrail.py
    test_validate_dataset.py
  README.md
  README_KO.md
  requirements.txt
  run_windows.ps1
```

## 5. Dataset Format

Create a CSV file with this schema:

```text
id,language,attack_type,category,risk_label,prompt_text,notes
```

Column meanings:

- `id`: unique prompt id.
- `language`: `ko` or `en`.
- `attack_type`: `benign`, `direct`, `roleplay`, `instruction_override`, `translation_bypass`, etc.
- `category`: high-level category such as `benign`, `cyber`, `privacy`, `self_harm`, `violence`, or `misinformation`.
- `risk_label`: ground-truth label, either `benign` or `harmful`.
- `prompt_text`: prompt text to evaluate.
- `notes`: optional memo.

Do not publish detailed harmful instructions in the repository. If you use a public benchmark, keep the raw benchmark file private or include only redacted examples in the public repo.

## 6. Run

From this folder:

```powershell
python src/build_extended_dataset.py --output data/prompts_extended.csv
python src/build_challenge_dataset.py --output data/prompts_challenge.csv
python src/run_pipeline.py --input data/prompts_extended.csv --challenge-input data/prompts_challenge.csv --reports-dir reports
```

On Windows, you can also run:

```powershell
.\run_windows.ps1
```

This one command creates:

- `reports/validation.json`
- `reports/dataset_summary.json`
- `reports/results.json`
- `reports/ml_results.json`
- `reports/algorithm_comparison.csv`
- `reports/errors.csv`
- `reports/ml_errors.csv`
- `reports/challenge_algorithm_comparison.csv`
- `reports/challenge_report.md`
- `reports/challenge_errors.csv`
- `reports/challenge_ml_errors.csv`
- `reports/portfolio_report.md`
- `reports/portfolio_report_ko.md`
- `reports/chart_accuracy_by_language.svg`
- `reports/chart_false_allow_by_attack_type.svg`
- `reports/chart_dataset_by_attack_type.svg`
- `reports/metrics_by_language.csv`
- `reports/metrics_by_attack_type.csv`

You can also run each step separately:

```powershell
python src/validate_dataset.py --input data/prompts_seed.csv --output reports/validation.json
python src/dataset_summary.py --input data/prompts_seed.csv --output reports/dataset_summary.json
python src/evaluate_guardrail.py --input data/prompts_seed.csv --output reports/results.json
python src/error_analysis.py --input reports/results.json --output reports/errors.csv
python src/export_assets.py --dataset-summary reports/dataset_summary.json --results reports/results.json --reports-dir reports
python src/make_markdown_report.py --dataset-summary reports/dataset_summary.json --results reports/results.json --errors reports/errors.csv --output reports/portfolio_report.md
```

Run tests:

```powershell
python -m unittest discover tests
```

## 7. What To Improve Next

After the scaffold works, improve it in this order:

1. Open `docs/BEGINNER_GUIDE.md` first.
2. Read `docs/ALGORITHM_NOTES.md`.
3. Run `run_windows.ps1` or the two Python commands above.
4. Compare rule-based and Naive Bayes results in `reports/algorithm_comparison.csv`.
5. Inspect challenge-set generalization in `reports/challenge_algorithm_comparison.csv`.
6. Add manual labeling rules for LLM responses: safe refusal, partial compliance, unsafe compliance.
7. Add a short PDF report based on `reports/portfolio_report_ko.md`.

## 8. Current Limitation

This baseline is intentionally simple. It uses keyword and pattern rules, so it will miss many subtle cases and may over-block normal prompts. That limitation is useful for a portfolio because it gives you something concrete to analyze and improve.
