$ErrorActionPreference = "Stop"

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}

if (-not $python) {
    throw "Python was not found. Install Python or add it to PATH, then run this script again."
}

& $python.Source src\build_extended_dataset.py --output data\prompts_extended.csv
& $python.Source src\build_challenge_dataset.py --output data\prompts_challenge.csv
& $python.Source src\run_pipeline.py --input data\prompts_extended.csv --challenge-input data\prompts_challenge.csv --reports-dir reports
& $python.Source -m unittest discover tests
