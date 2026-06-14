from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from coglang.parser import canonicalize, parse
from coglang.preflight import preflight_expression
from coglang.schema_versions import (
    PYTHON_SCHEMA_SIDECAR_DEMO_SCHEMA_VERSION,
    PYTHON_SCHEMA_SIDECAR_RECORD_DEMO_SCHEMA_VERSION,
)
from coglang.validator import valid_coglang


SUMMARY_SCHEMA_VERSION = PYTHON_SCHEMA_SIDECAR_DEMO_SCHEMA_VERSION
AUDIT_RECORD_SCHEMA_VERSION = PYTHON_SCHEMA_SIDECAR_RECORD_DEMO_SCHEMA_VERSION
EVENT_SCHEMA_VERSION = "generated-expression-event/v0.1"

EVENT_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "CogLang generated expression event demo",
    "type": "object",
    "additionalProperties": True,
    "required": [
        "event_id",
        "source_system",
        "schema_version",
        "generated_expression",
        "enabled_capabilities",
    ],
    "properties": {
        "event_id": {"type": "string", "minLength": 1},
        "source_system": {"type": "string", "minLength": 1},
        "schema_version": {"const": EVENT_SCHEMA_VERSION},
        "generated_expression": {"type": "string", "minLength": 1},
        "enabled_capabilities": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
        "generator": {"type": "object"},
        "runtime": {"type": "object"},
        "correlation_id": {"type": "string"},
    },
}


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise TypeError(f"event line {line_number} must be a JSON object")
        records.append(record)
    return records


