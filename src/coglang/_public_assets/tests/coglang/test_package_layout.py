from __future__ import annotations

from pathlib import Path


def test_coglang_package_uses_relative_internal_imports():
    root = Path(__file__).resolve().parents[2]
    package_dir = root / "src" / "logos" / "coglang"
    offenders: list[str] = []
    for path in package_dir.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "from logos.coglang" in text or "import logos.coglang" in text:
            offenders.append(str(path.relative_to(root)).replace("\\", "/"))
    assert offenders == []
