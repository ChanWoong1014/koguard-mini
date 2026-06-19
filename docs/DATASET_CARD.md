# Dataset Card: KoGuard-Mini Prompt Seed Dataset

## Dataset Name

`data/prompts_extended.csv`

Challenge dataset:

`data/prompts_challenge.csv`

## Purpose

This dataset is a small seed dataset for evaluating whether a prompt looks benign or adversarial in an LLM safety context.

It is designed for an undergraduate portfolio project, not for production safety benchmarking.

## Size

- Total rows: 200
- English rows: 100
- Korean rows: 100
- Benign rows: 100
- Harmful-style rows: 100

Challenge set:

- Total rows: 80
- English rows: 40
- Korean rows: 40
- Benign rows: 40
- Harmful-style rows: 40

## Columns

| Column | Meaning |
|---|---|
| `id` | Unique row identifier |
| `language` | `ko` or `en` |
| `attack_type` | Prompt type such as `benign`, `instruction_override`, `roleplay`, `privacy`, or `tool_misuse` |
| `category` | High-level category |
| `risk_label` | Ground-truth label: `benign` or `harmful` |
| `prompt_text` | Prompt text |
| `notes` | Short construction note |

## Attack Types

- `benign`: normal educational, coding, evaluation, or portfolio questions
- `instruction_override`: asks the system to ignore or override rules
- `roleplay`: asks the assistant to act as an unrestricted or non-refusing persona
- `translation_bypass`: uses translation or rewriting as a bypass frame
- `policy_removal`: asks the assistant to remove or ignore policy restrictions
- `filter_disable`: assumes filters or moderation layers are off
- `privacy`: asks for information that should not be exposed
- `obfuscation`: asks to hide or rephrase unsafe intent
- `prompt_leakage`: asks for hidden prompts or developer instructions
- `tool_misuse`: asks tools to be used outside normal safety limits
- `authority_impersonation`: pretends to have authority to skip checks

## Safety Constraints

The dataset intentionally avoids detailed harmful instructions. Harmful-style examples are sanitized and non-actionable.

This makes the dataset safer for a public GitHub portfolio, but it also means the benchmark is easier and less realistic than real-world adversarial traffic.

## Known Limitations

- The dataset is small.
- Labels are manually assigned.
- The dataset is synthetic and sanitized.
- It evaluates prompt-level risk, not model response safety.
- It should not be used to claim production-grade safety.

## Recommended Use

Use this dataset to demonstrate:

- dataset construction,
- bilingual evaluation,
- simple baseline implementation,
- generalization testing with a challenge set,
- error analysis,
- honest limitation writing.
