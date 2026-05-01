from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .parser import CogLangExpr, canonicalize, parse
from .schema_versions import (
    EFFECT_SUMMARY_SCHEMA_VERSION,
    GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION,
    GRAPH_BUDGET_SCHEMA_VERSION,
    PREFLIGHT_DECISION_SCHEMA_VERSION,
    PREFLIGHT_FIXTURE_RESULT_SCHEMA_VERSION,
    PREFLIGHT_FIXTURE_SCHEMA_VERSION,
    STATIC_PREFLIGHT_ESTIMATOR,
)
from .validator import valid_coglang
from .vocab import OPAQUE_ARG_HEADS

DEFAULT_PREFLIGHT_FIXTURE = "preflight_minimal_v0_1.json"

EFFECT_CATEGORIES = frozenset(
    {
        "pure",
        "graph.read",
        "graph.traverse",
        "graph.write",
        "graph.delete",
        "graph.unify",
        "meta.trace",
        "host.submit",
        "host.policy",
        "human.review",
        "external.tool",
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
        # Proposal spelling from the v1.2 vocabulary note.
        "BudgetExceeded",
        "HostCostUnsupported",
        "PathExplosion",
        "PreflightRejected",
        "ReviewRequired",
        "CapabilityRequired",
        "Timeout",
        "TraversalLimitExceeded",
        "ResultLimitExceeded",
        "UnificationLimitExceeded",
        # Finer-grained implementation spelling; canonical names are not frozen.
        "PathLimitExceeded",
        "RecursionLimitExceeded",
        "UnificationBranchLimitExceeded",
        "IntermediateBindingLimitExceeded",
        "ExecutionTimeout",
        "MemoryBudgetExceeded",
    }
)

