from __future__ import annotations

import json
from collections import Counter
from typing import Any

import networkx as nx

from coglang import PythonCogLangExecutor, canonicalize, parse
from coglang.executor import Observer
from coglang.preflight import preflight_expression


MODEL_OUTPUTS = [
    {
        "event_id": "model-read-risks",
        "expression": 'Trace[Query[n_, Equal[Get[n_, "kind"], "Risk"], {"k": 5}]]',
        "enabled_capabilities": ["graph.read"],
    },
    {
        "event_id": "model-propose-memory",
        "expression": (
            'Create["Entity", {"id": "memory-1", "kind": "Memory", '
            '"title": "Keep evidence before execution", "confidence": 0.9}]'
        ),
        "enabled_capabilities": ["graph.read", "graph.write"],
    },
]


class TraceRecorder(Observer):
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def on_trace(self, expr: Any, result: Any, depth: int) -> None:
        self.events.append(
            {
                "expr": canonicalize(expr),
                "result": _render_result(result),
                "depth": depth,
            }
        )

    def on_assert_fail(self, message: str, depth: int) -> None:
        self.events.append({"assert_fail": message, "depth": depth})


def _render_result(value: Any) -> Any:
    return canonicalize(value) if hasattr(value, "head") else value


def _action_for(decision: str) -> str:
    if decision in {"accepted", "accepted_with_warnings"}:
        return "allow"
    if decision in {"requires_review", "cannot_estimate"}:
        return "queue_review"
    return "reject"


def _seed_executor() -> tuple[PythonCogLangExecutor, TraceRecorder]:
    graph = nx.DiGraph()
    graph.add_node("risk-1", kind="Risk", title="Unreviewed write", confidence=1.0)
    graph.add_node("decision-1", kind="Decision", title="Keep HRC narrow", confidence=1.0)
    recorder = TraceRecorder()
    return PythonCogLangExecutor(graph, observer=recorder), recorder


def run_demo() -> dict[str, Any]:
    executor, recorder = _seed_executor()
    records: list[dict[str, Any]] = []

    for output in MODEL_OUTPUTS:
        expr = parse(str(output["expression"]))
        canonical = None if expr.head == "ParseError" else canonicalize(expr)
        decision = preflight_expression(
            expr,
            graph=executor.graph_backend.graph,
            correlation_id=str(output["event_id"]),
            enabled_capabilities=list(output["enabled_capabilities"]),
        ).to_dict()
        action = _action_for(str(decision["decision"]))
        trace_start = len(recorder.events)
        executed = action == "allow"
        result = _render_result(executor.execute(expr)) if executed else None
        effect_summary = decision.get("effect_summary") or {}
        records.append(
            {
                "event_id": output["event_id"],
                "source_expression": output["expression"],
                "canonical_expression": canonical,
                "expression_hash": effect_summary.get("expression_hash"),
                "preflight_decision": decision["decision"],
                "effects": effect_summary.get("effects", []),
                "audit_action": action,
                "executed": executed,
                "execution_result": result,
                "trace": recorder.events[trace_start:],
            }
        )

    action_counts = Counter(str(record["audit_action"]) for record in records)
    return {
        "tool": "coglang-readme-end-to-end-audit-demo",
        "ok": True,
        "provider_sdk": False,
        "network": False,
        "hrc_contract_expanded": False,
        "record_count": len(records),
        "audit_action_counts": dict(sorted(action_counts.items())),
        "records": records,
    }


def main() -> int:
    print(json.dumps(run_demo(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
