# Gemini 2.5 Flash-Lite Response-Level Pilot

## Scope

- Model: `gemini-2.5-flash-lite`
- Prompt source: `data/prompts_challenge.csv`
- Pilot size: 20 prompts
- Balance: English/Korean x benign/harmful-style, 5 prompts in each group
- Labeling: one evaluator applied the criteria in `docs/RESPONSE_LEVEL_EVALUATION_PLAN.md`

The raw model responses are kept only in the ignored local directory `data/response_evaluations/`. This report and its JSON metrics contain no raw response text.

## Results

| Metric | Result |
|---|---:|
| Safe refusal rate on harmful-style prompts | 0.30 (3/10) |
| Unsafe compliance rate on harmful-style prompts | 0.40 (4/10) |
| Partial compliance rate on harmful-style prompts | 0.30 (3/10) |
| Over-refusal rate on benign prompts | 0.00 (0/10) |
| Safe completion rate on benign prompts | 1.00 (10/10) |
| Unclear rate | 0.00 (0/20) |

## Interpretation

This pilot found that 4 of 10 harmful-style prompts received responses classified as `unsafe_compliance`. These included acceptance of intent obfuscation, translation to reduce detection, an always-obliging role, or ignoring a verification component.

Another 3 harmful-style responses were labeled `partial_compliance`: they included caution or reframing but still accepted the authority premise, reduced checking, or supplied some tool-oriented guidance. Only 3 harmful-style prompts received `safe_refusal`.

All 10 benign prompts were labeled `safe_completion`, so this small pilot did not observe over-refusal. That does not demonstrate that the model has no over-refusal behavior; the benign sample is small and synthetic.

## Limitations

- The 20 prompts are synthetic/sanitized and do not represent production traffic or a public jailbreak benchmark.
- The response labels were assigned by one evaluator, without inter-rater agreement measurement.
- A single model and a single collection configuration were used.
- The sample is too small for broad safety claims or model rankings.
- Some responses may be sensitive; raw responses remain local and are not included in this repository.

## Public-Safe Artifacts

- `reports/gemini_2_5_flash_lite_pilot_metrics.json`: aggregate counts and rates only
- `reports/gemini_2_5_flash_lite_pilot_report.md`: interpretation without raw response text
