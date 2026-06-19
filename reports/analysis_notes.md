# KoGuard-Mini Analysis Notes

## Current Snapshot

- Main dataset rows: 600
- Challenge dataset rows: 80
- Languages: English and Korean
- Labels: benign and harmful-style
- Baselines: rule-based guardrail, character n-gram Naive Bayes, TF-IDF Logistic Regression

## Main Result

The rule-based guardrail is explainable but brittle. On the 600-row main dataset, it keeps false refusal at 0.0 but misses 42% of harmful-style prompts.

The character n-gram Naive Bayes baseline performs best on the current synthetic dataset. It reaches perfect scores on the main dataset and remains strong on the challenge set, but this should not be interpreted as production-grade safety.

The TF-IDF Logistic Regression baseline also performs strongly after threshold tuning. It has 0.0 false allow on both the main dataset and challenge set, but it still has some false refusals.

## Challenge Set

The challenge set exposes the weakness of the rule-based approach. The rule-based harmful recall drops to 0.075, with a false allow rate of 0.925.

This supports the main project lesson:

> Simple keyword rules are easy to explain, but they are fragile when wording changes.

## Important Caveat

The dataset is synthetic and sanitized. The strong ML baseline results may come from repeated wording patterns rather than deep understanding of unsafe intent.

The project should be described as a learning and evaluation pipeline, not as a deployable LLM security system.

## Short Project Summary

I built a Korean-English LLM prompt safety evaluation pipeline with a 600-row synthetic prompt dataset and an 80-row challenge set. I compared an interpretable rule-based guardrail with character n-gram Naive Bayes and TF-IDF Logistic Regression baselines, then analyzed false allows, false refusals, confusion matrices, and challenge-set generalization behavior.
