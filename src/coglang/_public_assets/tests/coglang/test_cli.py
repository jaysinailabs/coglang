from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import types
import tomllib
from contextlib import redirect_stdout
from pathlib import Path

from coglang.cli import (
    COGLANG_LANGUAGE_RELEASE,
    EXAMPLES,
    HOST_DEMO_TOP_LEVEL_KEYS,
    REFERENCE_HOST_DEMO_TOP_LEVEL_KEYS,
    _bundle_payload,
    _conformance_targets,
    _distribution_metadata,
    _doctor_payload,
    _examples_payload,
    _formal_open_source_readiness_payload,
    _info_payload,
    _manifest_payload,
    _minimal_ci_baseline_payload,
    _public_repo_extract_manifest_payload,
    _open_source_boundary_payload,
    _release_check_payload,
    _run_conformance_suite,
    _run_demo,
    _run_host_demo,
    _run_reference_host_demo,
    _run_repl,
    _run_smoke,
    _vocab_payload,
    main,
)
from coglang.generation_eval import (
    load_generation_eval_cases,
    reference_generation_eval_answers,
)
from coglang.local_host import LocalHostSnapshot, LocalHostSummary, LocalHostTrace
from coglang.write_bundle import (
    LocalWriteHeader,
    LocalWriteQueryResult,
    LocalWriteSubmissionRecord,
    WriteBundleResponseMessage,
    WriteBundleSubmissionMessage,
)

CLI_MODULE_PATH = "coglang.cli"
MODULE_ENTRY = "coglang"
DISTRIBUTION_NAME = "coglang"

_TEST_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_PROJECT_PYPROJECT = _TEST_PROJECT_ROOT / "pyproject.toml"
if _PROJECT_PYPROJECT.exists():
    DISTRIBUTION_NAME = tomllib.loads(_PROJECT_PYPROJECT.read_text(encoding="utf-8"))["project"]["name"]
_EXTRACTED_LAYOUT = DISTRIBUTION_NAME == "coglang"
if _EXTRACTED_LAYOUT:
    MODULE_ENTRY = "coglang"


def _path_in_layout(source_path: str, extracted_path: str) -> str:
    return extracted_path if _EXTRACTED_LAYOUT else source_path


def _cli_attr(name: str) -> str:
    return f"{CLI_MODULE_PATH}.{name}"


def _cli_host_attr(name: str) -> str:
    return f"{CLI_MODULE_PATH}.LocalCogLangHost.{name}"


def _run(argv: list[str]) -> tuple[int, str]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(argv)
    return code, buffer.getvalue().strip()


def test_cli_version_output_includes_distribution_and_language_release():
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        try:
            main(["--version"])
        except SystemExit as exc:
            assert exc.code == 0
        else:
            raise AssertionError("--version should terminate argument parsing")

    output = buffer.getvalue().strip()
    assert output.startswith("coglang ")
    assert f"(language_release {COGLANG_LANGUAGE_RELEASE})" in output


def test_cli_parse_canonical_output():
    code, output = _run(["parse", 'Equal[1, 1]'])
    assert code == 0
    assert output == 'Equal[1, 1]'


def test_cli_parse_json_output():
    code, output = _run(["parse", "--format", "json", 'Equal[1, 1]'])
    assert code == 0
    assert '"head": "Equal"' in output


def test_cli_validate_success_plain_text():
    code, output = _run(["validate", 'Equal[1, 1]'])
    assert code == 0
    assert output == "true"


def test_cli_validate_failure_unknown_head():
    code, output = _run(["validate", 'UnknownHead[1]'])
    assert code == 1
    assert output == "false"


def test_cli_execute_returns_canonical_result():
    code, output = _run(["execute", 'Equal[1, 1]'])
    assert code == 0
    assert output == "True[]"


def test_cli_execute_json_result():
    code, output = _run(["execute", "--format", "json", 'Equal[1, 2]'])
    assert code == 0
    assert '"head": "False"' in output


def test_cli_preflight_json_accepts_query_with_warning():
    code, output = _run(
        ["preflight", "--correlation-id", "cli-preflight-001", EXAMPLES["query"]]
    )
    payload = json.loads(output)

    assert code == 0
    assert payload["schema_version"] == "coglang-preflight-decision/v0.1"
    assert payload["decision"] == "accepted_with_warnings"
    assert payload["reasons"] == ["effect.graph_read", "budget.within_default"]
    assert payload["required_review"] is False
    assert payload["effect_summary"]["effects"] == ["graph.read"]
    assert payload["budget_estimate"]["estimate_confidence"] == "estimated"
    assert payload["correlation_id"] == "cli-preflight-001"


def test_cli_preflight_text_requires_review_for_write():
    code, output = _run(["preflight", "--format", "text", EXAMPLES["write"]])

    assert code == 0
    assert "schema_version: coglang-preflight-decision/v0.1" in output
    assert "decision: requires_review" in output
    assert "required_review: true" in output
    assert "reasons: effect.graph_write, policy.review_required" in output
    assert "effects: graph.write, host.policy, human.review" in output


def test_cli_preflight_rejects_invalid_expression():
    code, output = _run(["preflight", "UnknownHead[]"])
    payload = json.loads(output)

    assert code == 1
    assert payload["decision"] == "rejected"
    assert payload["reasons"] == ["validation.invalid"]


def test_cli_preflight_rejects_missing_enabled_capability():
    code, output = _run(
        [
            "preflight",
            "--enabled-capability",
            "graph.read",
            EXAMPLES["write"],
        ]
    )
    payload = json.loads(output)

    assert code == 1
    assert payload["decision"] == "rejected"
    assert payload["reasons"] == [
        "capability.missing",
        "capability.missing.graph_write",
    ]
    assert payload["effect_summary"]["required_capabilities"] == ["graph.write"]
    assert payload["possible_errors"] == ["CapabilityRequired"]


def test_cli_preflight_rejects_known_result_count_over_budget():
    code, output = _run(
        [
            "preflight",
            "--max-result-count",
            "0",
            'Get["ada", "category"]',
        ]
    )
    payload = json.loads(output)

    assert code == 1
    assert payload["decision"] == "rejected"
    assert payload["reasons"] == ["budget.result_count_exceeded"]
    assert payload["budget"]["max_result_count"] == 0
    assert payload["budget_estimate"]["estimated_result_count"] == 1
    assert payload["possible_errors"] == ["BudgetExceeded", "ResultLimitExceeded"]


def test_cli_preflight_rejects_known_unification_branches_over_budget():
    code, output = _run(
        [
            "preflight",
            "--max-unification-branches",
            "0",
            "Unify[f[X_, b], f[a, Y_]]",
        ]
    )
    payload = json.loads(output)

    assert code == 1
    assert payload["decision"] == "rejected"
    assert payload["reasons"] == ["budget.unification_branches_exceeded"]
    assert payload["budget"]["max_unification_branches"] == 0
    assert payload["budget_estimate"]["estimated_unification_branches"] == 1
    assert payload["possible_errors"] == [
        "UnificationBranchLimitExceeded",
        "BudgetExceeded",
        "UnificationLimitExceeded",
    ]


def test_cli_preflight_fixture_json_output():
    code, output = _run(["preflight-fixture"])
    payload = json.loads(output)

    assert code == 0
    assert payload["schema_version"] == "coglang-preflight-fixture-result/v0.1"
    assert payload["fixture_schema_version"] == "coglang-preflight-fixture/v0.1"
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


def test_cli_preflight_fixture_text_output():
    code, output = _run(["preflight-fixture", "--format", "text"])

    assert code == 0
    assert "schema_version: coglang-preflight-fixture-result/v0.1" in output
    assert "fixture_schema_version: coglang-preflight-fixture/v0.1" in output
    assert "case_count: 9" in output
    assert "PF-001: ok decision=accepted_with_warnings" in output
    assert "PF-004: ok decision=rejected" in output
    assert "PF-007: ok decision=rejected" in output
    assert "PF-008: ok decision=rejected" in output
    assert "PF-009: ok decision=rejected" in output


