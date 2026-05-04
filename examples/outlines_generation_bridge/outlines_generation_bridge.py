from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from coglang.parser import canonicalize, parse
from coglang.preflight import preflight_expression
from coglang.schema_versions import (
    OUTLINES_GENERATION_BRIDGE_DEMO_SCHEMA_VERSION,
    OUTLINES_GENERATION_BRIDGE_RECORD_DEMO_SCHEMA_VERSION,
)
from coglang.validator import valid_coglang


SUMMARY_SCHEMA_VERSION = OUTLINES_GENERATION_BRIDGE_DEMO_SCHEMA_VERSION
AUDIT_RECORD_SCHEMA_VERSION = OUTLINES_GENERATION_BRIDGE_RECORD_DEMO_SCHEMA_VERSION


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise TypeError(f"generation line {line_number} must be a JSON object")
        records.append(record)
    return records


def _audit_action(decision: str, parse_ok: bool, validate_ok: bool) -> str:
    if not parse_ok or not validate_ok or decision == "rejected":
        return "reject"
    if decision in {"requires_review", "cannot_estimate"}:
        return "queue_review"
    return "allow"


def _review_reason(
    decision_payload: dict[str, Any],
    action: str,
    parse_ok: bool,
    validate_ok: bool,
) -> str:
    if not parse_ok:
        return "Generated text did not parse as a CogLang expression"
    if not validate_ok:
        return "Generated expression parsed but failed CogLang validation"
    if action == "allow":
        return "CogLang preflight accepted before host execution"
    if action == "queue_review":
        return "CogLang preflight requires human review before host execution"
    reasons = decision_payload.get("reasons", [])
    return ", ".join(str(reason) for reason in reasons) or "CogLang preflight rejected"


def _audit_record(record: dict[str, Any]) -> dict[str, Any]:
    event_id = str(record["event_id"])
    correlation_id = str(record.get("correlation_id", event_id))
    generated_expression = str(record["generated_expression"])
    enabled_capabilities = [str(item) for item in record.get("enabled_capabilities", [])]

    expr = parse(generated_expression)
    parse_ok = expr.head != "ParseError"
    validate_ok = bool(parse_ok and valid_coglang(expr))
    canonical_expression = canonicalize(expr) if parse_ok else None
    decision = preflight_expression(
        expr,
        correlation_id=correlation_id,
        enabled_capabilities=enabled_capabilities,
        require_review_for_writes=True,
    )
    decision_payload = decision.to_dict()
    effect_summary = decision_payload.get("effect_summary") or {}
    action = _audit_action(str(decision_payload["decision"]), parse_ok, validate_ok)

    return {
        "schema_version": AUDIT_RECORD_SCHEMA_VERSION,
        "event_id": event_id,
        "case_id": str(record.get("case_id", event_id)),
        "source_system": str(record.get("source_system", "outlines-style-fixture")),
        "event_kind": "external.constrained_generation.coglang_expression",
        "correlation_id": correlation_id,
        "decoder": str(record.get("decoder", "outlines-style-constrained-generation")),
        "grammar": {
            "name": str(record.get("grammar_name", "")),
            "version": str(record.get("grammar_version", "")),
            "authoritative": False,
        },
        "prompt": str(record.get("prompt", "")),
        "generated_expression": generated_expression,
        "parse": {
            "ok": parse_ok,
            "head": str(expr.head),
        },
        "validation": {
            "ok": validate_ok,
            "validator": "coglang.validator.valid_coglang",
        },
        "canonical_expression": canonical_expression,
        "expression_hash": effect_summary.get("expression_hash"),
        "preflight": {
            "schema_version": decision_payload["schema_version"],
            "decision": decision_payload["decision"],
            "required_review": decision_payload["required_review"],
            "reasons": decision_payload["reasons"],
            "effects": effect_summary.get("effects", []),
            "required_capabilities": effect_summary.get("required_capabilities", []),
            "possible_errors": decision_payload["possible_errors"],
        },
        "audit_action": action,
        "human_review": {
            "required": action == "queue_review",
            "reason": _review_reason(decision_payload, action, parse_ok, validate_ok),
        },
        "bridge_boundary": {
            "example_kind": "companion-outlines-generation-bridge",
            "stable_protocol": False,
            "official_outlines_integration": False,
            "outlines_dependency": False,
            "outlines_executed": False,
            "model_executed": False,
            "host_executed": False,
            "transport_envelope": False,
            "hrc_contract_expanded": False,
        },
    }


def write_audit_records(events_path: Path, output_path: Path) -> dict[str, Any]:
    events = _load_jsonl(events_path)
    audit_records = [_audit_record(record) for record in events]
    output_path.write_text(
        "\n".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True)
            for record in audit_records
        )
        + "\n",
        encoding="utf-8",
    )
    decision_counts = Counter(
        str(record["preflight"]["decision"]) for record in audit_records
    )
    action_counts = Counter(str(record["audit_action"]) for record in audit_records)
    parse_counts = Counter(
        "parse_ok" if record["parse"]["ok"] else "parse_error"
        for record in audit_records
    )
    validation_counts = Counter(
        "validate_ok" if record["validation"]["ok"] else "validate_error"
        for record in audit_records
    )
    decoder_counts = Counter(str(record["decoder"]) for record in audit_records)

    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "tool": "coglang-outlines-generation-bridge-demo",
        "ok": True,
        "example_kind": "companion-outlines-generation-bridge",
        "stable_protocol": False,
        "official_outlines_integration": False,
        "outlines_dependency": False,
        "outlines_executed": False,
        "model_executed": False,
        "host_executed": False,
        "hrc_contract_expanded": False,
        "input_path": str(events_path),
        "output_path": str(output_path),
        "event_count": len(events),
        "audit_record_count": len(audit_records),
        "decoder_counts": dict(sorted(decoder_counts.items())),
        "parse_counts": dict(sorted(parse_counts.items())),
        "validation_counts": dict(sorted(validation_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "audit_action_counts": dict(sorted(action_counts.items())),
        "checks": [
            "jsonl-outlines-style-generation-output-input",
            "generated-expression-parse-validate-preflight",
            "coglang-audit-jsonl-output",
            "companion-boundary-no-outlines-dependency",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print(
            "usage: outlines_generation_bridge.py GENERATED_EXPRESSIONS_JSONL AUDIT_JSONL",
            file=sys.stderr,
        )
        return 2
    try:
        payload = write_audit_records(Path(args[0]), Path(args[1]))
    except Exception as exc:
        print(f"outlines_generation_bridge.py: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
