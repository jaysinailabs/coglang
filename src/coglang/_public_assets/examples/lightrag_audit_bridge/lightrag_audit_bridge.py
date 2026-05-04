from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from coglang.parser import canonicalize, parse
from coglang.preflight import preflight_expression
from coglang.schema_versions import (
    LIGHTRAG_AUDIT_BRIDGE_DEMO_SCHEMA_VERSION,
    LIGHTRAG_AUDIT_BRIDGE_RECORD_DEMO_SCHEMA_VERSION,
)


SUMMARY_SCHEMA_VERSION = LIGHTRAG_AUDIT_BRIDGE_DEMO_SCHEMA_VERSION
AUDIT_RECORD_SCHEMA_VERSION = LIGHTRAG_AUDIT_BRIDGE_RECORD_DEMO_SCHEMA_VERSION
DEFAULT_TUPLE_DELIMITER = "<|#|>"


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


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
    return slug or "unknown"


def _parse_lightrag_tuple(record: dict[str, Any]) -> dict[str, Any]:
    delimiter = str(record.get("tuple_delimiter", DEFAULT_TUPLE_DELIMITER))
    raw_tuple = str(record["raw_tuple"])
    parts = [part.strip() for part in raw_tuple.split(delimiter)]
    tuple_kind = parts[0].lower() if parts else ""
    problems: list[str] = []

    if tuple_kind == "entity":
        if len(parts) != 4:
            problems.append("lightrag_tuple.entity_field_count")
        name = parts[1] if len(parts) > 1 else ""
        entity_type = parts[2] if len(parts) > 2 else ""
        description = parts[3] if len(parts) > 3 else ""
        if not name:
            problems.append("lightrag_tuple.entity_name_missing")
        if not entity_type:
            problems.append("lightrag_tuple.entity_type_missing")
        return {
            "tuple_kind": "entity",
            "fields": {
                "entity_name": name,
                "entity_type": entity_type,
                "entity_description": description,
            },
            "problems": problems,
        }

    if tuple_kind == "relation":
        if len(parts) != 5:
            problems.append("lightrag_tuple.relation_field_count")
        source_entity = parts[1] if len(parts) > 1 else ""
        target_entity = parts[2] if len(parts) > 2 else ""
        keywords = parts[3] if len(parts) > 3 else ""
        description = parts[4] if len(parts) > 4 else ""
        if not source_entity:
            problems.append("lightrag_tuple.source_entity_missing")
        if not target_entity:
            problems.append("lightrag_tuple.target_entity_missing")
        if not keywords:
            problems.append("lightrag_tuple.relationship_keywords_missing")
        return {
            "tuple_kind": "relation",
            "fields": {
                "source_entity": source_entity,
                "target_entity": target_entity,
                "relationship_keywords": keywords,
                "relationship_description": description,
            },
            "problems": problems,
        }

    return {
        "tuple_kind": tuple_kind or "unknown",
        "fields": {},
        "problems": ["lightrag_tuple.unknown_kind"],
    }


def _expression_for_tuple(record: dict[str, Any], parsed_tuple: dict[str, Any]) -> str:
    problems = parsed_tuple["problems"]
    if problems:
        return f'ParseError["{problems[0]}"]'

    fields = parsed_tuple["fields"]
    document_id = str(record.get("document_id", "unknown-document"))
    chunk_id = str(record.get("chunk_id", "unknown-chunk"))
    if parsed_tuple["tuple_kind"] == "entity":
        entity_name = str(fields["entity_name"])
        attrs = {
            "category": str(fields["entity_type"]),
            "description": str(fields["entity_description"]),
            "id": f"entity:{_slug(entity_name)}",
            "label": entity_name,
            "source_chunk_id": chunk_id,
            "source_document_id": document_id,
        }
        return f'Create["Entity", {canonicalize(attrs)}]'

    source_entity = str(fields["source_entity"])
    target_entity = str(fields["target_entity"])
    attrs = {
        "description": str(fields["relationship_description"]),
        "from": source_entity,
        "id": f"edge:{_slug(source_entity)}:{_slug(target_entity)}",
        "relation_type": str(fields["relationship_keywords"]),
        "source_chunk_id": chunk_id,
        "source_document_id": document_id,
        "to": target_entity,
    }
    return f'Create["Edge", {canonicalize(attrs)}]'