def test_cli_conformance_targets_smoke():
    targets = _conformance_targets("smoke")
    normalized = [t.replace("\\", "/") for t in targets]
    assert any(
        item.endswith("tests/coglang/test_cli.py")
        or item.endswith("coglang/_public_assets/tests/coglang/test_cli.py")
        for item in normalized
    )
    assert any(
        item.endswith("tests/coglang/test_parser.py")
        or item.endswith("coglang/_public_assets/tests/coglang/test_parser.py")
        for item in normalized
    )
    assert any(
        item.endswith("tests/coglang/test_validator.py")
        or item.endswith("coglang/_public_assets/tests/coglang/test_validator.py")
        for item in normalized
    )


def test_cli_conformance_targets_full():
    normalized = [t.replace("\\", "/") for t in _conformance_targets("full")]
    assert len(normalized) == 1
    assert normalized[0].endswith("tests/coglang") or normalized[0].endswith(
        "coglang/_public_assets/tests/coglang"
    )


def test_cli_conformance_dispatch(monkeypatch):
    seen: dict[str, object] = {}

    def fake_runner(suite: str, pytest_args: list[str] | None = None) -> int:
        seen["suite"] = suite
        seen["pytest_args"] = pytest_args
        return 0

    monkeypatch.setattr(_cli_attr("_run_conformance_suite"), fake_runner)
    code, _ = _run(["conformance", "core", "--", "-k", "query_local_write"])
    assert code == 0
    assert seen["suite"] == "core"
    assert seen["pytest_args"] == ["-k", "query_local_write"]


def test_run_conformance_suite_cleans_tempdir_and_restores_environment(
    monkeypatch,
    tmp_path,
):
    root = tmp_path / "workspace"
    root.mkdir()
    seen: dict[str, object] = {}
    original_temp = os.environ.get("TEMP")
    original_tmp = os.environ.get("TMP")
    original_tempdir = tempfile.tempdir

    def fake_main(args: list[str]) -> int:
        redirected_tmp = root / ".tmp_pytest"
        seen["args"] = list(args)
        seen["temp"] = os.environ.get("TEMP")
        seen["tmp"] = os.environ.get("TMP")
        seen["tempdir"] = tempfile.tempdir
        seen["tmp_exists_during_run"] = redirected_tmp.exists()
        (redirected_tmp / "sentinel.lock").write_text("lock", encoding="utf-8")
        return 0

    monkeypatch.setitem(sys.modules, "pytest", types.SimpleNamespace(main=fake_main))
    monkeypatch.setattr(_cli_attr("_project_root"), lambda: root)
    monkeypatch.setattr(
        _cli_attr("_conformance_targets"),
        lambda suite: ["tests/coglang/test_cli.py"],
    )

    assert _run_conformance_suite("smoke") == 0
    assert seen["args"] == ["tests/coglang/test_cli.py"]
    assert seen["temp"] == str(root / ".tmp_pytest")
    assert seen["tmp"] == str(root / ".tmp_pytest")
    assert seen["tempdir"] == str(root / ".tmp_pytest")
    assert seen["tmp_exists_during_run"] is True
    assert not (root / ".tmp_pytest").exists()
    assert tempfile.tempdir == original_tempdir
    assert os.environ.get("TEMP") == original_temp
    assert os.environ.get("TMP") == original_tmp


def test_repl_executes_one_expression_then_quits():
    stdin = io.StringIO('Equal[1, 1]\n:quit\n')
    stdout = io.StringIO()
    code = _run_repl(stdin=stdin, stdout=stdout)
    rendered = stdout.getvalue()
    assert code == 0
    assert "CogLang REPL" in rendered
    assert "True[]" in rendered


def test_repl_prints_parse_error():
    stdin = io.StringIO('Equal[1, 1\n:quit\n')
    stdout = io.StringIO()
    code = _run_repl(stdin=stdin, stdout=stdout)
    rendered = stdout.getvalue()
    assert code == 0
    assert 'ParseError[' in rendered


def test_repl_help_then_exit():
    stdin = io.StringIO(':help\n:exit\n')
    stdout = io.StringIO()
    code = _run_repl(stdin=stdin, stdout=stdout)
    rendered = stdout.getvalue()
    assert code == 0
    assert "Enter one CogLang expression" in rendered


def test_cli_info_payload_shape():
    payload = _info_payload()
    assert payload["tool"] == "coglang"
    assert payload["package"] == DISTRIBUTION_NAME
    assert payload["language_release"] == "v1.1.0"
    assert "parse" in payload["commands"]
    assert "preflight" in payload["commands"]
    assert "preflight-fixture" in payload["commands"]
    assert "generation-eval" in payload["commands"]
    assert "smoke" in payload["conformance_suites"]
    assert "host-demo" in payload["commands"]
    assert "reference-host-demo" in payload["commands"]


def test_cli_info_json_output():
    code, output = _run(["info"])
    assert code == 0
    assert '"tool": "coglang"' in output
    assert f'"package": "{DISTRIBUTION_NAME}"' in output
    assert '"language_release": "v1.1.0"' in output


def test_cli_info_text_output():
    code, output = _run(["info", "--format", "text"])
    assert code == 0
    assert "tool: coglang" in output
    assert "language_release: v1.1.0" in output
    assert "conformance_suites: smoke, core, full" in output


def test_cli_manifest_payload_shape():
    payload = _manifest_payload()
    assert payload["schema_version"] == "coglang-cli-manifest/v0.1"
    assert payload["license"] == "Apache-2.0"
    assert payload["language_release"] == "v1.1.0"
    assert payload["entrypoints"]["console_script"] == "coglang"
    assert payload["entrypoints"]["recommended"] == "coglang"
    assert payload["implementation_metadata"]["distribution_name"] == DISTRIBUTION_NAME
    assert payload["docs"]["install_guide"].endswith("CogLang_Standalone_Install_and_Release_Guide_v0_1.md")
    assert payload["docs"]["hrc_v0_2_final_freeze"].endswith(
        "CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md"
    )
    assert payload["docs"]["vision_proposal"].endswith("CogLang_Vision_Proposal_v0_1.md")
    assert payload["docs"]["evolution_boundary_proposal"].endswith(
        "CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md"
    )
    assert payload["docs"]["effect_budget_preflight_vocabulary"].endswith(
        "CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md"
    )
    assert payload["docs"]["roadmap"].endswith("ROADMAP.md")
    assert payload["docs"]["maintenance"].endswith("MAINTENANCE.md")
    assert payload["machine_readable_summaries"]["llms"].endswith("llms.txt")
    assert payload["machine_readable_summaries"]["llms_full"].endswith("llms-full.txt")
    assert payload["public_release_surface"]["entrypoint"] == "coglang"
    assert payload["public_release_surface"]["project_docs"]["readme"] == payload["docs"]["readme"]
    assert (
        payload["public_release_surface"]["project_docs"]["vision_proposal"]
        == payload["docs"]["vision_proposal"]
    )
    assert (
        payload["public_release_surface"]["project_docs"]["evolution_boundary_proposal"]
        == payload["docs"]["evolution_boundary_proposal"]
    )
    assert (
        payload["public_release_surface"]["project_docs"]["effect_budget_preflight_vocabulary"]
        == payload["docs"]["effect_budget_preflight_vocabulary"]
    )
    assert payload["open_source_boundary"]["schema_version"] == "coglang-open-source-boundary/v0.1"
    assert payload["open_source_boundary"]["public_distribution_name"] == "coglang"
    assert payload["open_source_boundary"]["release_roots_exist"] is True
    assert payload["minimal_ci_baseline"]["schema_version"] == "coglang-minimal-ci-baseline/v0.1"
    assert payload["minimal_ci_baseline"]["required_command_names_present"] is True
    assert payload["minimal_ci_baseline"]["public_entrypoint_only"] is True
    assert payload["public_repo_extract_manifest"]["schema_version"] == "coglang-public-repo-extract-manifest/v0.1"
    assert payload["public_repo_extract_manifest"]["source_paths_exist"] is True
    assert payload["public_repo_extract_manifest"]["destination_paths_unique"] is True
    assert payload["formal_open_source_readiness"]["schema_version"] == "coglang-formal-open-source-readiness/v0.1"
    assert payload["formal_open_source_readiness"]["ready_for_candidate_decision"] is True


