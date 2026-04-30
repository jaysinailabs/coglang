import json

import coglang.preflight as preflight_module
from coglang import EffectSummary as PublicEffectSummary
from coglang import GraphBudget as PublicGraphBudget
from coglang import GraphBudgetEstimate as PublicGraphBudgetEstimate
from coglang import PreflightDecision as PublicPreflightDecision
from coglang import preflight_expression as public_preflight_expression
from coglang import preflight_fixture_payload as public_preflight_fixture_payload
from coglang.parser import parse
from coglang.preflight import (
    BUDGET_ERROR_CATEGORIES,
    EFFECT_CATEGORIES,
    EFFECT_SUMMARY_SCHEMA_VERSION,
    GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION,
    GRAPH_BUDGET_SCHEMA_VERSION,
    PREFLIGHT_DECISION_SCHEMA_VERSION,
    PREFLIGHT_DECISIONS,
    PREFLIGHT_FIXTURE_RESULT_SCHEMA_VERSION,
    PREFLIGHT_FIXTURE_SCHEMA_VERSION,
    EffectSummary,
    GraphBudget,
    GraphBudgetEstimate,
    PreflightDecision,
    canonical_expression_hash,
    default_graph_budget,
    default_preflight_fixture_path,
    estimate_graph_budget,
    load_preflight_fixture,
    preflight_expression,
    preflight_fixture_payload,
    summarize_effects,
)
from coglang.vocab import OPAQUE_ARG_HEADS


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
        estimated_traversal_depth=2,
        estimated_visited_nodes=1000,
        estimated_visited_edges=2500,
        estimated_result_count=100,
        estimated_path_count=50,
        estimated_unification_branches=10,
        estimate_confidence="estimated",
        estimator="local-host-v0.1",
        notes=["index statistics are approximate"],
    )

    payload = estimate.to_dict()
    assert payload["schema_version"] == GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION
    assert payload["estimated_visited_edges"] == 2500
    assert payload["estimated_path_count"] == 50
    assert payload["estimated_unification_branches"] == 10
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


def test_preflight_decision_roundtrip_preserves_null_nested_objects():
    decision = PreflightDecision(
        decision="cannot_estimate",
        reasons=["budget.host_unsupported"],
        required_review=True,
        effect_summary=None,
        budget=None,
        budget_estimate=None,
        possible_errors=["HostCostUnsupported"],
        correlation_id="preflight-null-001",
    )

    payload = decision.to_dict()
    assert payload["effect_summary"] is None
    assert payload["budget"] is None
    assert payload["budget_estimate"] is None
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
    assert "graph.delete" in EFFECT_CATEGORIES
    assert "graph.unify" in EFFECT_CATEGORIES
    assert "meta.trace" in EFFECT_CATEGORIES
    assert "external.tool" in EFFECT_CATEGORIES
    assert "cannot_estimate" in PREFLIGHT_DECISIONS
    assert {
        "BudgetExceeded",
        "TraversalLimitExceeded",
        "ResultLimitExceeded",
        "UnificationLimitExceeded",
        "PathExplosion",
        "Timeout",
        "HostCostUnsupported",
        "PreflightRejected",
        "ReviewRequired",
        "CapabilityRequired",
    } <= BUDGET_ERROR_CATEGORIES


def test_preflight_public_exports():
    assert PublicEffectSummary is EffectSummary
    assert PublicGraphBudget is GraphBudget
    assert PublicGraphBudgetEstimate is GraphBudgetEstimate
    assert PublicPreflightDecision is PreflightDecision
    assert public_preflight_expression is preflight_expression
    assert public_preflight_fixture_payload is preflight_fixture_payload


def test_preflight_uses_shared_opaque_argument_metadata():
    assert preflight_module.OPAQUE_ARG_HEADS is OPAQUE_ARG_HEADS


def test_preflight_fixture_loads_minimal_cases():
    fixture = load_preflight_fixture()

    assert fixture["schema_version"] == PREFLIGHT_FIXTURE_SCHEMA_VERSION
    assert fixture["name"] == "minimal-v1-2-candidate-preflight-fixture"
    assert fixture["path"] == str(default_preflight_fixture_path())
    assert [case["case_id"] for case in fixture["cases"]] == [
        "PF-001",
        "PF-002",
        "PF-003",
        "PF-004",
        "PF-005",
        "PF-006",
        "PF-007",
        "PF-008",
        "PF-009",
    ]


