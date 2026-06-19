# Data

This folder contains safe template data only.

For a real portfolio experiment, create a private CSV file using the same schema as `prompts_template.csv`.

Recommended public-safe workflow:

1. Keep raw harmful benchmark data out of the public repository.
2. Store private raw data under `data/private/`, which is ignored by git.
3. Publish only aggregate statistics, redacted prompt examples, and non-actionable error analysis.
4. Make clear in the report that the project evaluates safety behavior and does not provide instructions for harmful activity.