def _stdlib_validate_event(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in EVENT_JSON_SCHEMA["required"]:
        if key not in record:
            errors.append(f"missing required field: {key}")

    string_fields = ("event_id", "source_system", "schema_version", "generated_expression")
    for key in string_fields:
        if key in record and not isinstance(record[key], str):
            errors.append(f"{key} must be a string")
        elif key in record and not record[key].strip():
            errors.append(f"{key} must be non-empty")

    if record.get("schema_version") != EVENT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {EVENT_SCHEMA_VERSION}")

    capabilities = record.get("enabled_capabilities")
    if not isinstance(capabilities, list):
        errors.append("enabled_capabilities must be a list")
    elif not all(isinstance(item, str) and item for item in capabilities):
        errors.append("enabled_capabilities entries must be non-empty strings")

    for key in ("generator", "runtime"):
        if key in record and not isinstance(record[key], dict):
            errors.append(f"{key} must be an object")

    if "correlation_id" in record and not isinstance(record["correlation_id"], str):
        errors.append("correlation_id must be a string")

    return errors


def _pydantic_validate_event(record: dict[str, Any]) -> list[str]:
    try:
        from pydantic import BaseModel, ConfigDict, Field, ValidationError
    except ImportError as exc:  # pragma: no cover - optional dependency path
        raise RuntimeError("pydantic is not installed; use --validator stdlib") from exc

    class GeneratedExpressionEvent(BaseModel):
        model_config = ConfigDict(extra="allow")

        event_id: str = Field(min_length=1)
        source_system: str = Field(min_length=1)
        schema_version: str
        generated_expression: str = Field(min_length=1)
        enabled_capabilities: list[str]
        generator: dict[str, Any] = Field(default_factory=dict)
        runtime: dict[str, Any] = Field(default_factory=dict)
        correlation_id: str | None = None

    try:
        event = GeneratedExpressionEvent.model_validate(record)
    except ValidationError as exc:  # pragma: no cover - optional dependency path
        return [str(error) for error in exc.errors()]
    if event.schema_version != EVENT_SCHEMA_VERSION:
        return [f"schema_version must be {EVENT_SCHEMA_VERSION}"]
    return []


_FASTJSONSCHEMA_VALIDATOR: Any | None = None


def _fastjsonschema_validate_event(record: dict[str, Any]) -> list[str]:
    global _FASTJSONSCHEMA_VALIDATOR
    try:
        import fastjsonschema
    except ImportError as exc:  # pragma: no cover - optional dependency path
        raise RuntimeError("fastjsonschema is not installed; use --validator stdlib") from exc

    if _FASTJSONSCHEMA_VALIDATOR is None:
        _FASTJSONSCHEMA_VALIDATOR = fastjsonschema.compile(EVENT_JSON_SCHEMA)
    try:
        _FASTJSONSCHEMA_VALIDATOR(record)
    except Exception as exc:  # pragma: no cover - optional dependency path
        return [str(exc)]
    return []


def _validate_event(record: dict[str, Any], validator: str) -> dict[str, Any]:
    if validator == "stdlib":
        errors = _stdlib_validate_event(record)
        identity = "stdlib-demo-shape-check/v0.1"
    elif validator == "pydantic":
        errors = _pydantic_validate_event(record)
        identity = "pydantic-sidecar-optional"
    elif validator == "fastjsonschema":
        errors = _fastjsonschema_validate_event(record)
        identity = "fastjsonschema-sidecar-optional"
    else:
        raise ValueError(f"unsupported validator: {validator}")

    return {
        "strategy": validator,
        "identity": identity,
        "schema_version": EVENT_SCHEMA_VERSION,
        "ok": not errors,
        "errors": errors,
    }


def _audit_action(decision: str, envelope_ok: bool, parse_ok: bool, validate_ok: bool) -> str:
    if not envelope_ok or not parse_ok or not validate_ok or decision == "rejected":
        return "reject"
    if decision in {"requires_review", "cannot_estimate"}:
        return "queue_review"
    return "allow"


def _review_reason(
    adapter_validation: dict[str, Any],
    decision_payload: dict[str, Any] | None,
    action: str,
    parse_ok: bool,
    validate_ok: bool,
) -> str:
    if not adapter_validation["ok"]:
        return "Generated-event envelope failed sidecar schema validation"
    if not parse_ok:
        return "Generated expression did not parse as a CogLang expression"
    if not validate_ok:
        return "Generated expression parsed but failed CogLang validation"
    if action == "allow":
        return "CogLang preflight accepted before host execution"
    if action == "queue_review":
        return "CogLang preflight requires human or host policy review"
    reasons = (decision_payload or {}).get("reasons", [])
    return ", ".join(str(reason) for reason in reasons) or "CogLang preflight rejected"


def _empty_preflight() -> dict[str, Any]:
    return {
        "schema_version": None,
        "decision": "rejected",
        "required_review": False,
        "reasons": ["adapter.invalid_envelope"],
        "effects": [],
        "required_capabilities": [],
        "possible_errors": ["AdapterValidationError"],
    }


def _audit_record(record: dict[str, Any], validator: str) -> dict[str, Any]:
    event_id = str(record.get("event_id", "unknown-event"))
    correlation_id = str(record.get("correlation_id", event_id))
    adapter_validation = _validate_event(record, validator)
    expression_source = (
        str(record["generated_expression"])
        if adapter_validation["ok"]
        else None
    )

    expr = parse(expression_source) if expression_source is not None else None
    parse_ok = bool(expr is not None and expr.head != "ParseError")
    validate_ok = bool(parse_ok and valid_coglang(expr))
    canonical_expression = canonicalize(expr) if parse_ok and expr is not None else None

    decision_payload: dict[str, Any] | None = None
    effect_summary: dict[str, Any] = {}
    if expr is not None:
        decision = preflight_expression(
            expr,
            correlation_id=correlation_id,
            enabled_capabilities=[
                str(item) for item in record.get("enabled_capabilities", [])
            ],
            require_review_for_writes=True,
        )
        decision_payload = decision.to_dict()
        effect_summary = decision_payload.get("effect_summary") or {}
        preflight_payload = {
            "schema_version": decision_payload["schema_version"],
            "decision": decision_payload["decision"],
            "required_review": decision_payload["required_review"],
            "reasons": decision_payload["reasons"],
            "effects": effect_summary.get("effects", []),
            "required_capabilities": effect_summary.get("required_capabilities", []),
            "possible_errors": decision_payload["possible_errors"],
        }
    else:
        preflight_payload = _empty_preflight()

    action = _audit_action(
        str(preflight_payload["decision"]),
        bool(adapter_validation["ok"]),
        parse_ok,
        validate_ok,
    )

    return {
        "schema_version": AUDIT_RECORD_SCHEMA_VERSION,
        "event_id": event_id,
        "source_system": str(record.get("source_system", "unknown")),
        "correlation_id": correlation_id,
        "adapter_validation": adapter_validation,
        "generator": dict(record.get("generator", {}))
        if isinstance(record.get("generator", {}), dict)
        else {},
        "runtime": dict(record.get("runtime", {}))
        if isinstance(record.get("runtime", {}), dict)
        else {},
        "generated_expression": expression_source,
        "parse": {
            "ok": parse_ok,
            "head": None if expr is None else expr.head,
        },
        "validation": {
            "ok": validate_ok,
        },
        "canonical_expression": canonical_expression,
        "expression_hash": effect_summary.get("expression_hash"),
        "preflight": preflight_payload,
        "audit_action": action,
        "human_review": {
            "required": action == "queue_review",
            "reason": _review_reason(
                adapter_validation,
                decision_payload,
                action,
                parse_ok,
                validate_ok,
            ),
        },
        "sidecar_boundary": {
            "example_kind": "companion-python-schema-sidecar",
            "stable_protocol": False,
            "pydantic_core_dependency": False,
            "fastjsonschema_core_dependency": False,
            "optional_validator_dependency": validator in {"pydantic", "fastjsonschema"},
            "host_executed": False,
            "hrc_contract_expanded": False,
        },
    }


def write_audit_records(
    events_path: Path,
    output_path: Path,
    *,
    validator: str = "stdlib",
) -> dict[str, Any]:
    events = _load_jsonl(events_path)
    audit_records = [_audit_record(record, validator) for record in events]
    output_path.write_text(
        "\n".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True)
            for record in audit_records
        )
        + "\n",
        encoding="utf-8",
    )
    envelope_counts = Counter(
        "envelope_ok" if record["adapter_validation"]["ok"] else "envelope_error"
        for record in audit_records
    )
    parse_counts = Counter(
        "parse_ok" if record["parse"]["ok"] else "parse_error"
        for record in audit_records
        if record["adapter_validation"]["ok"]
    )
    if any(not record["adapter_validation"]["ok"] for record in audit_records):
        parse_counts["parse_not_attempted"] += sum(
            1 for record in audit_records if not record["adapter_validation"]["ok"]
        )
    validation_counts = Counter(
        "validate_ok" if record["validation"]["ok"] else "validate_error"
        for record in audit_records
        if record["adapter_validation"]["ok"]
    )
    if any(not record["adapter_validation"]["ok"] for record in audit_records):
        validation_counts["validate_not_attempted"] += sum(
            1 for record in audit_records if not record["adapter_validation"]["ok"]
        )
    decision_counts = Counter(
        str(record["preflight"]["decision"]) for record in audit_records
    )
    action_counts = Counter(str(record["audit_action"]) for record in audit_records)
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "tool": "coglang-python-schema-sidecar-demo",
        "ok": True,
        "example_kind": "companion-python-schema-sidecar",
        "stable_protocol": False,
        "pydantic_core_dependency": False,
        "fastjsonschema_core_dependency": False,
        "validator_strategy": validator,
        "input_path": str(events_path),
        "output_path": str(output_path),
        "event_count": len(events),
        "audit_record_count": len(audit_records),
        "envelope_counts": dict(sorted(envelope_counts.items())),
        "parse_counts": dict(sorted(parse_counts.items())),
        "validation_counts": dict(sorted(validation_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "audit_action_counts": dict(sorted(action_counts.items())),
        "checks": [
            "jsonl-generated-expression-event-input",
            "sidecar-envelope-validation",
            "coglang-parse-validate-preflight",
            "python-schema-sidecar-audit-jsonl-output",
            "companion-boundary-no-core-validator-dependency",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate generated CogLang-expression events through a Python schema sidecar.",
    )
    parser.add_argument("events_jsonl")
    parser.add_argument("audit_jsonl")
    parser.add_argument(
        "--validator",
        choices=("stdlib", "pydantic", "fastjsonschema"),
        default="stdlib",
        help="Sidecar envelope validator strategy. Optional third-party strategies require their packages.",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    try:
        payload = write_audit_records(
            Path(args.events_jsonl),
            Path(args.audit_jsonl),
            validator=args.validator,
        )
    except Exception as exc:
        print(f"python_schema_sidecar.py: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
