from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from coglang.parser import CogLangExpr, canonicalize, parse
from coglang.preflight import preflight_expression
from coglang.schema_versions import (
    AGENT_MEMORY_AUDIT_PRESSURE_TESTS_RECORD_SCHEMA_VERSION,
    AGENT_MEMORY_AUDIT_PRESSURE_TESTS_SCHEMA_VERSION,
)
from coglang.validator import valid_coglang


FIXTURE_SCHEMA_VERSION = AGENT_MEMORY_AUDIT_PRESSURE_TESTS_SCHEMA_VERSION
RECORD_SCHEMA_VERSION = AGENT_MEMORY_AUDIT_PRESSURE_TESTS_RECORD_SCHEMA_VERSION


def _load_fixture(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("fixture root must be a JSON object")
    if payload.get("schema_version") != FIXTURE_SCHEMA_VERSION:
        raise ValueError("unexpected pressure-test fixture schema_version")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("fixture must contain at least one case")
    return payload


def _walk_values(value: Any):
    if isinstance(value, CogLangExpr):
        yield value
        for arg in value.args:
            yield from _walk_values(arg)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk_values(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_values(item)


def _head_counts(expr: CogLangExpr) -> dict[str, int]:
    counts = Counter(node.head for node in _walk_values(expr))
    return dict(sorted(counts.items()))


def _candidate_shape_status(candidate_text: str) -> dict[str, Any]:
    expr = parse(candidate_text)
    return {
        "parse_ok": expr.head != "ParseError",
        "head": str(expr.head),
        "valid_current_coglang": bool(expr.head != "ParseError" and valid_coglang(expr)),
    }


def _count_floor_checks(
    expected: dict[str, Any],
    head_counts: dict[str, int],
) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    floor_specs = {
        "min_create_count": "Create",
        "min_delete_count": "Delete",
        "min_get_count": "Get",
        "min_query_count": "Query",
        "min_trace_count": "Trace",
        "min_update_count": "Update",
    }
    for key, head in floor_specs.items():
        if key in expected:
            check_name = f"{head.lower()}_count_meets_pressure_floor"
            checks[check_name] = head_counts.get(head, 0) >= int(expected[key])
    return checks


def _validate_case(case: dict[str, Any]) -> dict[str, Any]:
    case_id = str(case["id"])
    expression_text = str(case["current_v1_1_expression"])
    expected = case["expected"]
    expr = parse(expression_text)
    parse_ok = expr.head != "ParseError"
    validate_ok = bool(parse_ok and valid_coglang(expr))
    canonical_expression = canonicalize(expr) if parse_ok else None
    decision = preflight_expression(
        expr,
        correlation_id=case_id,
        enabled_capabilities=["graph.read", "graph.write"],
        require_review_for_writes=True,
    )
    decision_payload = decision.to_dict()
    effect_summary = decision_payload.get("effect_summary") or {}
    head_counts = _head_counts(expr) if parse_ok else {}
    candidate_shape = _candidate_shape_status(str(case["proposed_after_shape"]))

    checks = {
        "parse_ok": parse_ok,
        "validate_ok": validate_ok,
        "canonical_matches_expected": (
            canonical_expression == expected["canonical_expression"]
        ),
        "preflight_decision_matches_expected": (
            decision_payload["decision"] == expected["preflight_decision"]
        ),
        "effects_match_expected": (
            effect_summary.get("effects", []) == expected["effects"]
        ),
        "required_capabilities_match_expected": (
            effect_summary.get("required_capabilities", [])
            == expected["required_capabilities"]
        ),
        "required_review_matches_expected": (
            decision_payload["required_review"] == expected["required_review"]
        ),
        "candidate_shape_parse_ok": candidate_shape["parse_ok"],
        "candidate_shape_is_not_current_core": (
            not candidate_shape["valid_current_coglang"]
        ),
    }
    checks.update(_count_floor_checks(expected, head_counts))

    return {
        "schema_version": RECORD_SCHEMA_VERSION,
        "case_id": case_id,
        "name": str(case["name"]),
        "candidate_track": str(case["candidate_track"]),
        "ok": all(checks.values()),
        "checks": checks,
        "current": {
            "parse_ok": parse_ok,
            "validate_ok": validate_ok,
            "canonical_expression": canonical_expression,
            "expression_char_count": len(expression_text),
            "head_counts": head_counts,
            "preflight_decision": decision_payload["decision"],
            "preflight_reasons": decision_payload["reasons"],
            "effects": effect_summary.get("effects", []),
            "required_capabilities": effect_summary.get("required_capabilities", []),
            "required_review": decision_payload["required_review"],
            "expression_hash": effect_summary.get("expression_hash"),
        },
        "candidate_after_shape": {
            "text": str(case["proposed_after_shape"]),
            **candidate_shape,
        },
        "pressure_note": str(case["pressure_note"]),
        "promotion_risk": str(case["promotion_risk"]),
        "conformance_test_sketch": str(case["conformance_test_sketch"]),
        "boundary": {
            "example_kind": "companion-agent-memory-audit-pressure-test",
            "stable_protocol": False,
            "language_change": False,
            "vocab_change": False,
            "hrc_contract_expanded": False,
            "host_executed": False,
            "memory_written": False,
            "provider_called": False,
            "proposal_commitment": False,
        },
    }


def write_pressure_results(fixture_path: Path, output_path: Path) -> dict[str, Any]:
    fixture = _load_fixture(fixture_path)
    records = [_validate_case(case) for case in fixture["cases"]]
    output_path.write_text(
        "\n".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True)
            for record in records
        )
        + "\n",
        encoding="utf-8",
    )
    track_counts = Counter(str(record["candidate_track"]) for record in records)
    decision_counts = Counter(
        str(record["current"]["preflight_decision"]) for record in records
    )
    ok = all(record["ok"] for record in records)
    return {
        "schema_version": FIXTURE_SCHEMA_VERSION,
        "tool": "coglang-agent-memory-audit-pressure-tests",
        "ok": ok,
        "status": fixture["status"],
        "scenario": fixture["scenario"],
        "language_baseline": fixture["language_baseline"],
        "stable_protocol": False,
        "language_change": False,
        "vocab_change": False,
        "hrc_contract_expanded": False,
        "host_executed": False,
        "memory_written": False,
        "provider_called": False,
        "proposal_commitment": False,
        "input_path": str(fixture_path),
        "output_path": str(output_path),
        "case_count": len(records),
        "track_counts": dict(sorted(track_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "failed_cases": [
            record["case_id"] for record in records if not record["ok"]
        ],
        "checks": [
            "current-v1-1-expressions-parse-and-validate",
            "expected-canonical-text",
            "expected-current-preflight",
            "candidate-after-shapes-remain-text-only",
            "companion-boundary-no-language-hrc-or-memory-write-change",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print(
            "usage: agent_memory_audit_pressure_tests.py FIXTURE_JSON RESULTS_JSONL",
            file=sys.stderr,
        )
        return 2
    try:
        payload = write_pressure_results(Path(args[0]), Path(args[1]))
    except Exception as exc:
        print(f"agent_memory_audit_pressure_tests.py: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
