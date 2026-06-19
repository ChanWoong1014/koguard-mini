"""Collect one reproducible set of OpenAI Responses API outputs for a local pilot CSV.

The script deliberately requires two explicit cost guards before it sends API
requests. It stores raw outputs only in the caller-provided local CSV, which
should remain below data/response_evaluations/ and therefore outside Git.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from prepare_response_pilot import RESPONSE_COLUMNS


DEFAULT_ENDPOINT = "https://api.openai.com/v1/responses"


def load_dotenv(path: Path) -> None:
    """Load only missing environment variables from a small KEY=VALUE .env file."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        missing = [column for column in RESPONSE_COLUMNS if column not in columns]
        if missing:
            raise ValueError(f"Input CSV is missing required columns: {', '.join(missing)}")
        return list(reader)


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESPONSE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def extract_output_text(payload: dict[str, Any]) -> str:
    """Read text from either a convenience field or the structured response output."""
    convenience_text = payload.get("output_text")
    if isinstance(convenience_text, str) and convenience_text.strip():
        return convenience_text.strip()

    text_parts: list[str] = []
    for output_item in payload.get("output", []):
        if not isinstance(output_item, dict):
            continue
        for content in output_item.get("content", []):
            if not isinstance(content, dict):
                continue
            text = content.get("text")
            if isinstance(text, str) and text.strip():
                text_parts.append(text.strip())
    if text_parts:
        return "\n".join(text_parts)
    raise ValueError("The API response did not contain readable output text.")


def request_response(api_key: str, model: str, prompt: str, endpoint: str, timeout_seconds: int) -> str:
    body = json.dumps({"model": model, "input": prompt}).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return extract_output_text(payload)


def pending_row_indexes(rows: list[dict[str, str]]) -> list[int]:
    return [index for index, row in enumerate(rows) if not row["response_text"].strip()]


def ensure_safe_output_path(path: Path) -> None:
    if "response_evaluations" not in {part.lower() for part in path.parts}:
        raise ValueError("--output must be inside data/response_evaluations/ so raw responses stay out of Git.")


def api_key_from_environment(env_name: str, env_file: Path) -> str:
    load_dotenv(env_file)
    api_key = os.environ.get(env_name, "").strip()
    if not api_key or api_key == "replace_with_your_api_key":
        raise ValueError(
            f"{env_name} is missing. Put it in {env_file} or set it as an environment variable. Do not pass it on the command line."
        )
    return api_key


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect local response-level evaluation data through the OpenAI Responses API.")
    parser.add_argument("--input", required=True, help="Pilot CSV created by prepare_response_pilot.py")
    parser.add_argument("--output", required=True, help="Local output under data/response_evaluations/")
    parser.add_argument("--model", required=True, help="Exact OpenAI model ID chosen for this experiment")
    parser.add_argument("--env-file", default=".env", help="Local .env file that stores OPENAI_API_KEY")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY", help="Environment variable name for the API key")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Responses API endpoint")
    parser.add_argument("--timeout-seconds", type=int, default=60, help="Timeout for one API request")
    parser.add_argument("--limit", type=int, help="Optional number of currently empty rows to collect")
    parser.add_argument(
        "--max-requests",
        type=int,
        default=0,
        help="Safety guard. Must be at least the number of requests that will be sent.",
    )
    parser.add_argument(
        "--confirm-model-calls",
        action="store_true",
        help="Required explicit confirmation before the script can make paid model calls.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show the planned request count without calling the API")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    ensure_safe_output_path(output_path)

    rows = load_rows(output_path if output_path.exists() else input_path)
    pending_indexes = pending_row_indexes(rows)
    if args.limit is not None:
        if args.limit < 1:
            raise SystemExit("--limit must be at least 1 when provided.")
        pending_indexes = pending_indexes[: args.limit]

    print(f"Model: {args.model}")
    print(f"Rows already collected: {len(rows) - len(pending_row_indexes(rows))}")
    print(f"Requests planned: {len(pending_indexes)}")

    if args.dry_run:
        print("Dry run only. No API request was sent.")
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
            response_text = request_response(
                api_key=api_key,
                model=args.model,
                prompt=row["prompt_text"],
                endpoint=args.endpoint,
                timeout_seconds=args.timeout_seconds,
            )
        except HTTPError as exc:
            raise SystemExit(f"API request failed with HTTP {exc.code} at prompt_id={row['prompt_id']}.") from exc
        except URLError as exc:
            raise SystemExit(f"Network request failed at prompt_id={row['prompt_id']}: {exc.reason}") from exc

        row["model_name"] = args.model
        row["response_text"] = response_text
        row["response_label"] = ""
        row["rationale"] = ""
        row["redacted"] = "no"
        row["notes"] = (
            "Collected through the OpenAI Responses API at "
            f"{datetime.now(UTC).isoformat()}. Label locally before reporting."
        )
        write_rows(output_path, rows)
        print(f"Collected {position}/{len(pending_indexes)}: prompt_id={row['prompt_id']}")

    print(f"Completed raw response collection: {output_path}")
    print("Next: label response_label and rationale, then run evaluate_response_level.py.")


if __name__ == "__main__":
    main()
