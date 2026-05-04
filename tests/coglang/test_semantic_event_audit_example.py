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
    return _repo_root() / "examples" / "semantic_event_audit"


def test_semantic_event_audit_example_writes_preflight_audit_records(tmp_path):
    script = _example_root() / "audit_events.py"
    events_path = _example_root() / "fixtures" / "external_events.jsonl"
    audit_path = tmp_path / "audit.jsonl"

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

    assert summary["schema_version"] == "coglang-semantic-event-audit-demo/v0.1"
    assert summary["ok"] is True
    assert summary["example_kind"] == "companion-semantic-event-audit"
    assert summary["stable_protocol"] is False
    assert summary["provider_sdk"] is False
    assert summary["host_executed"] is False
    assert summary["hrc_contract_expanded"] is False
    assert summary["event_count"] == 3
    assert summary["audit_record_count"] == 3
    assert summary["decision_counts"] == {
        "accepted_with_warnings": 1,
        "rejected": 1,
        "requires_review": 1,
    }
    assert summary["audit_action_counts"] == {
        "allow": 1,
        "queue_review": 1,
        "reject": 1,
    }
    assert summary["checks"] == [
        "jsonl-event-input",
        "coglang-parse-and-preflight",
        "semantic-audit-jsonl-output",
        "companion-boundary-no-protocol",
    ]

    assert [record["event_id"] for record in records] == [
        "audit-read-projects",
        "audit-create-memory",
        "audit-missing-write-capability",
    ]
    assert {record["schema_version"] for record in records} == {
        "coglang-semantic-event-audit-record-demo/v0.1"
    }
    assert [record["audit_action"] for record in records] == [
        "allow",
        "queue_review",
        "reject",
    ]
    assert [record["preflight"]["decision"] for record in records] == [
        "accepted_with_warnings",
        "requires_review",
        "rejected",
    ]
    assert records[0]["preflight"]["effects"] == ["graph.read"]
    assert records[1]["preflight"]["effects"] == [
        "graph.write",
        "host.policy",
        "human.review",
    ]
    assert records[2]["preflight"]["reasons"] == [
        "capability.missing",
        "capability.missing.graph_write",
    ]
    assert all(record["expression_hash"].startswith("sha256:") for record in records)
    assert all(record["host_boundary"]["host_executed"] is False for record in records)
    assert all(
        record["host_boundary"]["hrc_contract_expanded"] is False
        for record in records
    )


def test_semantic_event_audit_fixture_expressions_parse_and_validate():
    events_path = _example_root() / "fixtures" / "external_events.jsonl"
    events = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(events) == 3
    for event in events:
        expr = parse(event["expression"])
        assert expr.head != "ParseError"
        assert valid_coglang(expr)


def test_semantic_event_audit_readme_declares_companion_boundary():
    readme = (_example_root() / "README.md").read_text(encoding="utf-8")

    assert "companion example material" in readme
    assert "not a hosted runner" in readme
    assert "not a hosted runner, provider SDK integration, transport envelope" in readme
    assert "does not define a stable semantic-event schema" in readme
    assert "does not add a `coglang` CLI command" in readme
    assert "does not submit HRC write envelopes" in readme
    assert "does not expand HRC v0.2 frozen scope" in readme
