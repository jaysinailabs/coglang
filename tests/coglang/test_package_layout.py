from __future__ import annotations

from pathlib import Path


def test_coglang_package_uses_relative_internal_imports():
    root = Path(__file__).resolve().parents[2]
    package_dir = root / "src" / "coglang"
    offenders: list[str] = []
    legacy_namespace = "".join(["lo", "gos", ".", "cog", "lang"])
    forbidden_imports = [
        "from " + legacy_namespace,
        "import " + legacy_namespace,
    ]
    for path in package_dir.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if any(marker in text for marker in forbidden_imports):
            offenders.append(str(path.relative_to(root)).replace("\\", "/"))
    assert offenders == []