def _audit_action(decision: str, tuple_problems: list[str]) -> str:
    if tuple_problems or decision == "rejected":
        return "reject"
    if decision in {"requires_review", "cannot_estimate"}:
        return "queue_review"
    return "allow"


def _review_reason(
    decision_payload: dict[str, Any],
    action: str,
    tuple_problems: list[str],
) -> str:
    if tuple_problems:
        return ", ".join(tuple_problems)
    if action == "allow":
        return "CogLang preflight accepted before graph storage write"
    if action == "queue_review":
        return "CogLang preflight requires human review before graph storage write"
    reasons = decision_payload.get("reasons", [])
    return ", ".join(str(reason) for reason in reasons) or "CogLang preflight rejected"


def _audit_record(record: dict[str, Any]) -> dict[str, Any]:
    event_id = str(record["event_id"])
    correlation_id = str(record.get("correlation_id", event_id))
    enabled_capabilities = [str(item) for item in record.get("enabled_capabilities", [])]
    parsed_tuple = _parse_lightrag_tuple(record)
    expression_source = _expression_for_tuple(record, parsed_tuple)
    expr = parse(expression_source)
    canonical_expression = None if expr.head == "ParseError" else canonicalize(expr)
    decision = preflight_expression(
        expr,
        correlation_id=correlation_id,
        enabled_capabilities=enabled_capabilities,
        require_review_for_writes=True,
    )
    decision_payload = decision.to_dict()
    effect_summary = decision_payload.get("effect_summary") or {}
    tuple_problems = [str(item) for item in parsed_tuple["problems"]]
    action = _audit_action(str(decision_payload["decision"]), tuple_problems)

    return {
        "schema_version": AUDIT_RECORD_SCHEMA_VERSION,
        "event_id": event_id,
        "source_system": str(record.get("source_system", "lightrag-extraction-sample")),
        "event_kind": "external.graphrag.extraction_tuple",
        "correlation_id": correlation_id,
        "document_id": str(record.get("document_id", "")),
        "chunk_id": str(record.get("chunk_id", "")),
        "lightrag_tuple": {
            "raw_tuple": str(record["raw_tuple"]),
            "tuple_delimiter": str(record.get("tuple_delimiter", DEFAULT_TUPLE_DELIMITER)),
            "tuple_kind": str(parsed_tuple["tuple_kind"]),
            "fields": dict(parsed_tuple["fields"]),
            "problems": tuple_problems,
        },
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
            "reason": _review_reason(decision_payload, action, tuple_problems),
        },
        "bridge_boundary": {
            "example_kind": "companion-lightrag-audit-bridge",
            "stable_protocol": False,
            "official_lightrag_integration": False,
            "lightrag_dependency": False,
            "lightrag_executed": False,
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
    tuple_kind_counts = Counter(
        str(record["lightrag_tuple"]["tuple_kind"]) for record in audit_records
    )
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "tool": "coglang-lightrag-audit-bridge-demo",
        "ok": True,
        "example_kind": "companion-lightrag-audit-bridge",
        "stable_protocol": False,
        "official_lightrag_integration": False,
        "lightrag_dependency": False,
        "lightrag_executed": False,
        "host_executed": False,
        "hrc_contract_expanded": False,
        "input_path": str(events_path),
        "output_path": str(output_path),
        "event_count": len(events),
        "audit_record_count": len(audit_records),
        "tuple_kind_counts": dict(sorted(tuple_kind_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "audit_action_counts": dict(sorted(action_counts.items())),
        "checks": [
            "jsonl-lightrag-style-extraction-tuple-input",
            "lightrag-tuple-to-coglang-intent",
            "coglang-parse-and-preflight",
            "graphrag-audit-jsonl-output",
            "companion-boundary-no-lightrag-dependency",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print(
            "usage: lightrag_audit_bridge.py LIGHTRAG_TUPLES_JSONL AUDIT_JSONL",
            file=sys.stderr,
        )
        return 2
    try:
        payload = write_audit_records(Path(args[0]), Path(args[1]))
    except Exception as exc:
        print(f"lightrag_audit_bridge.py: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
