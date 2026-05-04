from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "coglang-generation-eval-offline-runner-demo/v0.1"
RESPONSE_SCHEMA_VERSION = "coglang-generation-eval-response/v0.1"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise TypeError(f"request line {line_number} must be a JSON object")
        records.append(record)
    return records


def _response_for_request(record: dict[str, Any]) -> dict[str, str]:
    if "reference_expr" not in record:
        raise KeyError(
            "mock_responses.py requires request records exported with --include-reference"
        )
    return {
        "schema_version": RESPONSE_SCHEMA_VERSION,
        "case_id": str(record["case_id"]),
        "output": str(record["reference_expr"]),
    }


def write_mock_responses(requests_path: Path, responses_path: Path) -> dict[str, Any]:
    requests = _load_jsonl(requests_path)
    responses = [_response_for_request(record) for record in requests]
    responses_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in responses) + "\n",
        encoding="utf-8",
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": "coglang-generation-eval-offline-runner-demo",
        "ok": True,
        "request_path": str(requests_path),
        "response_path": str(responses_path),
        "request_count": len(requests),
        "response_count": len(responses),
        "checks": [
            "jsonl-request-input",
            "reference-expression-present",
            "jsonl-response-output",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print(
            "usage: mock_responses.py REQUESTS_JSONL RESPONSES_JSONL",
            file=sys.stderr,
        )
        return 2
    payload = write_mock_responses(Path(args[0]), Path(args[1]))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
