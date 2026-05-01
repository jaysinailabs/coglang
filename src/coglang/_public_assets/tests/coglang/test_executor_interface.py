from __future__ import annotations

from typing import Any

from coglang.executor import (
    CogLangExecutor,
    NullObserver,
    PythonCogLangExecutor,
    _typed_list_to_dicts,
    _typed_to_dict,
    _typed_to_json,
)
from coglang.parser import CogLangExpr


class MinimalExecutor(CogLangExecutor):
    """Smallest valid executor implementation for interface-regression tests."""

    def execute(self, expr: Any) -> Any:
        return expr

    def validate(self, expr: Any) -> bool:
        return True


class TinyTypedEnvelope:
    def __init__(self, value: str) -> None:
        self.value = value

    def to_dict(self) -> dict[str, Any]:
        return {"value": self.value}

    def to_json(self) -> str:
        return f'{{"value":"{self.value}"}}'


def test_coglang_executor_abc_requires_only_semantic_minimum():
    assert CogLangExecutor.__abstractmethods__ == frozenset({"execute", "validate"})


def test_minimal_executor_implementation_does_not_need_host_local_helpers():
    executor = MinimalExecutor()
    expr = CogLangExpr("True", ())
    observer = NullObserver()

    assert executor.execute(expr) == expr
    assert executor.validate(expr) is True
    assert executor.execute_with_write_bundle_candidate(expr) == (expr, None)
    assert executor.peek_write_bundle_candidate() is None
    assert executor.consume_write_bundle_candidate() is None
    assert executor.validate_write_bundle_candidate() == (True, [])

    executor.set_observer(observer)
    assert executor.observer is observer
    assert not hasattr(executor, "query_local_write_result")
    assert not hasattr(executor, "query_local_write_result_json")


def test_python_executor_keeps_host_local_helpers_concrete():
    assert "query_local_write_result" not in CogLangExecutor.__dict__
    assert "query_local_write_result_json" not in CogLangExecutor.__dict__
    assert callable(getattr(PythonCogLangExecutor, "query_local_write_result"))
    assert callable(getattr(PythonCogLangExecutor, "query_local_write_result_json"))


def test_executor_typed_serialization_helpers_preserve_missing_values():
    envelope = TinyTypedEnvelope("ok")

    assert _typed_to_dict(None) is None
    assert _typed_to_json(None) is None
    assert _typed_to_dict(envelope) == {"value": "ok"}
    assert _typed_to_json(envelope) == '{"value":"ok"}'
    assert _typed_list_to_dicts([envelope]) == [{"value": "ok"}]
