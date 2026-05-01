from __future__ import annotations

import tomllib
from pathlib import Path

import pytest


def _source_repo_root_or_skip() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (
            (parent / "pyproject.toml").exists()
            and (parent / "src" / "coglang" / "_public_assets").is_dir()
        ):
            return parent
    pytest.skip("public asset mirror check requires a source or extracted repo layout")


def _one_to_one_public_asset_paths(root: Path) -> list[str]:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    package_data = pyproject["tool"]["setuptools"]["package-data"]["coglang"]
    prefix = "_public_assets/"
    return sorted(
        item.removeprefix(prefix)
        for item in package_data
        if item.startswith(prefix) and "*" not in item
    )


def _normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_public_assets_one_to_one_files_match_root_public_files():
    root = _source_repo_root_or_skip()
    assets_root = root / "src" / "coglang" / "_public_assets"
    missing: list[str] = []
    mismatched: list[str] = []

    for relative_path in _one_to_one_public_asset_paths(root):
        source = root / relative_path
        mirror = assets_root / relative_path
        if not source.exists() or not mirror.exists():
            missing.append(relative_path)
            continue
        if _normalized_text(source) != _normalized_text(mirror):
            mismatched.append(relative_path)

    assert missing == []
    assert mismatched == []
