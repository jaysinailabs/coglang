from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .generation_eval import (
    GenerationEvalCase,
    load_generation_eval_fixture,
)
from .schema_versions import (
    GENERATION_EVAL_FIXTURE_SCHEMA_VERSION,
    GENERATION_EVAL_REQUEST_BATCH_SCHEMA_VERSION,
    GENERATION_EVAL_REQUEST_SCHEMA_VERSION,
    GENERATION_EVAL_RESPONSE_BATCH_SCHEMA_VERSION,
    GENERATION_EVAL_RESPONSE_SCHEMA_VERSION,
)

GENERATION_EVAL_OUTPUT_INSTRUCTIONS = (
    "Return exactly one CogLang M-expression as the output for this case. "
    "Do not include Markdown fences, prose, or multiple alternatives."
)


def generation_eval_request_batch_payload(
    *,
    fixture_path: str | Path | None = None,
    include_reference: bool = False,
) -> dict[str, Any]:
    """Build provider-neutral prompt records for an external LLM runner.

    This is an offline adapter boundary. It prepares request records but does
    not call a model provider or import any provider SDK.
    """

    fixture = load_generation_eval_fixture(fixture_path)
    cases = [GenerationEvalCase.from_dict(dict(item)) for item in fixture["cases"]]
    requests: list[dict[str, Any]] = []
    for case in cases:
        request = {
            "schema_version": GENERATION_EVAL_REQUEST_SCHEMA_VERSION,
            "case_id": case.case_id,
            "level": case.level,
            "prompt": case.prompt,
            "instructions": GENERATION_EVAL_OUTPUT_INSTRUCTIONS,
            "expected_top_level_heads": list(case.expected_top_level_heads),
        }
        if include_reference:
            request["reference_expr"] = case.reference_expr
        requests.append(request)

    return {
        "schema_version": GENERATION_EVAL_REQUEST_BATCH_SCHEMA_VERSION,
        "tool": "coglang",
        "fixture_schema_version": GENERATION_EVAL_FIXTURE_SCHEMA_VERSION,
        "fixture_path": fixture["path"],
        "case_count": len(requests),
        "include_reference": include_reference,
        "response_schema_version": GENERATION_EVAL_RESPONSE_BATCH_SCHEMA_VERSION,
        "request_record_schema_version": GENERATION_EVAL_REQUEST_SCHEMA_VERSION,
        "response_record_schema_version": GENERATION_EVAL_RESPONSE_SCHEMA_VERSION,
        "response_contract": {
            "format": "json_or_jsonl",
            "required_fields": ["schema_version", "case_id"],
            "optional_fields": ["model", "provider", "latency_ms", "raw_response_id"],
            "preferred_output_field": "output",
            "accepted_output_fields": ["output", "text", "completion"],
            "output_instructions": GENERATION_EVAL_OUTPUT_INSTRUCTIONS,
        },
        "requests": requests,
    }


def generation_eval_request_jsonl(
    *,
    fixture_path: str | Path | None = None,
    include_reference: bool = False,
) -> str:
    payload = generation_eval_request_batch_payload(
        fixture_path=fixture_path,
        include_reference=include_reference,
    )
    return "\n".join(
        json.dumps(request, ensure_ascii=False, sort_keys=True)
        for request in payload["requests"]
    )


def load_generation_eval_response_answers(path: str | Path) -> dict[str, str]:
    """Load model responses in JSON or JSONL form and return scorer answers."""

    records = _load_response_records(Path(path))
    answers: dict[str, str] = {}
    for record in records:
        if not isinstance(record, dict):
            raise TypeError("generation eval response entries must be objects")
        _validate_response_schema_version(record)
        case_id = str(record["case_id"])
        output = _response_output(record)
        answers[case_id] = output
    return answers


def generation_eval_response_answers_payload(path: str | Path) -> dict[str, Any]:
    answers = load_generation_eval_response_answers(path)
    return {
        "schema_version": GENERATION_EVAL_RESPONSE_BATCH_SCHEMA_VERSION,
        "tool": "coglang",
        "source_path": str(path),
        "answer_count": len(answers),
        "answers": [
            {
                "schema_version": GENERATION_EVAL_RESPONSE_SCHEMA_VERSION,
                "case_id": case_id,
                "output": output,
            }
            for case_id, output in sorted(answers.items())
        ],
    }


def _load_response_records(path: Path) -> list[Any]:
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return []
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        return [
            json.loads(line)
            for line in text.splitlines()
            if line.strip()
        ]
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "case_id" in data and any(key in data for key in ("output", "text", "completion")):
            return [data]
        if "responses" in data:
            raw_records = data["responses"]
        elif "answers" in data:
            raw_records = data["answers"]
        else:
            raise TypeError(
                "generation eval response batch must contain a responses list"
            )
        if not isinstance(raw_records, list):
            raise TypeError("generation eval response batch must contain a responses list")
        return raw_records
    raise TypeError("generation eval responses must be JSON object, list, or JSONL")


def _validate_response_schema_version(record: dict[str, Any]) -> None:
    schema_version = record.get("schema_version")
    if schema_version is None:
        return
    if schema_version != GENERATION_EVAL_RESPONSE_SCHEMA_VERSION:
        raise ValueError(
            "generation eval response entry schema_version must be "
            f"{GENERATION_EVAL_RESPONSE_SCHEMA_VERSION}"
        )


def _response_output(record: dict[str, Any]) -> str:
    for key in ("output", "text", "completion"):
        value = record.get(key)
        if value is not None:
            return str(value)
    raise KeyError("generation eval response entry missing output/text/completion")
