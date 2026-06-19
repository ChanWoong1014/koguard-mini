"""List Gemini models that advertise generateContent support for the current API key."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from collect_openai_responses import api_key_from_environment


MODELS_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"


def available_model_rows(payload: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for model in payload.get("models", []):
        if not isinstance(model, dict):
            continue
        methods = model.get("supportedGenerationMethods", [])
        if "generateContent" not in methods:
            continue
        name = str(model.get("name", "")).removeprefix("models/")
        if not name:
            continue
        rows.append(
            {
                "model_id": name,
                "display_name": str(model.get("displayName", "")),
                "description": str(model.get("description", "")),
            }
        )
    return sorted(rows, key=lambda row: row["model_id"])


def fetch_models(api_key: str, timeout_seconds: int) -> dict[str, Any]:
    request = Request(MODELS_ENDPOINT, headers={"x-goog-api-key": api_key}, method="GET")
    with urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="List Gemini generateContent model IDs available to the current API key.")
    parser.add_argument("--env-file", default=".env", help="Local .env file with GEMINI_API_KEY")
    parser.add_argument("--api-key-env", default="GEMINI_API_KEY", help="Environment variable name for the API key")
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument("--flash-only", action="store_true", help="Show only available model IDs containing 'flash'")
    args = parser.parse_args()

    api_key = api_key_from_environment(args.api_key_env, Path(args.env_file))
    try:
        rows = available_model_rows(fetch_models(api_key, args.timeout_seconds))
    except HTTPError as exc:
        raise SystemExit(f"Gemini model listing failed with HTTP {exc.code}.") from exc
    except URLError as exc:
        raise SystemExit(f"Gemini model listing network failure: {exc.reason}") from exc

    if args.flash_only:
        rows = [row for row in rows if "flash" in row["model_id"].lower()]

    if not rows:
        raise SystemExit("No matching Gemini generateContent models were returned for this API key.")

    for row in rows:
        print(f"{row['model_id']}\t{row['display_name']}")


if __name__ == "__main__":
    main()
