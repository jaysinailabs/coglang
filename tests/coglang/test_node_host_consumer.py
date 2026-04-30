from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_node_host_consumer_reads_hrc_schema_pack_and_envelopes():
    root = _repo_root()
    script = root / "examples" / "node_host_consumer" / "consume_hrc_envelopes.mjs"

    completed = subprocess.run(
        ["node", str(script)],
        check=True,
        cwd=root,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["schema_version"] == "coglang-node-host-consumer-demo/v0.1"
    assert payload["ok"] is True
    assert payload["runtime"] == "node"
    assert payload["schema_pack"] == "urn:coglang:host-runtime-schema-pack:v0.1"
    assert payload["schema_count"] == 11
    assert payload["sample_count"] == 8
    assert payload["checks"] == [
        "schema-pack-header",
        "schema-files-and-ids",
        "sample-files",
        "submission-response-envelopes",
        "local-view-consistency",
    ]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_node_host_consumer_accepts_schema_pack_directory_argument():
    root = _repo_root()
    script = root / "examples" / "node_host_consumer" / "consume_hrc_envelopes.mjs"
    schema_dir = root / "internal_schemas" / "host_runtime" / "v0.1"

    completed = subprocess.run(
        ["node", str(script), str(schema_dir)],
        check=True,
        cwd=root,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["ok"] is True
    assert Path(payload["schema_dir"]) == schema_dir
