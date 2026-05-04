from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from coglang.parser import parse
from coglang.validator import valid_coglang


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _example_root() -> Path:
    return _repo_root() / "examples" / "outlines_generation_bridge"


def test_outlines_generation_bridge_example_writes_audit_evidence(tmp_path):
    script = _example_root() / "outlines_generation_bridge.py"
    events_path = _example_root() / "fixtures" / "outlines_generated_expressions.jsonl"
    audit_path = tmp_path / "outlines-generation-audit.jsonl"

    completed = subprocess.run(
        [sys.executable, str(script), str(events_path), str(audit_path)],
        check=True,
        cwd=_repo_root(),
        text=True,
        capture_output=True,
    )
    summary = json.loads(completed.stdout)
    records = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert summary["schema_version"] == "coglang-outlines-generation-bridge-demo/v0.1"
    assert summary["ok"] is True
    assert summary["example_kind"] == "companion-outlines-generation-bridge"
    assert summary["stable_protocol"] is False
    assert summary["official_outlines_integration"] is False
    assert summary["outlines_dependency"] is False
    assert summary["outlines_executed"] is False
    assert summary["model_executed"] is False
    assert summary["host_executed"] is False
    assert summary["hrc_contract_expanded"] is False
    assert summary["event_count"] == 4
    assert summary["audit_record_count"] == 4
    assert summary["decoder_counts"] == {
        "outlines-style-constrained-generation": 3,
        "unconstrained-baseline": 1,
    }
    assert summary["parse_counts"] == {
        "parse_error": 1,
        "parse_ok": 3,
    }
    assert summary["validation_counts"] == {
        "validate_error": 2,
        "validate_ok": 2,
    }
    assert summary["decision_counts"] == {
        "accepted_with_warnings": 1,
        "rejected": 2,
        "requires_review": 1,
    }
    assert summary["audit_action_counts"] == {
        "allow": 1,
        "queue_review": 1,
        "reject": 2,
    }
    assert summary["checks"] == [
        "jsonl-outlines-style-generation-output-input",
        "generated-expression-parse-validate-preflight",
        "coglang-audit-jsonl-output",
        "companion-boundary-no-outlines-dependency",
    ]

    assert [record["event_id"] for record in records] == [
        "outlines-read-all-nodes",
        "outlines-create-review-node",
        "outlines-unknown-head",
        "outlines-malformed-expression",
    ]
    assert {record["schema_version"] for record in records} == {
        "coglang-outlines-generation-bridge-record-demo/v0.1"
    }
    assert [record["audit_action"] for record in records] == [
        "allow",
        "queue_review",
        "reject",
        "reject",
    ]
    assert [record["preflight"]["decision"] for record in records] == [
        "accepted_with_warnings",
        "requires_review",
        "rejected",
        "rejected",
    ]
    assert records[0]["parse"]["ok"] is True
    assert records[0]["validation"]["ok"] is True
    assert records[0]["canonical_expression"] == "AllNodes[]"
    assert records[0]["human_review"]["required"] is False
    assert records[1]["parse"]["head"] == "Create"
    assert records[1]["preflight"]["effects"] == [
        "graph.write",
        "host.policy",
        "human.review",
    ]
    assert records[1]["human_review"]["required"] is True
    assert records[2]["parse"]["head"] == "CreateRepository"
    assert records[2]["validation"]["ok"] is False
    assert records[2]["human_review"]["reason"] == (
        "Generated expression parsed but failed CogLang validation"
    )
    assert records[3]["parse"]["head"] == "ParseError"
    assert records[3]["canonical_expression"] is None
    assert records[3]["expression_hash"] is None
    assert records[3]["human_review"]["required"] is False
    assert all(
        record["bridge_boundary"]["official_outlines_integration"] is False
        for record in records
    )
    assert all(
        record["bridge_boundary"]["outlines_dependency"] is False
        for record in records
    )


def test_outlines_generation_bridge_valid_fixture_expressions_parse_and_validate():
    events_path = _example_root() / "fixtures" / "outlines_generated_expressions.jsonl"
    events = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(events) == 4
    for event in events[:2]:
        expr = parse(event["generated_expression"])
        assert expr.head != "ParseError"
        assert valid_coglang(expr)

    invalid_head = parse(events[2]["generated_expression"])
    assert invalid_head.head == "CreateRepository"
    assert not valid_coglang(invalid_head)

    malformed = parse(events[3]["generated_expression"])
    assert malformed.head == "ParseError"


def test_outlines_generation_bridge_readme_declares_companion_boundary():
    readme = (_example_root() / "README.md").read_text(encoding="utf-8")

    assert "companion example material" in readme
    assert "not an official Outlines integration" in readme
    assert "does not import, run, wrap, or modify Outlines" in readme
    assert "does not add a `coglang` CLI command" in readme
    assert "does not call Outlines or depend on Outlines packages" in readme
    assert "does not submit HRC write envelopes" in readme
    assert "does not expand HRC v0.2 frozen scope" in readme
