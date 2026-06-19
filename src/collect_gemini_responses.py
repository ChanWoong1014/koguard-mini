"""Collect one local Gemini response set for the response-level safety pilot."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from collect_openai_responses import (
    api_key_from_environment,
    ensure_safe_output_path,
    load_rows,
    pending_row_indexes,
    write_rows,
)


GEMINI_ENDPOINT_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def normalize_model_id(model: str) -> str:
    return model.strip().removeprefix("models/")


def extract_output_text(payload: dict[str, Any]) -> str:
    """Return text output, or a reviewable marker when Gemini returned no text."""
    text_parts: list[str] = []
    for candidate in payload.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        content = candidate.get("content", {})
        if not isinstance(content, dict):
            continue
        for part in content.get("parts", []):
            if isinstance(part, dict) and isinstance(part.get("text"), str) and part["text"].strip():
                text_parts.append(part["text"].strip())
        if text_parts:
            return "\n".join(text_parts)

    finish_reasons = [
        str(candidate.get("finishReason", "unknown"))
        for candidate in payload.get("candidates", [])
        if isinstance(candidate, dict)
    ]
    feedback = payload.get("promptFeedback", {})
    block_reason = feedback.get("blockReason", "") if isinstance(feedback, dict) else ""
    return "[NO_TEXT_RESPONSE: finish_reason=" + ",".join(finish_reasons or ["none"]) + f"; block_reason={block_reason or 'none'}]"


def request_response(api_key: str, model: str, prompt: str, timeout_seconds: int) -> str:
    normalized_model = normalize_model_id(model)
    if not normalized_model:
        raise ValueError("--model cannot be empty.")

    endpoint = GEMINI_ENDPOINT_TEMPLATE.format(model=quote(normalized_model, safe="-._"))
    body = json.dumps({"contents": [{"role": "user", "parts": [{"text": prompt}]}]}).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return extract_output_text(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect local response-level evaluation data through the Gemini API.")
    parser.add_argument("--input", required=True, help="Pilot CSV created by prepare_response_pilot.py")
    parser.add_argument("--output", required=True, help="Local output under data/response_evaluations/")
    parser.add_argument("--model", required=True, help="Exact Gemini model ID returned by list_gemini_models.py")
    parser.add_argument("--env-file", default=".env", help="Local .env file that stores GEMINI_API_KEY")
    parser.add_argument("--api-key-env", default="GEMINI_API_KEY", help="Environment variable name for the API key")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--limit", type=int, help="Optional number of currently empty rows to collect")
    parser.add_argument("--max-requests", type=int, default=0, help="Must be at least the planned request count")
    parser.add_argument("--confirm-model-calls", action="store_true", help="Required before model calls are sent")
    parser.add_argument("--dry-run", action="store_true", help="Show the planned request count without calling Gemini")
    args = parser.parse_args()

    output_path = Path(args.output)
    ensure_safe_output_path(output_path)
    rows = load_rows(output_path if output_path.exists() else Path(args.input))
    pending_indexes = pending_row_indexes(rows)
    if args.limit is not None:
        if args.limit < 1:
            raise SystemExit("--limit must be at least 1 when provided.")
        pending_indexes = pending_indexes[: args.limit]

    print(f"Model: {normalize_model_id(args.model)}")
    print(f"Rows already collected: {len(rows) - len(pending_row_indexes(rows))}")
    print(f"Requests planned: {len(pending_indexes)}")

    if args.dry_run:
        print("Dry run only. No Gemini API request was sent.")
        return
    if not args.confirm_model_calls:
        raise SystemExit("Add --confirm-model-calls only after checking the model and request count.")
    if not pending_indexes:
        print("No empty response rows remain. Nothing to collect.")
        return
    if args.max_requests < len(pending_indexes):
        raise SystemExit(
            f"--max-requests ({args.max_requests}) is lower than the planned request count ({len(pending_indexes)})."
        )

    api_key = api_key_from_environment(args.api_key_env, Path(args.env_file))
    for position, row_index in enumerate(pending_indexes, start=1):
        row = rows[row_index]
        try:
            response_text = request_response(api_key, args.model, row["prompt_text"], args.timeout_seconds)
        except HTTPError as exc:
            raise SystemExit(f"Gemini API request failed with HTTP {exc.code} at prompt_id={row['prompt_id']}.") from exc
        except URLError as exc:
            raise SystemExit(f"Gemini network request failed at prompt_id={row['prompt_id']}: {exc.reason}") from exc

        row["model_name"] = normalize_model_id(args.model)
        row["response_text"] = response_text
        row["response_label"] = ""
        row["rationale"] = ""
        row["redacted"] = "no"
        row["notes"] = (
            "Collected through the Gemini generateContent API at "
            f"{datetime.now(UTC).isoformat()}. Label locally before reporting."
        )
        write_rows(output_path, rows)
        print(f"Collected {position}/{len(pending_indexes)}: prompt_id={row['prompt_id']}")

    print(f"Completed raw Gemini response collection: {output_path}")
    print("Next: label response_label and rationale, then run evaluate_response_level.py.")


if __name__ == "__main__":
    main()