def test_cli_manifest_json_output():
    code, output = _run(["manifest"])
    assert code == 0
    assert '"schema_version": "coglang-cli-manifest/v0.1"' in output
    assert '"license": "Apache-2.0"' in output
    assert '"language_release": "v1.1.0"' in output
    assert '"public_release_surface"' in output
    assert '"machine_readable_summaries"' in output
    assert '"open_source_boundary"' in output
    assert '"minimal_ci_baseline"' in output
    assert '"public_repo_extract_manifest"' in output
    assert '"formal_open_source_readiness"' in output


def test_cli_manifest_text_output():
    code, output = _run(["manifest", "--format", "text"])
    assert code == 0
    assert "schema_version: coglang-cli-manifest/v0.1" in output
    assert "language_release: v1.1.0" in output
    assert "recommended_entrypoint: coglang" in output
    assert "console_script: coglang" in output
    assert f"roadmap: {_path_in_layout('ROADMAP.md', 'ROADMAP.md')}" in output
    assert (
        f"vision_proposal: "
        f"{_path_in_layout('CogLang_Vision_Proposal_v0_1.md', 'CogLang_Vision_Proposal_v0_1.md')}"
        in output
    )
    assert (
        f"evolution_boundary_proposal: "
        f"{_path_in_layout('CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md', 'CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md')}"
        in output
    )
    assert (
        f"effect_budget_preflight_vocabulary: "
        f"{_path_in_layout('CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md', 'CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md')}"
        in output
    )
    assert f"maintenance: {_path_in_layout('MAINTENANCE.md', 'MAINTENANCE.md')}" in output
    assert f"llms: {_path_in_layout('llms.txt', 'llms.txt')}" in output
    assert f"llms_full: {_path_in_layout('llms-full.txt', 'llms-full.txt')}" in output
    assert "open_source_boundary.strategy: standalone_repository" in output
    assert "open_source_boundary.distribution: coglang" in output
    assert (
        f"minimal_ci_baseline.path: "
        f"{_path_in_layout('CogLang_Minimal_CI_Baseline_v0_1.json', 'CogLang_Minimal_CI_Baseline_v0_1.json')}"
        in output
    )
    assert (
        f"public_repo_extract_manifest.path: "
        f"{_path_in_layout('CogLang_Public_Repo_Extract_Manifest_v0_1.json', 'CogLang_Public_Repo_Extract_Manifest_v0_1.json')}"
        in output
    )
    assert "formal_open_source_readiness.status: ready-for-formal-open-source-candidate-decision" in output


def test_cli_bundle_payload_shape():
    payload = _bundle_payload()
    assert payload["schema_version"] == "coglang-release-bundle/v0.1"
    assert payload["language_release"] == "v1.1.0"
    assert payload["public_release_surface"]["entrypoint"] == "coglang"
    assert payload["public_release_surface"]["project_docs"]["readme"].endswith(
        _path_in_layout("README.md", "README.md")
    )
    assert payload["open_source_boundary"]["repository_strategy"] == "standalone_repository"
    assert payload["minimal_ci_baseline"]["schema_version"] == "coglang-minimal-ci-baseline/v0.1"
    assert payload["public_repo_extract_manifest"]["schema_version"] == "coglang-public-repo-extract-manifest/v0.1"
    assert payload["formal_open_source_readiness"]["ready_for_candidate_decision"] is True
    assert payload["release_check"]["ok"] is True
    assert payload["doctor"]["ok"] is True


def test_cli_bundle_json_output():
    code, output = _run(["bundle"])
    assert code == 0
    assert '"schema_version": "coglang-release-bundle/v0.1"' in output
    assert '"language_release": "v1.1.0"' in output
    assert '"release_check"' in output
    assert '"doctor"' in output
    assert '"public_release_surface"' in output
    assert '"open_source_boundary"' in output
    assert '"minimal_ci_baseline"' in output
    assert '"public_repo_extract_manifest"' in output
    assert '"formal_open_source_readiness"' in output


def test_cli_bundle_text_output():
    code, output = _run(["bundle", "--format", "text"])
    assert code == 0
    assert "schema_version: coglang-release-bundle/v0.1" in output
    assert "language_release: v1.1.0" in output
    assert "public_release.entrypoint: coglang" in output
    assert f"public_release.readme: {_path_in_layout('README.md', 'README.md')}" in output
    assert "open_source_boundary.strategy: standalone_repository" in output
    assert (
        f"minimal_ci_baseline.path: "
        f"{_path_in_layout('CogLang_Minimal_CI_Baseline_v0_1.json', 'CogLang_Minimal_CI_Baseline_v0_1.json')}"
        in output
    )
    assert (
        f"public_repo_extract_manifest.path: "
        f"{_path_in_layout('CogLang_Public_Repo_Extract_Manifest_v0_1.json', 'CogLang_Public_Repo_Extract_Manifest_v0_1.json')}"
        in output
    )
    assert "formal_open_source_readiness.status: ready-for-formal-open-source-candidate-decision" in output
    assert "release_check.ok: true" in output
    assert "doctor.ok: true" in output


def test_cli_doctor_payload_shape():
    payload = _doctor_payload()
    assert payload["tool"] == "coglang"
    assert payload["language_release"] == "v1.1.0"
    assert isinstance(payload["checks"], list)
    assert any(item["name"] == "parse" for item in payload["checks"])


def test_cli_doctor_json_output():
    code, output = _run(["doctor"])
    assert code == 0
    assert '"tool": "coglang"' in output
    assert '"language_release": "v1.1.0"' in output
    assert '"checks"' in output


def test_cli_doctor_text_output():
    code, output = _run(["doctor", "--format", "text"])
    assert code == 0
    assert "tool: coglang" in output
    assert "language_release: v1.1.0" in output
    assert "parse: ok" in output


def test_cli_vocab_payload_shape():
    payload = _vocab_payload()
    assert payload["tool"] == "coglang"
    assert payload["vocab_size"] >= payload["error_head_count"]
    assert "Create" in payload["vocab"]


def test_cli_vocab_json_output():
    code, output = _run(["vocab"])
    assert code == 0
    assert '"vocab_size"' in output
    assert '"error_heads"' in output


def test_cli_vocab_text_output():
    code, output = _run(["vocab", "--format", "text"])
    assert code == 0
    assert "vocab_size:" in output
    assert "error_heads:" in output


def test_cli_examples_payload_shape():
    payload = _examples_payload()
    assert payload["tool"] == "coglang"
    assert payload["example_count"] >= 1
    assert any(item["name"] == "query" for item in payload["examples"])


def test_cli_examples_json_output():
    code, output = _run(["examples"])
    assert code == 0
    assert '"example_count"' in output
    assert '"examples"' in output


def test_cli_examples_text_output():
    code, output = _run(["examples", "--format", "text"])
    assert code == 0
    assert "example_count:" in output
    assert "query:" in output


def test_cli_examples_named_output():
    code, output = _run(["examples", "--name", "bind"])
    assert code == 0
    assert output == 'IfFound[Traverse["einstein", "born_in"], x_, x_, "unknown"]'


def _write_generation_eval_answers(path: Path, overrides: dict[str, str]) -> None:
    cases = load_generation_eval_cases()
    answers = reference_generation_eval_answers(cases)
    answers.update(overrides)
    path.write_text(
        json.dumps(
            {
                "answers": [
                    {"case_id": case_id, "output": output}
                    for case_id, output in answers.items()
                ]
            }
        ),
        encoding="utf-8",
    )


def test_cli_generation_eval_json_output():
    code, output = _run(["generation-eval"])
    payload = json.loads(output)

    assert code == 0
    assert payload["schema_version"] == "coglang-generation-eval-result/v0.1"
    assert payload["answer_source"] == "fixture_reference"
    assert payload["case_count"] == 50
    assert payload["failure_case_count"] == 0
    assert payload["failure_cases"] == []
    assert payload["summary"]["validate_ok_count"] == 50
    assert payload["summary"]["failure_category_counts"] == {}
    assert payload["maturity"]["highest_contiguous_level"] == "L3"
    assert payload["maturity"]["blocked_level"] is None
    assert payload["level_summary"]["L1"]["case_count"] == 18
    assert payload["level_summary"]["L2"]["case_count"] == 16
    assert payload["level_summary"]["L3"]["case_count"] == 16


