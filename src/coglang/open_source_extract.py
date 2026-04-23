from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_public_repo_extract_manifest(project_root: Path | None = None) -> dict[str, Any]:
    root = project_root or _project_root()
    descriptor_path = root / "plans" / "coglang" / "CogLang_Public_Repo_Extract_Manifest_v0_1.json"
    payload = json.loads(descriptor_path.read_text(encoding="utf-8"))
    payload["path"] = str(descriptor_path.relative_to(root)).replace("\\", "/")
    return payload


def _copy_tree_entry(source_root: Path, destination_root: Path, includes: list[str] | None) -> None:
    if not includes:
        shutil.copytree(source_root, destination_root)
        return

    destination_root.mkdir(parents=True, exist_ok=True)
    for relative_path in includes:
        source = source_root / Path(relative_path)
        destination = destination_root / Path(relative_path)
        if source.is_dir():
            shutil.copytree(source, destination)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def _mirror_public_assets(destination_root: Path, entries: list[dict[str, Any]]) -> int:
    assets_root = destination_root / "src" / "coglang" / "_public_assets"
    mirrored_files = 0

    for entry in entries:
        destination = Path(str(entry.get("destination", "")))
        if not destination.parts or destination.parts[0] == "src":
            continue

        source_path = destination_root / destination
        asset_path = assets_root / destination

        if entry.get("kind") == "file":
            if not source_path.exists():
                continue
            asset_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, asset_path)
            mirrored_files += 1
            continue

        if entry.get("kind") != "tree" or not source_path.exists():
            continue

        if asset_path.exists():
            shutil.rmtree(asset_path)
        shutil.copytree(source_path, asset_path)
        mirrored_files += sum(1 for path in asset_path.rglob("*") if path.is_file())

    return mirrored_files


def materialize_public_repo_extract(
    destination_root: Path,
    project_root: Path | None = None,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    root = project_root or _project_root()
    payload = load_public_repo_extract_manifest(root)
    entries = payload.get("entries", [])
    destination_root = Path(destination_root)
    destination_root.mkdir(parents=True, exist_ok=True)

    copied_trees = 0
    copied_files = 0

    for entry in entries:
        kind = entry["kind"]
        source = root / Path(entry["source"])
        destination = destination_root / Path(entry["destination"])

        if destination.exists():
            if not overwrite:
                raise FileExistsError(str(destination))
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()

        destination.parent.mkdir(parents=True, exist_ok=True)
        if kind == "tree":
            _copy_tree_entry(source, destination, entry.get("include"))
            copied_trees += 1
        elif kind == "file":
            shutil.copy2(source, destination)
            copied_files += 1
        else:
            raise ValueError(f"Unsupported extract entry kind: {kind}")

    mirrored_files = _mirror_public_assets(destination_root, entries)

    return {
        "schema_version": "coglang-public-repo-extract-run/v0.1",
        "manifest_path": payload["path"],
        "destination_root": str(destination_root),
        "entry_count": len(entries),
        "copied_trees": copied_trees,
        "copied_files": copied_files,
        "mirrored_asset_files": mirrored_files,
    }