def test_preflight_fixture_payload_scores_all_cases_cleanly():
    payload = preflight_fixture_payload()

    assert payload["schema_version"] == PREFLIGHT_FIXTURE_RESULT_SCHEMA_VERSION
    assert payload["fixture_schema_version"] == PREFLIGHT_FIXTURE_SCHEMA_VERSION
    assert payload["case_count"] == 9
    assert payload["ok"] is True
    assert [case["case_id"] for case in payload["cases"]] == [
        "PF-001",
        "PF-002",
        "PF-003",
        "PF-004",
        "PF-005",
        "PF-006",
        "PF-007",
        "PF-008",
        "PF-009",
    ]
    assert all(case["ok"] is True for case in payload["cases"])
    assert all(case["mismatches"] == [] for case in payload["cases"])

    decisions = {case["case_id"]: case["actual"]["decision"] for case in payload["cases"]}
    assert decisions == {
        "PF-001": "accepted_with_warnings",
        "PF-002": "requires_review",
        "PF-003": "cannot_estimate",
        "PF-004": "rejected",
        "PF-005": "rejected",
        "PF-006": "rejected",
        "PF-007": "rejected",
        "PF-008": "rejected",
        "PF-009": "rejected",
    }


def test_canonical_expression_hash_uses_canonical_text():
    left = canonical_expression_hash('Query[n_, Equal[Get[n_, "category"], "Person"]]')
    right = canonical_expression_hash(parse('Query[n_,Equal[Get[n_,"category"],"Person"]]'))

    assert left == right
    assert left.startswith("sha256:")


def test_summarize_effects_for_query_is_static_and_conservative():
    summary = summarize_effects('Query[n_, Equal[Get[n_, "category"], "Person"]]')

    assert summary.expression_hash.startswith("sha256:")
    assert summary.effects == ["graph.read"]
    assert summary.required_capabilities == ["graph.read"]
    assert summary.possible_errors == []
    assert summary.confidence == "known"


def test_estimate_graph_budget_for_query_records_static_uncertainty():
    estimate = estimate_graph_budget('Query[n_, Equal[Get[n_, "category"], "Person"]]')

    assert estimate.estimated_result_count is None
    assert estimate.estimated_visited_nodes is None
    assert estimate.estimate_confidence == "estimated"
    assert estimate.estimator == "coglang-static-preflight/v0.1"
    assert estimate.notes == ["query result cardinality depends on host graph state"]


def test_preflight_accepts_bounded_query_with_warning_caveat():
    decision = preflight_expression(
        'Query[n_, Equal[Get[n_, "category"], "Person"]]',
        correlation_id="preflight-query-001",
    )

    assert decision.decision == "accepted_with_warnings"
    assert decision.required_review is False
    assert decision.reasons == ["effect.graph_read", "budget.within_default"]
    assert decision.effect_summary.effects == ["graph.read"]
    assert decision.budget == default_graph_budget()
    assert decision.budget_estimate.estimate_confidence == "estimated"
    assert decision.correlation_id == "preflight-query-001"


def test_preflight_requires_review_for_graph_write():
    decision = preflight_expression(
        'Create["Entity", {"id": "x", "category": "Person"}]',
        correlation_id="preflight-write-001",
    )

    assert decision.decision == "requires_review"
    assert decision.required_review is True
    assert decision.reasons == ["effect.graph_write", "policy.review_required"]
    assert decision.effect_summary.effects == ["graph.write", "host.policy", "human.review"]
    assert decision.effect_summary.required_capabilities == ["graph.write"]
    assert decision.possible_errors == ["CapabilityRequired", "ReviewRequired"]


def test_preflight_rejects_missing_enabled_capability_before_review():
    decision = preflight_expression(
        'Create["Entity", {"id": "x", "category": "Person"}]',
        enabled_capabilities={"graph.read"},
        correlation_id="preflight-missing-capability-001",
    )

    assert decision.decision == "rejected"
    assert decision.required_review is False
    assert decision.reasons == ["capability.missing", "capability.missing.graph_write"]
    assert decision.effect_summary.effects == ["graph.write"]
    assert decision.effect_summary.required_capabilities == ["graph.write"]
    assert decision.possible_errors == ["CapabilityRequired"]
    assert decision.correlation_id == "preflight-missing-capability-001"


