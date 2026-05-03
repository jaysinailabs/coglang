from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from coglang.parser import canonicalize, parse
from coglang.preflight import preflight_expression
from coglang.schema_versions import (
    SEMANTIC_EVENT_AUDIT_DEMO_SCHEMA_VERSION,
    SEMANTIC_EVENT_AUDIT_RECORD_DEMO_SCHEMA_VERSION,
)


SUMMARY_SCHEMA_VERSION = SEMANTIC_EVENT_AUDIT_DEMO_SCHEMA_VERSION
AUDIT_RECORD_SCHEMA_VERSION = SEMANTIC_EVENT_AUDIT_RECORD_DEMO_SCHEMA_VERSION


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


def _audit_action(decision: str) -> str:
    if decision in {"accepted", "accepted_with_warnings"}:
        return "allow"
    if decision in {"requires_review", "cannot_estimate"}:
        return "queue_review"
    return "reject"


def _review_reason(decision_payload: dict[str, Any], action: str) -> str:
    if action == "allow":
        return "preflight accepted before host execution"
    if action == "queue_review":
        return "preflight requires human or host policy review"
    reasons = decision_payload.get("reasons", [])
    return ", ".join(str(reason) for reason in reasons) or "preflight rejected"


def _audit_record(record: dict[str, Any]) -> dict[str, Any]:
    event_id = str(record["event_id"])
    expression_source = str(record["expression"])
    correlation_id = str(record.get("correlation_id", event_id))
    enabled_capabilities = [str(item) for item in record.get("enabled_capabilities", [])]
    require_review_for_writes = bool(record.get("require_review_for_writes", True))
    expr = parse(expression_source)
    canonical_expression = None if expr.head == "ParseError" else canonicalize(expr)
    decision = preflight_expression(
        expr,
        correlation_id=correlation_id,
        enabled_capabilities=enabled_capabilities,
        require_review_for_writes=require_review_for_writes,
    )
    decision_payload = decision.to_dict()
    effect_summary = decision_payload.get("effect_summary") or {}
    action = _audit_action(str(decision_payload["decision"]))

    return {
        "schema_version": AUDIT_RECORD_SCHEMA_VERSION,
        "event_id": event_id,
        "runner": str(record.get("runner", "external-runner")),
        "event_kind": str(record.get("event_kind", "graph.intent")),
        "correlation_id": correlation_id,
        "source_expression": expression_source,
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
            "required": bool(decision_payload["required_review"]),
            "reason": _review_reason(decision_payload, action),
        },
        "host_boundary": {
            "host_executed": False,
            "transport_envelope": False,
            "hrc_contract_expanded": False,
        },
        "example_boundary": {
            "example_kind": "companion-semantic-event-audit",
            "stable_protocol": False,
            "provider_sdk": False,
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
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "tool": "coglang-semantic-event-audit-demo",
        "ok": True,
        "example_kind": "companion-semantic-event-audit",
        "stable_protocol": False,
        "provider_sdk": False,
        "host_executed": False,
        "hrc_contract_expanded": False,
        "input_path": str(events_path),
        "output_path": str(output_path),
        "event_count": len(events),
        "audit_record_count": len(audit_records),
        "decision_counts": dict(sorted(decision_counts.items())),
        "audit_action_counts": dict(sorted(action_counts.items())),
        "checks": [
            "jsonl-event-input",
            "coglang-parse-and-preflight",
            "semantic-audit-jsonl-output",
            "companion-boundary-no-protocol",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print("usage: audit_events.py EVENTS_JSONL AUDIT_JSONL", file=sys.stderr)
        return 2
    try:
        payload = write_audit_records(Path(args[0]), Path(args[1]))
    except Exception as exc:
        print(f"audit_events.py: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
