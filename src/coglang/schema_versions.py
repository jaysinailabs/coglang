from __future__ import annotations

from types import MappingProxyType

CLI_SCHEMA_VERSION = "coglang-cli-manifest/v0.1"
HOST_DEMO_SCHEMA_VERSION = "coglang-host-demo/v0.1"
REFERENCE_HOST_DEMO_SCHEMA_VERSION = "coglang-reference-host-demo/v0.1"
RELEASE_BUNDLE_SCHEMA_VERSION = "coglang-release-bundle/v0.1"
FORMAL_OPEN_SOURCE_READINESS_SCHEMA_VERSION = (
    "coglang-formal-open-source-readiness/v0.1"
)

OPEN_SOURCE_BOUNDARY_SCHEMA_VERSION = "coglang-open-source-boundary/v0.1"
MINIMAL_CI_BASELINE_SCHEMA_VERSION = "coglang-minimal-ci-baseline/v0.1"
PUBLIC_REPO_EXTRACT_MANIFEST_SCHEMA_VERSION = (
    "coglang-public-repo-extract-manifest/v0.1"
)
PUBLIC_REPO_EXTRACT_RUN_SCHEMA_VERSION = "coglang-public-repo-extract-run/v0.1"

EFFECT_SUMMARY_SCHEMA_VERSION = "coglang-effect-summary/v0.1"
GRAPH_BUDGET_SCHEMA_VERSION = "coglang-graph-budget/v0.1"
GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION = "coglang-graph-budget-estimate/v0.1"
PREFLIGHT_DECISION_SCHEMA_VERSION = "coglang-preflight-decision/v0.1"
PREFLIGHT_FIXTURE_SCHEMA_VERSION = "coglang-preflight-fixture/v0.1"
PREFLIGHT_FIXTURE_RESULT_SCHEMA_VERSION = "coglang-preflight-fixture-result/v0.1"
STATIC_PREFLIGHT_ESTIMATOR = "coglang-static-preflight/v0.1"

GENERATION_EVAL_FIXTURE_SCHEMA_VERSION = "coglang-generation-eval-fixture/v0.1"
GENERATION_EVAL_RESULT_SCHEMA_VERSION = "coglang-generation-eval-result/v0.1"

NODE_HOST_CONSUMER_DEMO_SCHEMA_VERSION = "coglang-node-host-consumer-demo/v0.1"
NODE_MINIMAL_HOST_RUNTIME_STUB_DEMO_SCHEMA_VERSION = (
    "coglang-node-minimal-host-runtime-stub-demo/v0.1"
)
HOST_RUNTIME_SCHEMA_PACK_ID = "urn:coglang:host-runtime-schema-pack:v0.1"

SCHEMA_VERSION_REGISTRY = MappingProxyType(
    {
        "cli_manifest": CLI_SCHEMA_VERSION,
        "host_demo": HOST_DEMO_SCHEMA_VERSION,
        "reference_host_demo": REFERENCE_HOST_DEMO_SCHEMA_VERSION,
        "release_bundle": RELEASE_BUNDLE_SCHEMA_VERSION,
        "formal_open_source_readiness": FORMAL_OPEN_SOURCE_READINESS_SCHEMA_VERSION,
        "open_source_boundary": OPEN_SOURCE_BOUNDARY_SCHEMA_VERSION,
        "minimal_ci_baseline": MINIMAL_CI_BASELINE_SCHEMA_VERSION,
        "public_repo_extract_manifest": PUBLIC_REPO_EXTRACT_MANIFEST_SCHEMA_VERSION,
        "public_repo_extract_run": PUBLIC_REPO_EXTRACT_RUN_SCHEMA_VERSION,
        "effect_summary": EFFECT_SUMMARY_SCHEMA_VERSION,
        "graph_budget": GRAPH_BUDGET_SCHEMA_VERSION,
        "graph_budget_estimate": GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION,
        "preflight_decision": PREFLIGHT_DECISION_SCHEMA_VERSION,
        "preflight_fixture": PREFLIGHT_FIXTURE_SCHEMA_VERSION,
        "preflight_fixture_result": PREFLIGHT_FIXTURE_RESULT_SCHEMA_VERSION,
        "static_preflight_estimator": STATIC_PREFLIGHT_ESTIMATOR,
        "generation_eval_fixture": GENERATION_EVAL_FIXTURE_SCHEMA_VERSION,
        "generation_eval_result": GENERATION_EVAL_RESULT_SCHEMA_VERSION,
        "node_host_consumer_demo": NODE_HOST_CONSUMER_DEMO_SCHEMA_VERSION,
        "node_minimal_host_runtime_stub_demo": (
            NODE_MINIMAL_HOST_RUNTIME_STUB_DEMO_SCHEMA_VERSION
        ),
        "host_runtime_schema_pack": HOST_RUNTIME_SCHEMA_PACK_ID,
    }
)

__all__ = [
    "CLI_SCHEMA_VERSION",
    "EFFECT_SUMMARY_SCHEMA_VERSION",
    "FORMAL_OPEN_SOURCE_READINESS_SCHEMA_VERSION",
    "GENERATION_EVAL_FIXTURE_SCHEMA_VERSION",
    "GENERATION_EVAL_RESULT_SCHEMA_VERSION",
    "GRAPH_BUDGET_ESTIMATE_SCHEMA_VERSION",
    "GRAPH_BUDGET_SCHEMA_VERSION",
    "HOST_DEMO_SCHEMA_VERSION",
    "HOST_RUNTIME_SCHEMA_PACK_ID",
    "MINIMAL_CI_BASELINE_SCHEMA_VERSION",
    "NODE_HOST_CONSUMER_DEMO_SCHEMA_VERSION",
    "NODE_MINIMAL_HOST_RUNTIME_STUB_DEMO_SCHEMA_VERSION",
    "OPEN_SOURCE_BOUNDARY_SCHEMA_VERSION",
    "PREFLIGHT_DECISION_SCHEMA_VERSION",
    "PREFLIGHT_FIXTURE_RESULT_SCHEMA_VERSION",
    "PREFLIGHT_FIXTURE_SCHEMA_VERSION",
    "PUBLIC_REPO_EXTRACT_MANIFEST_SCHEMA_VERSION",
    "PUBLIC_REPO_EXTRACT_RUN_SCHEMA_VERSION",
    "REFERENCE_HOST_DEMO_SCHEMA_VERSION",
    "RELEASE_BUNDLE_SCHEMA_VERSION",
    "SCHEMA_VERSION_REGISTRY",
    "STATIC_PREFLIGHT_ESTIMATOR",
]
