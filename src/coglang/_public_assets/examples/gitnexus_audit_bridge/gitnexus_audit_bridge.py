from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from coglang.parser import canonicalize, parse
from coglang.preflight import preflight_expression
from coglang.schema_versions import (
    GITNEXUS_AUDIT_BRIDGE_DEMO_SCHEMA_VERSION,
    GITNEXUS_AUDIT_BRIDGE_RECORD_DEMO_SCHEMA_VERSION,
)


SUMMARY_SCHEMA_VERSION = GITNEXUS_AUDIT_BRIDGE_DEMO_SCHEMA_VERSION
AUDIT_RECORD_SCHEMA_VERSION = GITNEXUS_AUDIT_BRIDGE_RECORD_DEMO_SCHEMA_VERSION
HIGH_RISK_LEVELS = {"high", "critical"}
TOOL_RESULT_SUMMARY_KEYS = (
    "status",
    "risk_level",
    "changed_count",
    "affected_count",
    "changed_files",
    "files_affected",
    "total_edits",
    "graph_edits",
    "text_search_edits",
    "affected_processes",
)


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


def _summary_subset(data: dict[str, Any]) -> dict[str, Any]:
    return {key: data[key] for key in TOOL_RESULT_SUMMARY_KEYS if key in data}


def _risk_level(record: dict[str, Any]) -> str:
    tool_result = record.get("tool_result")
    if not isinstance(tool_result, dict):
        return "unknown"
    return str(tool_result.get("risk_level", "unknown")).lower()


def _audit_action(decision: str, risk_level: str) -> str:
    if decision == "rejected":
        return "reject"
    if decision in {"requires_review", "cannot_estimate"}:
        return "queue_review"
    if risk_level in HIGH_RISK_LEVELS:
        return "queue_review"
    return "allow"


def _review_reason(decision_payload: dict[str, Any], action: str, risk_level: str) -> str:
    if action == "allow":
        return "CogLang preflight accepted and GitNexus-style risk is not high"
    if action == "queue_review" and risk_level in HIGH_RISK_LEVELS:
        return "GitNexus-style result reports high-risk graph evidence"
    if action == "queue_review":
        return "CogLang preflight requires human or host policy review"
    reasons = decision_payload.get("reasons", [])
    return ", ".join(str(reason) for reason in reasons) or "CogLang preflight rejected"


def _audit_record(record: dict[str, Any]) -> dict[str, Any]:
    event_id = str(record["event_id"])
    expression_source = str(record["coglang_expression"])
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
    risk_level = _risk_level(record)
    action = _audit_action(str(decision_payload["decision"]), risk_level)
    tool_result = record.get("tool_result")
    tool_result_summary = _summary_subset(tool_result) if isinstance(tool_result, dict) else {}

    return {
        "schema_version": AUDIT_RECORD_SCHEMA_VERSION,
        "event_id": event_id,
        "source_system": str(record.get("source_system", "gitnexus-mcp-sample")),
        "event_kind": "external.code_graph.tool_call",
        "tool_name": str(record["tool_name"]),
        "correlation_id": correlation_id,
        "tool_call": dict(record.get("tool_call", {})),
        "tool_result_summary": tool_result_summary,
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
            "required": action == "queue_review",
            "reason": _review_reason(decision_payload, action, risk_level),
        },
        "bridge_boundary": {
            "example_kind": "companion-gitnexus-audit-bridge",
            "stable_protocol": False,
            "official_gitnexus_integration": False,
            "gitnexus_dependency": False,
            "gitnexus_executed": False,
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
    tool_counts = Counter(str(record["tool_name"]) for record in audit_records)
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "tool": "coglang-gitnexus-audit-bridge-demo",
        "ok": True,
        "example_kind": "companion-gitnexus-audit-bridge",
        "stable_protocol": False,
        "official_gitnexus_integration": False,
        "gitnexus_dependency": False,
        "gitnexus_executed": False,
        "host_executed": False,
        "hrc_contract_expanded": False,
        "input_path": str(events_path),
        "output_path": str(output_path),
        "event_count": len(events),
        "audit_record_count": len(audit_records),
        "tool_counts": dict(sorted(tool_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "audit_action_counts": dict(sorted(action_counts.items())),
        "checks": [
            "jsonl-gitnexus-style-tool-event-input",
            "coglang-parse-and-preflight",
            "code-graph-audit-jsonl-output",
            "companion-boundary-no-gitnexus-dependency",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print(
            "usage: gitnexus_audit_bridge.py GITNEXUS_EVENTS_JSONL AUDIT_JSONL",
            file=sys.stderr,
        )
        return 2
    try:
        payload = write_audit_records(Path(args[0]), Path(args[1]))
    except Exception as exc:
        print(f"gitnexus_audit_bridge.py: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
