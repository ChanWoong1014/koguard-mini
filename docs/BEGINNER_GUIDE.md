# KoGuard-Mini Beginner Guide

The main project documentation is written in Korean because this is a personal learning project.

Recommended reading order:

1. `README.md`
2. `docs/BEGINNER_GUIDE_KO.md`
3. `docs/ALGORITHM_NOTES.md`
4. `docs/DATASET_CARD.md`
5. `reports/experiment_report_ko.md`

Short English summary:

KoGuard-Mini is a Korean-English LLM prompt-level safety evaluation experiment. It started from curiosity after working on PromptLouter: before routing a user request to an LLM, can we roughly detect whether the prompt itself contains safety-risk signals?

The project compares:

- a rule-based guardrail,
- a character n-gram Naive Bayes baseline,
- a separate challenge set for generalization testing.

It is not a production safety system.
