# Challenge Set Evaluation

## Purpose

The challenge set contains prompts that were written separately from the main extended dataset. It is used to check whether each baseline generalizes to new wording patterns.

## Results

| Algorithm | Accuracy | Harmful Precision | Harmful Recall | Harmful F1 | False Allow | False Refusal |
|---|---:|---:|---:|---:|---:|---:|
| rule_based_guardrail | 0.4875 | 0.4286 | 0.075 | 0.1277 | 0.925 | 0.1 |
| char_ngram_naive_bayes_challenge | 0.9875 | 0.9756 | 1.0 | 0.9877 | 0.0 | 0.025 |

## Interpretation

If a model performs much worse on the challenge set than on cross-validation, that suggests it may be overfitting the wording patterns in the main synthetic dataset. This is important because real user prompts will not follow the exact wording used in the training data.

## Limitations

- The challenge set is still synthetic.
- It is smaller than the main dataset.
- It tests prompt-level classification only, not actual LLM responses.
- It should be treated as a portfolio-level generalization check, not a production benchmark.