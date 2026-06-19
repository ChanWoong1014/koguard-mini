# Current Analysis Notes

## Dataset Snapshot

- Extended dataset: `data/prompts_extended.csv`
- Extended rows: 200
- Challenge dataset: `data/prompts_challenge.csv`
- Challenge rows: 80
- Extended dataset validation errors: 0

## Main Algorithm Comparison

| Algorithm | Accuracy | Harmful Precision | Harmful Recall | Harmful F1 | False Allow | False Refusal |
|---|---:|---:|---:|---:|---:|---:|
| rule-based guardrail | 0.79 | 1.0 | 0.58 | 0.7342 | 0.42 | 0.0 |
| char n-gram Naive Bayes | 0.99 | 0.9804 | 1.0 | 0.9901 | 0.0 | 0.02 |

## Challenge Set Comparison

| Algorithm | Accuracy | Harmful Precision | Harmful Recall | Harmful F1 | False Allow | False Refusal |
|---|---:|---:|---:|---:|---:|---:|
| rule-based guardrail | 0.4875 | 0.4286 | 0.075 | 0.1277 | 0.925 | 0.1 |
| char n-gram Naive Bayes | 0.9875 | 0.9756 | 1.0 | 0.9877 | 0.0 | 0.025 |

## Interpretation

The rule-based guardrail is highly explainable but brittle. On the challenge set, it over-blocks some benign safety discussion prompts and misses many harmful-style prompts with less direct wording.

The character n-gram Naive Bayes baseline performs much better, including on the challenge set. However, this should still be treated as a portfolio-level result because both datasets are synthetic and sanitized.

## Important Caveat

Do not claim that this is a production safety system.

A realistic claim:

> I built a Korean-English LLM prompt safety evaluation pipeline with a 200-row extended dataset and an 80-row challenge set. I compared an interpretable rule-based guardrail with a character n-gram Naive Bayes baseline, then analyzed false allows, false refusals, and generalization behavior.
