from __future__ import annotations

from pathlib import Path

import pytest

from coglang import (
    cli,
    generation_eval,
    generation_eval_adapters,
    open_source_extract,
    preflight,
    schema_versions,
)
from coglang.schema_versions import (
    CLI_SCHEMA_VERSION,
    EFFECT_SUMMARY_SCHEMA_VERSION,
    FORMAL_OPEN_SOURCE_READINESS_SCHEMA_VERSION,
    GENERATION_EVAL_FIXTURE_SCHEMA_VERSION,
    GENERATION_EVAL_REQUEST_BATCH_SCHEMA_VERSION,
    GENERATION_EVAL_REQUEST_SCHEMA_VERSION,
    GENERATION_EVAL_RESPONSE_BATCH_SCHEMA_VERSION,
    GENERATION_EVAL_RESPONSE_SCHEMA_VERSION,
    GENERATION_EVAL_RESULT_SCHEMA_VERSION,
    GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION,
    GRAPH_BUDGET_SCHEMA_VERSION,
    HOST_DEMO_SCHEMA_VERSION,
    HOST_RUNTIME_SCHEMA_PACK_ID,
    LOCAL_CI_SIMULATION_SCHEMA_VERSION,
    MINIMAL_CI_BASELINE_SCHEMA_VERSION,
    NODE_HOST_CONSUMER_DEMO_SCHEMA_VERSION,
    NODE_MINIMAL_HOST_RUNTIME_STUB_DEMO_SCHEMA_VERSION,
    OPEN_SOURCE_BOUNDARY_SCHEMA_VERSION,
    PREFLIGHT_DECISION_SCHEMA_VERSION,
    PREFLIGHT_FIXTURE_RESULT_SCHEMA_VERSION,
    PREFLIGHT_FIXTURE_SCHEMA_VERSION,
    PUBLIC_REPO_EXTRACT_MANIFEST_SCHEMA_VERSION,
    PUBLIC_REPO_EXTRACT_RUN_SCHEMA_VERSION,
    READABLE_RENDER_GOLDEN_CANDIDATES_SCHEMA_VERSION,
    REFERENCE_HOST_DEMO_SCHEMA_VERSION,
    RELEASE_BUNDLE_SCHEMA_VERSION,
    SCHEMA_VERSION_REGISTRY,
    STATIC_PREFLIGHT_ESTIMATOR,
)


EXPECTED_SCHEMA_VERSION_REGISTRY = {
    "cli_manifest": "coglang-cli-manifest/v0.1",
    "host_demo": "coglang-host-demo/v0.1",
    "reference_host_demo": "coglang-reference-host-demo/v0.1",
    "release_bundle": "coglang-release-bundle/v0.1",
    "formal_open_source_readiness": "coglang-formal-open-source-readiness/v0.1",
    "open_source_boundary": "coglang-open-source-boundary/v0.1",
    "minimal_ci_baseline": "coglang-minimal-ci-baseline/v0.1",
    "public_repo_extract_manifest": "coglang-public-repo-extract-manifest/v0.1",
    "public_repo_extract_run": "coglang-public-repo-extract-run/v0.1",
    "local_ci_simulation": "coglang-local-ci-simulation/v0.1",
    "effect_summary": "coglang-effect-summary/v0.1",
    "graph_budget": "coglang-graph-budget/v0.1",
    "graph_budget_estimate": "coglang-graph-budget-estimate/v0.1",
    "preflight_decision": "coglang-preflight-decision/v0.1",
    "preflight_fixture": "coglang-preflight-fixture/v0.1",
    "preflight_fixture_result": "coglang-preflight-fixture-result/v0.1",
    "static_preflight_estimator": "coglang-static-preflight/v0.1",
    "generation_eval_fixture": "coglang-generation-eval-fixture/v0.1",
    "generation_eval_result": "coglang-generation-eval-result/v0.1",
    "generation_eval_request_batch": "coglang-generation-eval-request-batch/v0.1",
    "generation_eval_request": "coglang-generation-eval-request/v0.1",
    "generation_eval_response_batch": "coglang-generation-eval-response-batch/v0.1",
    "generation_eval_response": "coglang-generation-eval-response/v0.1",
    "readable_render_golden_candidates": (
        "coglang-readable-render-golden-candidates/v0.1"
    ),
    "node_host_consumer_demo": "coglang-node-host-consumer-demo/v0.1",
    "node_minimal_host_runtime_stub_demo": (
        "coglang-node-minimal-host-runtime-stub-demo/v0.1"
    ),
    "host_runtime_schema_pack": "urn:coglang:host-runtime-schema-pack:v0.1",
}


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "src" / "coglang" / "schema_versions.py").exists():
            return parent
    raise AssertionError("CogLang repository root not found")


def test_schema_version_registry_is_complete_and_unique():
    assert dict(SCHEMA_VERSION_REGISTRY) == EXPECTED_SCHEMA_VERSION_REGISTRY
    assert len(set(SCHEMA_VERSION_REGISTRY.values())) == len(SCHEMA_VERSION_REGISTRY)

    with pytest.raises(TypeError):
        SCHEMA_VERSION_REGISTRY["new_schema"] = "coglang-new-schema/v0.1"


