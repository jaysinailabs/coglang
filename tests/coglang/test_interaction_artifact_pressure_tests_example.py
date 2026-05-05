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
    return _repo_root() / "examples" / "interaction_artifact_pressure_tests"


def test_interaction_artifact_pressure_tests_write_results(tmp_path):
    script = _example_root() / "interaction_artifact_pressure_tests.py"
    fixture_path = (
        _example_root()
        / "fixtures"
        / "interaction_artifact_pressure_tests_v0_1.json"
    )
    results_path = tmp_path / "interaction-artifact-pressure-results.jsonl"

    completed = subprocess.run(
        [sys.executable, str(script), str(fixture_path), str(results_path)],
        check=True,
        cwd=_repo_root(),
        text=True,
        capture_output=True,
    )
    summary = json.loads(completed.stdout)
    records = [
        json.loads(line)
        for line in results_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert summary["schema_version"] == (
        "coglang-interaction-artifact-pressure-tests/v0.1"
    )
    assert summary["ok"] is True
    assert summary["status"] == "companion-pressure-test"
    assert summary["stable_protocol"] is False
    assert summary["language_change"] is False
    assert summary["vocab_change"] is False
    assert summary["hrc_contract_expanded"] is False
    assert summary["host_executed"] is False
    assert summary["proposal_commitment"] is False
    assert summary["case_count"] == 5
    assert summary["track_counts"] == {
        "language-candidate": 2,
        "language-or-profile-candidate": 1,
        "profile-integration-candidate": 1,
        "profile-or-capability-candidate": 1,
    }
    assert summary["decision_counts"] == {
        "accepted_with_warnings": 1,
        "cannot_estimate": 2,
        "requires_review": 2,
    }
    assert summary["failed_cases"] == []
    assert summary["checks"] == [
        "current-v1-1-expressions-parse-and-validate",
        "expected-canonical-text",
        "expected-current-preflight",
        "candidate-after-shapes-remain-text-only",
        "companion-boundary-no-language-or-hrc-change",
    ]

    assert [record["case_id"] for record in records] == [
        "IAG-PT-001",
        "IAG-PT-002",
        "IAG-PT-003",
        "IAG-PT-004",
        "IAG-PT-005",
    ]
    assert {record["schema_version"] for record in records} == {
        "coglang-interaction-artifact-pressure-tests-record/v0.1"
    }
    assert all(record["ok"] is True for record in records)
    assert records[0]["current"]["head_counts"]["Traverse"] >= 6
    assert records[0]["current"]["preflight_decision"] == "cannot_estimate"
    assert records[1]["current"]["head_counts"]["Traverse"] >= 6
    assert records[2]["current"]["head_counts"]["Create"] == 3
    assert records[2]["current"]["preflight_decision"] == "requires_review"
    assert records[3]["current"]["head_counts"]["Create"] == 1
    assert records[3]["current"]["preflight_decision"] == "requires_review"
    assert records[4]["current"]["head_counts"]["Query"] == 3
    assert records[4]["current"]["preflight_decision"] == "accepted_with_warnings"
    assert all(
        record["candidate_after_shape"]["parse_ok"] is True for record in records
    )
    assert all(
        record["candidate_after_shape"]["valid_current_coglang"] is False
        for record in records
    )
    assert all(record["boundary"]["language_change"] is False for record in records)
    assert all(
        record["boundary"]["hrc_contract_expanded"] is False for record in records
    )


def test_interaction_artifact_pressure_fixture_current_expressions_are_valid():
    fixture_path = (
        _example_root()
        / "fixtures"
        / "interaction_artifact_pressure_tests_v0_1.json"
    )
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    assert fixture["status"] == "companion-pressure-test"
    assert fixture["stable_protocol"] is False
    for case in fixture["cases"]:
        expr = parse(case["current_v1_1_expression"])
        assert expr.head != "ParseError"
        assert valid_coglang(expr)

        proposed = parse(case["proposed_after_shape"])
        assert proposed.head != "ParseError"
        assert not valid_coglang(proposed)


def test_interaction_artifact_pressure_readme_declares_boundary():
    readme = (_example_root() / "README.md").read_text(encoding="utf-8")

    assert "companion pressure-test material" in readme
    assert "not a language proposal" in readme
    assert "Proposed after-shapes are not added to `COGLANG_VOCAB`" in readme
    assert "No HRC v0.2 frozen scope is expanded" in readme
    assert "No host execution, graph write, or transport envelope is performed" in readme