_EFFECT_ORDER = (
    "pure",
    "graph.read",
    "graph.traverse",
    "graph.write",
    "graph.delete",
    "graph.unify",
    "meta.trace",
    "host.submit",
    "host.policy",
    "human.review",
    "external.tool",
    "external.io",
)
_READ_HEADS = frozenset({"AllNodes", "Get", "Query"})
_TRAVERSE_HEADS = frozenset({"Traverse"})
_WRITE_HEADS = frozenset({"Create", "Update"})
_DELETE_HEADS = frozenset({"Delete"})
_UNIFY_HEADS = OPAQUE_ARG_HEADS
_TRACE_HEADS = frozenset({"Assert", "Compare", "Explain", "Trace"})
_HOST_SUBMIT_HEADS = frozenset({"Send"})
_EXTERNAL_TOOL_HEADS = frozenset(
    {"Decompose", "Defer", "Estimate", "Explore", "Inspect", "Instantiate", "Merge", "Probe", "Resume"}
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


def _coerce_expr(expr_or_source: CogLangExpr | str) -> CogLangExpr:
    if isinstance(expr_or_source, CogLangExpr):
        return expr_or_source
    if isinstance(expr_or_source, str):
        return parse(expr_or_source)
    raise TypeError("preflight expects a CogLangExpr or source string")


def _iter_exprs(value: Any) -> list[CogLangExpr]:
    found: list[CogLangExpr] = []
    if isinstance(value, CogLangExpr):
        found.append(value)
        if value.head in OPAQUE_ARG_HEADS:
            return found
        for arg in value.args:
            found.extend(_iter_exprs(arg))
        return found
    if isinstance(value, dict):
        for item in value.values():
            found.extend(_iter_exprs(item))
        return found
    if isinstance(value, (list, tuple)):
        for item in value:
            found.extend(_iter_exprs(item))
    return found


def _max_traversal_depth(value: Any, current_depth: int = 0) -> int:
    if isinstance(value, CogLangExpr):
        next_depth = current_depth + 1 if value.head in _TRAVERSE_HEADS else current_depth
        max_depth = next_depth
        if value.head in OPAQUE_ARG_HEADS:
            return max_depth
        for arg in value.args:
            max_depth = max(max_depth, _max_traversal_depth(arg, next_depth))
        return max_depth
    if isinstance(value, dict):
        return max(
            (_max_traversal_depth(item, current_depth) for item in value.values()),
            default=current_depth,
        )
    if isinstance(value, (list, tuple)):
        return max(
            (_max_traversal_depth(item, current_depth) for item in value),
            default=current_depth,
        )
    return current_depth


def _ordered_effects(effects: set[str]) -> list[str]:
    return [effect for effect in _EFFECT_ORDER if effect in effects]


def _append_unique(items: list[str], *values: str) -> list[str]:
    result = list(items)
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _missing_capabilities(
    required_capabilities: list[str],
    enabled_capabilities: set[str] | list[str] | tuple[str, ...] | None,
) -> list[str]:
    if enabled_capabilities is None:
        return []
    enabled = {str(item) for item in enabled_capabilities}
    return [
        capability
        for capability in required_capabilities
        if capability not in enabled
    ]


def _with_policy_review(summary: "EffectSummary") -> "EffectSummary":
    return EffectSummary(
        expression_hash=summary.expression_hash,
        effects=_append_unique(summary.effects, "host.policy", "human.review"),
        required_capabilities=list(summary.required_capabilities),
        possible_errors=_append_unique(
            summary.possible_errors,
            "CapabilityRequired",
            "ReviewRequired",
        ),
        confidence=summary.confidence,
        notes=list(summary.notes),
        schema_version=summary.schema_version,
    )


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


def canonical_expression_hash(expr_or_source: CogLangExpr | str) -> str | None:
    """Return a stable SHA-256 hash over canonical expression text.

    Parse errors have no stable source expression, so the helper returns None
    instead of hashing the error envelope.
    """
    expr = _coerce_expr(expr_or_source)
    if expr.head == "ParseError":
        return None
    canonical = canonicalize(expr)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def default_graph_budget() -> GraphBudget:
    """Return the small bounded budget used by the v1.2 preflight examples."""
    return GraphBudget(
        max_traversal_depth=1,
        max_visited_nodes=1000,
        max_result_count=100,
        max_execution_ms=1000,
        host_cost_class="bounded",
    )


def default_preflight_fixture_path() -> Path:
    return Path(__file__).resolve().parent / "eval_fixtures" / DEFAULT_PREFLIGHT_FIXTURE


def load_preflight_fixture(path: str | Path | None = None) -> dict[str, Any]:
    fixture_path = Path(path) if path is not None else default_preflight_fixture_path()
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != PREFLIGHT_FIXTURE_SCHEMA_VERSION:
        raise ValueError("unsupported preflight fixture schema_version")
    if not isinstance(data.get("cases"), list):
        raise TypeError("preflight fixture must contain a cases list")
    data["path"] = str(fixture_path)
    return data


def _preflight_fixture_actual_value(payload: dict[str, Any], key: str) -> Any:
    effect_summary = payload.get("effect_summary") or {}
    budget_estimate = payload.get("budget_estimate") or {}
    values = {
        "decision": payload.get("decision"),
        "required_review": payload.get("required_review"),
        "reasons": payload.get("reasons"),
        "effects": effect_summary.get("effects"),
        "required_capabilities": effect_summary.get("required_capabilities"),
        "possible_errors": payload.get("possible_errors"),
        "estimate_confidence": budget_estimate.get("estimate_confidence"),
    }
    if key not in values:
        raise KeyError(f"unsupported preflight fixture expected key: {key}")
    return values[key]


def preflight_fixture_payload(path: str | Path | None = None) -> dict[str, Any]:
    """Run the minimal v1.2-candidate preflight fixture without executing expressions."""
    fixture = load_preflight_fixture(path)
    results: list[dict[str, Any]] = []

    for raw_case in fixture["cases"]:
        case = dict(raw_case)
        budget = (
            GraphBudget.from_dict(dict(case["budget"]))
            if isinstance(case.get("budget"), dict)
            else None
        )
        decision = preflight_expression(
            str(case["expression"]),
            budget=budget,
            correlation_id=case.get("correlation_id"),
            enabled_capabilities=case.get("enabled_capabilities"),
            require_review_for_writes=bool(case.get("require_review_for_writes", True)),
        )
        decision_payload = decision.to_dict()
        expected = dict(case["expected"])
        actual = {
            key: _preflight_fixture_actual_value(decision_payload, key)
            for key in expected
        }
        mismatches = [
            {
                "field": key,
                "expected": expected[key],
                "actual": actual[key],
            }
            for key in expected
            if actual[key] != expected[key]
        ]
        results.append(
            {
                "case_id": str(case["case_id"]),
                "description": str(case.get("description", "")),
                "expression": str(case["expression"]),
                "ok": not mismatches,
                "expected": expected,
                "actual": actual,
                "mismatches": mismatches,
                "decision": decision_payload,
            }
        )

    return {
        "schema_version": PREFLIGHT_FIXTURE_RESULT_SCHEMA_VERSION,
        "fixture_schema_version": PREFLIGHT_FIXTURE_SCHEMA_VERSION,
        "fixture_path": fixture["path"],
        "case_count": len(results),
        "ok": all(item["ok"] for item in results),
        "cases": results,
    }


def summarize_effects(
    expr_or_source: CogLangExpr | str,
    *,
    graph: Any = None,
) -> EffectSummary:
    """Conservatively summarize effects without executing the expression."""
    expr = _coerce_expr(expr_or_source)
    if expr.head == "ParseError":
        return EffectSummary(
            expression_hash=None,
            effects=["pure"],
            possible_errors=["ParseError"],
            confidence="known",
            notes=["input could not be parsed"],
        )

    effects: set[str] = set()
    possible_errors: list[str] = []
    notes: list[str] = []
    valid = valid_coglang(expr, graph=graph)

    if not valid:
        possible_errors.append("TypeError")
        notes.append("expression does not validate against the static vocabulary")

    for node in _iter_exprs(expr):
        head = node.head
        if head in _READ_HEADS:
            effects.add("graph.read")
        if head in _TRAVERSE_HEADS:
            effects.update({"graph.read", "graph.traverse"})
            possible_errors = _append_unique(possible_errors, "TraversalLimitExceeded")
        if head in _WRITE_HEADS:
            effects.add("graph.write")
        if head in _DELETE_HEADS:
            effects.update({"graph.write", "graph.delete"})
        if head in _UNIFY_HEADS:
            effects.add("graph.unify")
            possible_errors = _append_unique(possible_errors, "UnificationBranchLimitExceeded")
        if head in _TRACE_HEADS:
            effects.add("meta.trace")
        if head in _HOST_SUBMIT_HEADS:
            effects.add("host.submit")
            possible_errors = _append_unique(possible_errors, "StubError")
        if head in _EXTERNAL_TOOL_HEADS:
            effects.add("external.tool")
            possible_errors = _append_unique(possible_errors, "StubError")

    if not effects:
        effects.add("pure")

    required_capabilities: list[str] = []
    if "graph.read" in effects or "graph.traverse" in effects:
        required_capabilities.append("graph.read")
    if "graph.write" in effects or "graph.delete" in effects:
        required_capabilities.append("graph.write")
    if "graph.unify" in effects:
        required_capabilities.append("graph.unify")
    if "host.submit" in effects:
        required_capabilities.append("host.submit")
    if "external.tool" in effects:
        required_capabilities.append("external.tool")

    return EffectSummary(
        expression_hash=canonical_expression_hash(expr),
        effects=_ordered_effects(effects),
        required_capabilities=required_capabilities,
        possible_errors=possible_errors,
        confidence="known" if valid else "unknown",
        notes=notes,
    )


def estimate_graph_budget(
    expr_or_source: CogLangExpr | str,
    *,
    estimator: str = STATIC_PREFLIGHT_ESTIMATOR,
) -> GraphBudgetEstimate:
    """Return a structural cost estimate without inspecting a live graph."""
    expr = _coerce_expr(expr_or_source)
    if expr.head == "ParseError":
        return GraphBudgetEstimate(
            estimate_confidence="not_supported",
            estimator=estimator,
            notes=["cannot estimate a parse error"],
        )

    nodes = _iter_exprs(expr)
    traverse_count = sum(1 for node in nodes if node.head in _TRAVERSE_HEADS)
    traversal_depth = _max_traversal_depth(expr)
    unification_count = sum(1 for node in nodes if node.head in _UNIFY_HEADS)
    query_like_count = sum(1 for node in nodes if node.head in {"AllNodes", "Query"})

    notes: list[str] = []
    confidence = "known"
    estimated_result_count: int | None = 1
    estimated_visited_nodes: int | None = 0

    if query_like_count:
        confidence = "estimated"
        estimated_result_count = None
        estimated_visited_nodes = None
        notes.append("query result cardinality depends on host graph state")
    if traverse_count:
        confidence = "unknown"
        estimated_result_count = None
        estimated_visited_nodes = None
        notes.append("static helper does not inspect graph degree statistics")

    return GraphBudgetEstimate(
        estimated_traversal_depth=traversal_depth if traversal_depth else None,
        estimated_visited_nodes=estimated_visited_nodes,
        estimated_result_count=estimated_result_count,
        estimated_unification_branches=unification_count if unification_count else None,
        estimate_confidence=confidence,
        estimator=estimator,
        notes=notes,
    )


def preflight_expression(
    expr_or_source: CogLangExpr | str,
    *,
    budget: GraphBudget | None = None,
    correlation_id: str | None = None,
    graph: Any = None,
    enabled_capabilities: set[str] | list[str] | tuple[str, ...] | None = None,
    require_review_for_writes: bool = True,
) -> PreflightDecision:
    """Return a minimal static preflight decision for a CogLang expression."""
    expr = _coerce_expr(expr_or_source)
    applied_budget = budget or default_graph_budget()
    summary = summarize_effects(expr, graph=graph)
    estimate = estimate_graph_budget(expr)
    possible_errors = list(summary.possible_errors)

    if expr.head == "ParseError":
        return PreflightDecision(
            decision="rejected",
            reasons=["parse.error"],
            required_review=False,
            effect_summary=summary,
            budget=applied_budget,
            budget_estimate=estimate,
            possible_errors=possible_errors,
            correlation_id=correlation_id,
        )

    if not valid_coglang(expr, graph=graph):
        return PreflightDecision(
            decision="rejected",
            reasons=["validation.invalid"],
            required_review=False,
            effect_summary=summary,
            budget=applied_budget,
            budget_estimate=estimate,
            possible_errors=possible_errors,
            correlation_id=correlation_id,
        )

    missing_capabilities = _missing_capabilities(
        summary.required_capabilities,
        enabled_capabilities,
    )
    if missing_capabilities:
        possible_errors = _append_unique(possible_errors, "CapabilityRequired")
        missing_reasons = [
            f"capability.missing.{capability.replace('.', '_')}"
            for capability in missing_capabilities
        ]
        return PreflightDecision(
            decision="rejected",
            reasons=["capability.missing", *missing_reasons],
            required_review=False,
            effect_summary=summary,
            budget=applied_budget,
            budget_estimate=estimate,
            possible_errors=possible_errors,
            correlation_id=correlation_id,
        )

    if (
        estimate.estimated_traversal_depth is not None
        and applied_budget.max_traversal_depth is not None
        and estimate.estimated_traversal_depth > applied_budget.max_traversal_depth
    ):
        possible_errors = _append_unique(
            possible_errors,
            "BudgetExceeded",
            "TraversalLimitExceeded",
        )
        return PreflightDecision(
            decision="rejected",
            reasons=["budget.traversal_depth_exceeded"],
            required_review=False,
            effect_summary=summary,
            budget=applied_budget,
            budget_estimate=estimate,
            possible_errors=possible_errors,
            correlation_id=correlation_id,
        )

    if (
        estimate.estimated_result_count is not None
        and applied_budget.max_result_count is not None
        and estimate.estimated_result_count > applied_budget.max_result_count
    ):
        possible_errors = _append_unique(
            possible_errors,
            "BudgetExceeded",
            "ResultLimitExceeded",
        )
        return PreflightDecision(
            decision="rejected",
            reasons=["budget.result_count_exceeded"],
            required_review=False,
            effect_summary=summary,
            budget=applied_budget,
            budget_estimate=estimate,
            possible_errors=possible_errors,
            correlation_id=correlation_id,
        )

    if (
        estimate.estimated_unification_branches is not None
        and applied_budget.max_unification_branches is not None
        and estimate.estimated_unification_branches > applied_budget.max_unification_branches
    ):
        possible_errors = _append_unique(
            possible_errors,
            "BudgetExceeded",
            "UnificationLimitExceeded",
        )
        return PreflightDecision(
            decision="rejected",
            reasons=["budget.unification_branches_exceeded"],
            required_review=False,
            effect_summary=summary,
            budget=applied_budget,
            budget_estimate=estimate,
            possible_errors=possible_errors,
            correlation_id=correlation_id,
        )

    if "graph.traverse" in summary.effects and estimate.estimate_confidence == "unknown":
        possible_errors = _append_unique(possible_errors, "HostCostUnsupported")
        return PreflightDecision(
            decision="cannot_estimate",
            reasons=["budget.traversal_unbounded", "host.index_unknown"],
            required_review=True,
            effect_summary=_with_policy_review(summary),
            budget=applied_budget,
            budget_estimate=estimate,
            possible_errors=possible_errors,
            correlation_id=correlation_id,
        )

    if require_review_for_writes and (
        "graph.write" in summary.effects or "graph.delete" in summary.effects
    ):
        summary = _with_policy_review(summary)
        possible_errors = _append_unique(possible_errors, "CapabilityRequired", "ReviewRequired")
        return PreflightDecision(
            decision="requires_review",
            reasons=["effect.graph_write", "policy.review_required"],
            required_review=True,
            effect_summary=summary,
            budget=applied_budget,
            budget_estimate=estimate,
            possible_errors=possible_errors,
            correlation_id=correlation_id,
        )

    reasons = [
        f"effect.{effect.replace('.', '_')}"
        for effect in summary.effects
        if effect != "pure"
    ]
    if not reasons:
        reasons.append("effect.pure")
    reasons.append("budget.within_default")
    decision = "accepted_with_warnings" if summary.notes or estimate.notes else "accepted"
    return PreflightDecision(
        decision=decision,
        reasons=reasons,
        required_review=False,
        effect_summary=summary,
        budget=applied_budget,
        budget_estimate=estimate,
        possible_errors=possible_errors,
        correlation_id=correlation_id,
    )
