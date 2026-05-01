from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_node_minimal_host_runtime_stub_runs_success_and_failure_paths():
    root = _repo_root()
    script = root / "examples" / "node_minimal_host_runtime_stub" / "run_demo.mjs"

    completed = subprocess.run(
        ["node", str(script)],
        check=True,
        cwd=root,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["schema_version"] == "coglang-node-minimal-host-runtime-stub-demo/v0.1"
    assert payload["ok"] is True
    assert payload["runtime"] == "node"
    assert payload["example_kind"] == "experimental-in-repository-stub"
    assert payload["hrc_scope"] == "post-freeze-example-only"
    assert payload["hrc_contract_expanded"] is False
    assert payload["checks"] == [
        "runtime-validate-execute",
        "submission-envelope-read",
        "success-write-result-envelope",
        "failure-error-report-envelope",
        "identity-preservation",
        "local-write-header",
    ]

    assert payload["runtime_checks"] == {
        "validate_ok": True,
        "execute_value": True,
        "unsupported_error_kind": "UnsupportedExpression",
    }

    success = payload["success_response"]
    assert success["header"]["message_type"] == "KnowledgeMessage"
    assert success["header"]["operation"] == "write_bundle_response"
    assert success["header"]["payload_kind"] == "WriteResult"
    assert success["header"]["correlation_id"] == "corr-1"
    assert success["header"]["submission_id"] == "sub-1"
    assert success["metadata"]["owner"] == "tester"
    assert success["payload"]["correlation_id"] == "corr-1"
    assert success["payload"]["submission_id"] == "sub-1"
    assert success["payload"]["owner"] == "tester"
    assert success["payload"]["applied_ops"] == 1
    assert success["payload"]["touched_node_ids"] == ["node-1"]

    failure = payload["failure_response"]
    assert failure["header"]["payload_kind"] == "ErrorReport"
    assert failure["header"]["correlation_id"] == "corr-node-stub-error"
    assert failure["header"]["submission_id"] == "sub-node-stub-error"
    assert failure["payload"]["correlation_id"] == "corr-node-stub-error"
    assert failure["payload"]["submission_id"] == "sub-node-stub-error"
    assert failure["payload"]["owner"] == "tester"
    assert failure["payload"]["retryable"] is False
    assert failure["payload"]["error_kind"] == "ValidationError"
    assert failure["payload"]["errors"] == ["op[0] unsupported op 'unsupported_write'"]

    assert payload["local_headers"]["success"] == {
        "correlation_id": "corr-1",
        "payload_kind": "WriteResult",
        "status": "committed",
        "submission_id": "sub-1",
    }
    assert payload["local_headers"]["failure"] == {
        "correlation_id": "corr-node-stub-error",
        "payload_kind": "ErrorReport",
        "status": "failed",
        "submission_id": "sub-node-stub-error",
    }
    assert payload["local_headers"]["missing"] == {
        "correlation_id": "corr-node-stub-missing",
        "payload_kind": None,
        "status": "not_found",
        "submission_id": None,
    }
    assert payload["graph_state"]["node_count"] == 1
