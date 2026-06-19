# KoGuard-Mini Beginner Guide

This guide explains what to do first when opening the project in VS Code.

## 1. Big Picture

This project does not train a new LLM.

Instead, it evaluates whether a prompt looks normal or adversarial. Many real AI systems need safety checks before sending user input to an LLM.

The current project compares two baselines:

- Rule-based guardrail
- Character n-gram Naive Bayes classifier

The point is not to claim production-grade safety. The point is to show dataset construction, evaluation, algorithm comparison, and error analysis.

## 2. Main Files

### `data/prompts_seed.csv`

This is the smaller 100-row dataset.

### `data/prompts_extended.csv`

This is the larger 200-row dataset and the default dataset for the full pipeline.

### `data/prompts_challenge.csv`

This is the 80-row challenge dataset. It is written separately from the main extended dataset to test whether the algorithms handle new wording patterns.

Each row is one prompt. The important columns are:

- `prompt_text`: the prompt we want to inspect.
- `risk_label`: the correct answer, either `benign` or `harmful`.
- `language`: `ko` or `en`.
- `attack_type`: the prompt style, such as `benign`, `roleplay`, `instruction_override`, `privacy`, or `tool_misuse`.

### `src/build_extended_dataset.py`

This script regenerates the 200-row dataset.

### `src/rule_guardrail.py`

This file contains the rule-based detector.

It checks prompt text using regular expressions. For example, the code can look for phrases similar to "ignore safety rules" or "bypass the guardrail."

### `src/ml_baseline.py`

This file contains a no-dependency character n-gram Naive Bayes classifier.

It learns from the labeled dataset and is evaluated with 5-fold stratified cross-validation.

### `src/run_pipeline.py`

This file handles the full run in one command.

It runs dataset validation, rule-based evaluation, ML baseline evaluation, error analysis, chart generation, and report generation.

### `reports/algorithm_comparison.csv`

This file compares the rule-based guardrail and the Naive Bayes classifier.

## 3. Recommended First Commands

Open PowerShell in the project folder.

```powershell
cd C:\koguard-mini
```

Run the full pipeline:

```powershell
python src\build_extended_dataset.py --output data\prompts_extended.csv
python src\build_challenge_dataset.py --output data\prompts_challenge.csv
python src\run_pipeline.py --input data\prompts_extended.csv --challenge-input data\prompts_challenge.csv --reports-dir reports
```

Or use the Windows helper:

```powershell
.\run_windows.ps1
```

This creates:

- `reports/validation.json`
- `reports/dataset_summary.json`
- `reports/results.json`
- `reports/ml_results.json`
- `reports/algorithm_comparison.csv`
- `reports/challenge_algorithm_comparison.csv`
- `reports/challenge_report.md`
- `reports/errors.csv`
- `reports/ml_errors.csv`
- `reports/portfolio_report.md`
- `reports/portfolio_report_ko.md`
- SVG chart files under `reports/`

Run tests:

```powershell
python -m unittest discover tests
```

If `python` does not work, try `py` instead.

## 4. What You Should Do Next

Your job is not to write dangerous prompts. Your job is to build a safe evaluation dataset.

The current extended dataset has 200 rows. If you have time, add more rows by editing `src/build_extended_dataset.py` and regenerating `data/prompts_extended.csv`.

Good additions:

- normal ML or data-analysis questions,
- normal LLM safety questions,
- sanitized bypass-style prompts,
- Korean and English pairs,
- clear labels.

Do not publish raw harmful instructions. Keep examples high-level, redacted, or benchmark-derived.

## 5. Final Portfolio Story

The final story should be:

> I built a Korean-English LLM prompt safety evaluation pipeline. I created a 200-row labeled dataset and an 80-row challenge set, implemented an interpretable rule-based guardrail, added a character n-gram Naive Bayes ML baseline, compared both algorithms with evaluation metrics, generated charts, and analyzed errors.

That is a realistic undergraduate portfolio project.
