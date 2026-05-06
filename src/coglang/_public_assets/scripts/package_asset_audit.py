from __future__ import annotations

import json
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any


def _classify(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.endswith(".md"):
        return "markdown"
    if "/examples/" in normalized:
        return "examples"
    if "/tests/" in normalized:
        return "tests"
    if "/internal_schemas/" in normalized or normalized.endswith(".json"):
        return "schemas_and_json"
    if "/scripts/" in normalized:
        return "scripts"
    return "metadata_or_other"


def audit_package_assets(root: Path) -> dict[str, Any]:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    patterns = pyproject["tool"]["setuptools"]["package-data"]["coglang"]
    package_root = root / "src" / "coglang"
    expanded: list[Path] = []
    for pattern in patterns:
        expanded.extend(path for path in package_root.glob(pattern) if path.is_file())

    unique = sorted(set(expanded))
    public_assets = [path for path in unique if "_public_assets" in path.parts]
    public_relative = [
        path.relative_to(package_root).as_posix()
        for path in public_assets
    ]
    category_counts = Counter(_classify(path) for path in public_relative)
    total_bytes = sum(path.stat().st_size for path in unique)
    public_asset_bytes = sum(path.stat().st_size for path in public_assets)
    markdown_files = [path for path in public_relative if path.endswith(".md")]

    return {
        "tool": "coglang-package-asset-audit",
        "ok": True,
        "scope": "evidence-only-for-future-wheel-trimming",
        "package_data_pattern_count": len(patterns),
        "expanded_file_count": len(unique),
        "expanded_bytes": total_bytes,
        "public_asset_file_count": len(public_assets),
        "public_asset_bytes": public_asset_bytes,
        "public_asset_markdown_file_count": len(markdown_files),
        "public_asset_category_counts": dict(sorted(category_counts.items())),
        "trim_candidates": [
            "historical release notes",
            "promotion and announcement material",
            "future-work governance notes",
            "mirrored tests not needed by installed runtime",
        ],
        "non_goals": [
            "does not change package-data",
            "does not delete public assets",
            "does not redefine release-check",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[0]).resolve() if args else Path.cwd()
    print(json.dumps(audit_package_assets(root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
