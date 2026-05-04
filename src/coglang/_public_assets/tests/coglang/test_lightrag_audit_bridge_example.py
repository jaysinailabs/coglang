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
    return _repo_root() / "examples" / "lightrag_audit_bridge"


def test_lightrag_audit_bridge_example_writes_review_evidence(tmp_path):
    script = _example_root() / "lightrag_audit_bridge.py"
    events_path = _example_root() / "fixtures" / "lightrag_extraction_tuples.jsonl"
    audit_path = tmp_path / "lightrag-audit.jsonl"

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

    assert summary["schema_version"] == "coglang-lightrag-audit-bridge-demo/v0.1"
    assert summary["ok"] is True
    assert summary["example_kind"] == "companion-lightrag-audit-bridge"
    assert summary["stable_protocol"] is False
    assert summary["official_lightrag_integration"] is False
    assert summary["lightrag_dependency"] is False
    assert summary["lightrag_executed"] is False
    assert summary["host_executed"] is False
    assert summary["hrc_contract_expanded"] is False
    assert summary["event_count"] == 3
    assert summary["audit_record_count"] == 3
    assert summary["tuple_kind_counts"] == {
        "entity": 1,
        "relation": 2,
    }
    assert summary["decision_counts"] == {
        "rejected": 1,
        "requires_review": 2,
    }
    assert summary["audit_action_counts"] == {
        "queue_review": 2,
        "reject": 1,
    }
    assert summary["checks"] == [
        "jsonl-lightrag-style-extraction-tuple-input",
        "lightrag-tuple-to-coglang-intent",
        "coglang-parse-and-preflight",
        "graphrag-audit-jsonl-output",
        "companion-boundary-no-lightrag-dependency",
    ]

    assert [record["event_id"] for record in records] == [
        "lightrag-entity-ada",
        "lightrag-relation-ada-engine",
        "lightrag-bad-relation-missing-target",
    ]
    assert {record["schema_version"] for record in records} == {
        "coglang-lightrag-audit-bridge-record-demo/v0.1"
    }
    assert [record["audit_action"] for record in records] == [
        "queue_review",
        "queue_review",
        "reject",
    ]
    assert [record["preflight"]["decision"] for record in records] == [
        "requires_review",
        "requires_review",
        "rejected",
    ]
    assert records[0]["lightrag_tuple"]["tuple_kind"] == "entity"
    assert records[0]["preflight"]["effects"] == [
        "graph.write",
        "host.policy",
        "human.review",
    ]
    assert records[1]["lightrag_tuple"]["tuple_kind"] == "relation"
    assert records[1]["lightrag_tuple"]["fields"]["target_entity"] == "Analytical Engine"
    assert records[1]["preflight"]["required_capabilities"] == ["graph.write"]
    assert records[2]["lightrag_tuple"]["problems"] == [
        "lightrag_tuple.target_entity_missing"
    ]
    assert records[2]["expression_hash"] is None
    assert records[2]["human_review"]["required"] is False
    assert all(
        record["bridge_boundary"]["official_lightrag_integration"] is False
        for record in records
    )
    assert all(
        record["bridge_boundary"]["lightrag_dependency"] is False
        for record in records
    )


def test_lightrag_audit_bridge_valid_fixture_expressions_parse_and_validate():
    events_path = _example_root() / "fixtures" / "lightrag_extraction_tuples.jsonl"
    events = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(events) == 3
    for event in events[:2]:
        raw_tuple = event["raw_tuple"]
        assert raw_tuple.startswith(("entity<|#|>", "relation<|#|>"))

    script_dir = _example_root()
    sys.path.insert(0, str(script_dir))
    try:
        import lightrag_audit_bridge

        for event in events[:2]:
            parsed_tuple = lightrag_audit_bridge._parse_lightrag_tuple(event)
            expression = lightrag_audit_bridge._expression_for_tuple(event, parsed_tuple)
            expr = parse(expression)
            assert expr.head != "ParseError"
            assert valid_coglang(expr)
    finally:
        sys.path.remove(str(script_dir))
        sys.modules.pop("lightrag_audit_bridge", None)


def test_lightrag_audit_bridge_readme_declares_companion_boundary():
    readme = (_example_root() / "README.md").read_text(encoding="utf-8")

    assert "companion example material" in readme
    assert "not an official LightRAG integration" in readme
    assert "not import, run, wrap, or modify LightRAG" in readme
    assert "does not add a `coglang` CLI command" in readme
    assert "does not call LightRAG or depend on LightRAG packages" in readme
    assert "does not submit HRC write envelopes" in readme
    assert "does not expand HRC v0.2 frozen scope" in readme