def test_cli_generation_eval_summary_only_json_output():
    code, output = _run(["generation-eval", "--summary-only"])
    payload = json.loads(output)

    assert code == 0
    assert payload["case_count"] == 50
    assert "summary" in payload
    assert "level_summary" in payload
    assert "maturity" in payload
    assert payload["failure_cases"] == []
    assert "cases" not in payload


def test_cli_generation_eval_failures_only_json_output(tmp_path):
    answers_path = tmp_path / "answers.json"
    _write_generation_eval_answers(answers_path, {"L2-001": "BetterQuery[n_]"})

    code, output = _run(
        [
            "generation-eval",
            "--answers-file",
            str(answers_path),
            "--failures-only",
        ]
    )
    payload = json.loads(output)

    assert code == 1
    assert payload["case_count"] == 50
    assert payload["failure_case_count"] == 1
    assert [case["case_id"] for case in payload["cases"]] == ["L2-001"]
    assert [case["case_id"] for case in payload["failure_cases"]] == ["L2-001"]
    assert payload["maturity"]["highest_contiguous_level"] == "L1"
    assert payload["maturity"]["blocked_level"] == "L2"


def test_cli_generation_eval_text_output():
    code, output = _run(["generation-eval", "--format", "text"])

    assert code == 0
    assert "schema_version: coglang-generation-eval-result/v0.1" in output
    assert "answer_source: fixture_reference" in output
    assert "case_count: 50" in output
    assert "failure_case_count: 0" in output
    assert "maturity.highest_contiguous_level: L3" in output
    assert "maturity.blocked_level: none" in output
    assert "validate_ok: 50/50" in output
    assert "failure_category_counts: none" in output
    assert "L1: validate_ok 18/18, head_ok 18/18, hallucinated 0" in output
    assert "L2: validate_ok 16/16, head_ok 16/16, hallucinated 0" in output
    assert "L3: validate_ok 16/16, head_ok 16/16, hallucinated 0" in output


def test_cli_generation_eval_text_reports_failure_cases(tmp_path):
    answers_path = tmp_path / "answers.json"
    _write_generation_eval_answers(answers_path, {"L2-001": "BetterQuery[n_]"})

    code, output = _run(
        [
            "generation-eval",
            "--answers-file",
            str(answers_path),
            "--format",
            "text",
        ]
    )

    assert code == 1
    assert "failure_case_count: 1" in output
    assert "maturity.highest_contiguous_level: L1" in output
    assert "maturity.blocked_level: L2" in output
    assert (
        "failure L2-001 level=L2 "
        "categories=validation_error, top_level_head_mismatch, hallucinated_operator"
    ) in output


def test_cli_smoke_dispatch_success(monkeypatch):
    monkeypatch.setattr(_cli_attr("_doctor_payload"), lambda: {"ok": True, "checks": [1, 2, 3]})
    monkeypatch.setattr(_cli_attr("_run_conformance_suite"), lambda suite, pytest_args=None: 0)
    code, output = _run(["smoke"])
    assert code == 0
    assert '"suite": "smoke"' in output
    assert '"ok": true' in output


def test_cli_smoke_stops_on_doctor_failure(monkeypatch):
    monkeypatch.setattr(_cli_attr("_doctor_payload"), lambda: {"ok": False, "checks": []})
    code, output = _run(["smoke"])
    assert code == 1
    assert '"conformance": null' in output


def test_run_smoke_forwards_pytest_args(monkeypatch):
    seen: dict[str, object] = {}
    monkeypatch.setattr(_cli_attr("_doctor_payload"), lambda: {"ok": True, "checks": [1]})

    def fake_run(suite: str, pytest_args: list[str] | None = None) -> int:
        seen["suite"] = suite
        seen["pytest_args"] = pytest_args
        return 0

    monkeypatch.setattr(_cli_attr("_run_conformance_suite"), fake_run)
    code = _run_smoke(["-k", "cli"])
    assert code == 0
    assert seen["suite"] == "smoke"
    assert seen["pytest_args"] == ["-k", "cli"]


def test_cli_demo_payload():
    payload = _run_demo()
    assert payload["tool"] == "coglang"
    assert payload["ok"] is True
    assert len(payload["steps"]) >= 5


def test_cli_demo_json_output():
    code, output = _run(["demo"])
    assert code == 0
    assert '"steps"' in output
    assert '"ok": true' in output


def test_cli_demo_text_output():
    code, output = _run(["demo", "--format", "text"])
    assert code == 0
    assert "tool: coglang" in output
    assert "step1: ok" in output


