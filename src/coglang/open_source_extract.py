from __future__ import annotations

import json
import shutil
import tomllib
from pathlib import Path
from typing import Any

from .schema_versions import PUBLIC_REPO_EXTRACT_RUN_SCHEMA_VERSION


PUBLIC_ASSETS_MIRROR_ROOT = Path("src") / "coglang" / "_public_assets"


def _project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parents[3]


def load_public_repo_extract_manifest(project_root: Path | None = None) -> dict[str, Any]:
    root = project_root or _project_root()
    descriptor_candidates = [
        root / "CogLang_Public_Repo_Extract_Manifest_v0_1.json",
    ]
    descriptor_path = next((path for path in descriptor_candidates if path.exists()), descriptor_candidates[0])
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


def _is_public_asset_mirror_entry(entry: dict[str, Any]) -> bool:
    destination = Path(str(entry.get("destination", "")))
    return bool(destination.parts) and destination.parts[0] != "src"


def _copy_public_asset_mirror_entry(
    source_root: Path,
    assets_root: Path,
    entry: dict[str, Any],
) -> int:
    destination = Path(str(entry["destination"]))
    source_path = source_root / destination
    asset_path = assets_root / destination

    if entry.get("kind") == "file":
        if not source_path.exists():
            return 0
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, asset_path)
        return 1

    if entry.get("kind") != "tree" or not source_path.exists():
        return 0

    if asset_path.exists():
        shutil.rmtree(asset_path)
    _copy_tree_entry(source_path, asset_path, entry.get("include"))
    return sum(1 for path in asset_path.rglob("*") if path.is_file())


def _mirror_public_assets(destination_root: Path, entries: list[dict[str, Any]]) -> int:
    assets_root = destination_root / "src" / "coglang" / "_public_assets"
    mirrored_files = 0

    for entry in entries:
        if not _is_public_asset_mirror_entry(entry):
            continue

        mirrored_files += _copy_public_asset_mirror_entry(
            destination_root, assets_root, entry
        )

    return mirrored_files


def _path_key(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _one_to_one_public_asset_package_data_paths(root: Path) -> list[Path]:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    package_data = pyproject["tool"]["setuptools"]["package-data"]["coglang"]
    prefix = "_public_assets/"
    return sorted(
        Path(item.removeprefix(prefix))
        for item in package_data
        if item.startswith(prefix) and "*" not in item
    )


def _manifest_public_asset_file_destinations(root: Path) -> list[Path]:
    payload = load_public_repo_extract_manifest(root)
    return sorted(
        Path(str(entry["destination"]))
        for entry in payload.get("entries", [])
        if entry.get("kind") == "file" and _is_public_asset_mirror_entry(entry)
    )


def check_public_assets_mirror(project_root: Path | None = None) -> dict[str, Any]:
    root = project_root or _project_root()
    payload = load_public_repo_extract_manifest(root)
    assets_root = root / PUBLIC_ASSETS_MIRROR_ROOT
    package_data_paths = _one_to_one_public_asset_package_data_paths(root)
    manifest_file_paths = _manifest_public_asset_file_destinations(root)
    package_data_set = {str(path).replace("\\", "/") for path in package_data_paths}
    manifest_file_set = {str(path).replace("\\", "/") for path in manifest_file_paths}

    checked_file_count = 0
    missing_package_data_entries = sorted(manifest_file_set - package_data_set)
    extra_package_data_entries = sorted(package_data_set - manifest_file_set)
    missing_sources: list[str] = []
    missing_mirrors: list[str] = []
    mismatched_mirrors: list[str] = []

    for relative_path in package_data_paths:
        checked_file_count += 1
        source_file = root / relative_path
        mirror_file = assets_root / relative_path
        if not source_file.exists():
            missing_sources.append(_path_key(source_file, root))
            continue
        if not mirror_file.exists():
            missing_mirrors.append(_path_key(mirror_file, root))
            continue
        if source_file.read_bytes() != mirror_file.read_bytes():
            mismatched_mirrors.append(_path_key(mirror_file, root))

    ok = not (
        missing_package_data_entries
        or extra_package_data_entries
        or missing_sources
        or missing_mirrors
        or mismatched_mirrors
    )
    return {
        "ok": ok,
        "manifest_path": payload["path"],
        "checked_file_count": checked_file_count,
        "missing_package_data_entries": missing_package_data_entries,
        "extra_package_data_entries": extra_package_data_entries,
        "missing_sources": sorted(missing_sources),
        "missing_mirrors": sorted(missing_mirrors),
        "mismatched_mirrors": sorted(mismatched_mirrors),
    }


def sync_public_assets_mirror(project_root: Path | None = None) -> dict[str, Any]:
    root = project_root or _project_root()
    payload = load_public_repo_extract_manifest(root)
    assets_root = root / PUBLIC_ASSETS_MIRROR_ROOT
    mirrored_files = 0
    for relative_path in _manifest_public_asset_file_destinations(root):
        source_file = root / relative_path
        mirror_file = assets_root / relative_path
        if not source_file.exists():
            continue
        mirror_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, mirror_file)
        mirrored_files += 1
    check = check_public_assets_mirror(root)
    return {
        "ok": check["ok"],
        "manifest_path": payload["path"],
        "mirrored_file_count": mirrored_files,
        "check": check,
    }


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
        if not source.exists():
            source = root / Path(entry["destination"])
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
        "schema_version": PUBLIC_REPO_EXTRACT_RUN_SCHEMA_VERSION,
        "manifest_path": payload["path"],
        "destination_root": str(destination_root),
        "entry_count": len(entries),
        "copied_trees": copied_trees,
        "copied_files": copied_files,
        "mirrored_asset_files": mirrored_files,
    }
