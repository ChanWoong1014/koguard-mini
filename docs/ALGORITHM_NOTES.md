# Algorithm Notes

This project currently compares two baselines.

## 1. Rule-Based Guardrail

File:

```text
src/rule_guardrail.py
```

This method uses regular expressions. It checks whether a prompt contains suspicious patterns such as:

- ignore rules
- bypass guardrail
- hidden system prompt
- safety filter disabled
- private data
- policy removed

### Strengths

- Easy to understand.
- Easy to explain in an interview.
- No training data required.
- Shows which rule matched.

### Weaknesses

- Brittle when wording changes.
- Korean sentence order can reduce detection.
- It misses implicit or indirect intent.
- Adding too many rules can cause false refusals.

## 2. Character N-Gram Naive Bayes

File:

```text
src/ml_baseline.py
```

This method learns from labeled examples. It breaks each prompt into short character chunks, such as 3-gram to 5-gram features, and learns which chunks are more common in benign or harmful-style prompts.

It uses 5-fold stratified cross-validation.

### Why Character N-Grams?

Character n-grams work reasonably well for both English and Korean because they do not depend strongly on English whitespace or Korean morphological analysis.

### Strengths

- Can learn patterns that are not manually written as rules.
- Works without external libraries.
- Useful as a simple ML baseline.
- Provides an algorithm comparison against the rule-based baseline.

### Weaknesses

- It can overfit synthetic wording patterns.
- It is not a production safety classifier.
- It does not understand meaning deeply.
- It evaluates prompt text only, not actual LLM responses.

## 3. How To Explain This In A Portfolio

Good explanation:

> I implemented two baselines: an interpretable rule-based guardrail and a character n-gram Naive Bayes classifier. The rule-based system is explainable but brittle, while the ML baseline improves recall by learning lexical patterns from the labeled dataset. I compared both methods using accuracy, harmful precision, harmful recall, F1, false allow rate, and false refusal rate.

Avoid saying:

> This system solves LLM safety.

That would be too strong.

## 4. Challenge Set

The project also includes `data/prompts_challenge.csv`.

This dataset is written separately from the main 200-row extended dataset. It includes:

- benign prompts that contain safety-related words such as bypass or hidden prompt,
- harmful-style prompts that use less direct wording,
- Korean and English examples.

The challenge set is useful because it checks whether a model is only memorizing the synthetic wording patterns in the main dataset.

Current interpretation:

- The rule-based guardrail struggles on challenge prompts because keyword rules are brittle.
- The Naive Bayes baseline performs better, but it can still over-block benign safety discussion prompts.
- This makes the project more realistic than reporting only one high cross-validation score.