def test_cli_host_demo_payload():
    payload = _run_host_demo()
    assert list(payload) == list(HOST_DEMO_TOP_LEVEL_KEYS)
    assert payload["schema_version"] == "coglang-host-demo/v0.1"
    assert payload["tool"] == "coglang"
    assert payload["ok"] is True
    assert payload["write_header"]["correlation_id"] == payload["correlation_id"]
    assert payload["write_header"]["submission_id"] == payload["submission_id"]
    assert payload["write_header"]["status"] == payload["status"]
    assert payload["write_header"]["payload_kind"] == payload["payload_kind"]
    assert payload["typed_write_header"] == payload["write_header"]
    assert (
        LocalWriteHeader.from_json(
            LocalWriteHeader.from_dict(payload["typed_write_header"]).to_json()
        ).to_dict()
        == payload["typed_write_header"]
    )
    assert payload["status"] == "committed"
    assert payload["payload_kind"] == "WriteResult"
    assert isinstance(payload["node_id"], str)
    assert isinstance(payload["correlation_id"], str)
    assert isinstance(payload["submission_id"], str)
    assert payload["typed_submission_message"]["header"]["correlation_id"] == payload["correlation_id"]
    assert payload["typed_submission_message"]["header"]["submission_id"] == payload["submission_id"]
    assert (
        WriteBundleSubmissionMessage.from_json(
            WriteBundleSubmissionMessage.from_dict(
                payload["typed_submission_message"]
            ).to_json()
        ).to_dict()
        == payload["typed_submission_message"]
    )
    assert payload["typed_response"]["header"]["correlation_id"] == payload["correlation_id"]
    assert payload["typed_response"]["header"]["submission_id"] == payload["submission_id"]
    assert payload["typed_response"]["header"]["payload_kind"] == payload["payload_kind"]
    assert (
        WriteBundleResponseMessage.from_json(
            WriteBundleResponseMessage.from_dict(payload["typed_response"]).to_json()
        ).to_dict()
        == payload["typed_response"]
    )
    assert payload["typed_submission_record"]["correlation_id"] == payload["correlation_id"]
    assert payload["typed_submission_record"]["submission_id"] == payload["submission_id"]
    assert payload["typed_submission_record"]["status"] == "committed"
    assert (
        LocalWriteSubmissionRecord.from_json(
            LocalWriteSubmissionRecord.from_dict(
                payload["typed_submission_record"]
            ).to_json()
        ).to_dict()
        == payload["typed_submission_record"]
    )
    assert len(payload["steps"]) == 5
    assert [step["name"] for step in payload["steps"]] == [
        "execute_and_submit_to",
        "typed_response",
        "query_result",
        "trace",
        "error_report",
    ]
    assert payload["steps"][0]["ok"] is True
    assert payload["steps"][0]["node_id"] == payload["node_id"]
    assert payload["steps"][0]["correlation_id"] == payload["correlation_id"]
    assert payload["steps"][0]["submission_id"] == payload["submission_id"]
    assert payload["steps"][0]["correlation_id"] == payload["write_header"]["correlation_id"]
    assert payload["steps"][0]["submission_id"] == payload["write_header"]["submission_id"]
    assert payload["steps"][1]["ok"] is True
    assert payload["steps"][1]["payload_kind"] == payload["payload_kind"]
    assert payload["steps"][1]["correlation_id"] == payload["correlation_id"]
    assert payload["steps"][1]["submission_id"] == payload["submission_id"]
    assert payload["steps"][1]["payload_kind"] == payload["typed_response"]["header"]["payload_kind"]
    assert payload["steps"][1]["correlation_id"] == payload["typed_response"]["header"]["correlation_id"]
    assert payload["steps"][1]["submission_id"] == payload["typed_response"]["header"]["submission_id"]
    assert payload["steps"][2]["ok"] is True
    assert payload["steps"][2]["status"] == payload["status"]
    assert payload["steps"][2]["submission_id"] == payload["submission_id"]
    assert payload["steps"][2]["status"] == payload["typed_query_result"]["status"]
    assert payload["steps"][2]["submission_id"] == payload["typed_query_result"]["submission_id"]
    assert payload["steps"][3]["ok"] is True
    assert payload["steps"][3]["submission_id"] == payload["submission_id"]
    assert payload["steps"][3]["submission_id"] == payload["typed_trace"]["submission_id"]
    assert payload["steps"][4]["ok"] is True
    assert payload["steps"][4]["status"] == "failed"
    assert payload["steps"][4]["payload_kind"] == "ErrorReport"
    assert payload["steps"][4]["error_kind"] == "ValidationError"
    assert payload["steps"][4]["retryable"] is True
    assert payload["steps"][4]["error_count"] >= 1
    assert payload["steps"][4]["correlation_id"] != payload["correlation_id"]
    assert payload["steps"][4]["submission_id"] != payload["submission_id"]
    assert payload["typed_query_result"]["status"] == "committed"
    assert payload["typed_query_result"]["status"] == payload["status"]
    assert payload["typed_query_result"]["correlation_id"] == payload["correlation_id"]
    assert payload["typed_query_result"]["submission_id"] == payload["submission_id"]
    assert (
        LocalWriteQueryResult.from_json(
            LocalWriteQueryResult.from_dict(payload["typed_query_result"]).to_json()
        ).to_dict()
        == payload["typed_query_result"]
    )
    assert payload["typed_trace"]["query_result"]["status"] == "committed"
    assert payload["typed_trace"]["correlation_id"] == payload["correlation_id"]
    assert payload["typed_trace"]["submission_id"] == payload["submission_id"]
    assert payload["typed_trace"]["request"] == payload["typed_submission_message"]
    assert payload["typed_trace"]["response"] == payload["typed_response"]
    assert payload["typed_trace"]["record"] == payload["typed_submission_record"]
    assert payload["typed_trace"]["query_result"] == payload["typed_query_result"]
    assert (
        LocalHostTrace.from_json(
            LocalHostTrace.from_dict(payload["typed_trace"]).to_json()
        ).to_dict()
        == payload["typed_trace"]
    )
    assert payload["typed_snapshot"]["graph"]["directed"] is True
    assert len(payload["typed_snapshot"]["graph"]["nodes"]) == 1
    assert len(payload["typed_snapshot"]["graph"]["edges"]) == 0
    assert len(payload["typed_snapshot"]["write_submission_messages"]) == 1
    assert len(payload["typed_snapshot"]["write_response_messages"]) == 1
    assert len(payload["typed_snapshot"]["write_submission_records"]) == 1
    assert len(payload["typed_snapshot"]["write_query_results"]) == 1
    assert len(payload["typed_snapshot"]["write_traces"]) == 1
    assert (
        LocalHostSnapshot.from_json(
            LocalHostSnapshot.from_dict(payload["typed_snapshot"]).to_json()
        ).to_dict()
        == payload["typed_snapshot"]
    )
    assert (
        payload["typed_snapshot"]["write_submission_messages"][0]
        == payload["typed_submission_message"]
    )
    assert (
        payload["typed_snapshot"]["write_response_messages"][0]
        == payload["typed_response"]
    )
    assert (
        payload["typed_snapshot"]["write_submission_records"][0]
        == payload["typed_submission_record"]
    )
    assert (
        payload["typed_snapshot"]["write_query_results"][0]
        == payload["typed_query_result"]
    )
    assert payload["typed_snapshot"]["write_traces"][0] == payload["typed_trace"]
    assert payload["typed_summary"]["node_count"] == 1
    assert payload["typed_summary"]["edge_count"] == 0
    assert payload["typed_summary"]["request_count"] == 1
    assert payload["typed_summary"]["trace_count"] == 1
    assert payload["typed_summary"]["response_count"] == 1
    assert payload["typed_summary"]["submission_record_count"] == 1
    assert payload["typed_summary"]["query_result_count"] == 1
    assert payload["typed_summary"]["status_counts"] == {"committed": 1}
    assert (
        LocalHostSummary.from_json(
            LocalHostSummary.from_dict(payload["typed_summary"]).to_json()
        ).to_dict()
        == payload["typed_summary"]
    )
    assert payload["typed_summary"]["node_count"] == len(payload["typed_snapshot"]["graph"]["nodes"])
    assert payload["typed_summary"]["edge_count"] == len(payload["typed_snapshot"]["graph"]["edges"])
    assert (
        payload["typed_summary"]["request_count"]
        == len(payload["typed_snapshot"]["write_submission_messages"])
    )
    assert (
        payload["typed_summary"]["response_count"]
        == len(payload["typed_snapshot"]["write_response_messages"])
    )
    assert (
        payload["typed_summary"]["submission_record_count"]
        == len(payload["typed_snapshot"]["write_submission_records"])
    )
    assert (
        payload["typed_summary"]["query_result_count"]
        == len(payload["typed_snapshot"]["write_query_results"])
    )
    assert (
        payload["typed_summary"]["trace_count"]
        == len(payload["typed_snapshot"]["write_traces"])
    )
    assert payload["snapshot_summary"] == LocalHostSummary.from_snapshot(
        LocalHostSnapshot.from_dict(payload["typed_snapshot"])
    ).to_dict()
    assert payload["typed_summary"] == payload["snapshot_summary"]
    assert payload["snapshot_summary"]["node_count"] == 1
    assert payload["snapshot_summary"]["edge_count"] == 0
    assert payload["snapshot_summary"]["request_count"] == 1
    assert payload["snapshot_summary"]["trace_count"] == 1
    assert payload["snapshot_summary"]["response_count"] == 1
    assert payload["snapshot_summary"]["submission_record_count"] == 1
    assert payload["snapshot_summary"]["query_result_count"] == 1
    assert payload["snapshot_summary"]["status_counts"] == {"committed": 1}


def test_cli_host_demo_json_output():
    code, output = _run(["host-demo"])
    assert code == 0
    assert '"schema_version": "coglang-host-demo/v0.1"' in output
    assert '"name": "execute_and_submit_to"' in output
    assert '"name": "typed_response"' in output
    assert '"name": "query_result"' in output
    assert '"name": "trace"' in output
    assert '"name": "error_report"' in output
    assert '"correlation_id"' in output
    assert '"submission_id"' in output
    assert '"status": "committed"' in output
    assert '"payload_kind": "WriteResult"' in output
    assert '"payload_kind": "ErrorReport"' in output
    assert '"error_kind": "ValidationError"' in output
    assert '"write_header"' in output
    assert '"typed_write_header"' in output
    assert '"node_id"' in output
    assert '"typed_submission_message"' in output
    assert '"typed_response"' in output
    assert '"typed_submission_record"' in output
    assert '"steps"' in output
    assert '"ok": true' in output
    assert '"status": "committed"' in output
    assert '"typed_query_result"' in output
    assert '"typed_snapshot"' in output
    assert '"typed_summary"' in output
    assert '"snapshot_summary"' in output


def test_cli_host_demo_text_output():
    code, output = _run(["host-demo", "--format", "text"])
    assert code == 0
    assert "schema_version: coglang-host-demo/v0.1" in output
    assert "tool: coglang" in output
    assert "correlation_id:" in output
    assert "submission_id:" in output
    assert "payload_kind: WriteResult" in output
    assert "node_id:" in output
    assert "write_header:" in output
    assert "typed_write_header:" in output
    assert "  correlation_id:" in output
    assert "status: committed" in output
    assert "step1: ok" in output
    assert "name: execute_and_submit_to" in output
    assert "name: typed_response" in output
    assert "name: query_result" in output
    assert "name: trace" in output
    assert "name: error_report" in output
    assert "payload_kind: ErrorReport" in output
    assert "error_kind: ValidationError" in output
    assert "typed_submission_message:" in output
    assert "typed_response:" in output
    assert "typed_submission_record:" in output
    assert "typed_query_result:" in output
    assert "typed_trace:" in output
    assert "typed_snapshot:" in output
    assert "typed_summary:" in output
    assert "snapshot_summary:" in output


