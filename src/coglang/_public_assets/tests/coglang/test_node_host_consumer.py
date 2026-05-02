from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _npm_executable() -> str | None:
    return shutil.which("npm.cmd") or shutil.which("npm")


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


def test_node_host_consumer_package_scaffold_stays_private_example():
    package_path = _repo_root() / "examples" / "node_host_consumer" / "package.json"
    payload = json.loads(package_path.read_text(encoding="utf-8"))

    assert payload["name"] == "@coglang/hrc-envelope-consumer-example"
    assert payload["version"] == "0.0.0"
    assert payload["private"] is True
    assert payload["type"] == "module"
    assert payload["bin"] == {
        "coglang-hrc-consumer-example": "./consume_hrc_envelopes.mjs"
    }
    assert payload["scripts"] == {
        "test": "node ./consume_hrc_envelopes.mjs ../..",
        "pack:dry": "npm pack --dry-run",
    }
    assert payload["files"] == [
        "README.md",
        "consume_hrc_envelopes.mjs",
    ]


@pytest.mark.skipif(_npm_executable() is None, reason="npm is not installed")
def test_node_host_consumer_npm_pack_dry_run_lists_expected_files():
    root = _repo_root()
    example_root = root / "examples" / "node_host_consumer"
    npm = _npm_executable()
    assert npm is not None

    completed = subprocess.run(
        [npm, "pack", "--dry-run", "--json"],
        check=True,
        cwd=example_root,
        text=True,
        capture_output=True,
    )
    [payload] = json.loads(completed.stdout)
    paths = {entry["path"] for entry in payload["files"]}

    assert payload["name"] == "@coglang/hrc-envelope-consumer-example"
    assert payload["version"] == "0.0.0"
    assert paths == {
        "README.md",
        "consume_hrc_envelopes.mjs",
        "package.json",
    }
