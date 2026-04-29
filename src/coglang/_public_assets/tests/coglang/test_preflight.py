import json

from coglang import EffectSummary as PublicEffectSummary
from coglang import GraphBudget as PublicGraphBudget
from coglang import GraphBudgetEstimate as PublicGraphBudgetEstimate
from coglang import PreflightDecision as PublicPreflightDecision
from coglang.preflight import (
    BUDGET_ERROR_CATEGORIES,
    EFFECT_CATEGORIES,
    EFFECT_SUMMARY_SCHEMA_VERSION,
    GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION,
    GRAPH_BUDGET_SCHEMA_VERSION,
    PREFLIGHT_DECISION_SCHEMA_VERSION,
    PREFLIGHT_DECISIONS,
    EffectSummary,
    GraphBudget,
    GraphBudgetEstimate,
    PreflightDecision,
)


def _accepted_preflight_decision() -> PreflightDecision:
    return PreflightDecision(
        decision="accepted",
        reasons=["effect.graph_read", "budget.within_default"],
        required_review=False,
        effect_summary=EffectSummary(
            expression_hash="sha256:example",
            effects=["graph.read"],
            required_capabilities=["graph.read"],
            possible_errors=[],
            confidence="known",
        ),
        budget=GraphBudget(
            max_traversal_depth=1,
            max_visited_nodes=1000,
            max_result_count=100,
            max_execution_ms=1000,
            host_cost_class="bounded",
        ),
        budget_estimate=GraphBudgetEstimate(
            estimated_traversal_depth=0,
            estimated_visited_nodes=1000,
            estimated_result_count=100,
            estimate_confidence="estimated",
            estimator="local-host-v0.1",
        ),
        possible_errors=[],
        correlation_id="preflight-example-001",
    )


def test_effect_summary_roundtrip_dict_json():
    summary = EffectSummary(
        expression_hash="sha256:test",
        effects=["graph.read", "graph.traverse"],
        required_capabilities=["graph.read"],
        possible_errors=["TraversalLimitExceeded"],
        confidence="estimated",
        notes=["fanout depends on host statistics"],
    )

    payload = summary.to_dict()
    assert payload["schema_version"] == EFFECT_SUMMARY_SCHEMA_VERSION
    assert payload["notes"] == ["fanout depends on host statistics"]
    assert EffectSummary.from_dict(payload) == summary
    assert EffectSummary.from_json(summary.to_json()) == summary


def test_graph_budget_roundtrip_preserves_present_budget_fields():
    budget = GraphBudget(
        max_traversal_depth=2,
        max_visited_nodes=100,
        max_visited_edges=250,
        max_result_count=10,
        max_path_count=5,
        max_recursion_depth=4,
        max_unification_branches=20,
        max_intermediate_bindings=50,
        max_execution_ms=1000,
        max_memory_bytes=4_194_304,
        host_cost_class="small",
    )

    payload = budget.to_dict()
    assert payload["schema_version"] == GRAPH_BUDGET_SCHEMA_VERSION
    assert payload["max_memory_bytes"] == 4_194_304
    assert GraphBudget.from_dict(payload) == budget
    assert GraphBudget.from_json(budget.to_json()) == budget


def test_graph_budget_omits_unset_optional_fields():
    payload = GraphBudget(max_result_count=1).to_dict()

    assert payload == {
        "schema_version": GRAPH_BUDGET_SCHEMA_VERSION,
        "max_result_count": 1,
    }


def test_graph_budget_estimate_roundtrip_dict_json():
    estimate = GraphBudgetEstimate(
        estimated_visited_nodes=1000,
        estimated_result_count=100,
        estimate_confidence="estimated",
        estimator="local-host-v0.1",
        notes=["index statistics are approximate"],
    )

    payload = estimate.to_dict()
    assert payload["schema_version"] == GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION
    assert payload["estimate_confidence"] == "estimated"
    assert GraphBudgetEstimate.from_dict(payload) == estimate
    assert GraphBudgetEstimate.from_json(estimate.to_json()) == estimate


def test_preflight_decision_roundtrip_nested_objects():
    decision = _accepted_preflight_decision()

    payload = decision.to_dict()
    assert payload["schema_version"] == PREFLIGHT_DECISION_SCHEMA_VERSION
    assert payload["effect_summary"]["effects"] == ["graph.read"]
    assert payload["budget"]["host_cost_class"] == "bounded"
    assert payload["budget_estimate"]["estimator"] == "local-host-v0.1"
    assert PreflightDecision.from_dict(payload) == decision
    assert PreflightDecision.from_json(decision.to_json()) == decision


def test_preflight_decision_json_matches_document_shape():
    payload = json.loads(_accepted_preflight_decision().to_json())

    assert payload == {
        "schema_version": "coglang-preflight-decision/v0.1",
        "decision": "accepted",
        "reasons": ["effect.graph_read", "budget.within_default"],
        "required_review": False,
        "effect_summary": {
            "schema_version": "coglang-effect-summary/v0.1",
            "expression_hash": "sha256:example",
            "effects": ["graph.read"],
            "required_capabilities": ["graph.read"],
            "possible_errors": [],
            "confidence": "known",
        },
        "budget": {
            "schema_version": "coglang-graph-budget/v0.1",
            "max_traversal_depth": 1,
            "max_visited_nodes": 1000,
            "max_result_count": 100,
            "max_execution_ms": 1000,
            "host_cost_class": "bounded",
        },
        "budget_estimate": {
            "schema_version": "coglang-graph-budget-estimate/v0.1",
            "estimated_traversal_depth": 0,
            "estimated_visited_nodes": 1000,
            "estimated_result_count": 100,
            "estimate_confidence": "estimated",
            "estimator": "local-host-v0.1",
        },
        "possible_errors": [],
        "correlation_id": "preflight-example-001",
    }


def test_preflight_candidate_vocabularies_are_exposed():
    assert "graph.read" in EFFECT_CATEGORIES
    assert "cannot_estimate" in PREFLIGHT_DECISIONS
    assert "TraversalLimitExceeded" in BUDGET_ERROR_CATEGORIES


def test_preflight_public_exports():
    assert PublicEffectSummary is EffectSummary
    assert PublicGraphBudget is GraphBudget
    assert PublicGraphBudgetEstimate is GraphBudgetEstimate
    assert PublicPreflightDecision is PreflightDecision