def test_cli_reference_host_demo_payload():
    payload = _run_reference_host_demo()
    assert list(payload) == list(REFERENCE_HOST_DEMO_TOP_LEVEL_KEYS)
    assert payload["schema_version"] == "coglang-reference-host-demo/v0.1"
    assert payload["tool"] == "coglang"
    assert payload["ok"] is True
    assert payload["host_kind"] == "reference_transport_host"
    assert payload["status"] == "committed"
    assert payload["payload_kind"] == "WriteResult"
    assert payload["correlation_id"] == "reference-host-demo-success"
    assert payload["typed_submission_message"]["header"]["correlation_id"] == payload["correlation_id"]
    assert payload["typed_submission_message"]["header"]["submission_id"] == payload["submission_id"]
    assert payload["typed_response"]["header"]["correlation_id"] == payload["correlation_id"]
    assert payload["typed_response"]["header"]["submission_id"] == payload["submission_id"]
    assert payload["typed_response"]["header"]["payload_kind"] == "WriteResult"
    assert payload["typed_submission_record"]["correlation_id"] == payload["correlation_id"]
    assert payload["typed_submission_record"]["submission_id"] == payload["submission_id"]
    assert payload["typed_submission_record"]["status"] == "committed"
    assert payload["typed_query_result"]["correlation_id"] == payload["correlation_id"]
    assert payload["typed_query_result"]["submission_id"] == payload["submission_id"]
    assert payload["typed_query_result"]["status"] == "committed"
    assert payload["typed_write_header"] == {
        "correlation_id": payload["correlation_id"],
        "submission_id": payload["submission_id"],
        "status": "committed",
        "payload_kind": "WriteResult",
    }
    assert (
        WriteBundleSubmissionMessage.from_json(
            WriteBundleSubmissionMessage.from_dict(
                payload["typed_submission_message"]
            ).to_json()
        ).to_dict()
        == payload["typed_submission_message"]
    )
    assert (
        WriteBundleResponseMessage.from_json(
            WriteBundleResponseMessage.from_dict(payload["typed_response"]).to_json()
        ).to_dict()
        == payload["typed_response"]
    )
    assert (
        LocalWriteSubmissionRecord.from_json(
            LocalWriteSubmissionRecord.from_dict(
                payload["typed_submission_record"]
            ).to_json()
        ).to_dict()
        == payload["typed_submission_record"]
    )
    assert (
        LocalWriteQueryResult.from_json(
            LocalWriteQueryResult.from_dict(payload["typed_query_result"]).to_json()
        ).to_dict()
        == payload["typed_query_result"]
    )
    assert (
        LocalWriteHeader.from_json(
            LocalWriteHeader.from_dict(payload["typed_write_header"]).to_json()
        ).to_dict()
        == payload["typed_write_header"]
    )
    node_ids = {node["id"] for node in payload["graph"]["nodes"]}
    assert {"ada", "analytical_engine"} <= node_ids
    edges = payload["graph"].get("links", payload["graph"].get("edges", []))
    edge_refs = {
        (edge["source"], edge["target"], edge["relation_type"]) for edge in edges
    }
    assert ("ada", "analytical_engine", "designed") in edge_refs
    assert [step["name"] for step in payload["steps"]] == [
        "submit_json",
        "query_result",
        "write_header",
        "error_report",
    ]
    assert all(step["ok"] for step in payload["steps"])
    assert payload["steps"][-1]["status"] == "failed"
    assert payload["steps"][-1]["payload_kind"] == "ErrorReport"
    assert payload["steps"][-1]["error_kind"] == "ValidationError"
    assert payload["steps"][-1]["error_count"] >= 1
    assert payload["error_write_header"]["correlation_id"] == "reference-host-demo-error"
    assert payload["error_write_header"]["status"] == "failed"
    assert payload["error_write_header"]["payload_kind"] == "ErrorReport"
    assert payload["error_response"]["header"]["payload_kind"] == "ErrorReport"
    assert payload["error_response"]["payload"]["error_kind"] == "ValidationError"


def test_cli_reference_host_demo_json_output():
    code, output = _run(["reference-host-demo"])
    assert code == 0
    assert '"schema_version": "coglang-reference-host-demo/v0.1"' in output
    assert '"host_kind": "reference_transport_host"' in output
    assert '"name": "submit_json"' in output
    assert '"name": "query_result"' in output
    assert '"name": "write_header"' in output
    assert '"name": "error_report"' in output
    assert '"payload_kind": "WriteResult"' in output
    assert '"payload_kind": "ErrorReport"' in output
    assert '"error_kind": "ValidationError"' in output


def test_cli_reference_host_demo_text_output():
    code, output = _run(["reference-host-demo", "--format", "text"])
    assert code == 0
    assert "schema_version: coglang-reference-host-demo/v0.1" in output
    assert "host_kind: reference_transport_host" in output
    assert "status: committed" in output
    assert "payload_kind: WriteResult" in output
    assert "step1: ok" in output
    assert "name: submit_json" in output
    assert "name: query_result" in output
    assert "name: write_header" in output
    assert "name: error_report" in output
    assert "typed_submission_message:" in output
    assert "typed_response:" in output
    assert "typed_submission_record:" in output
    assert "typed_query_result:" in output
    assert "typed_write_header:" in output
    assert "error_response:" in output
    assert "error_write_header:" in output


def test_cli_host_demo_failure_payload_shape(monkeypatch):
    monkeypatch.setattr(
        _cli_host_attr("execute_and_submit_to_trace"),
        lambda self, target_host, expr, env=None, correlation_id=None, metadata=None: (None, None, None),
    )
    payload = _run_host_demo()
    assert list(payload) == list(HOST_DEMO_TOP_LEVEL_KEYS)
    assert payload["schema_version"] == "coglang-host-demo/v0.1"
    assert payload["ok"] is False
    assert payload["write_header"] is None
    assert payload["typed_write_header"] is None
    assert payload["status"] == "not_found"
    assert payload["payload_kind"] is None
    assert payload["node_id"] is None
    assert payload["correlation_id"] is None
    assert payload["submission_id"] is None
    assert payload["typed_submission_message"] is None
    assert payload["typed_response"] is None
    assert payload["typed_submission_record"] is None
    assert payload["typed_query_result"] is None
    assert payload["typed_trace"] is None
    assert payload["typed_snapshot"] is None
    assert payload["typed_summary"] is None
    assert payload["snapshot_summary"] is None
    assert payload["steps"] == [
        {
            "name": "create",
            "ok": False,
            "detail": "failed to execute and submit through LocalCogLangHost",
        }
    ]


def test_cli_host_demo_failure_when_public_trace_view_missing(monkeypatch):
    monkeypatch.setattr(
        _cli_host_attr("query_write_trace_dict"),
        lambda self, correlation_id: None,
    )
    payload = _run_host_demo()
    assert payload["ok"] is False
    assert payload["write_header"] is None
    assert payload["typed_trace"] is None
    assert payload["typed_submission_message"] is None
    assert payload["typed_response"] is None
    assert payload["typed_submission_record"] is None
    assert payload["typed_query_result"] is None
    assert payload["typed_snapshot"] is None
    assert payload["typed_summary"] is None
    assert payload["steps"] == [
        {
            "name": "create",
            "ok": False,
            "detail": "failed to execute and submit through LocalCogLangHost",
        }
    ]


def test_cli_host_demo_not_ok_when_typed_write_header_disagrees(monkeypatch):
    monkeypatch.setattr(
        _cli_host_attr("query_write_header"),
        lambda self, correlation_id: LocalWriteHeader(
            correlation_id="mismatch-correlation",
            submission_id="mismatch-submission",
            status="failed",
            payload_kind="ErrorReport",
        ),
    )
    payload = _run_host_demo()
    assert payload["ok"] is False
    assert payload["write_header"]["status"] == "committed"
    assert payload["typed_write_header"]["status"] == "failed"
    assert payload["write_header"] != payload["typed_write_header"]
    assert payload["typed_trace"] is not None
    assert payload["typed_snapshot"] is not None
    assert payload["typed_summary"] is not None
    assert payload["snapshot_summary"] is not None


