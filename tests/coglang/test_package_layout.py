from __future__ import annotations

from pathlib import Path


def test_coglang_executor_abc_surface_is_minimal():
    from coglang.executor import CogLangExecutor

    assert CogLangExecutor.__abstractmethods__ == frozenset(
        {
            "execute",
            "validate",
        }
    )
    assert len(CogLangExecutor.__abstractmethods__) <= 2


def test_minimal_coglang_executor_subclass_can_instantiate():
    from coglang.executor import CogLangExecutor, NullObserver

    class MinimalExecutor(CogLangExecutor):
        def execute(self, expr):
            return expr

        def validate(self, expr):
            return True

    executor = MinimalExecutor()

    assert executor.execute("ok") == "ok"
    assert executor.validate("ok") is True
    assert executor.execute_with_write_bundle_candidate("ok") == ("ok", None)
    assert executor.peek_write_bundle_candidate() is None
    assert executor.consume_write_bundle_candidate() is None
    assert executor.validate_write_bundle_candidate() == (True, [])
    assert executor.validate_write_bundle_candidate(object()) == (
        False,
        ["write bundle candidates are not supported by this executor"],
    )
    executor.set_observer(NullObserver())


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