def test_schema_version_constants_match_registry_values():
    assert CLI_SCHEMA_VERSION == SCHEMA_VERSION_REGISTRY["cli_manifest"]
    assert HOST_DEMO_SCHEMA_VERSION == SCHEMA_VERSION_REGISTRY["host_demo"]
    assert (
        REFERENCE_HOST_DEMO_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["reference_host_demo"]
    )
    assert RELEASE_BUNDLE_SCHEMA_VERSION == SCHEMA_VERSION_REGISTRY["release_bundle"]
    assert (
        FORMAL_OPEN_SOURCE_READINESS_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["formal_open_source_readiness"]
    )
    assert (
        OPEN_SOURCE_BOUNDARY_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["open_source_boundary"]
    )
    assert (
        MINIMAL_CI_BASELINE_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["minimal_ci_baseline"]
    )
    assert (
        PUBLIC_REPO_EXTRACT_MANIFEST_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["public_repo_extract_manifest"]
    )
    assert (
        PUBLIC_REPO_EXTRACT_RUN_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["public_repo_extract_run"]
    )
    assert (
        LOCAL_CI_SIMULATION_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["local_ci_simulation"]
    )
    assert EFFECT_SUMMARY_SCHEMA_VERSION == SCHEMA_VERSION_REGISTRY["effect_summary"]
    assert GRAPH_BUDGET_SCHEMA_VERSION == SCHEMA_VERSION_REGISTRY["graph_budget"]
    assert (
        GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["graph_budget_estimate"]
    )
    assert (
        PREFLIGHT_DECISION_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["preflight_decision"]
    )
    assert PREFLIGHT_FIXTURE_SCHEMA_VERSION == SCHEMA_VERSION_REGISTRY["preflight_fixture"]
    assert (
        PREFLIGHT_FIXTURE_RESULT_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["preflight_fixture_result"]
    )
    assert (
        STATIC_PREFLIGHT_ESTIMATOR
        == SCHEMA_VERSION_REGISTRY["static_preflight_estimator"]
    )
    assert (
        GENERATION_EVAL_FIXTURE_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["generation_eval_fixture"]
    )
    assert (
        GENERATION_EVAL_RESULT_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["generation_eval_result"]
    )
    assert (
        GENERATION_EVAL_REQUEST_BATCH_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["generation_eval_request_batch"]
    )
    assert (
        GENERATION_EVAL_REQUEST_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["generation_eval_request"]
    )
    assert (
        GENERATION_EVAL_RESPONSE_BATCH_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["generation_eval_response_batch"]
    )
    assert (
        GENERATION_EVAL_RESPONSE_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["generation_eval_response"]
    )
    assert (
        READABLE_RENDER_GOLDEN_CANDIDATES_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["readable_render_golden_candidates"]
    )
    assert (
        NODE_HOST_CONSUMER_DEMO_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["node_host_consumer_demo"]
    )
    assert (
        NODE_MINIMAL_HOST_RUNTIME_STUB_DEMO_SCHEMA_VERSION
        == SCHEMA_VERSION_REGISTRY["node_minimal_host_runtime_stub_demo"]
    )
    assert HOST_RUNTIME_SCHEMA_PACK_ID == SCHEMA_VERSION_REGISTRY["host_runtime_schema_pack"]


def test_runtime_modules_import_schema_versions_from_registry():
    assert cli.CLI_SCHEMA_VERSION == schema_versions.CLI_SCHEMA_VERSION
    assert cli.HOST_DEMO_SCHEMA_VERSION == schema_versions.HOST_DEMO_SCHEMA_VERSION
    assert (
        cli.REFERENCE_HOST_DEMO_SCHEMA_VERSION
        == schema_versions.REFERENCE_HOST_DEMO_SCHEMA_VERSION
    )
    assert preflight.EFFECT_SUMMARY_SCHEMA_VERSION == EFFECT_SUMMARY_SCHEMA_VERSION
    assert preflight.GRAPH_BUDGET_SCHEMA_VERSION == GRAPH_BUDGET_SCHEMA_VERSION
    assert (
        preflight.GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION
        == GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION
    )
    assert (
        preflight.PREFLIGHT_DECISION_SCHEMA_VERSION
        == PREFLIGHT_DECISION_SCHEMA_VERSION
    )
    assert generation_eval.GENERATION_EVAL_FIXTURE_SCHEMA_VERSION == (
        GENERATION_EVAL_FIXTURE_SCHEMA_VERSION
    )
    assert (
        generation_eval.GENERATION_EVAL_RESULT_SCHEMA_VERSION
        == GENERATION_EVAL_RESULT_SCHEMA_VERSION
    )
    assert (
        generation_eval_adapters.GENERATION_EVAL_REQUEST_BATCH_SCHEMA_VERSION
        == GENERATION_EVAL_REQUEST_BATCH_SCHEMA_VERSION
    )
    assert (
        generation_eval_adapters.GENERATION_EVAL_REQUEST_SCHEMA_VERSION
        == GENERATION_EVAL_REQUEST_SCHEMA_VERSION
    )
    assert (
        generation_eval_adapters.GENERATION_EVAL_RESPONSE_BATCH_SCHEMA_VERSION
        == GENERATION_EVAL_RESPONSE_BATCH_SCHEMA_VERSION
    )
    assert (
        generation_eval_adapters.GENERATION_EVAL_RESPONSE_SCHEMA_VERSION
        == GENERATION_EVAL_RESPONSE_SCHEMA_VERSION
    )
    assert (
        open_source_extract.PUBLIC_REPO_EXTRACT_RUN_SCHEMA_VERSION
        == PUBLIC_REPO_EXTRACT_RUN_SCHEMA_VERSION
    )


def test_python_runtime_schema_versions_are_declared_only_in_registry():
    src_root = _repo_root() / "src" / "coglang"
    offenders: list[str] = []
    for path in sorted(src_root.glob("*.py")):
        if path.name == "schema_versions.py":
            continue
        text = path.read_text(encoding="utf-8")
        for value in SCHEMA_VERSION_REGISTRY.values():
            if value in text:
                offenders.append(f"{path.name}: {value}")

    assert offenders == []
