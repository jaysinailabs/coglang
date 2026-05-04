from __future__ import annotations

import importlib
import json
import sys
import tomllib
from pathlib import Path

try:
    from coglang.open_source_extract import (
        check_public_assets_mirror,
        materialize_public_repo_extract,
        sync_public_assets_mirror,
    )
except ModuleNotFoundError:
    from coglang.open_source_extract import (
        check_public_assets_mirror,
        materialize_public_repo_extract,
        sync_public_assets_mirror,
    )


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "CogLang_Public_Repo_Extract_Manifest_v0_1.json").exists():
            return parent
    raise AssertionError("CogLang public extract manifest not found")


def _extract_manifest_counts() -> dict[str, int]:
    manifest_path = _repo_root() / "CogLang_Public_Repo_Extract_Manifest_v0_1.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest["entries"]
    return {
        "entry_count": len(entries),
        "copied_trees": sum(1 for entry in entries if entry["kind"] == "tree"),
        "copied_files": sum(1 for entry in entries if entry["kind"] == "file"),
    }


def test_materialize_public_repo_extract_creates_importable_public_root(monkeypatch, tmp_path):
    destination = tmp_path / "coglang-public-root"
    payload = materialize_public_repo_extract(destination)
    manifest_counts = _extract_manifest_counts()

    assert payload["schema_version"] == "coglang-public-repo-extract-run/v0.1"
    assert payload["entry_count"] == manifest_counts["entry_count"]
    assert payload["copied_trees"] == manifest_counts["copied_trees"]
    assert payload["copied_files"] == manifest_counts["copied_files"]

    assert (destination / "pyproject.toml").exists()
    assert (destination / "CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md").exists()
    assert (destination / "CogLang_HRC_Companion_Asset_Classification_v0_1.md").exists()
    assert (destination / "CogLang_HRC_v0_2_Freeze_Candidate_2026_04_28.md").exists()
    assert (destination / "src" / "coglang" / "reference_host.py").exists()
    assert (destination / ".gitignore").exists()
    assert (destination / ".mailmap").exists()
    assert (destination / "pytest.ini").exists()
    assert (destination / "README.md").exists()
    assert (destination / "CONTRIBUTING.md").exists()
    assert (destination / "CogLang_Open_Source_Boundary_v0_1.json").exists()
    assert (destination / "CogLang_Minimal_CI_Baseline_v0_1.json").exists()
    assert (destination / "CogLang_Public_Repo_Extract_Manifest_v0_1.json").exists()
    assert (destination / "src" / "coglang" / "preflight.py").exists()
    assert (destination / "src" / "coglang" / "schema_versions.py").exists()
    assert (destination / "src" / "coglang" / "generation_eval_adapters.py").exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "eval_fixtures"
        / "readable_render_golden_candidates_v0_1.json"
    ).exists()
    assert (destination / "tests" / "coglang" / "test_catalog_alignment.py").exists()
    assert (destination / "tests" / "coglang" / "test_executor_interface.py").exists()
    assert (destination / "tests" / "coglang" / "test_preflight.py").exists()
    assert (destination / "tests" / "coglang" / "test_generation_eval_adapters.py").exists()
    assert (
        destination / "tests" / "coglang" / "test_readable_render_golden_candidates.py"
    ).exists()
    assert (destination / "tests" / "coglang" / "test_schema_versions.py").exists()
    assert (
        destination / "tests" / "coglang" / "test_generation_eval_offline_runner.py"
    ).exists()
    assert (destination / "tests" / "coglang" / "test_local_ci_script.py").exists()
    assert (destination / "tests" / "coglang" / "test_grammar_examples.py").exists()
    assert (
        destination / "tests" / "coglang" / "test_vscode_textmate_syntax_example.py"
    ).exists()
    assert (
        destination / "tests" / "coglang" / "test_semantic_event_audit_example.py"
    ).exists()
    assert (destination / "tests" / "coglang" / "test_node_host_consumer.py").exists()
    assert (destination / "tests" / "coglang" / "test_node_minimal_host_runtime_stub.py").exists()
    assert (destination / "tests" / "coglang" / "test_public_assets_mirror.py").exists()
    assert (destination / "examples" / "node_host_consumer" / "consume_hrc_envelopes.mjs").exists()
    assert (destination / "examples" / "node_host_consumer" / "README.md").exists()
    assert (destination / "examples" / "node_host_consumer" / "package.json").exists()
    assert (destination / "examples" / "node_minimal_host_runtime_stub" / "run_demo.mjs").exists()
    assert (destination / "examples" / "node_minimal_host_runtime_stub" / "host_stub.mjs").exists()
    assert (destination / "examples" / "node_minimal_host_runtime_stub" / "runtime_stub.mjs").exists()
    assert (destination / "examples" / "node_minimal_host_runtime_stub" / "README.md").exists()
    assert (destination / "examples" / "grammar" / "coglang.lark").exists()
    assert (destination / "examples" / "grammar" / "coglang.gbnf").exists()
    assert (destination / "examples" / "grammar" / "README.md").exists()
    assert (
        destination / "examples" / "generation_eval_offline_runner" / "README.md"
    ).exists()
    assert (
        destination
        / "examples"
        / "generation_eval_offline_runner"
        / "mock_responses.py"
    ).exists()
    assert (
        destination
        / "examples"
        / "generation_eval_offline_runner"
        / "fixtures"
        / "generation_eval_three_case_v0_1.json"
    ).exists()
    assert (
        destination
        / "examples"
        / "generation_eval_offline_runner"
        / "fixtures"
        / "mock_responses.jsonl"
    ).exists()
    assert (destination / "examples" / "vscode_textmate_syntax" / "README.md").exists()
    assert (destination / "examples" / "vscode_textmate_syntax" / "package.json").exists()
    assert (
        destination / "examples" / "vscode_textmate_syntax" / "language-configuration.json"
    ).exists()
    assert (
        destination
        / "examples"
        / "vscode_textmate_syntax"
        / "syntaxes"
        / "coglang.tmLanguage.json"
    ).exists()
    assert (
        destination / "examples" / "vscode_textmate_syntax" / "samples" / "basic.coglang"
    ).exists()
    assert (destination / "examples" / "semantic_event_audit" / "audit_events.py").exists()
    assert (destination / "examples" / "semantic_event_audit" / "README.md").exists()
    assert (
        destination
        / "examples"
        / "semantic_event_audit"
        / "fixtures"
        / "external_events.jsonl"
    ).exists()
    assert (destination / "scripts" / "local_ci.py").exists()
    assert (destination / "CogLang_Operator_Catalog_v1_1_0.md").exists()
    assert (destination / "CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md").exists()
    assert (destination / "CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md").exists()
    assert (destination / "CogLang_Readable_Render_Boundary_v0_1.md").exists()
    assert (
        destination / "CogLang_Readable_Render_Golden_Example_Candidates_v0_1.md"
    ).exists()
    assert (
        destination / "CogLang_Readable_Render_API_Promotion_Checklist_v0_1.md"
    ).exists()
    assert (
        destination / "CogLang_Generation_Eval_Request_Response_Contract_v0_1.md"
    ).exists()
    assert (destination / "CogLang_Use_Cases_and_Positioning_v0_1.md").exists()
    assert (destination / "CogLang_Small_Scale_Promotion_Plan_v0_1.md").exists()
    assert (destination / "CogLang_Announcement_Kit_v0_1.md").exists()
    assert (destination / "CogLang_Quickstart_v1_1_0.zh-CN.md").exists()
    assert (destination / "CogLang_Specification_v1_1_0_Draft.zh-CN.md").exists()
    assert (destination / "CogLang_Conformance_Suite_v1_1_0.zh-CN.md").exists()
    assert (destination / "CogLang_Standalone_Install_and_Release_Guide_v0_1.zh-CN.md").exists()
    assert (destination / "CogLang_Release_Notes_v1_1_0.zh-CN.md").exists()
    assert (destination / "CogLang_Release_Notes_v1_1_5.md").exists()
    assert (destination / "CogLang_Release_Notes_v1_1_5.zh-CN.md").exists()
    assert (destination / "CogLang_Release_Notes_v1_1_4.md").exists()
    assert (destination / "CogLang_Release_Notes_v1_1_4.zh-CN.md").exists()
    assert (destination / "CogLang_Release_Notes_v1_1_3.md").exists()
    assert (destination / "CogLang_Release_Notes_v1_1_3.zh-CN.md").exists()
    assert (destination / "CogLang_Release_Notes_v1_1_2.md").exists()
    assert (destination / "CogLang_Release_Notes_v1_1_2.zh-CN.md").exists()
    assert (destination / "CogLang_Release_Notes_v1_1_1.md").exists()
    assert (destination / "CogLang_Release_Notes_v1_1_1.zh-CN.md").exists()
    assert (destination / "CogLang_Contribution_Guide_v0_1.zh-CN.md").exists()
    assert (destination / "CogLang_Vision_Proposal_v0_1.md").exists()
    assert (destination / "CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md").exists()
    assert (destination / "CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md").exists()
    assert (destination / "CogLang_Host_Runtime_Contract_v0_1.zh-CN.md").exists()
    assert (destination / "CogLang_Profiles_and_Capabilities_v1_1_0.zh-CN.md").exists()
    assert (destination / "CogLang_Operator_Catalog_v1_1_0.zh-CN.md").exists()
    assert (
        destination / ".github" / "ISSUE_TEMPLATE" / "external_host_consumer.yml"
    ).exists()
    assert (destination / ".github" / "PULL_REQUEST_TEMPLATE.md").exists()
    assert (destination / ".github" / "workflows" / "ci.yml").exists()
    assert (destination / ".github" / "workflows" / "publish.yml").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "README.md").exists()
    assert (
        destination / "src" / "coglang" / "_public_assets" / "CONTRIBUTING.md"
    ).exists()
    assert (destination / "src" / "coglang" / "_public_assets" / ".mailmap").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / ".gitignore").exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "CogLang_Open_Source_Boundary_v0_1.json"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "pytest.ini"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / ".github"
        / "ISSUE_TEMPLATE"
        / "external_host_consumer.yml"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / ".github"
        / "PULL_REQUEST_TEMPLATE.md"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / ".github"
        / "workflows"
        / "ci.yml"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / ".github"
        / "workflows"
        / "publish.yml"
    ).exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_cli.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "conftest.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_catalog_alignment.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_executor_interface.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_preflight.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_generation_eval_adapters.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_node_host_consumer.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_node_minimal_host_runtime_stub.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_public_assets_mirror.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_readable_render_golden_candidates.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_schema_versions.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_generation_eval_offline_runner.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_local_ci_script.py").exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "tests" / "coglang" / "test_grammar_examples.py").exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "tests"
        / "coglang"
        / "test_vscode_textmate_syntax_example.py"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "tests"
        / "coglang"
        / "test_semantic_event_audit_example.py"
    ).exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "examples" / "node_host_consumer" / "consume_hrc_envelopes.mjs").exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "node_host_consumer"
        / "package.json"
    ).exists()
    assert (destination / "src" / "coglang" / "_public_assets" / "examples" / "node_minimal_host_runtime_stub" / "run_demo.mjs").exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "grammar"
        / "coglang.gbnf"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "generation_eval_offline_runner"
        / "mock_responses.py"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "generation_eval_offline_runner"
        / "fixtures"
        / "generation_eval_three_case_v0_1.json"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "generation_eval_offline_runner"
        / "fixtures"
        / "mock_responses.jsonl"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "vscode_textmate_syntax"
        / "README.md"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "vscode_textmate_syntax"
        / "package.json"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "vscode_textmate_syntax"
        / "language-configuration.json"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "vscode_textmate_syntax"
        / "syntaxes"
        / "coglang.tmLanguage.json"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "vscode_textmate_syntax"
        / "samples"
        / "basic.coglang"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "semantic_event_audit"
        / "audit_events.py"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "semantic_event_audit"
        / "README.md"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "examples"
        / "semantic_event_audit"
        / "fixtures"
        / "external_events.jsonl"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "scripts"
        / "local_ci.py"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "CogLang_Readable_Render_Boundary_v0_1.md"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "CogLang_Readable_Render_Golden_Example_Candidates_v0_1.md"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "CogLang_Readable_Render_API_Promotion_Checklist_v0_1.md"
    ).exists()
    assert (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "CogLang_HRC_Companion_Asset_Classification_v0_1.md"
    ).exists()
    assert (destination / "internal_schemas" / "host_runtime" / "v0.1" / "schema-pack.json").exists()
    assert (destination / "src" / "coglang" / "cli.py").exists()
    assert (destination / "tests" / "coglang").exists()
    assert (destination / "LICENSE").exists()
    pyproject = tomllib.loads((destination / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["authors"] == [{"name": "Jason Xin"}]
    assert pyproject["project"]["license"] == "Apache-2.0"
    assert pyproject["project"]["license-files"] == ["LICENSE"]
    assert "License :: OSI Approved :: Apache Software License" not in pyproject["project"]["classifiers"]
    forbidden_markers = [
        ("NG" + "LM").lower(),
        ("Lo" + "gos").lower(),
        ("plans" + "/coglang").lower(),
        ("src" + "/lo" + "gos").lower(),
        ("lo" + "gos.coglang").lower(),
    ]
    leaked_forbidden_markers = {marker: 0 for marker in forbidden_markers}
    for path in destination.rglob("*"):
        relative_path = str(path.relative_to(destination)).replace("\\", "/").lower()
        for marker in forbidden_markers:
            assert marker not in relative_path
        if path.is_file() and path.suffix in {".py", ".json", ".md", ".toml", ".txt", ".yml", ".yaml"}:
            text = path.read_text(encoding="utf-8").lower()
            for marker in forbidden_markers:
                leaked_forbidden_markers[marker] += text.count(marker)
    assert leaked_forbidden_markers == {marker: 0 for marker in forbidden_markers}

    monkeypatch.syspath_prepend(str(destination / "src"))
    importlib.invalidate_caches()
    sys.modules.pop("coglang", None)
    sys.modules.pop("coglang.cli", None)
    extracted_cli = importlib.import_module("coglang.cli")

    distribution = extracted_cli._distribution_metadata()
    manifest = extracted_cli._manifest_payload()
    release_check = extracted_cli._release_check_payload()
    public_extract_manifest = extracted_cli._public_repo_extract_manifest_payload()

    assert manifest["package"] == "coglang"
    assert manifest["docs"]["readme"] == "README.md"
    assert manifest["docs"]["vision_proposal"] == "CogLang_Vision_Proposal_v0_1.md"
    assert (
        manifest["docs"]["evolution_boundary_proposal"]
        == "CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md"
    )
    assert (
        manifest["docs"]["effect_budget_preflight_vocabulary"]
        == "CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md"
    )
    assert (
        manifest["docs"]["reserved_operator_promotion_criteria"]
        == "CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md"
    )
    assert (
        manifest["docs"]["send_carry_forward_exit_matrix"]
        == "CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md"
    )
    assert (
        manifest["docs"]["readable_render_boundary"]
        == "CogLang_Readable_Render_Boundary_v0_1.md"
    )
    assert (
        manifest["docs"]["readable_render_golden_examples"]
        == "CogLang_Readable_Render_Golden_Example_Candidates_v0_1.md"
    )
    assert (
        manifest["docs"]["readable_render_api_promotion_checklist"]
        == "CogLang_Readable_Render_API_Promotion_Checklist_v0_1.md"
    )
    assert (
        manifest["docs"]["generation_eval_request_response_contract"]
        == "CogLang_Generation_Eval_Request_Response_Contract_v0_1.md"
    )
    assert (
        manifest["docs"]["use_cases_and_positioning"]
        == "CogLang_Use_Cases_and_Positioning_v0_1.md"
    )
    assert (
        manifest["docs"]["small_scale_promotion_plan"]
        == "CogLang_Small_Scale_Promotion_Plan_v0_1.md"
    )
    assert manifest["docs"]["announcement_kit"] == "CogLang_Announcement_Kit_v0_1.md"
    assert (
        manifest["docs"]["hrc_companion_asset_classification"]
        == "CogLang_HRC_Companion_Asset_Classification_v0_1.md"
    )
    assert manifest["docs"]["roadmap"] == "ROADMAP.md"
    assert manifest["machine_readable_summaries"]["llms"] == "llms.txt"
    assert distribution["console_script"] == "coglang"
    assert distribution["console_script_target"] == "coglang.cli:main"
    assert public_extract_manifest["path"] == "CogLang_Public_Repo_Extract_Manifest_v0_1.json"
    assert public_extract_manifest["required_destinations_present"] is True
    assert manifest["minimal_ci_baseline"]["workflow_template_present"] is True
    assert manifest["minimal_ci_baseline"]["publish_workflow_template_present"] is True
    assert manifest["minimal_ci_baseline"]["publish_workflow_required_snippets_present"] is True
    assert release_check["ok"] is True
    assert callable(extracted_cli.main)

    monkeypatch.setattr(extracted_cli, "_project_root", lambda: destination / "_installed_like_root")
    installed_like_manifest = extracted_cli._manifest_payload()
    installed_like_release_check = extracted_cli._release_check_payload()

    assert installed_like_manifest["docs"]["readme"] == "README.md"
    assert (
        installed_like_manifest["docs"]["reserved_operator_promotion_criteria"]
        == "CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md"
    )
    assert (
        installed_like_manifest["docs"]["send_carry_forward_exit_matrix"]
        == "CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md"
    )
    assert (
        installed_like_manifest["docs"]["readable_render_boundary"]
        == "CogLang_Readable_Render_Boundary_v0_1.md"
    )
    assert (
        installed_like_manifest["docs"]["readable_render_golden_examples"]
        == "CogLang_Readable_Render_Golden_Example_Candidates_v0_1.md"
    )
    assert (
        installed_like_manifest["docs"]["readable_render_api_promotion_checklist"]
        == "CogLang_Readable_Render_API_Promotion_Checklist_v0_1.md"
    )
    assert (
        installed_like_manifest["docs"]["generation_eval_request_response_contract"]
        == "CogLang_Generation_Eval_Request_Response_Contract_v0_1.md"
    )
    assert (
        installed_like_manifest["docs"]["use_cases_and_positioning"]
        == "CogLang_Use_Cases_and_Positioning_v0_1.md"
    )
    assert (
        installed_like_manifest["docs"]["small_scale_promotion_plan"]
        == "CogLang_Small_Scale_Promotion_Plan_v0_1.md"
    )
    assert (
        installed_like_manifest["docs"]["announcement_kit"]
        == "CogLang_Announcement_Kit_v0_1.md"
    )
    assert (
        installed_like_manifest["docs"]["hrc_companion_asset_classification"]
        == "CogLang_HRC_Companion_Asset_Classification_v0_1.md"
    )
    assert installed_like_manifest["open_source_boundary"]["status"] != "missing"
    assert installed_like_manifest["minimal_ci_baseline"]["workflow_template_present"] is True
    assert installed_like_manifest["minimal_ci_baseline"]["publish_workflow_template_present"] is True
    assert installed_like_release_check["ok"] is True
    installed_like_targets = [item.replace("\\", "/") for item in extracted_cli._conformance_targets("smoke")]
    assert any(item.endswith("coglang/_public_assets/tests/coglang/test_cli.py") for item in installed_like_targets)
    assert any(item.endswith("coglang/_public_assets/tests/coglang/test_parser.py") for item in installed_like_targets)
    assert any(item.endswith("coglang/_public_assets/tests/coglang/test_validator.py") for item in installed_like_targets)

    gitignore_lines = (destination / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".venv/" in gitignore_lines
    assert "dist/" in gitignore_lines
    assert ".tmp_ci_wheel/" in gitignore_lines
    assert ".tmp_ci_sdist/" in gitignore_lines
    assert ".tmp_publish_wheel/" in gitignore_lines
    pytest_ini_text = (destination / "pytest.ini").read_text(encoding="utf-8")
    assert "L1: level 1 smoke and conformance marker" in pytest_ini_text
    assert "L2: level 2 smoke and conformance marker" in pytest_ini_text


def test_public_assets_mirror_check_reports_clean_source_tree():
    payload = check_public_assets_mirror(_repo_root())

    assert payload["ok"] is True
    assert payload["checked_file_count"] >= 50
    assert payload["missing_package_data_entries"] == []
    assert payload["extra_package_data_entries"] == []
    assert payload["missing_sources"] == []
    assert payload["missing_mirrors"] == []
    assert payload["mismatched_mirrors"] == []


def test_external_host_issue_template_preserves_boundary_questions():
    template_path = (
        _repo_root() / ".github" / "ISSUE_TEMPLATE" / "external_host_consumer.yml"
    )
    text = template_path.read_text(encoding="utf-8")

    assert "External host or consumer" in text
    assert "Contribution type" in text
    assert "HRC asset class consumed" in text
    assert "This proposal does not expand HRC v0.2 frozen scope." in text
    assert (
        "Companion schema material will not be presented as a normative JSON Schema contract."
        in text
    )


def test_contributing_entrypoint_routes_external_host_contributions():
    text = (_repo_root() / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "CogLang_Contribution_Guide_v0_1.md" in text
    assert ".github/PULL_REQUEST_TEMPLATE.md" in text
    assert ".github/ISSUE_TEMPLATE/external_host_consumer.yml" in text
    assert "coglang release-check" in text
    assert "coglang public-assets --sync" in text
    assert "scripts/local_ci.py" in text
    assert "Do not expand HRC v0.2 frozen scope" in text


def test_sync_public_assets_mirror_repairs_materialized_extract_mirror(tmp_path):
    destination = tmp_path / "coglang-public-root"
    materialize_public_repo_extract(destination)

    source_readme = destination / "README.md"
    mirror_readme = destination / "src" / "coglang" / "_public_assets" / "README.md"
    wildcard_sentinel = (
        destination
        / "src"
        / "coglang"
        / "_public_assets"
        / "tests"
        / "coglang"
        / "sentinel.tmp"
    )
    mirror_readme.write_text("stale mirror\n", encoding="utf-8")
    wildcard_sentinel.write_text("do not touch tree mirror\n", encoding="utf-8")

    stale_check = check_public_assets_mirror(destination)
    assert stale_check["ok"] is False
    assert "src/coglang/_public_assets/README.md" in stale_check["mismatched_mirrors"]

    payload = sync_public_assets_mirror(destination)

    assert payload["ok"] is True
    assert payload["mirrored_file_count"] >= 50
    assert payload["check"]["ok"] is True
    assert mirror_readme.read_text(encoding="utf-8") == source_readme.read_text(
        encoding="utf-8"
    )
    assert wildcard_sentinel.read_text(encoding="utf-8") == "do not touch tree mirror\n"


def test_public_assets_mirror_check_reports_missing_exact_files(tmp_path):
    destination = tmp_path / "coglang-public-root"
    materialize_public_repo_extract(destination)

    source_readme = destination / "README.md"
    mirror_license = destination / "src" / "coglang" / "_public_assets" / "LICENSE"
    source_readme.unlink()
    mirror_license.unlink()

    payload = check_public_assets_mirror(destination)

    assert payload["ok"] is False
    assert "README.md" in payload["missing_sources"]
    assert "src/coglang/_public_assets/LICENSE" in payload["missing_mirrors"]


def test_materialize_public_repo_extract_rejects_existing_destination_without_overwrite(tmp_path):
    destination = tmp_path / "coglang-public-root"
    materialize_public_repo_extract(destination)

    try:
        materialize_public_repo_extract(destination)
    except FileExistsError as exc:
        assert "pyproject.toml" in str(exc) or "src" in str(exc)
    else:
        raise AssertionError("Expected FileExistsError when destination already contains extract output")