def test_cli_host_demo_not_ok_when_typed_trace_disagrees_with_public_views(monkeypatch):
    def _mismatched_trace(self, correlation_id):
        trace = self.query_write_trace(correlation_id)
        assert trace is not None
        trace_dict = trace.to_dict()
        trace_dict["query_result"] = dict(trace_dict["query_result"])
        trace_dict["query_result"]["status"] = "failed"
        return trace_dict

    monkeypatch.setattr(
        _cli_host_attr("query_write_trace_dict"),
        _mismatched_trace,
    )
    payload = _run_host_demo()
    assert payload["ok"] is False
    assert payload["typed_trace"] is not None
    assert payload["typed_query_result"]["status"] == "committed"
    assert payload["typed_trace"]["query_result"]["status"] == "failed"
    assert payload["typed_trace"]["query_result"] != payload["typed_query_result"]
    assert payload["typed_snapshot"] is not None
    assert payload["snapshot_summary"] is not None


def test_cli_host_demo_not_ok_when_submission_message_disagrees_with_write_header(monkeypatch):
    def _mismatched_submission_message(self, correlation_id):
        message = self.query_write_submission_message_dict_by_submission_id(
            self.query_write(correlation_id).submission_id
        )
        assert message is not None
        message = dict(message)
        message["header"] = dict(message["header"])
        message["header"]["correlation_id"] = "mismatch-correlation"
        return message

    monkeypatch.setattr(
        _cli_host_attr("query_write_submission_message_dict"),
        _mismatched_submission_message,
    )
    payload = _run_host_demo()
    assert payload["ok"] is False
    assert payload["typed_submission_message"]["header"]["correlation_id"] == "mismatch-correlation"
    assert payload["write_header"]["correlation_id"] != payload["typed_submission_message"]["header"]["correlation_id"]
    assert payload["typed_trace"] is not None
    assert payload["typed_snapshot"] is not None


def test_cli_host_demo_not_ok_when_node_id_disagrees_with_response_payload(monkeypatch):
    def _mismatched_response(self, correlation_id):
        response = self.query_write_response_message_dict_by_submission_id(
            self.query_write(correlation_id).submission_id
        )
        assert response is not None
        response = dict(response)
        response["payload"] = dict(response["payload"])
        response["payload"]["touched_node_ids"] = ["mismatch-node-id"]
        return response

    monkeypatch.setattr(
        _cli_host_attr("query_write_response_message_dict"),
        _mismatched_response,
    )
    payload = _run_host_demo()
    assert payload["ok"] is False
    assert payload["node_id"] != payload["typed_response"]["payload"]["touched_node_ids"][0]
    assert payload["typed_snapshot"] is not None
    assert payload["typed_summary"] is not None


def test_cli_host_demo_not_ok_when_node_id_disagrees_with_submission_message(monkeypatch):
    def _mismatched_submission_message(self, correlation_id):
        message = self.query_write_submission_message_dict_by_submission_id(
            self.query_write(correlation_id).submission_id
        )
        assert message is not None
        message = dict(message)
        payload = dict(message["payload"])
        candidate = dict(payload["candidate"])
        operations = [dict(item) for item in candidate["operations"]]
        operations[0] = dict(operations[0])
        operations[0]["payload"] = dict(operations[0]["payload"])
        operations[0]["payload"]["id"] = "mismatch-node-id"
        candidate["operations"] = operations
        payload["candidate"] = candidate
        message["payload"] = payload
        return message

    monkeypatch.setattr(
        _cli_host_attr("query_write_submission_message_dict"),
        _mismatched_submission_message,
    )
    payload = _run_host_demo()
    assert payload["ok"] is False
    assert payload["typed_submission_message"]["payload"]["candidate"]["operations"][0]["payload"]["id"] == "mismatch-node-id"
    assert payload["node_id"] != payload["typed_submission_message"]["payload"]["candidate"]["operations"][0]["payload"]["id"]
    assert payload["typed_response"] is not None
    assert payload["typed_snapshot"] is not None


def test_cli_host_demo_not_ok_when_error_report_demo_is_missing(monkeypatch):
    monkeypatch.setattr(
        _cli_host_attr("submit_candidate_and_trace"),
        lambda self, candidate=None, correlation_id=None, metadata=None, consume=False: (None, None),
    )
    payload = _run_host_demo()
    assert payload["ok"] is False
    assert payload["steps"][-1]["name"] == "error_report"
    assert payload["steps"][-1]["ok"] is False
    assert "invalid write candidate" in payload["steps"][-1]["detail"]


def test_cli_host_demo_failure_text_output(monkeypatch):
    monkeypatch.setattr(
        _cli_host_attr("execute_and_submit_to_trace"),
        lambda self, target_host, expr, env=None, correlation_id=None, metadata=None: (None, None, None),
    )
    code, output = _run(["host-demo", "--format", "text"])
    assert code == 1
    assert "schema_version: coglang-host-demo/v0.1" in output
    assert "status: not_found" in output
    assert "payload_kind: None" in output
    assert "correlation_id: None" in output
    assert "submission_id: None" in output
    assert "node_id: None" in output
    assert "step1: fail" in output
    assert "name: create" in output
    assert "detail: failed to execute and submit through LocalCogLangHost" in output
    assert "write_header:" in output
    assert "typed_write_header:" in output
    assert "typed_submission_message:" in output
    assert "typed_response:" in output
    assert "typed_submission_record:" in output
    assert "typed_query_result:" in output
    assert "typed_trace:" in output
    assert "typed_snapshot:" in output
    assert "typed_summary:" in output
    assert "snapshot_summary:" in output
    assert "  null" in output


def test_cli_release_check_payload_shape():
    payload = _release_check_payload()
    assert payload["tool"] == "coglang"
    assert payload["language_release"] == "v1.1.0"
    assert isinstance(payload["checks"], list)
    assert any(item["name"] == "console_script" for item in payload["checks"])
    assert any(item["name"] == "distribution_metadata" for item in payload["checks"])
    assert any(item["name"] == "license_file" and item["ok"] is True for item in payload["checks"])
    assert any(item["name"] == "public_release_docs" and item["ok"] is True for item in payload["checks"])
    assert any(item["name"] == "open_source_boundary" and item["ok"] is True for item in payload["checks"])
    assert any(item["name"] == "minimal_ci_baseline" and item["ok"] is True for item in payload["checks"])
    assert any(item["name"] == "public_repo_extract_manifest" and item["ok"] is True for item in payload["checks"])
    assert any(item["name"] == "formal_open_source_readiness" and item["ok"] is True for item in payload["checks"])
    assert any(item["name"] == "preflight_fixture" and item["ok"] is True for item in payload["checks"])
    assert any(item["name"] == "generation_eval" and item["ok"] is True for item in payload["checks"])
    assert any(item["name"] == "node_host_consumer" and item["ok"] is True for item in payload["checks"])
    assert any(
        item["name"] == "node_minimal_host_runtime_stub"
        and item["ok"] is True
        for item in payload["checks"]
    )
    assert any(
        item["name"] == "executor_interface"
        and item["ok"] is True
        and item["detail"] == "abstract_methods=execute,validate"
        for item in payload["checks"]
    )
    assert payload["ok"] is True


def test_cli_release_check_json_output():
    code, output = _run(["release-check"])
    assert code == 0
    assert '"language_release": "v1.1.0"' in output
    assert '"checks"' in output
    assert '"license_file"' in output
    assert '"distribution_metadata"' in output
    assert '"public_release_docs"' in output
    assert '"open_source_boundary"' in output
    assert '"minimal_ci_baseline"' in output
    assert '"public_repo_extract_manifest"' in output
    assert '"formal_open_source_readiness"' in output
    assert '"preflight_fixture"' in output
    assert '"generation_eval"' in output
    assert '"node_host_consumer"' in output
    assert '"node_minimal_host_runtime_stub"' in output
    assert '"executor_interface"' in output


