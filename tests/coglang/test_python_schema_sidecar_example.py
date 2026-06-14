from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _example_root() -> Path:
    return _repo_root() / "examples" / "python_schema_sidecar"


def test_python_schema_sidecar_example_writes_audit_evidence(tmp_path):
    script = _example_root() / "python_schema_sidecar.py"
    events_path = _example_root() / "fixtures" / "generated_expression_events.jsonl"
    audit_path = tmp_path / "python-schema-sidecar-audit.jsonl"

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

    assert summary["schema_version"] == "coglang-python-schema-sidecar-demo/v0.1"
    assert summary["ok"] is True
    assert summary["example_kind"] == "companion-python-schema-sidecar"
    assert summary["stable_protocol"] is False
    assert summary["pydantic_core_dependency"] is False
    assert summary["fastjsonschema_core_dependency"] is False
    assert summary["validator_strategy"] == "stdlib"
    assert summary["event_count"] == 5
    assert summary["audit_record_count"] == 5
    assert summary["envelope_counts"] == {
        "envelope_error": 1,
        "envelope_ok": 4,
    }
    assert summary["parse_counts"] == {
        "parse_error": 1,
        "parse_not_attempted": 1,
        "parse_ok": 3,
    }
    assert summary["validation_counts"] == {
        "validate_error": 2,
        "validate_not_attempted": 1,
        "validate_ok": 2,
    }
    assert summary["decision_counts"] == {
        "accepted_with_warnings": 1,
        "rejected": 3,
        "requires_review": 1,
    }
    assert summary["audit_action_counts"] == {
        "allow": 1,
        "queue_review": 1,
        "reject": 3,
    }
    assert summary["checks"] == [
        "jsonl-generated-expression-event-input",
        "sidecar-envelope-validation",
        "coglang-parse-validate-preflight",
        "python-schema-sidecar-audit-jsonl-output",
        "companion-boundary-no-core-validator-dependency",
    ]

    assert [record["event_id"] for record in records] == [
        "schema-sidecar-read",
        "schema-sidecar-write-review",
        "schema-sidecar-unknown-head",
        "schema-sidecar-malformed-expression",
        "schema-sidecar-invalid-envelope",
    ]
    assert {record["schema_version"] for record in records} == {
        "coglang-python-schema-sidecar-record-demo/v0.1"
    }
    assert [record["audit_action"] for record in records] == [
        "allow",
        "queue_review",
        "reject",
        "reject",
        "reject",
    ]
    assert [record["preflight"]["decision"] for record in records] == [
        "accepted_with_warnings",
        "requires_review",
        "rejected",
        "rejected",
        "rejected",
    ]
    assert records[0]["adapter_validation"]["ok"] is True
    assert records[0]["canonical_expression"] == "AllNodes[]"
    assert records[0]["expression_hash"].startswith("sha256:")
    assert records[1]["human_review"]["required"] is True
    assert records[1]["preflight"]["effects"] == [
        "graph.write",
        "host.policy",
        "human.review",
    ]
    assert records[2]["parse"]["head"] == "CreateRepository"
    assert records[2]["validation"]["ok"] is False
    assert records[3]["parse"]["head"] == "ParseError"
    assert records[3]["expression_hash"] is None
    assert records[4]["adapter_validation"]["ok"] is False
    assert records[4]["generated_expression"] is None
    assert records[4]["parse"]["head"] is None
    assert records[4]["preflight"]["reasons"] == ["adapter.invalid_envelope"]
    assert all(
        record["sidecar_boundary"]["pydantic_core_dependency"] is False
        for record in records
    )
    assert all(
        record["sidecar_boundary"]["fastjsonschema_core_dependency"] is False
        for record in records
    )


def test_python_schema_sidecar_does_not_add_core_dependencies():
    pyproject = tomllib.loads((_repo_root() / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = set(pyproject["project"]["dependencies"])

    assert "networkx" in dependencies
    assert not any("pydantic" in item.lower() for item in dependencies)
    assert not any("fastjsonschema" in item.lower() for item in dependencies)


def test_python_schema_sidecar_readme_declares_companion_boundary():
    readme = (_example_root() / "README.md").read_text(encoding="utf-8")

    assert "companion example material" in readme
    assert "not a Pydantic integration package" in readme
    assert "fastjsonschema integration package" in readme
    assert "does not add Pydantic or fastjsonschema to `pyproject.toml`" in readme
    assert "does not replace CogLang validation" in readme
    assert "does not define a stable audit-envelope schema" in readme
    assert "does not submit HRC write envelopes" in readme
    assert "does not expand HRC v0.2 frozen scope" in readme
