from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_package_asset_audit_reports_current_public_asset_weight():
    completed = subprocess.run(
        [sys.executable, "scripts/package_asset_audit.py", str(_repo_root())],
        check=True,
        cwd=_repo_root(),
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["tool"] == "coglang-package-asset-audit"
    assert payload["ok"] is True
    assert payload["scope"] == "evidence-only-for-future-wheel-trimming"
    assert payload["package_data_pattern_count"] >= 70
    assert payload["public_asset_file_count"] >= 150
    assert payload["public_asset_bytes"] >= 1_000_000
    assert payload["public_asset_markdown_file_count"] >= 40
    assert payload["public_asset_category_counts"]["markdown"] >= 40
    assert payload["public_asset_category_counts"]["tests"] >= 30
    assert "historical release notes" in payload["trim_candidates"]
    assert "does not change package-data" in payload["non_goals"]