def test_preflight_with_enabled_write_capability_preserves_review_policy():
    decision = preflight_expression(
        'Create["Entity", {"id": "x", "category": "Person"}]',
        enabled_capabilities={"graph.write"},
    )

    assert decision.decision == "requires_review"
    assert decision.required_review is True
    assert decision.reasons == ["effect.graph_write", "policy.review_required"]


def test_preflight_cannot_estimate_traversal_without_graph_statistics():
    decision = preflight_expression(
        'Traverse["einstein", "related"]',
        correlation_id="preflight-traverse-001",
    )

    assert decision.decision == "cannot_estimate"
    assert decision.required_review is True
    assert decision.reasons == ["budget.traversal_unbounded", "host.index_unknown"]
    assert decision.effect_summary.effects == [
        "graph.read",
        "graph.traverse",
        "host.policy",
        "human.review",
    ]
    assert decision.budget_estimate.estimate_confidence == "unknown"
    assert decision.possible_errors == ["TraversalLimitExceeded", "HostCostUnsupported"]


def test_preflight_rejects_traversal_when_static_depth_exceeds_budget():
    decision = preflight_expression(
        'Traverse["einstein", "related"]',
        budget=GraphBudget(max_traversal_depth=0, host_cost_class="closed"),
        correlation_id="preflight-budget-exceeded-001",
    )

    assert decision.decision == "rejected"
    assert decision.required_review is False
    assert decision.reasons == ["budget.traversal_depth_exceeded"]
    assert decision.effect_summary.effects == ["graph.read", "graph.traverse"]
    assert decision.budget.max_traversal_depth == 0
    assert decision.budget_estimate.estimated_traversal_depth == 1
    assert decision.possible_errors == [
        "TraversalLimitExceeded",
        "BudgetExceeded",
    ]
    assert decision.correlation_id == "preflight-budget-exceeded-001"


def test_preflight_rejects_known_result_count_over_budget():
    decision = preflight_expression(
        'Get["ada", "category"]',
        budget=GraphBudget(max_result_count=0, host_cost_class="closed"),
        correlation_id="preflight-result-budget-exceeded-001",
    )

    assert decision.decision == "rejected"
    assert decision.required_review is False
    assert decision.reasons == ["budget.result_count_exceeded"]
    assert decision.effect_summary.effects == ["graph.read"]
    assert decision.budget.max_result_count == 0
    assert decision.budget_estimate.estimated_result_count == 1
    assert decision.possible_errors == ["BudgetExceeded", "ResultLimitExceeded"]
    assert decision.correlation_id == "preflight-result-budget-exceeded-001"


def test_preflight_rejects_known_unification_branches_over_budget():
    decision = preflight_expression(
        "Unify[f[X_, b], f[a, Y_]]",
        budget=GraphBudget(max_unification_branches=0, host_cost_class="closed"),
        correlation_id="preflight-unification-budget-exceeded-001",
    )

    assert decision.decision == "rejected"
    assert decision.required_review is False
    assert decision.reasons == ["budget.unification_branches_exceeded"]
    assert decision.effect_summary.effects == ["graph.unify"]
    assert decision.budget.max_unification_branches == 0
    assert decision.budget_estimate.estimated_unification_branches == 1
    assert decision.possible_errors == [
        "UnificationBranchLimitExceeded",
        "BudgetExceeded",
        "UnificationLimitExceeded",
    ]
    assert decision.correlation_id == "preflight-unification-budget-exceeded-001"


def test_preflight_rejects_invalid_expression_before_runtime():
    decision = preflight_expression("UnknownHead[]")

    assert decision.decision == "rejected"
    assert decision.reasons == ["validation.invalid"]
    assert decision.effect_summary.expression_hash.startswith("sha256:")
    assert decision.effect_summary.confidence == "unknown"
    assert decision.possible_errors == ["TypeError"]


def test_preflight_rejects_parse_error_before_runtime():
    decision = preflight_expression('Query[n_, Equal[Get[n_, "category"], "Person"]')

    assert decision.decision == "rejected"
    assert decision.reasons == ["parse.error"]
    assert decision.effect_summary.expression_hash is None
    assert decision.effect_summary.possible_errors == ["ParseError"]
    assert decision.budget_estimate.estimate_confidence == "not_supported"