def test_cli_release_check_text_output():
    code, output = _run(["release-check", "--format", "text"])
    assert code == 0
    assert "tool: coglang" in output
    assert "language_release: v1.1.0" in output
    assert "license_file: ok (LICENSE)" in output
    assert "public_release_docs: ok (README + roadmap + maintenance + llms summaries)" in output
    assert (
        f"open_source_boundary: ok "
        f"({_path_in_layout('CogLang_Open_Source_Boundary_v0_1.json', 'CogLang_Open_Source_Boundary_v0_1.json')})"
        in output
    )
    assert (
        f"minimal_ci_baseline: ok "
        f"({_path_in_layout('CogLang_Minimal_CI_Baseline_v0_1.json', 'CogLang_Minimal_CI_Baseline_v0_1.json')})"
        in output
    )
    assert (
        f"public_repo_extract_manifest: ok "
        f"({_path_in_layout('CogLang_Public_Repo_Extract_Manifest_v0_1.json', 'CogLang_Public_Repo_Extract_Manifest_v0_1.json')})"
        in output
    )
    assert "formal_open_source_readiness: ok (ready-for-formal-open-source-candidate-decision)" in output
    assert "preflight_fixture: ok (9 cases)" in output
    assert "generation_eval: ok (50 cases)" in output
    assert "node_host_consumer: ok (examples/node_host_consumer + package data)" in output
    assert (
        "node_minimal_host_runtime_stub: ok "
        "(examples/node_minimal_host_runtime_stub + package data)" in output
    )
    assert "executor_interface: ok (abstract_methods=execute,validate)" in output


def test_cli_open_source_boundary_payload_shape():
    payload = _open_source_boundary_payload()
    assert payload["schema_version"] == "coglang-open-source-boundary/v0.1"
    assert payload["repository_strategy"] == "standalone_repository"
    assert payload["public_distribution_name"] == "coglang"
    assert payload["public_console_script"] == "coglang"
    assert payload["public_runtime_module"] == "coglang"
    assert "src/coglang" in payload["release_roots"]
    assert payload["release_roots_exist"] is True


def test_cli_minimal_ci_baseline_payload_shape():
    payload = _minimal_ci_baseline_payload()
    assert payload["schema_version"] == "coglang-minimal-ci-baseline/v0.1"
    assert payload["status"] == "defined-for-formal-open-source-prep"
    assert payload["workflow_template_path"] in {
        "CogLang_Public_CI_Workflow_v0_1.yml",
        ".github/workflows/ci.yml",
    }
    assert payload["workflow_template_present"] is True
    assert payload["publish_workflow_template_path"] in {
        "CogLang_Public_PyPI_Publish_Workflow_v0_1.yml",
        ".github/workflows/publish.yml",
    }
    assert payload["publish_workflow_template_present"] is True
    assert payload["publish_workflow_required_snippets_present"] is True
    assert payload["stable_release_policy"] == {
        "stable_language_tag": "v1.1.0",
        "stable_python_distribution_version": "1.1.2",
        "package_index": "PyPI",
        "pypi_project": "coglang",
        "trusted_publishing": True,
        "long_lived_api_token": False,
        "pre_releases_are_github_only": True,
    }
    assert payload["required_command_names_present"] is True
    assert payload["required_packaging_check_names_present"] is True
    assert payload["workflow_required_step_names_present"] is True
    assert payload["workflow_required_smoke_snippets_present"] is True
    assert payload["public_entrypoint_only"] is True
    assert payload["required_command_names"] == [
        "bundle",
        "release_check",
        "smoke",
        "conformance_smoke",
    ]
    assert payload["required_packaging_check_names"] == [
        "build_distributions",
        "wheel_install_release_check",
        "wheel_install_smoke",
        "sdist_install_release_check",
        "sdist_install_smoke",
    ]
    assert payload["workflow_required_step_names"] == [
        "Install build frontend",
        "Build sdist and wheel",
        "Validate installed wheel",
        "Validate installed sdist",
    ]
    assert payload["workflow_required_smoke_snippets"] == [
        ".tmp_ci_wheel/bin/python -m coglang smoke",
        ".tmp_ci_sdist/bin/python -m coglang smoke",
    ]
    assert payload["publish_workflow_required_snippets"] == [
        "pypa/gh-action-pypi-publish@release/v1",
        "id-token: write",
        "Verify stable tag matches package version",
    ]


def test_cli_public_repo_extract_manifest_payload_shape():
    payload = _public_repo_extract_manifest_payload()
    assert payload["schema_version"] == "coglang-public-repo-extract-manifest/v0.1"
    assert payload["repository_strategy"] == "standalone_repository"
    assert payload["public_distribution_name"] == "coglang"
    assert payload["entry_count"] == 48
    assert payload["required_destinations"] == [
        "pyproject.toml",
        "README.md",
        ".gitignore",
        "pytest.ini",
        "src/coglang",
        "tests/coglang",
        "LICENSE",
    ]
    assert payload["required_destinations_present"] is True
    assert payload["source_paths_exist"] is True
    assert payload["destination_paths_unique"] is True
    tree_entries = {item["source"]: item for item in payload["entries"] if item["kind"] == "tree"}
    assert "eval_fixtures" in tree_entries["src/coglang"]["include"]
    assert "generation_eval.py" in tree_entries["src/coglang"]["include"]
    assert "preflight.py" in tree_entries["src/coglang"]["include"]
    assert "test_catalog_alignment.py" in tree_entries["tests/coglang"]["include"]
    assert "test_executor_interface.py" in tree_entries["tests/coglang"]["include"]
    assert "test_generation_eval.py" in tree_entries["tests/coglang"]["include"]
    assert "test_node_host_consumer.py" in tree_entries["tests/coglang"]["include"]
    assert "test_node_minimal_host_runtime_stub.py" in tree_entries["tests/coglang"]["include"]
    assert "test_preflight.py" in tree_entries["tests/coglang"]["include"]
    assert "examples/node_host_consumer" in [
        item["source"] for item in payload["entries"]
    ]
    assert "examples/node_minimal_host_runtime_stub" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Operator_Catalog_v1_1_0.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Quickstart_v1_1_0.zh-CN.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Specification_v1_1_0_Draft.zh-CN.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Conformance_Suite_v1_1_0.zh-CN.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Release_Notes_v1_1_0.zh-CN.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Release_Notes_v1_1_2.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Release_Notes_v1_1_2.zh-CN.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Release_Notes_v1_1_1.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Release_Notes_v1_1_1.zh-CN.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Contribution_Guide_v0_1.zh-CN.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Vision_Proposal_v0_1.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Standalone_Install_and_Release_Guide_v0_1.zh-CN.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Host_Runtime_Contract_v0_1.zh-CN.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Profiles_and_Capabilities_v1_1_0.zh-CN.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "CogLang_Operator_Catalog_v1_1_0.zh-CN.md" in [
        item["source"] for item in payload["entries"]
    ]
    assert "internal_schemas/host_runtime/v0.1" in [
        item["source"] for item in payload["entries"]
    ]
    assert ".github/workflows/ci.yml" in [
        item["source"] for item in payload["entries"]
    ]
    assert ".github/workflows/publish.yml" in [
        item["source"] for item in payload["entries"]
    ]
    assert ".gitignore" in [
        item["source"] for item in payload["entries"]
    ]
    assert "pytest.ini" in [
        item["source"] for item in payload["entries"]
    ]


def test_cli_formal_open_source_readiness_payload_shape():
    payload = _formal_open_source_readiness_payload()
    assert payload["schema_version"] == "coglang-formal-open-source-readiness/v0.1"
    assert payload["gate_count"] == 7
    assert payload["passed_gate_count"] == 7
    assert payload["ready_for_candidate_decision"] is True
    assert payload["status"] == "ready-for-formal-open-source-candidate-decision"
    assert payload["decision_required"] is True
    assert [item["name"] for item in payload["gates"]] == [
        "G1_public_docs_boundary",
        "G2_public_release_surface",
        "G3_install_and_validation_surface",
        "G4_repo_package_boundary",
        "G5_minimal_ci_release_baseline",
        "G6_maintenance_and_contribution_surface",
        "G7_host_runtime_freeze_evidence",
    ]
    assert payload["gates"][-1]["detail"] == "HRC v0.2 final freeze record + host demos + Node consumer"


def test_cli_distribution_metadata_shape():
    payload = _distribution_metadata()
    assert payload["name"] == DISTRIBUTION_NAME
    assert payload["console_script"] == "coglang"
    assert payload["console_script_target"] == f"{MODULE_ENTRY}.cli:main"
    assert payload["module_entry"] == MODULE_ENTRY
    normalized = [item.replace("\\", "/") for item in payload["runtime_entry_paths"]]
    assert any(
        item == "src/coglang/cli.py"
        or item.endswith("/site-packages/coglang/cli.py")
        for item in normalized
    )
    assert any(
        item == "src/coglang/__main__.py"
        or item.endswith("/site-packages/coglang/__main__.py")
        for item in normalized
    )
