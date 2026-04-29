from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

EFFECT_SUMMARY_SCHEMA_VERSION = "coglang-effect-summary/v0.1"
GRAPH_BUDGET_SCHEMA_VERSION = "coglang-graph-budget/v0.1"
GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION = "coglang-graph-budget-estimate/v0.1"
PREFLIGHT_DECISION_SCHEMA_VERSION = "coglang-preflight-decision/v0.1"

EFFECT_CATEGORIES = frozenset(
    {
        "pure",
        "graph.read",
        "graph.traverse",
        "graph.write",
        "host.policy",
        "human.review",
        "external.io",
    }
)
PREFLIGHT_DECISIONS = frozenset(
    {
        "accepted",
        "accepted_with_warnings",
        "requires_review",
        "rejected",
        "cannot_estimate",
    }
)
BUDGET_ERROR_CATEGORIES = frozenset(
    {
        "HostCostUnsupported",
        "TraversalLimitExceeded",
        "ResultLimitExceeded",
        "PathLimitExceeded",
        "RecursionLimitExceeded",
        "UnificationBranchLimitExceeded",
        "IntermediateBindingLimitExceeded",
        "ExecutionTimeout",
        "MemoryBudgetExceeded",
    }
)


def _string_list(data: dict[str, Any], key: str) -> list[str]:
    return [str(item) for item in data.get(key, [])]


def _optional_int(data: dict[str, Any], key: str) -> int | None:
    value = data.get(key)
    if value is None:
        return None
    return int(value)


def _loads_object(payload: str) -> dict[str, Any]:
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise TypeError("expected a JSON object")
    return data


@dataclass(frozen=True)
class EffectSummary:
    """Candidate v1.2 preflight effect summary typed object.

    This object is intentionally transport-only for now: it records the public
    vocabulary shape without changing v1.1 execution semantics.
    """

    expression_hash: str | None
    effects: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    possible_errors: list[str] = field(default_factory=list)
    confidence: str = "unknown"
    notes: list[str] = field(default_factory=list)
    schema_version: str = EFFECT_SUMMARY_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "expression_hash": self.expression_hash,
            "effects": list(self.effects),
            "required_capabilities": list(self.required_capabilities),
            "possible_errors": list(self.possible_errors),
            "confidence": self.confidence,
        }
        if self.notes:
            payload["notes"] = list(self.notes)
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EffectSummary":
        expression_hash = data.get("expression_hash")
        return cls(
            schema_version=str(data.get("schema_version", EFFECT_SUMMARY_SCHEMA_VERSION)),
            expression_hash=None if expression_hash is None else str(expression_hash),
            effects=_string_list(data, "effects"),
            required_capabilities=_string_list(data, "required_capabilities"),
            possible_errors=_string_list(data, "possible_errors"),
            confidence=str(data.get("confidence", "unknown")),
            notes=_string_list(data, "notes"),
        )

    @classmethod
    def from_json(cls, payload: str) -> "EffectSummary":
        return cls.from_dict(_loads_object(payload))


@dataclass(frozen=True)
class GraphBudget:
    """Candidate v1.2 host-owned budget limits for graph computation."""

    max_traversal_depth: int | None = None
    max_visited_nodes: int | None = None
    max_visited_edges: int | None = None
    max_result_count: int | None = None
    max_path_count: int | None = None
    max_recursion_depth: int | None = None
    max_unification_branches: int | None = None
    max_intermediate_bindings: int | None = None
    max_execution_ms: int | None = None
    max_memory_bytes: int | None = None
    host_cost_class: str | None = None
    schema_version: str = GRAPH_BUDGET_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"schema_version": self.schema_version}
        for key in (
            "max_traversal_depth",
            "max_visited_nodes",
            "max_visited_edges",
            "max_result_count",
            "max_path_count",
            "max_recursion_depth",
            "max_unification_branches",
            "max_intermediate_bindings",
            "max_execution_ms",
            "max_memory_bytes",
            "host_cost_class",
        ):
            value = getattr(self, key)
            if value is not None:
                payload[key] = value
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GraphBudget":
        host_cost_class = data.get("host_cost_class")
        return cls(
            schema_version=str(data.get("schema_version", GRAPH_BUDGET_SCHEMA_VERSION)),
            max_traversal_depth=_optional_int(data, "max_traversal_depth"),
            max_visited_nodes=_optional_int(data, "max_visited_nodes"),
            max_visited_edges=_optional_int(data, "max_visited_edges"),
            max_result_count=_optional_int(data, "max_result_count"),
            max_path_count=_optional_int(data, "max_path_count"),
            max_recursion_depth=_optional_int(data, "max_recursion_depth"),
            max_unification_branches=_optional_int(data, "max_unification_branches"),
            max_intermediate_bindings=_optional_int(data, "max_intermediate_bindings"),
            max_execution_ms=_optional_int(data, "max_execution_ms"),
            max_memory_bytes=_optional_int(data, "max_memory_bytes"),
            host_cost_class=None if host_cost_class is None else str(host_cost_class),
        )

    @classmethod
    def from_json(cls, payload: str) -> "GraphBudget":
        return cls.from_dict(_loads_object(payload))


