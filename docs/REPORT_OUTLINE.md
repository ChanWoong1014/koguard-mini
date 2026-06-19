# Report Outline

## Title

KoGuard-Mini: Korean-English LLM Prompt Safety Evaluation with a Rule-Based Guardrail Baseline

## 1. Introduction

- LLM services need safety evaluation.
- Many safety examples are English-heavy.
- Korean prompts may contain different phrasing and bypass patterns.
- This project builds a small bilingual evaluation pipeline.

## 2. Research Question

Main question:

> Can a simple rule-based guardrail detect sanitized English and Korean bypass-style prompts?

Sub-questions:

- Does performance differ between Korean and English prompts?
- Which attack types are easiest or hardest to detect?
- What errors does the baseline make?

## 3. Dataset

- Number of rows.
- Language split.
- Benign/harmful split.
- Attack types.
- Safety note: harmful examples are sanitized and non-actionable.

## 4. Method

- Rule-based baseline.
- Pattern matching.
- Prediction labels: `benign` or `harmful`.
- Character n-gram Naive Bayes baseline.
- 5-fold stratified cross-validation for the ML baseline.

## 5. Metrics

- Accuracy.
- Precision for harmful prompts.
- Recall for harmful prompts.
- F1 score.
- False allow rate.
- False refusal rate.

## 6. Algorithm Comparison

Compare:

- rule-based guardrail
- character n-gram Naive Bayes

Discuss:

- rule-based explainability
- ML baseline recall improvement
- risk of overfitting synthetic prompts

## 7. Challenge Set Evaluation

Explain:

- why the challenge set was created separately
- whether rule-based performance drops
- whether ML performance stays strong
- why this is still not a production benchmark

## 8. Results

Insert:

- Summary table.
- By-language table.
- By-attack-type table.

## 9. Error Analysis

Analyze:

- False allows: harmful prompts that passed.
- False refusals: benign prompts that were blocked.
- Korean-specific issues.
- English-specific issues.

## 10. Limitations

- Dataset is small.
- Labels are manually assigned.
- Rule-based guardrail is brittle.
- Naive Bayes is a simple baseline and may overfit synthetic wording.
- No real LLM response evaluation yet.
- No external human labeler agreement.

## 11. Future Work

- Add LLM response collection.
- Add manual response labels: safe refusal, partial compliance, unsafe compliance.
- Compare rule-based guardrail with ML classifier.
- Use public benchmark subsets with redaction.
- Add visualization dashboard.
