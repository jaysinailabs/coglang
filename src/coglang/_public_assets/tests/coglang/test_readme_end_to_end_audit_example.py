from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _example_root() -> Path:
    return _repo_root() / "examples" / "readme_end_to_end_audit"


def test_readme_end_to_end_audit_demo_runs_parse_preflight_execute_trace():
    script = _example_root() / "readme_end_to_end_audit.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        check=True,
        cwd=_repo_root(),
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["tool"] == "coglang-readme-end-to-end-audit-demo"
    assert payload["ok"] is True
    assert payload["provider_sdk"] is False
    assert payload["network"] is False
    assert payload["hrc_contract_expanded"] is False
    assert payload["record_count"] == 2
    assert payload["audit_action_counts"] == {"allow": 1, "queue_review": 1}

    read_record, write_record = payload["records"]
    assert read_record["event_id"] == "model-read-risks"
    assert read_record["preflight_decision"] == "accepted_with_warnings"
    assert read_record["audit_action"] == "allow"
    assert read_record["executed"] is True
    assert read_record["execution_result"] == 'List["risk-1"]'
    assert read_record["trace"] == [
        {
            "depth": 0,
            "expr": 'Query[n_, Equal[Get[n_, "kind"], "Risk"], {"k": 5}]',
            "result": 'List["risk-1"]',
        }
    ]

    assert write_record["event_id"] == "model-propose-memory"
    assert write_record["preflight_decision"] == "requires_review"
    assert write_record["audit_action"] == "queue_review"
    assert write_record["executed"] is False
    assert write_record["execution_result"] is None
    assert write_record["trace"] == []
    assert all(record["expression_hash"].startswith("sha256:") for record in payload["records"])


def test_readme_end_to_end_audit_readme_declares_boundary():
    readme = (_example_root() / "README.md").read_text(encoding="utf-8")

    assert "provider-neutral" in readme
    assert "does not import an LLM SDK" in readme
    assert "does not import an LLM SDK, make network calls" in readme
    assert "does not import an LLM SDK, make network calls,\nsubmit HRC envelopes" in readme
    assert "not a host implementation" in readme