@dataclass(frozen=True)
class GraphBudgetEstimate:
    """Candidate v1.2 host-side estimate for graph computation cost."""

    estimated_traversal_depth: int | None = None
    estimated_visited_nodes: int | None = None
    estimated_visited_edges: int | None = None
    estimated_result_count: int | None = None
    estimated_path_count: int | None = None
    estimated_unification_branches: int | None = None
    estimate_confidence: str = "unknown"
    estimator: str | None = None
    notes: list[str] = field(default_factory=list)
    schema_version: str = GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "estimate_confidence": self.estimate_confidence,
        }
        for key in (
            "estimated_traversal_depth",
            "estimated_visited_nodes",
            "estimated_visited_edges",
            "estimated_result_count",
            "estimated_path_count",
            "estimated_unification_branches",
        ):
            value = getattr(self, key)
            if value is not None:
                payload[key] = value
        if self.estimator is not None:
            payload["estimator"] = self.estimator
        if self.notes:
            payload["notes"] = list(self.notes)
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GraphBudgetEstimate":
        estimator = data.get("estimator")
        return cls(
            schema_version=str(data.get("schema_version", GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION)),
            estimated_traversal_depth=_optional_int(data, "estimated_traversal_depth"),
            estimated_visited_nodes=_optional_int(data, "estimated_visited_nodes"),
            estimated_visited_edges=_optional_int(data, "estimated_visited_edges"),
            estimated_result_count=_optional_int(data, "estimated_result_count"),
            estimated_path_count=_optional_int(data, "estimated_path_count"),
            estimated_unification_branches=_optional_int(data, "estimated_unification_branches"),
            estimate_confidence=str(data.get("estimate_confidence", "unknown")),
            estimator=None if estimator is None else str(estimator),
            notes=_string_list(data, "notes"),
        )

    @classmethod
    def from_json(cls, payload: str) -> "GraphBudgetEstimate":
        return cls.from_dict(_loads_object(payload))


@dataclass(frozen=True)
class PreflightDecision:
    """Candidate v1.2 host-visible pre-execution decision object."""

    decision: str
    reasons: list[str] = field(default_factory=list)
    required_review: bool = False
    effect_summary: EffectSummary | None = None
    budget: GraphBudget | None = None
    budget_estimate: GraphBudgetEstimate | None = None
    possible_errors: list[str] = field(default_factory=list)
    correlation_id: str | None = None
    schema_version: str = PREFLIGHT_DECISION_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "decision": self.decision,
            "reasons": list(self.reasons),
            "required_review": self.required_review,
            "effect_summary": (
                self.effect_summary.to_dict() if self.effect_summary is not None else None
            ),
            "budget": self.budget.to_dict() if self.budget is not None else None,
            "budget_estimate": (
                self.budget_estimate.to_dict() if self.budget_estimate is not None else None
            ),
            "possible_errors": list(self.possible_errors),
        }
        if self.correlation_id is not None:
            payload["correlation_id"] = self.correlation_id
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PreflightDecision":
        effect_summary = data.get("effect_summary")
        budget = data.get("budget")
        budget_estimate = data.get("budget_estimate")
        correlation_id = data.get("correlation_id")
        return cls(
            schema_version=str(data.get("schema_version", PREFLIGHT_DECISION_SCHEMA_VERSION)),
            decision=str(data["decision"]),
            reasons=_string_list(data, "reasons"),
            required_review=bool(data.get("required_review", False)),
            effect_summary=(
                EffectSummary.from_dict(dict(effect_summary))
                if effect_summary is not None
                else None
            ),
            budget=GraphBudget.from_dict(dict(budget)) if budget is not None else None,
            budget_estimate=(
                GraphBudgetEstimate.from_dict(dict(budget_estimate))
                if budget_estimate is not None
                else None
            ),
            possible_errors=_string_list(data, "possible_errors"),
            correlation_id=None if correlation_id is None else str(correlation_id),
        )

    @classmethod
    def from_json(cls, payload: str) -> "PreflightDecision":
        return cls.from_dict(_loads_object(payload))
