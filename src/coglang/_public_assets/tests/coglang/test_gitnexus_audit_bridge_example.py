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
    return _repo_root() / "examples" / "gitnexus_audit_bridge"


def test_gitnexus_audit_bridge_example_writes_review_evidence(tmp_path):
    script = _example_root() / "gitnexus_audit_bridge.py"
    events_path = _example_root() / "fixtures" / "gitnexus_tool_events.jsonl"
    audit_path = tmp_path / "gitnexus-audit.jsonl"

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

    assert summary["schema_version"] == "coglang-gitnexus-audit-bridge-demo/v0.1"
    assert summary["ok"] is True
    assert summary["example_kind"] == "companion-gitnexus-audit-bridge"
    assert summary["stable_protocol"] is False
    assert summary["official_gitnexus_integration"] is False
    assert summary["gitnexus_dependency"] is False
    assert summary["gitnexus_executed"] is False
    assert summary["host_executed"] is False
    assert summary["hrc_contract_expanded"] is False
    assert summary["event_count"] == 3
    assert summary["audit_record_count"] == 3
    assert summary["tool_counts"] == {
        "detect_changes": 1,
        "impact": 1,
        "rename": 1,
    }
    assert summary["decision_counts"] == {
        "accepted_with_warnings": 2,
        "requires_review": 1,
    }
    assert summary["audit_action_counts"] == {
        "allow": 1,
        "queue_review": 2,
    }
    assert summary["checks"] == [
        "jsonl-gitnexus-style-tool-event-input",
        "coglang-parse-and-preflight",
        "code-graph-audit-jsonl-output",
        "companion-boundary-no-gitnexus-dependency",
    ]

    assert [record["event_id"] for record in records] == [
        "gitnexus-impact-userservice",
        "gitnexus-detect-staged",
        "gitnexus-rename-dry-run",
    ]
    assert {record["schema_version"] for record in records} == {
        "coglang-gitnexus-audit-bridge-record-demo/v0.1"
    }
    assert [record["tool_name"] for record in records] == [
        "impact",
        "detect_changes",
        "rename",
    ]
    assert [record["audit_action"] for record in records] == [
        "allow",
        "queue_review",
        "queue_review",
    ]
    assert [record["preflight"]["decision"] for record in records] == [
        "accepted_with_warnings",
        "accepted_with_warnings",
        "requires_review",
    ]
    assert records[0]["preflight"]["effects"] == ["graph.read", "meta.trace"]
    assert records[1]["tool_result_summary"]["risk_level"] == "high"
    assert records[1]["human_review"]["required"] is True
    assert records[2]["preflight"]["effects"] == [
        "graph.write",
        "meta.trace",
        "host.policy",
        "human.review",
    ]
    assert all(record["expression_hash"].startswith("sha256:") for record in records)
    assert all(
        record["bridge_boundary"]["official_gitnexus_integration"] is False
        for record in records
    )
    assert all(
        record["bridge_boundary"]["gitnexus_dependency"] is False
        for record in records
    )


def test_gitnexus_audit_bridge_fixture_expressions_parse_and_validate():
    events_path = _example_root() / "fixtures" / "gitnexus_tool_events.jsonl"
    events = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(events) == 3
    for event in events:
        expr = parse(event["coglang_expression"])
        assert expr.head != "ParseError"
        assert valid_coglang(expr)


def test_gitnexus_audit_bridge_readme_declares_companion_boundary():
    readme = (_example_root() / "README.md").read_text(encoding="utf-8")

    assert "companion example material" in readme
    assert "not an official GitNexus integration" in readme
    assert "not import, run, wrap, or modify GitNexus" in readme
    assert "does not add a `coglang` CLI command" in readme
    assert "does not call GitNexus or depend on GitNexus packages" in readme
    assert "does not submit HRC write envelopes" in readme
    assert "does not expand HRC v0.2 frozen scope" in readme
