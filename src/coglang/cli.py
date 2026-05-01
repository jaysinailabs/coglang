from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from tempfile import gettempdir
from textwrap import dedent
from typing import Any
import tomllib

from .executor import CogLangExecutor, PythonCogLangExecutor
from .generation_eval import generation_eval_payload
from .local_host import LocalCogLangHost, LocalHostSnapshot, LocalHostSummary
from .parser import CogLangExpr, CogLangVar, canonicalize, parse
from .preflight import GraphBudget, preflight_expression, preflight_fixture_payload
from .reference_host import ReferenceTransportHost
from .validator import valid_coglang
from .vocab import COGLANG_VOCAB, ERROR_HEADS
from .write_bundle import WriteBundleCandidate, WriteOperation

EXAMPLES: dict[str, str] = {
    "parse": 'Equal[1, 1]',
    "query": 'Query[n_, Equal[Get[n_, "category"], "Person"]]',
    "bind": 'IfFound[Traverse["einstein", "born_in"], x_, x_, "unknown"]',
    "write": 'Create["Entity", {"category": "Person", "label": "Ada"}]',
    "trace": 'Trace[Equal[1, 1]]',
}

CLI_SCHEMA_VERSION = "coglang-cli-manifest/v0.1"
HOST_DEMO_SCHEMA_VERSION = "coglang-host-demo/v0.1"
REFERENCE_HOST_DEMO_SCHEMA_VERSION = "coglang-reference-host-demo/v0.1"
COGLANG_LANGUAGE_RELEASE = "v1.1.0"
HOST_DEMO_TOP_LEVEL_KEYS = (
    "schema_version",
    "tool",
    "version",
    "ok",
    "write_header",
    "typed_write_header",
    "status",
    "payload_kind",
    "node_id",
    "correlation_id",
    "submission_id",
    "typed_submission_message",
    "typed_response",
    "typed_submission_record",
    "typed_query_result",
    "typed_trace",
    "typed_snapshot",
    "typed_summary",
    "snapshot_summary",
    "steps",
)
REFERENCE_HOST_DEMO_TOP_LEVEL_KEYS = (
    "schema_version",
    "tool",
    "version",
    "ok",
    "host_kind",
    "status",
    "payload_kind",
    "correlation_id",
    "submission_id",
    "typed_submission_message",
    "typed_response",
    "typed_submission_record",
    "typed_query_result",
    "typed_write_header",
    "graph",
    "error_response",
    "error_write_header",
    "steps",
)


def _project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parents[3]


def _package_dir() -> Path:
    return Path(__file__).resolve().parent


def _package_assets_root() -> Path:
    return _package_dir() / "_public_assets"


def _installed_public_package_mode() -> bool:
    return _package_assets_root().exists() and not (_project_root() / "src" / "coglang").exists()


def _paths_exist(root: Path, paths: list[str]) -> bool:
    if not paths:
        return False
    for raw_path in paths:
        path = Path(raw_path)
        candidate = path if path.is_absolute() else root / path
        if not candidate.exists():
            return False
    return True


def _conformance_base() -> Path:
    root = _project_root()
    project_base = root / "tests" / "coglang"
    if project_base.exists():
        return project_base
    assets_base = _package_assets_root() / "tests" / "coglang"
    if assets_base.exists():
        return assets_base
    return project_base


def _cli_version() -> str:
    distribution = _distribution_metadata()
    candidates = [distribution["name"], "coglang"]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            return package_version(candidate)
        except PackageNotFoundError:
            continue
    return "1.1.2"


def _resolve_project_artifact(*relative_candidates: str) -> tuple[Path, str]:
    root = _project_root()
    assets_root = _package_assets_root()
    normalized = [candidate.replace("\\", "/") for candidate in relative_candidates]
    for candidate, normalized_candidate in zip(relative_candidates, normalized):
        path = root / Path(candidate)
        if path.exists():
            return path, normalized_candidate
    if assets_root.exists():
        for candidate, normalized_candidate in zip(relative_candidates, normalized):
            path = assets_root / Path(candidate)
            if path.exists():
                return path, normalized_candidate
    return root / Path(relative_candidates[0]), normalized[0]


def _read_expr(args: argparse.Namespace) -> str:
    if args.expr is not None:
        return args.expr
    if args.file is not None:
        return Path(args.file).read_text(encoding="utf-8")
    return sys.stdin.read()


def _jsonable(value: Any) -> Any:
    if isinstance(value, CogLangVar):
        return {
            "kind": "var",
            "name": value.name,
            "is_anonymous": value.is_anonymous,
        }
    if isinstance(value, CogLangExpr):
        payload: dict[str, Any] = {
            "kind": "expr",
            "head": value.head,
            "args": [_jsonable(arg) for arg in value.args],
        }
        if value.partial is not None:
            payload["partial"] = _jsonable(value.partial)
        return payload
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    return value


def _emit(value: Any, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(_jsonable(value), ensure_ascii=False, indent=2))
        return
    if output_format == "repr":
        print(repr(value))
        return
    print(canonicalize(value))


def _info_payload() -> dict[str, Any]:
    distribution = _distribution_metadata()
    return {
        "tool": "coglang",
        "package": distribution["name"] or "coglang",
        "version": _cli_version(),
        "language_release": COGLANG_LANGUAGE_RELEASE,
        "commands": [
            "parse",
            "canonicalize",
            "validate",
            "preflight",
            "preflight-fixture",
            "execute",
            "conformance",
            "repl",
            "info",
            "manifest",
            "bundle",
            "doctor",
            "vocab",
            "examples",
            "generation-eval",
            "smoke",
            "demo",
            "host-demo",
            "reference-host-demo",
            "release-check",
        ],
        "conformance_suites": ["smoke", "core", "full"],
    }


def _distribution_metadata() -> dict[str, Any]:
    root = _project_root()
    package_dir = _package_dir()
    pyproject_path, _ = _resolve_project_artifact("pyproject.toml")
    if not pyproject_path.exists():
        return {
            "name": None,
            "console_script": None,
            "console_script_target": None,
            "entry_module": None,
            "module_entry": None,
            "runtime_entry_paths": [],
        }
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = pyproject.get("project", {})
    console_script = project.get("scripts", {}).get("coglang")
    entry_module = None
    module_entry = None
    runtime_entry_paths: list[str] = []
    if console_script:
        entry_module = console_script.split(":", 1)[0]
        module_entry = ".".join(entry_module.split(".")[:-1]) if "." in entry_module else entry_module
        cli_path = root / "src" / Path(*entry_module.split(".")).with_suffix(".py")
        if cli_path.exists():
            runtime_entry_paths.append(str(cli_path.relative_to(root)).replace("\\", "/"))
        else:
            runtime_entry_paths.append(str((package_dir / "cli.py").resolve()))
        if module_entry:
            main_path = root / "src" / Path(*module_entry.split(".")) / "__main__.py"
            if main_path.exists():
                runtime_entry_paths.append(str(main_path.relative_to(root)).replace("\\", "/"))
            else:
                runtime_entry_paths.append(str((package_dir / "__main__.py").resolve()))
    return {
        "name": project.get("name"),
        "console_script": "coglang" if console_script else None,
        "console_script_target": console_script,
        "entry_module": entry_module,
        "module_entry": module_entry,
        "runtime_entry_paths": runtime_entry_paths,
    }


def _open_source_boundary_payload() -> dict[str, Any]:
    root = _project_root()
    descriptor_path, descriptor_relpath = _resolve_project_artifact(
        "CogLang_Open_Source_Boundary_v0_1.json",
        "CogLang_Open_Source_Boundary_v0_1.json",
    )
    if not descriptor_path.exists():
        return {
            "path": descriptor_relpath,
            "schema_version": None,
            "status": "missing",
            "repository_strategy": None,
            "public_distribution_name": None,
            "public_console_script": None,
            "public_runtime_module": None,
            "release_roots": [],
            "release_roots_exist": False,
        }
    payload = json.loads(descriptor_path.read_text(encoding="utf-8"))
    release_roots = payload.get("release_roots", [])
    release_roots_exist = bool(release_roots) and all(
        (root / Path(path)).exists() for path in release_roots
    )
    if not release_roots_exist and (root / "pyproject.toml").exists():
        release_roots_exist = (root / "src" / "coglang").exists() and (root / "tests" / "coglang").exists()
    if not release_roots_exist and _installed_public_package_mode():
        release_roots_exist = _package_dir().exists() and _package_assets_root().exists()
    payload["path"] = descriptor_relpath
    payload["release_roots_exist"] = release_roots_exist
    return payload


def _minimal_ci_baseline_payload() -> dict[str, Any]:
    root = _project_root()
    descriptor_path, descriptor_relpath = _resolve_project_artifact(
        "CogLang_Minimal_CI_Baseline_v0_1.json",
        "CogLang_Minimal_CI_Baseline_v0_1.json",
    )
    workflow_template_path, workflow_template_relpath = _resolve_project_artifact(
        "CogLang_Public_CI_Workflow_v0_1.yml",
        ".github/workflows/ci.yml",
    )
    publish_workflow_template_path, publish_workflow_template_relpath = _resolve_project_artifact(
        "CogLang_Public_PyPI_Publish_Workflow_v0_1.yml",
        ".github/workflows/publish.yml",
    )
    required_command_names = [
        "bundle",
        "release_check",
        "smoke",
        "conformance_smoke",
        "host_demo",
        "reference_host_demo",
    ]
    required_packaging_check_names = [
        "build_distributions",
        "wheel_install_release_check",
        "wheel_install_smoke",
        "wheel_install_hrc_host_demos",
        "sdist_install_release_check",
        "sdist_install_smoke",
        "sdist_install_hrc_host_demos",
    ]
    workflow_required_step_names = [
        "Install build frontend",
        "Build sdist and wheel",
        "Validate installed wheel",
        "Validate installed sdist",
        "Run HRC host demos",
    ]
    workflow_required_smoke_snippets = [
        ".tmp_ci_wheel/bin/python -m coglang smoke",
        ".tmp_ci_wheel/bin/python -m coglang host-demo",
        ".tmp_ci_wheel/bin/python -m coglang reference-host-demo",
        ".tmp_ci_sdist/bin/python -m coglang smoke",
        ".tmp_ci_sdist/bin/python -m coglang host-demo",
        ".tmp_ci_sdist/bin/python -m coglang reference-host-demo",
        "python -m coglang host-demo",
        "python -m coglang reference-host-demo",
    ]
    publish_workflow_required_snippets = [
        "pypa/gh-action-pypi-publish@release/v1",
        "id-token: write",
        "Verify stable tag matches package version",
    ]
    if not descriptor_path.exists():
        return {
            "path": descriptor_relpath,
            "schema_version": None,
            "status": "missing",
            "commands": [],
            "workflow_template_path": workflow_template_relpath,
            "workflow_template_present": False,
            "publish_workflow_template_path": publish_workflow_template_relpath,
            "publish_workflow_template_present": False,
            "publish_workflow_required_snippets": publish_workflow_required_snippets,
            "publish_workflow_required_snippets_present": False,
            "required_command_names": required_command_names,
            "required_command_names_present": False,
            "packaging_verification": [],
            "required_packaging_check_names": required_packaging_check_names,
            "required_packaging_check_names_present": False,
            "workflow_required_step_names": workflow_required_step_names,
            "workflow_required_step_names_present": False,
            "workflow_required_smoke_snippets": workflow_required_smoke_snippets,
            "workflow_required_smoke_snippets_present": False,
            "public_entrypoint_only": False,
        }
    payload = json.loads(descriptor_path.read_text(encoding="utf-8"))
    commands = payload.get("commands", [])
    command_names = [item.get("name") for item in commands if isinstance(item, dict)]
    packaging_verification = payload.get("packaging_verification", [])
    packaging_check_names = [
        item.get("name") for item in packaging_verification if isinstance(item, dict)
    ]
    public_entrypoint_only = all(
        isinstance(item, dict) and str(item.get("command", "")).startswith("coglang ")
        for item in commands
    )
    workflow_text = (
        workflow_template_path.read_text(encoding="utf-8")
        if workflow_template_path.exists()
        else ""
    )
    publish_workflow_text = (
        publish_workflow_template_path.read_text(encoding="utf-8")
        if publish_workflow_template_path.exists()
        else ""
    )
    payload["path"] = descriptor_relpath
    payload["workflow_template_path"] = workflow_template_relpath
    payload["workflow_template_present"] = workflow_template_path.exists()
    payload["publish_workflow_template_path"] = publish_workflow_template_relpath
    payload["publish_workflow_template_present"] = publish_workflow_template_path.exists()
    payload["publish_workflow_required_snippets"] = publish_workflow_required_snippets
    payload["publish_workflow_required_snippets_present"] = all(
        snippet in publish_workflow_text for snippet in publish_workflow_required_snippets
    )
    payload["required_command_names"] = required_command_names
    payload["required_command_names_present"] = all(
        name in command_names for name in required_command_names
    )
    payload["required_packaging_check_names"] = required_packaging_check_names
    payload["required_packaging_check_names_present"] = all(
        name in packaging_check_names for name in required_packaging_check_names
    )
    payload["workflow_required_step_names"] = workflow_required_step_names
    payload["workflow_required_step_names_present"] = all(
        name in workflow_text for name in workflow_required_step_names
    )
    payload["workflow_required_smoke_snippets"] = workflow_required_smoke_snippets
    payload["workflow_required_smoke_snippets_present"] = all(
        snippet in workflow_text for snippet in workflow_required_smoke_snippets
    )
    payload["public_entrypoint_only"] = public_entrypoint_only
    return payload


def _public_repo_extract_manifest_payload() -> dict[str, Any]:
    root = _project_root()
    descriptor_path, descriptor_relpath = _resolve_project_artifact(
        "CogLang_Public_Repo_Extract_Manifest_v0_1.json",
        "CogLang_Public_Repo_Extract_Manifest_v0_1.json",
    )
    required_destinations = [
        "pyproject.toml",
        "README.md",
        ".gitignore",
        "pytest.ini",
        "src/coglang",
        "tests/coglang",
        "LICENSE",
    ]
    if not descriptor_path.exists():
        return {
            "path": descriptor_relpath,
            "schema_version": None,
            "status": "missing",
            "repository_strategy": None,
            "public_distribution_name": None,
            "entry_count": 0,
            "required_destinations": required_destinations,
            "required_destinations_present": False,
            "source_paths_exist": False,
            "destination_paths_unique": False,
        }
    payload = json.loads(descriptor_path.read_text(encoding="utf-8"))
    entries = payload.get("entries", [])
    sources = [str(item.get("source", "")) for item in entries if isinstance(item, dict)]
    destinations = [str(item.get("destination", "")) for item in entries if isinstance(item, dict)]
    payload["path"] = descriptor_relpath
    payload["entry_count"] = len(entries)
    payload["required_destinations"] = required_destinations
    payload["required_destinations_present"] = all(
        destination in destinations for destination in required_destinations
    )
    materialized_public_root = descriptor_path.parent == root and all(
        (root / Path(path)).exists() for path in required_destinations
    )
    payload["source_paths_exist"] = (
        bool(sources) and all((root / Path(path)).exists() for path in sources)
    ) or materialized_public_root
    if not payload["source_paths_exist"] and _installed_public_package_mode():
        payload["source_paths_exist"] = _package_dir().exists() and _package_assets_root().exists()
    payload["destination_paths_unique"] = bool(destinations) and len(destinations) == len(set(destinations))
    return payload


def _formal_open_source_readiness_payload() -> dict[str, Any]:
    root = _project_root()
    distribution = _distribution_metadata()
    boundary = _open_source_boundary_payload()
    ci_baseline = _minimal_ci_baseline_payload()
    public_repo_extract_manifest = _public_repo_extract_manifest_payload()
    info = _info_payload()
    readme_path, _ = _resolve_project_artifact("README.md", "README.md")
    quickstart_path, _ = _resolve_project_artifact(
        "CogLang_Quickstart_v1_1_0.md",
        "CogLang_Quickstart_v1_1_0.md",
    )
    reserved_operator_promotion_criteria_path, _ = _resolve_project_artifact(
        "CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md",
        "CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md",
    )
    send_carry_forward_exit_matrix_path, _ = _resolve_project_artifact(
        "CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md",
        "CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md",
    )
    readable_render_boundary_path, _ = _resolve_project_artifact(
        "CogLang_Readable_Render_Boundary_v0_1.md",
        "CogLang_Readable_Render_Boundary_v0_1.md",
    )
    install_guide_path, _ = _resolve_project_artifact(
        "CogLang_Standalone_Install_and_Release_Guide_v0_1.md",
        "CogLang_Standalone_Install_and_Release_Guide_v0_1.md",
    )
    contribution_guide_path, _ = _resolve_project_artifact(
        "CogLang_Contribution_Guide_v0_1.md",
        "CogLang_Contribution_Guide_v0_1.md",
    )
    release_notes_path, _ = _resolve_project_artifact(
        "CogLang_Release_Notes_v1_1_2.md",
        "CogLang_Release_Notes_v1_1_2.md",
    )
    hrc_v0_2_final_freeze_path, _ = _resolve_project_artifact(
        "CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md",
        "CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md",
    )
    hrc_companion_asset_classification_path, _ = _resolve_project_artifact(
        "CogLang_HRC_Companion_Asset_Classification_v0_1.md",
        "CogLang_HRC_Companion_Asset_Classification_v0_1.md",
    )
    node_consumer_script_path, _ = _resolve_project_artifact(
        "examples/node_host_consumer/consume_hrc_envelopes.mjs",
    )
    node_consumer_readme_path, _ = _resolve_project_artifact(
        "examples/node_host_consumer/README.md",
    )
    roadmap_path, _ = _resolve_project_artifact("ROADMAP.md", "ROADMAP.md")
    maintenance_path, _ = _resolve_project_artifact("MAINTENANCE.md", "MAINTENANCE.md")
    public_docs_checklist_path, _ = _resolve_project_artifact(
        "CogLang_Public_Docs_Readiness_Checklist_v0_1.md",
    )
    llms_path, _ = _resolve_project_artifact("llms.txt", "llms.txt")
    llms_full_path, _ = _resolve_project_artifact("llms-full.txt", "llms-full.txt")

    gates = [
        {
            "name": "G1_public_docs_boundary",
            "ok": (
                readme_path.exists()
                and quickstart_path.exists()
                and reserved_operator_promotion_criteria_path.exists()
                and send_carry_forward_exit_matrix_path.exists()
                and readable_render_boundary_path.exists()
                and llms_path.exists()
                and llms_full_path.exists()
            ),
            "detail": "public docs set + operator/render boundaries",
        },
        {
            "name": "G2_public_release_surface",
            "ok": (
                distribution["console_script"] == "coglang"
                and bool(distribution["console_script_target"])
                and boundary["public_distribution_name"] == "coglang"
                and boundary["public_console_script"] == "coglang"
            ),
            "detail": "coglang entrypoint + machine-readable release surface",
        },
        {
            "name": "G3_install_and_validation_surface",
            "ok": (
                install_guide_path.exists()
                and "bundle" in info["commands"]
                and "release-check" in info["commands"]
                and "smoke" in info["commands"]
                and ci_baseline["required_command_names_present"] is True
                and ci_baseline["required_packaging_check_names_present"] is True
                and ci_baseline["workflow_required_smoke_snippets_present"] is True
            ),
            "detail": "install guide + bundle/release-check/smoke path",
        },
        {
            "name": "G4_repo_package_boundary",
            "ok": (
                boundary["schema_version"] == "coglang-open-source-boundary/v0.1"
                and bool(boundary["repository_strategy"])
                and boundary["public_distribution_name"] == "coglang"
                and boundary["release_roots_exist"] is True
                and public_repo_extract_manifest["schema_version"]
                == "coglang-public-repo-extract-manifest/v0.1"
                and public_repo_extract_manifest["source_paths_exist"] is True
                and public_repo_extract_manifest["destination_paths_unique"] is True
                and public_repo_extract_manifest["required_destinations_present"] is True
            ),
            "detail": boundary["path"],
        },
        {
            "name": "G5_minimal_ci_release_baseline",
            "ok": (
                ci_baseline["schema_version"] == "coglang-minimal-ci-baseline/v0.1"
                and ci_baseline["required_command_names_present"] is True
                and ci_baseline["required_packaging_check_names_present"] is True
                and ci_baseline["public_entrypoint_only"] is True
                and ci_baseline["workflow_template_present"] is True
                and ci_baseline["workflow_required_step_names_present"] is True
                and ci_baseline["workflow_required_smoke_snippets_present"] is True
            ),
            "detail": ci_baseline["path"],
        },
        {
            "name": "G6_maintenance_and_contribution_surface",
            "ok": (
                contribution_guide_path.exists()
                and release_notes_path.exists()
                and roadmap_path.exists()
                and maintenance_path.exists()
            ),
            "detail": "contribution + release notes + roadmap + maintenance",
        },
        {
            "name": "G7_host_runtime_freeze_evidence",
            "ok": (
                hrc_v0_2_final_freeze_path.exists()
                and hrc_companion_asset_classification_path.exists()
                and "host-demo" in info["commands"]
                and "reference-host-demo" in info["commands"]
                and node_consumer_script_path.exists()
                and node_consumer_readme_path.exists()
            ),
            "detail": "HRC v0.2 final freeze record + companion classification + host demos + Node consumer",
        },
    ]
    passed_gate_count = sum(1 for item in gates if item["ok"])
    ready_for_candidate_decision = passed_gate_count == len(gates)
    return {
        "schema_version": "coglang-formal-open-source-readiness/v0.1",
        "gate_count": len(gates),
        "passed_gate_count": passed_gate_count,
        "ready_for_candidate_decision": ready_for_candidate_decision,
        "status": (
            "ready-for-formal-open-source-candidate-decision"
            if ready_for_candidate_decision
            else "not-ready-for-formal-open-source-candidate-decision"
        ),
        "decision_required": True,
        "gates": gates,
    }


def _manifest_payload() -> dict[str, Any]:
    info = _info_payload()
    distribution = _distribution_metadata()
    open_source_boundary = _open_source_boundary_payload()
    minimal_ci_baseline = _minimal_ci_baseline_payload()
    public_repo_extract_manifest = _public_repo_extract_manifest_payload()
    formal_open_source_readiness = _formal_open_source_readiness_payload()
    readme_relpath = _resolve_project_artifact("README.md", "README.md")[1]
    quickstart_relpath = _resolve_project_artifact(
        "CogLang_Quickstart_v1_1_0.md",
        "CogLang_Quickstart_v1_1_0.md",
    )[1]
    spec_relpath = _resolve_project_artifact(
        "CogLang_Specification_v1_1_0_Draft.md",
        "CogLang_Specification_v1_1_0_Draft.md",
    )[1]
    install_guide_relpath = _resolve_project_artifact(
        "CogLang_Standalone_Install_and_Release_Guide_v0_1.md",
        "CogLang_Standalone_Install_and_Release_Guide_v0_1.md",
    )[1]
    release_notes_relpath = _resolve_project_artifact(
        "CogLang_Release_Notes_v1_1_2.md",
        "CogLang_Release_Notes_v1_1_2.md",
    )[1]
    hrc_v0_2_final_freeze_relpath = _resolve_project_artifact(
        "CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md",
        "CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md",
    )[1]
    hrc_companion_asset_classification_relpath = _resolve_project_artifact(
        "CogLang_HRC_Companion_Asset_Classification_v0_1.md",
        "CogLang_HRC_Companion_Asset_Classification_v0_1.md",
    )[1]
    contribution_guide_relpath = _resolve_project_artifact(
        "CogLang_Contribution_Guide_v0_1.md",
        "CogLang_Contribution_Guide_v0_1.md",
    )[1]
    reserved_operator_promotion_criteria_relpath = _resolve_project_artifact(
        "CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md",
        "CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md",
    )[1]
    send_carry_forward_exit_matrix_relpath = _resolve_project_artifact(
        "CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md",
        "CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md",
    )[1]
    readable_render_boundary_relpath = _resolve_project_artifact(
        "CogLang_Readable_Render_Boundary_v0_1.md",
        "CogLang_Readable_Render_Boundary_v0_1.md",
    )[1]
    vision_proposal_relpath = _resolve_project_artifact(
        "CogLang_Vision_Proposal_v0_1.md",
        "CogLang_Vision_Proposal_v0_1.md",
    )[1]
    evolution_boundary_proposal_relpath = _resolve_project_artifact(
        "CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md",
        "CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md",
    )[1]
    effect_budget_preflight_vocabulary_relpath = _resolve_project_artifact(
        "CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md",
        "CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md",
    )[1]
    roadmap_relpath = _resolve_project_artifact("ROADMAP.md", "ROADMAP.md")[1]
    maintenance_relpath = _resolve_project_artifact("MAINTENANCE.md", "MAINTENANCE.md")[1]
    llms_relpath = _resolve_project_artifact("llms.txt", "llms.txt")[1]
    llms_full_relpath = _resolve_project_artifact("llms-full.txt", "llms-full.txt")[1]
    docs = {
        "readme": readme_relpath,
        "quickstart": quickstart_relpath,
        "spec": spec_relpath,
        "install_guide": install_guide_relpath,
        "release_notes": release_notes_relpath,
        "hrc_v0_2_final_freeze": hrc_v0_2_final_freeze_relpath,
        "hrc_companion_asset_classification": hrc_companion_asset_classification_relpath,
        "contribution_guide": contribution_guide_relpath,
        "reserved_operator_promotion_criteria": reserved_operator_promotion_criteria_relpath,
        "send_carry_forward_exit_matrix": send_carry_forward_exit_matrix_relpath,
        "readable_render_boundary": readable_render_boundary_relpath,
        "vision_proposal": vision_proposal_relpath,
        "evolution_boundary_proposal": evolution_boundary_proposal_relpath,
        "effect_budget_preflight_vocabulary": effect_budget_preflight_vocabulary_relpath,
        "roadmap": roadmap_relpath,
        "maintenance": maintenance_relpath,
    }
    machine_readable_summaries = {
        "llms": llms_relpath,
        "llms_full": llms_full_relpath,
    }
    return {
        "schema_version": CLI_SCHEMA_VERSION,
        "tool": info["tool"],
        "package": info["package"],
        "version": info["version"],
        "language_release": info["language_release"],
        "status": "stable-language-release",
        "license": "Apache-2.0",
        "entrypoints": {
            "recommended": "coglang",
            "console_script": "coglang",
        },
        "implementation_metadata": {
            "distribution_name": distribution["name"],
            "console_script_target": distribution["console_script_target"],
            "module_entry": distribution["module_entry"],
        },
        "commands": info["commands"],
        "conformance_suites": info["conformance_suites"],
        "docs": docs,
        "machine_readable_summaries": machine_readable_summaries,
        "public_release_surface": {
            "entrypoint": "coglang",
            "project_docs": {
                "readme": docs["readme"],
                "vision_proposal": docs["vision_proposal"],
                "evolution_boundary_proposal": docs["evolution_boundary_proposal"],
                "effect_budget_preflight_vocabulary": docs["effect_budget_preflight_vocabulary"],
                "reserved_operator_promotion_criteria": docs[
                    "reserved_operator_promotion_criteria"
                ],
                "send_carry_forward_exit_matrix": docs[
                    "send_carry_forward_exit_matrix"
                ],
                "readable_render_boundary": docs["readable_render_boundary"],
                "hrc_companion_asset_classification": docs[
                    "hrc_companion_asset_classification"
                ],
                "roadmap": docs["roadmap"],
                "maintenance": docs["maintenance"],
            },
            "machine_readable_summaries": machine_readable_summaries,
        },
        "open_source_boundary": open_source_boundary,
        "minimal_ci_baseline": minimal_ci_baseline,
        "public_repo_extract_manifest": public_repo_extract_manifest,
        "formal_open_source_readiness": formal_open_source_readiness,
    }


def _bundle_payload() -> dict[str, Any]:
    manifest = _manifest_payload()
    release_check = _release_check_payload()
    doctor = _doctor_payload()
    return {
        "schema_version": "coglang-release-bundle/v0.1",
        "tool": manifest["tool"],
        "version": manifest["version"],
        "language_release": manifest["language_release"],
        "status": manifest["status"],
        "license": manifest["license"],
        "manifest": manifest,
        "public_release_surface": manifest["public_release_surface"],
        "open_source_boundary": manifest["open_source_boundary"],
        "minimal_ci_baseline": manifest["minimal_ci_baseline"],
        "public_repo_extract_manifest": manifest["public_repo_extract_manifest"],
        "formal_open_source_readiness": manifest["formal_open_source_readiness"],
        "release_check": {
            "ok": release_check["ok"],
            "check_count": len(release_check["checks"]),
            "failed_checks": [item["name"] for item in release_check["checks"] if not item["ok"]],
        },
        "doctor": {
            "ok": doctor["ok"],
            "check_count": len(doctor["checks"]),
            "failed_checks": [item["name"] for item in doctor["checks"] if not item["ok"]],
        },
    }


def _vocab_payload() -> dict[str, Any]:
    vocab = sorted(COGLANG_VOCAB)
    errors = sorted(ERROR_HEADS)
    return {
        "tool": "coglang",
        "version": _cli_version(),
        "vocab_size": len(vocab),
        "error_head_count": len(errors),
        "vocab": vocab,
        "error_heads": errors,
    }


def _examples_payload() -> dict[str, Any]:
    return {
        "tool": "coglang",
        "version": _cli_version(),
        "example_count": len(EXAMPLES),
        "examples": [{"name": name, "expr": expr} for name, expr in EXAMPLES.items()],
    }


def _release_check_payload() -> dict[str, Any]:
    root = _project_root()
    pyproject_path, _ = _resolve_project_artifact("pyproject.toml")
    public_readme_path, _ = _resolve_project_artifact("README.md", "README.md")
    roadmap_path, _ = _resolve_project_artifact("ROADMAP.md", "ROADMAP.md")
    maintenance_path, _ = _resolve_project_artifact("MAINTENANCE.md", "MAINTENANCE.md")
    llms_path, _ = _resolve_project_artifact("llms.txt", "llms.txt")
    llms_full_path, _ = _resolve_project_artifact("llms-full.txt", "llms-full.txt")
    spec_path, _ = _resolve_project_artifact(
        "CogLang_Specification_v1_1_0_Draft.md",
        "CogLang_Specification_v1_1_0_Draft.md",
    )
    quickstart_path, _ = _resolve_project_artifact(
        "CogLang_Quickstart_v1_1_0.md",
        "CogLang_Quickstart_v1_1_0.md",
    )
    conformance_path, _ = _resolve_project_artifact(
        "CogLang_Conformance_Suite_v1_1_0.md",
        "CogLang_Conformance_Suite_v1_1_0.md",
    )
    host_contract_path, _ = _resolve_project_artifact(
        "CogLang_Host_Runtime_Contract_v0_1.md",
        "CogLang_Host_Runtime_Contract_v0_1.md",
    )
    hrc_companion_asset_classification_path, _ = _resolve_project_artifact(
        "CogLang_HRC_Companion_Asset_Classification_v0_1.md",
        "CogLang_HRC_Companion_Asset_Classification_v0_1.md",
    )
    reserved_operator_promotion_criteria_path, _ = _resolve_project_artifact(
        "CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md",
        "CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md",
    )
    send_carry_forward_exit_matrix_path, _ = _resolve_project_artifact(
        "CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md",
        "CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md",
    )
    readable_render_boundary_path, _ = _resolve_project_artifact(
        "CogLang_Readable_Render_Boundary_v0_1.md",
        "CogLang_Readable_Render_Boundary_v0_1.md",
    )
    node_consumer_script_path, _ = _resolve_project_artifact(
        "examples/node_host_consumer/consume_hrc_envelopes.mjs",
    )
    node_consumer_readme_path, _ = _resolve_project_artifact(
        "examples/node_host_consumer/README.md",
    )
    node_minimal_stub_run_path, _ = _resolve_project_artifact(
        "examples/node_minimal_host_runtime_stub/run_demo.mjs",
    )
    node_minimal_stub_readme_path, _ = _resolve_project_artifact(
        "examples/node_minimal_host_runtime_stub/README.md",
    )
    license_path, _ = _resolve_project_artifact("LICENSE")

    distribution = _distribution_metadata()
    open_source_boundary = _open_source_boundary_payload()
    minimal_ci_baseline = _minimal_ci_baseline_payload()
    public_repo_extract_manifest = _public_repo_extract_manifest_payload()
    formal_open_source_readiness = _formal_open_source_readiness_payload()
    preflight_fixture = preflight_fixture_payload()
    generation_eval = generation_eval_payload()
    license_declared = False
    pyproject: dict[str, Any] = {}
    if pyproject_path.exists():
        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        project = pyproject.get("project", {})
        license_declared = bool(project.get("license"))
    package_data = (
        pyproject.get("tool", {})
        .get("setuptools", {})
        .get("package-data", {})
        .get("coglang", [])
    )
    node_consumer_packaged = "_public_assets/examples/node_host_consumer/*" in package_data
    node_minimal_stub_packaged = (
        "_public_assets/examples/node_minimal_host_runtime_stub/*" in package_data
    )
    reserved_operator_promotion_criteria_packaged = (
        "_public_assets/CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md"
        in package_data
    )
    send_carry_forward_exit_matrix_packaged = (
        "_public_assets/CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md"
        in package_data
    )
    readable_render_boundary_packaged = (
        "_public_assets/CogLang_Readable_Render_Boundary_v0_1.md"
        in package_data
    )
    hrc_companion_asset_classification_packaged = (
        "_public_assets/CogLang_HRC_Companion_Asset_Classification_v0_1.md"
        in package_data
    )

    runtime_entry_paths = distribution["runtime_entry_paths"]
    runtime_entry_ok = _paths_exist(root, runtime_entry_paths)
    executor_abstract_methods = sorted(CogLangExecutor.__abstractmethods__)
    executor_interface_ok = (
        executor_abstract_methods == ["execute", "validate"]
        and "query_local_write_result" not in CogLangExecutor.__dict__
        and "query_local_write_result_json" not in CogLangExecutor.__dict__
        and callable(getattr(PythonCogLangExecutor, "query_local_write_result", None))
        and callable(getattr(PythonCogLangExecutor, "query_local_write_result_json", None))
    )

    checks = [
        {
            "name": "pyproject",
            "ok": pyproject_path.exists(),
            "detail": "pyproject.toml",
        },
        {
            "name": "distribution_metadata",
            "ok": bool(distribution["name"]),
            "detail": distribution["name"] or "missing",
        },
        {
            "name": "console_script",
            "ok": bool(distribution["console_script_target"]),
            "detail": (
                f"{distribution['console_script']} -> declared"
                if distribution["console_script_target"]
                else "missing"
            ),
        },
        {
            "name": "license_declared",
            "ok": license_declared,
            "detail": "project.license",
        },
        {
            "name": "license_file",
            "ok": license_path.exists(),
            "detail": "LICENSE",
        },
        {
            "name": "runtime_entry",
            "ok": runtime_entry_ok,
            "detail": (
                "module entry + __main__ entry"
                if runtime_entry_ok
                else "missing"
            ),
        },
        {
            "name": "spec_bundle",
            "ok": (
                spec_path.exists()
                and quickstart_path.exists()
                and conformance_path.exists()
                and host_contract_path.exists()
            ),
            "detail": "spec + quickstart + conformance + host contract",
        },
        {
            "name": "public_release_docs",
            "ok": (
                public_readme_path.exists()
                and roadmap_path.exists()
                and maintenance_path.exists()
                and llms_path.exists()
                and llms_full_path.exists()
            ),
            "detail": "README + roadmap + maintenance + llms summaries",
        },
        {
            "name": "reserved_operator_promotion_criteria",
            "ok": (
                reserved_operator_promotion_criteria_path.exists()
                and reserved_operator_promotion_criteria_packaged
            ),
            "detail": "reserved operator promotion criteria + package data",
        },
        {
            "name": "send_carry_forward_exit_matrix",
            "ok": (
                send_carry_forward_exit_matrix_path.exists()
                and send_carry_forward_exit_matrix_packaged
            ),
            "detail": "Send carry-forward exit matrix + package data",
        },
        {
            "name": "readable_render_boundary",
            "ok": (
                readable_render_boundary_path.exists()
                and readable_render_boundary_packaged
            ),
            "detail": "readable render boundary + package data",
        },
        {
            "name": "hrc_companion_asset_classification",
            "ok": (
                hrc_companion_asset_classification_path.exists()
                and hrc_companion_asset_classification_packaged
            ),
            "detail": "HRC companion asset classification + package data",
        },
        {
            "name": "open_source_boundary",
            "ok": (
                open_source_boundary["schema_version"] == "coglang-open-source-boundary/v0.1"
                and open_source_boundary["public_console_script"] == "coglang"
                and open_source_boundary["public_distribution_name"] == "coglang"
                and open_source_boundary["release_roots_exist"] is True
            ),
            "detail": open_source_boundary["path"],
        },
        {
            "name": "minimal_ci_baseline",
            "ok": (
                minimal_ci_baseline["schema_version"] == "coglang-minimal-ci-baseline/v0.1"
                and minimal_ci_baseline["required_command_names_present"] is True
                and minimal_ci_baseline["required_packaging_check_names_present"] is True
                and minimal_ci_baseline["public_entrypoint_only"] is True
                and minimal_ci_baseline["workflow_template_present"] is True
                and minimal_ci_baseline["workflow_required_step_names_present"] is True
                and minimal_ci_baseline["workflow_required_smoke_snippets_present"] is True
            ),
            "detail": minimal_ci_baseline["path"],
        },
        {
            "name": "public_repo_extract_manifest",
            "ok": (
                public_repo_extract_manifest["schema_version"]
                == "coglang-public-repo-extract-manifest/v0.1"
                and public_repo_extract_manifest["repository_strategy"]
                == "standalone_repository"
                and public_repo_extract_manifest["public_distribution_name"] == "coglang"
                and public_repo_extract_manifest["source_paths_exist"] is True
                and public_repo_extract_manifest["destination_paths_unique"] is True
                and public_repo_extract_manifest["required_destinations_present"] is True
            ),
            "detail": public_repo_extract_manifest["path"],
        },
        {
            "name": "formal_open_source_readiness",
            "ok": formal_open_source_readiness["ready_for_candidate_decision"] is True,
            "detail": formal_open_source_readiness["status"],
        },
        {
            "name": "preflight_fixture",
            "ok": (
                preflight_fixture["ok"] is True
                and preflight_fixture["case_count"] >= 1
            ),
            "detail": f"{preflight_fixture['case_count']} cases",
        },
        {
            "name": "generation_eval",
            "ok": (
                generation_eval["ok"] is True
                and generation_eval["case_count"] >= 1
                and generation_eval["summary"]["hallucinated_operator_count"] == 0
            ),
            "detail": f"{generation_eval['case_count']} cases",
        },
        {
            "name": "node_host_consumer",
            "ok": (
                node_consumer_script_path.exists()
                and node_consumer_readme_path.exists()
                and node_consumer_packaged
            ),
            "detail": "examples/node_host_consumer + package data",
        },
        {
            "name": "node_minimal_host_runtime_stub",
            "ok": (
                node_minimal_stub_run_path.exists()
                and node_minimal_stub_readme_path.exists()
                and node_minimal_stub_packaged
            ),
            "detail": "examples/node_minimal_host_runtime_stub + package data",
        },
        {
            "name": "executor_interface",
            "ok": executor_interface_ok,
            "detail": (
                "abstract_methods="
                + ",".join(executor_abstract_methods)
            ),
        },
    ]
    return {
        "tool": "coglang",
        "version": _cli_version(),
        "language_release": COGLANG_LANGUAGE_RELEASE,
        "ok": all(item["ok"] for item in checks),
        "checks": checks,
    }


def _run_demo() -> dict[str, Any]:
    executor = PythonCogLangExecutor()
    steps = [
        ('Create["Entity", {"id": "einstein", "category": "Person", "label": "Einstein"}]', '"einstein"'),
        ('Create["Entity", {"id": "ulm", "category": "City", "label": "Ulm"}]', '"ulm"'),
        (
            'Create["Edge", {"from": "einstein", "to": "ulm", "relation_type": "born_in"}]',
            'List["einstein", "born_in", "ulm"]',
        ),
        ('Query[n_, Equal[Get[n_, "category"], "Person"]]', 'List["einstein"]'),
        ('Traverse["einstein", "born_in"]', 'List["ulm"]'),
    ]
    results: list[dict[str, Any]] = []
    ok = True
    for source, expected in steps:
        expr = parse(source)
        result = executor.execute(expr)
        rendered = canonicalize(result)
        step_ok = rendered == expected
        ok = ok and step_ok
        results.append(
            {
                "expr": source,
                "result": rendered,
                "expected": expected,
                "ok": step_ok,
            }
        )
    return {
        "tool": "coglang",
        "version": _cli_version(),
        "language_release": COGLANG_LANGUAGE_RELEASE,
        "ok": ok,
        "steps": results,
    }


def _host_demo_failure_payload() -> dict[str, Any]:
    return {
        "schema_version": HOST_DEMO_SCHEMA_VERSION,
        "tool": "coglang",
        "version": _cli_version(),
        "ok": False,
        "write_header": None,
        "typed_write_header": None,
        "status": "not_found",
        "payload_kind": None,
        "node_id": None,
        "correlation_id": None,
        "submission_id": None,
        "typed_submission_message": None,
        "typed_response": None,
        "typed_submission_record": None,
        "typed_query_result": None,
        "typed_trace": None,
        "typed_snapshot": None,
        "typed_summary": None,
        "snapshot_summary": None,
        "steps": [
            {
                "name": "create",
                "ok": False,
                "detail": "failed to execute and submit through LocalCogLangHost",
            }
        ],
    }


def _host_demo_error_report_step() -> dict[str, Any]:
    error_host = LocalCogLangHost()
    error_candidate = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_edge",
                {"source_id": "Einstein", "target_id": "dog_1", "relation": "knows"},
            )
        ],
    )
    error_response, error_trace = error_host.submit_candidate_and_trace(
        candidate=error_candidate,
        correlation_id="host-demo-error-report",
    )
    if error_response is None or error_trace is None:
        return {
            "name": "error_report",
            "ok": False,
            "detail": "failed to submit invalid write candidate through LocalCogLangHost",
        }

    correlation_id = error_response.correlation_id
    write_header = error_host.query_write_header_dict(correlation_id)
    typed_submission_message = error_host.query_write_submission_message_dict(correlation_id)
    typed_response = error_host.query_write_response_message_dict(correlation_id)
    typed_submission_record = error_host.query_write_submission_record_dict(correlation_id)
    typed_query_result = error_host.query_write_dict(correlation_id)
    typed_trace = error_host.query_write_trace_dict(correlation_id)
    if (
        typed_submission_message is None
        or typed_response is None
        or typed_submission_record is None
        or typed_trace is None
    ):
        return {
            "name": "error_report",
            "ok": False,
            "detail": "failed to query ErrorReport public views through LocalCogLangHost",
        }

    payload = typed_response["payload"]
    ok = (
        write_header["payload_kind"] == "ErrorReport"
        and write_header["status"] == "failed"
        and typed_response["header"]["payload_kind"] == "ErrorReport"
        and typed_query_result["status"] == "failed"
        and typed_submission_record["status"] == "failed"
        and _primary_views_match_write_header(
            write_header=write_header,
            typed_submission_message=typed_submission_message,
            typed_response=typed_response,
            typed_submission_record=typed_submission_record,
            typed_query_result=typed_query_result,
        )
        and _trace_view_is_consistent(
            write_header=write_header,
            typed_submission_message=typed_submission_message,
            typed_response=typed_response,
            typed_submission_record=typed_submission_record,
            typed_query_result=typed_query_result,
            typed_trace=typed_trace,
        )
        and payload.get("error_kind") == "ValidationError"
        and isinstance(payload.get("errors"), list)
        and len(payload["errors"]) >= 1
    )
    return {
        "name": "error_report",
        "ok": ok,
        "correlation_id": write_header["correlation_id"],
        "submission_id": write_header["submission_id"],
        "status": write_header["status"],
        "payload_kind": write_header["payload_kind"],
        "error_kind": payload["error_kind"],
        "retryable": payload["retryable"],
        "error_count": len(payload["errors"]),
    }


def _summary_from_snapshot_dict(snapshot: dict[str, Any]) -> dict[str, Any]:
    return LocalHostSummary.from_snapshot(
        LocalHostSnapshot.from_dict(snapshot)
    ).to_dict()


def _trace_view_is_consistent(
    *,
    write_header: dict[str, Any],
    typed_submission_message: dict[str, Any],
    typed_response: dict[str, Any],
    typed_submission_record: dict[str, Any],
    typed_query_result: dict[str, Any],
    typed_trace: dict[str, Any] | None,
) -> bool:
    if typed_trace is None:
        return False
    return (
        typed_trace["correlation_id"] == write_header["correlation_id"]
        and typed_trace["submission_id"] == write_header["submission_id"]
        and typed_trace["request"] == typed_submission_message
        and typed_trace["response"] == typed_response
        and typed_trace["record"] == typed_submission_record
        and typed_trace["query_result"] == typed_query_result
    )


def _primary_views_match_write_header(
    *,
    write_header: dict[str, Any],
    typed_submission_message: dict[str, Any],
    typed_response: dict[str, Any],
    typed_submission_record: dict[str, Any],
    typed_query_result: dict[str, Any],
) -> bool:
    message_header = typed_submission_message.get("header", {})
    response_header = typed_response.get("header", {})
    return (
        message_header.get("correlation_id") == write_header["correlation_id"]
        and message_header.get("submission_id") == write_header["submission_id"]
        and response_header.get("correlation_id") == write_header["correlation_id"]
        and response_header.get("submission_id") == write_header["submission_id"]
        and response_header.get("payload_kind") == write_header["payload_kind"]
        and typed_submission_record["correlation_id"] == write_header["correlation_id"]
        and typed_submission_record["submission_id"] == write_header["submission_id"]
        and typed_submission_record["status"] == write_header["status"]
        and typed_query_result["correlation_id"] == write_header["correlation_id"]
        and typed_query_result["submission_id"] == write_header["submission_id"]
        and typed_query_result["status"] == write_header["status"]
    )


def _node_view_is_consistent(
    *,
    create_result: str,
    typed_submission_message: dict[str, Any],
    typed_response: dict[str, Any],
    typed_snapshot: dict[str, Any],
) -> bool:
    submission_payload = typed_submission_message.get("payload", {})
    candidate = submission_payload.get("candidate", {})
    candidate_operations = candidate.get("operations", [])
    commit_plan = submission_payload.get("commit_plan", {})
    create_nodes = commit_plan.get("phase_1a_create_nodes", [])
    response_payload = typed_response.get("payload", {})
    touched_node_ids = response_payload.get("touched_node_ids", [])
    snapshot_graph = typed_snapshot.get("graph", {})
    graph_nodes = snapshot_graph.get("nodes", [])
    return (
        any(
            operation.get("op") == "create_node"
            and operation.get("payload", {}).get("id") == create_result
            for operation in candidate_operations
        )
        and any(
            operation.get("op") == "create_node"
            and operation.get("payload", {}).get("id") == create_result
            for operation in create_nodes
        )
        and
        create_result in touched_node_ids
        and any(node.get("id") == create_result for node in graph_nodes)
    )


def _snapshot_primary_views_are_consistent(
    *,
    typed_snapshot: dict[str, Any],
    typed_submission_message: dict[str, Any],
    typed_response: dict[str, Any],
    typed_submission_record: dict[str, Any],
    typed_query_result: dict[str, Any],
    typed_trace: dict[str, Any] | None,
) -> bool:
    submission_messages = typed_snapshot.get("write_submission_messages", [])
    response_messages = typed_snapshot.get("write_response_messages", [])
    submission_records = typed_snapshot.get("write_submission_records", [])
    query_results = typed_snapshot.get("write_query_results", [])
    traces = typed_snapshot.get("write_traces", [])
    return (
        len(submission_messages) >= 1
        and len(response_messages) >= 1
        and len(submission_records) >= 1
        and len(query_results) >= 1
        and len(traces) >= 1
        and submission_messages[0] == typed_submission_message
        and response_messages[0] == typed_response
        and submission_records[0] == typed_submission_record
        and query_results[0] == typed_query_result
        and traces[0] == typed_trace
    )


def _host_demo_success_payload(
    *,
    create_result: str,
    response: dict[str, Any],
    write_header: dict[str, Any],
    typed_write_header: dict[str, Any],
    typed_submission_message: dict[str, Any],
    typed_response: dict[str, Any],
    typed_submission_record: dict[str, Any],
    typed_query_result: dict[str, Any],
    typed_trace: dict[str, Any] | None,
    typed_snapshot: dict[str, Any],
    typed_summary: dict[str, Any],
    error_report_step: dict[str, Any],
) -> dict[str, Any]:
    payload_kind = write_header["payload_kind"]
    response_header = None if typed_response is None else typed_response["header"]
    snapshot_summary = _summary_from_snapshot_dict(typed_snapshot)
    primary_views_match_header = _primary_views_match_write_header(
        write_header=write_header,
        typed_submission_message=typed_submission_message,
        typed_response=typed_response,
        typed_submission_record=typed_submission_record,
        typed_query_result=typed_query_result,
    )
    node_consistent = _node_view_is_consistent(
        create_result=create_result,
        typed_submission_message=typed_submission_message,
        typed_response=typed_response,
        typed_snapshot=typed_snapshot,
    )
    trace_consistent = _trace_view_is_consistent(
        write_header=write_header,
        typed_submission_message=typed_submission_message,
        typed_response=typed_response,
        typed_submission_record=typed_submission_record,
        typed_query_result=typed_query_result,
        typed_trace=typed_trace,
    )
    snapshot_consistent = _snapshot_primary_views_are_consistent(
        typed_snapshot=typed_snapshot,
        typed_submission_message=typed_submission_message,
        typed_response=typed_response,
        typed_submission_record=typed_submission_record,
        typed_query_result=typed_query_result,
        typed_trace=typed_trace,
    )
    ok = (
        payload_kind == "WriteResult"
        and typed_query_result["status"] == "committed"
        and typed_query_result["submission_id"] == write_header["submission_id"]
        and typed_write_header == write_header
        and primary_views_match_header
        and node_consistent
        and trace_consistent
        and snapshot_consistent
        and typed_summary == snapshot_summary
        and error_report_step["ok"] is True
    )
    return {
        "schema_version": HOST_DEMO_SCHEMA_VERSION,
        "tool": "coglang",
        "version": _cli_version(),
        "ok": ok,
        "write_header": write_header,
        "typed_write_header": typed_write_header,
        "status": write_header["status"],
        "payload_kind": payload_kind,
        "node_id": create_result,
        "correlation_id": write_header["correlation_id"],
        "submission_id": write_header["submission_id"],
        "typed_submission_message": typed_submission_message,
        "typed_response": typed_response,
        "typed_submission_record": typed_submission_record,
        "typed_query_result": typed_query_result,
        "typed_trace": typed_trace,
        "typed_snapshot": typed_snapshot,
        "typed_summary": typed_summary,
        "snapshot_summary": snapshot_summary,
        "steps": [
            {
                "name": "execute_and_submit_to",
                "ok": response is not None,
                "node_id": create_result,
                "correlation_id": write_header["correlation_id"],
                "submission_id": write_header["submission_id"],
            },
            {
                "name": "typed_response",
                "ok": response_header is not None,
                "payload_kind": None if response_header is None else response_header["payload_kind"],
                "correlation_id": None if response_header is None else response_header["correlation_id"],
                "submission_id": None if response_header is None else response_header["submission_id"],
            },
            {
                "name": "query_result",
                "ok": typed_query_result["status"] == "committed",
                "status": typed_query_result["status"],
                "submission_id": typed_query_result["submission_id"],
            },
            {
                "name": "trace",
                "ok": typed_trace is not None,
                "submission_id": None if typed_trace is None else typed_trace["submission_id"],
            },
            error_report_step,
        ],
    }


def _run_host_demo() -> dict[str, Any]:
    source_host = LocalCogLangHost()
    target_host = LocalCogLangHost()

    create_result, response, trace = source_host.execute_and_submit_to_trace(
        target_host,
        'Create["Entity", {"category": "Person", "label": "Ada"}]'
    )
    if not isinstance(create_result, str) or response is None or trace is None:
        return _host_demo_failure_payload()

    correlation_id = trace.correlation_id
    write_header = target_host.query_write_header_dict(correlation_id)
    typed_write_header = target_host.query_write_header(correlation_id).to_dict()
    typed_submission_message = target_host.query_write_submission_message_dict(
        correlation_id
    )
    typed_response = target_host.query_write_response_message_dict(correlation_id)
    typed_submission_record = target_host.query_write_submission_record_dict(
        correlation_id
    )
    typed_query_result = target_host.query_write_dict(correlation_id)
    typed_trace = target_host.query_write_trace_dict(correlation_id)
    typed_snapshot = target_host.export_snapshot_dict()
    typed_summary = target_host.export_summary_dict()
    if (
        typed_submission_message is None
        or typed_response is None
        or typed_submission_record is None
        or typed_trace is None
    ):
        return _host_demo_failure_payload()
    error_report_step = _host_demo_error_report_step()
    return _host_demo_success_payload(
        create_result=create_result,
        response=response.to_dict(),
        write_header=write_header,
        typed_write_header=typed_write_header,
        typed_submission_message=typed_submission_message,
        typed_response=typed_response,
        typed_submission_record=typed_submission_record,
        typed_query_result=typed_query_result,
        typed_trace=typed_trace,
        typed_snapshot=typed_snapshot,
        typed_summary=typed_summary,
        error_report_step=error_report_step,
    )


def _run_reference_host_demo() -> dict[str, Any]:
    host = ReferenceTransportHost()
    candidate = WriteBundleCandidate(
        owner="reference_transport_demo",
        operations=[
            WriteOperation(
                "create_node",
                {
                    "id": "ada",
                    "node_type": "Person",
                    "attrs": {"id": "ada", "label": "Ada Lovelace"},
                },
            ),
            WriteOperation(
                "create_node",
                {
                    "id": "analytical_engine",
                    "node_type": "Artifact",
                    "attrs": {"id": "analytical_engine", "label": "Analytical Engine"},
                },
            ),
            WriteOperation(
                "create_edge",
                {
                    "source_id": "ada",
                    "target_id": "analytical_engine",
                    "relation": "designed",
                },
            ),
        ],
    )
    submission_message = candidate.submission_message(
        correlation_id="reference-host-demo-success",
        metadata={"source": "reference-host-demo", "host_kind": "reference_transport_host"},
    )
    typed_response = json.loads(host.submit_json(submission_message.to_json()))
    typed_submission_record = host.record(submission_message.correlation_id).to_dict()
    typed_query_result = host.query_result(submission_message.correlation_id).to_dict()
    typed_write_header = host.query_header(submission_message.correlation_id).to_dict()
    graph = host.export_state()["graph"]

    error_candidate = WriteBundleCandidate(
        owner="reference_transport_demo",
        operations=[
            WriteOperation(
                "create_edge",
                {
                    "source_id": "missing_source",
                    "target_id": "missing_target",
                    "relation": "knows",
                },
            )
        ],
    )
    error_submission_message = error_candidate.submission_message(
        correlation_id="reference-host-demo-error",
        metadata={"source": "reference-host-demo", "host_kind": "reference_transport_host"},
    )
    error_response = host.submit_message(error_submission_message).to_dict()
    error_write_header = host.query_header(error_submission_message.correlation_id).to_dict()

    status = typed_write_header["status"]
    payload_kind = typed_write_header["payload_kind"]
    steps = [
        {
            "name": "submit_json",
            "ok": status == "committed" and payload_kind == "WriteResult",
            "status": status,
            "payload_kind": payload_kind,
            "correlation_id": submission_message.correlation_id,
            "submission_id": submission_message.submission_id,
        },
        {
            "name": "query_result",
            "ok": typed_query_result["status"] == "committed",
            "status": typed_query_result["status"],
            "submission_id": typed_query_result["submission_id"],
        },
        {
            "name": "write_header",
            "ok": typed_write_header["status"] == "committed",
            "status": typed_write_header["status"],
            "payload_kind": typed_write_header["payload_kind"],
        },
        {
            "name": "error_report",
            "ok": (
                error_write_header["status"] == "failed"
                and error_write_header["payload_kind"] == "ErrorReport"
            ),
            "status": error_write_header["status"],
            "payload_kind": error_write_header["payload_kind"],
            "error_kind": error_response["payload"]["error_kind"],
            "retryable": error_response["payload"]["retryable"],
            "error_count": len(error_response["payload"]["errors"]),
            "correlation_id": error_write_header["correlation_id"],
            "submission_id": error_write_header["submission_id"],
        },
    ]
    payload = {
        "schema_version": REFERENCE_HOST_DEMO_SCHEMA_VERSION,
        "tool": "coglang",
        "version": _cli_version(),
        "ok": all(step["ok"] for step in steps),
        "host_kind": "reference_transport_host",
        "status": status,
        "payload_kind": payload_kind,
        "correlation_id": submission_message.correlation_id,
        "submission_id": submission_message.submission_id,
        "typed_submission_message": submission_message.to_dict(),
        "typed_response": typed_response,
        "typed_submission_record": typed_submission_record,
        "typed_query_result": typed_query_result,
        "typed_write_header": typed_write_header,
        "graph": graph,
        "error_response": error_response,
        "error_write_header": error_write_header,
        "steps": steps,
    }
    return payload


def _doctor_payload() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add_check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    add_check("python", True, sys.version.split()[0])
    add_check("tempdir", True, gettempdir())

    expr = parse('Equal[1, 1]')
    add_check("parse", expr.head != "ParseError", canonicalize(expr))
    add_check("validate", expr.head != "ParseError" and valid_coglang(expr), "Equal[1, 1]")

    executor = PythonCogLangExecutor()
    result = executor.execute(expr)
    add_check(
        "execute",
        isinstance(result, CogLangExpr) and result.head == "True",
        canonicalize(result),
    )

    try:
        import pytest  # noqa: F401

        add_check("pytest", True, "available")
    except ImportError:
        add_check("pytest", False, "not installed")

    ok = all(item["ok"] for item in checks)
    return {
        "tool": "coglang",
        "version": _cli_version(),
        "language_release": COGLANG_LANGUAGE_RELEASE,
        "ok": ok,
        "checks": checks,
    }


def _run_smoke(pytest_args: list[str] | None = None) -> int:
    doctor = _doctor_payload()
    if not doctor["ok"]:
        print(json.dumps({"doctor": doctor, "conformance": None}, ensure_ascii=False, indent=2))
        return 1
    conformance_code = _run_conformance_suite("smoke", pytest_args)
    payload = {
        "doctor": {
            "ok": doctor["ok"],
            "check_count": len(doctor["checks"]),
        },
        "conformance": {
            "suite": "smoke",
            "exit_code": conformance_code,
            "ok": conformance_code == 0,
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if conformance_code == 0 else 1


def _run_repl(stdin: Any = None, stdout: Any = None) -> int:
    inp = sys.stdin if stdin is None else stdin
    out = sys.stdout if stdout is None else stdout
    executor = PythonCogLangExecutor()
    out.write(
        dedent(
            """\
            CogLang REPL
            Type one expression per line.
            Commands: :help, :quit, :exit
            """
        )
    )
    while True:
        out.write("coglang> ")
        out.flush()
        line = inp.readline()
        if line == "":
            out.write("\n")
            return 0
        source = line.strip()
        if not source:
            continue
        if source in {":quit", ":exit"}:
            return 0
        if source == ":help":
            out.write(
                "Enter one CogLang expression. Results print in canonical form.\n"
            )
            continue
        expr = parse(source)
        if expr.head == "ParseError":
            out.write(canonicalize(expr) + "\n")
            continue
        result = executor.execute(expr)
        out.write(canonicalize(result) + "\n")


def _print_text_mapping_block(label: str, payload: dict[str, Any] | None) -> None:
    print(f"{label}:")
    if payload is None:
        print("  null")
        return
    for key, value in payload.items():
        print(f"  {key}: {value}")


def _print_text_step_blocks(steps: list[dict[str, Any]]) -> None:
    for idx, step in enumerate(steps, start=1):
        status = "ok" if step["ok"] else "fail"
        print(f"step{idx}: {status}")
        print(f"  name: {step['name']}")
        for key, value in step.items():
            if key in {"name", "ok"}:
                continue
            print(f"  {key}: {value}")


def _preflight_budget_from_args(args: argparse.Namespace) -> GraphBudget | None:
    budget_fields = {
        "max_traversal_depth": args.max_traversal_depth,
        "max_visited_nodes": args.max_visited_nodes,
        "max_result_count": args.max_result_count,
        "max_unification_branches": args.max_unification_branches,
        "max_execution_ms": args.max_execution_ms,
    }
    if all(value is None for value in budget_fields.values()):
        return None
    return GraphBudget(**budget_fields)


def _print_preflight_text(payload: dict[str, Any]) -> None:
    print(f"schema_version: {payload['schema_version']}")
    print(f"decision: {payload['decision']}")
    print(f"required_review: {str(payload['required_review']).lower()}")
    print("reasons: " + ", ".join(payload["reasons"]))
    print("possible_errors: " + ", ".join(payload["possible_errors"]))
    effect_summary = payload.get("effect_summary") or {}
    print("effects: " + ", ".join(effect_summary.get("effects", [])))
    print(
        "required_capabilities: "
        + ", ".join(effect_summary.get("required_capabilities", []))
    )
    budget_estimate = payload.get("budget_estimate") or {}
    print(
        "estimate_confidence: "
        + str(budget_estimate.get("estimate_confidence", "unknown"))
    )
    if payload.get("correlation_id") is not None:
        print(f"correlation_id: {payload['correlation_id']}")


def _print_preflight_fixture_text(payload: dict[str, Any]) -> None:
    print(f"schema_version: {payload['schema_version']}")
    print(f"ok: {str(payload['ok']).lower()}")
    print(f"fixture_schema_version: {payload['fixture_schema_version']}")
    print(f"fixture_path: {payload['fixture_path']}")
    print(f"case_count: {payload['case_count']}")
    for case in payload["cases"]:
        status = "ok" if case["ok"] else "fail"
        print(f"{case['case_id']}: {status} decision={case['actual'].get('decision')}")


def _print_generation_eval_text(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    failure_counts = summary.get("failure_category_counts", {})
    print(f"schema_version: {payload['schema_version']}")
    print(f"tool: {payload['tool']}")
    print(f"ok: {str(payload['ok']).lower()}")
    print(f"answer_source: {payload['answer_source']}")
    print(f"case_count: {payload['case_count']}")
    print(f"failure_case_count: {payload.get('failure_case_count', 0)}")
    maturity = payload.get("maturity", {})
    print(
        "maturity.highest_contiguous_level: "
        + str(maturity.get("highest_contiguous_level", "unknown"))
    )
    print(
        "maturity.blocked_level: "
        + str(maturity.get("blocked_level") or "none")
    )
    print(f"missing_output_count: {summary['missing_output_count']}")
    print(f"parse_ok: {summary['parse_ok_count']}/{payload['case_count']}")
    print(f"canonicalize_ok: {summary['canonicalize_ok_count']}/{payload['case_count']}")
    print(f"validate_ok: {summary['validate_ok_count']}/{payload['case_count']}")
    print(
        "expected_top_level_head_ok: "
        f"{summary['expected_top_level_head_ok_count']}/{payload['case_count']}"
    )
    print(f"hallucinated_operator_count: {summary['hallucinated_operator_count']}")
    if failure_counts:
        failure_items = ", ".join(
            f"{category}={count}" for category, count in failure_counts.items()
        )
    else:
        failure_items = "none"
    print(f"failure_category_counts: {failure_items}")
    for failure in payload.get("failure_cases", []):
        categories = ", ".join(failure.get("failure_categories", []))
        print(
            f"failure {failure['case_id']} "
            f"level={failure['level']} categories={categories}"
        )
    for level, level_summary in payload.get("level_summary", {}).items():
        print(
            f"{level}: validate_ok "
            f"{level_summary['validate_ok_count']}/{level_summary['case_count']}, "
            f"head_ok "
            f"{level_summary['expected_top_level_head_ok_count']}/"
            f"{level_summary['case_count']}, "
            f"hallucinated {level_summary['hallucinated_operator_count']}"
        )


def _generation_eval_output_payload(
    payload: dict[str, Any],
    *,
    summary_only: bool = False,
    failures_only: bool = False,
) -> dict[str, Any]:
    if summary_only:
        output = dict(payload)
        output.pop("cases", None)
        return output
    if failures_only:
        failed_case_ids = {
            str(failure["case_id"])
            for failure in payload.get("failure_cases", [])
        }
        output = dict(payload)
        output["cases"] = [
            case
            for case in payload.get("cases", [])
            if str(case.get("case_id")) in failed_case_ids
        ]
        return output
    return payload


def _conformance_targets(suite: str) -> list[str]:
    base = _conformance_base()
    suites = {
        "smoke": [
            str(base / "test_cli.py"),
            str(base / "test_parser.py"),
            str(base / "test_validator.py"),
        ],
        "core": [
            str(base / "test_cli.py"),
            str(base / "test_parser.py"),
            str(base / "test_validator.py"),
            str(base / "test_unify.py"),
            str(base / "test_graph_ops.py"),
            str(base / "test_boundary.py"),
            str(base / "test_composition.py"),
            str(base / "test_completeness.py"),
        ],
        "full": [str(base)],
    }
    return suites[suite]


def _run_conformance_suite(suite: str, pytest_args: list[str] | None = None) -> int:
    try:
        import os
        import shutil
        import tempfile

        import pytest
    except ImportError:
        print("pytest is required for the conformance runner.")
        return 2

    root = _project_root()
    targets = _conformance_targets(suite)
    tmp = root / ".tmp_pytest"
    previous_temp = os.environ.get("TEMP")
    previous_tmp = os.environ.get("TMP")
    previous_tempdir = tempfile.tempdir
    tmp.mkdir(exist_ok=True)
    os.environ["TEMP"] = str(tmp)
    os.environ["TMP"] = str(tmp)
    tempfile.tempdir = str(tmp)
    args = targets + (pytest_args or [])
    try:
        return pytest.main(args)
    finally:
        tempfile.tempdir = previous_tempdir
        if previous_temp is None:
            os.environ.pop("TEMP", None)
        else:
            os.environ["TEMP"] = previous_temp
        if previous_tmp is None:
            os.environ.pop("TMP", None)
        else:
            os.environ["TMP"] = previous_tmp
        # Clean up redirected tempdir so transitively-invoked libraries
        # (filelock / huggingface_hub / etc.) don't leave sentinel files
        # accumulating across runs. ignore_errors covers Windows file-lock races.
        shutil.rmtree(tmp, ignore_errors=True)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="coglang",
        description="Minimal standalone CLI for CogLang parse/validate/execute flows.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_cli_version()} (language_release {COGLANG_LANGUAGE_RELEASE})",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_expr_source(subparser: argparse.ArgumentParser) -> None:
        source = subparser.add_mutually_exclusive_group()
        source.add_argument("expr", nargs="?", help="CogLang expression text.")
        source.add_argument("--file", help="Read expression text from a UTF-8 file.")

    parse_cmd = subparsers.add_parser("parse", help="Parse one CogLang expression.")
    add_expr_source(parse_cmd)
    parse_cmd.add_argument(
        "--format",
        choices=("canonical", "repr", "json"),
        default="canonical",
        help="Output format for the parsed AST.",
    )

    canonical_cmd = subparsers.add_parser(
        "canonicalize", help="Parse one expression and print canonical text."
    )
    add_expr_source(canonical_cmd)

    validate_cmd = subparsers.add_parser(
        "validate", help="Validate one expression against the current CogLang vocabulary."
    )
    add_expr_source(validate_cmd)
    validate_cmd.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON object instead of plain true/false.",
    )

    preflight_cmd = subparsers.add_parser(
        "preflight",
        help="Run a static v1.2-candidate preflight check without executing.",
    )
    add_expr_source(preflight_cmd)
    preflight_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the preflight decision.",
    )
    preflight_cmd.add_argument(
        "--correlation-id",
        help="Optional host correlation identifier to include in the decision.",
    )
    preflight_cmd.add_argument(
        "--allow-writes-without-review",
        action="store_true",
        help="Do not force graph writes into requires_review during static preflight.",
    )
    preflight_cmd.add_argument(
        "--enabled-capability",
        action="append",
        default=None,
        help=(
            "Declare one host-enabled capability. Repeat to provide a minimal "
            "capability manifest for preflight rejection checks."
        ),
    )
    preflight_cmd.add_argument(
        "--max-traversal-depth",
        type=int,
        help="Optional traversal-depth budget override.",
    )
    preflight_cmd.add_argument(
        "--max-visited-nodes",
        type=int,
        help="Optional visited-node budget override.",
    )
    preflight_cmd.add_argument(
        "--max-result-count",
        type=int,
        help="Optional result-count budget override.",
    )
    preflight_cmd.add_argument(
        "--max-unification-branches",
        type=int,
        help="Optional unification-branch budget override.",
    )
    preflight_cmd.add_argument(
        "--max-execution-ms",
        type=int,
        help="Optional execution-time budget override.",
    )

    preflight_fixture_cmd = subparsers.add_parser(
        "preflight-fixture",
        help="Run the packaged v1.2-candidate preflight fixture without execution.",
    )
    preflight_fixture_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the fixture run.",
    )
    preflight_fixture_cmd.add_argument(
        "--fixture",
        help="Optional path to a compatible preflight fixture JSON file.",
    )

    execute_cmd = subparsers.add_parser(
        "execute", help="Execute one expression against an empty in-memory graph."
    )
    add_expr_source(execute_cmd)
    execute_cmd.add_argument(
        "--format",
        choices=("canonical", "repr", "json"),
        default="canonical",
        help="Output format for the execution result.",
    )

    conformance_cmd = subparsers.add_parser(
        "conformance", help="Run the packaged CogLang conformance test suites."
    )
    conformance_cmd.add_argument(
        "suite",
        nargs="?",
        choices=("smoke", "core", "full"),
        default="smoke",
        help="Named conformance suite to execute.",
    )
    conformance_cmd.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Additional pytest arguments. Put them after '--'.",
    )

    subparsers.add_parser(
        "repl", help="Run a minimal in-memory CogLang REPL."
    )

    info_cmd = subparsers.add_parser(
        "info", help="Print minimal package and command metadata."
    )
    info_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for tool metadata.",
    )

    manifest_cmd = subparsers.add_parser(
        "manifest", help="Print stable machine-readable release-facing metadata."
    )
    manifest_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the manifest payload.",
    )

    bundle_cmd = subparsers.add_parser(
        "bundle", help="Print a minimal release-facing bundle summary for scripts and CI."
    )
    bundle_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the release bundle payload.",
    )

    doctor_cmd = subparsers.add_parser(
        "doctor", help="Run a minimal local environment self-check."
    )
    doctor_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the self-check report.",
    )

    vocab_cmd = subparsers.add_parser(
        "vocab", help="Print the packaged CogLang vocabulary."
    )
    vocab_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the vocabulary dump.",
    )

    examples_cmd = subparsers.add_parser(
        "examples", help="Print packaged starter examples."
    )
    examples_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the examples listing.",
    )
    examples_cmd.add_argument(
        "--name",
        choices=tuple(EXAMPLES.keys()),
        help="Print one named example instead of the full listing.",
    )

    generation_eval_cmd = subparsers.add_parser(
        "generation-eval",
        help="Score offline CogLang generation outputs against a prompt fixture.",
    )
    generation_eval_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the generation eval report.",
    )
    generation_eval_cmd.add_argument(
        "--fixture",
        help="Optional fixture JSON path. Defaults to the packaged minimal fixture.",
    )
    generation_eval_cmd.add_argument(
        "--answers-file",
        help="Optional answers JSON path. Defaults to fixture reference expressions.",
    )
    generation_eval_output = generation_eval_cmd.add_mutually_exclusive_group()
    generation_eval_output.add_argument(
        "--summary-only",
        action="store_true",
        help="Omit per-case results from JSON output.",
    )
    generation_eval_output.add_argument(
        "--failures-only",
        action="store_true",
        help="Limit JSON per-case results to failed cases.",
    )

    smoke_cmd = subparsers.add_parser(
        "smoke", help="Run the minimal release-facing health check path."
    )
    smoke_cmd.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Additional pytest arguments forwarded to the smoke conformance suite.",
    )

    demo_cmd = subparsers.add_parser(
        "demo", help="Run a minimal standalone in-memory CogLang workflow."
    )
    demo_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the demo run.",
    )

    host_demo_cmd = subparsers.add_parser(
        "host-demo", help="Run a minimal LocalCogLangHost request/submit/query workflow."
    )
    host_demo_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the host-demo run.",
    )

    reference_host_demo_cmd = subparsers.add_parser(
        "reference-host-demo",
        help="Run a minimal second-host write-envelope workflow.",
    )
    reference_host_demo_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the reference-host-demo run.",
    )

    release_check_cmd = subparsers.add_parser(
        "release-check", help="Check whether the minimal release-facing artifact set exists."
    )
    release_check_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format for the release-facing check report.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "conformance":
        pytest_args = list(args.pytest_args)
        if pytest_args and pytest_args[0] == "--":
            pytest_args = pytest_args[1:]
        return _run_conformance_suite(args.suite, pytest_args)

    if args.command == "repl":
        return _run_repl()

    if args.command == "info":
        payload = _info_payload()
        if args.format == "text":
            print(f"tool: {payload['tool']}")
            print(f"package: {payload['package']}")
            print(f"version: {payload['version']}")
            print(f"language_release: {payload['language_release']}")
            print("commands: " + ", ".join(payload["commands"]))
            print("conformance_suites: " + ", ".join(payload["conformance_suites"]))
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "manifest":
        payload = _manifest_payload()
        if args.format == "text":
            print(f"schema_version: {payload['schema_version']}")
            print(f"tool: {payload['tool']}")
            print(f"package: {payload['package']}")
            print(f"version: {payload['version']}")
            print(f"language_release: {payload['language_release']}")
            print(f"status: {payload['status']}")
            print(f"license: {payload['license']}")
            print(f"recommended_entrypoint: {payload['entrypoints']['recommended']}")
            print(f"console_script: {payload['entrypoints']['console_script']}")
            print(
                "implementation.console_script_target: "
                + str(payload["implementation_metadata"]["console_script_target"])
            )
            print("commands: " + ", ".join(payload["commands"]))
            print("conformance_suites: " + ", ".join(payload["conformance_suites"]))
            print(f"readme: {payload['docs']['readme']}")
            print(f"install_guide: {payload['docs']['install_guide']}")
            print(f"vision_proposal: {payload['docs']['vision_proposal']}")
            print(f"evolution_boundary_proposal: {payload['docs']['evolution_boundary_proposal']}")
            print(f"effect_budget_preflight_vocabulary: {payload['docs']['effect_budget_preflight_vocabulary']}")
            print(
                "reserved_operator_promotion_criteria: "
                + payload["docs"]["reserved_operator_promotion_criteria"]
            )
            print(
                "send_carry_forward_exit_matrix: "
                + payload["docs"]["send_carry_forward_exit_matrix"]
            )
            print(
                "readable_render_boundary: "
                + payload["docs"]["readable_render_boundary"]
            )
            print(
                "hrc_companion_asset_classification: "
                + payload["docs"]["hrc_companion_asset_classification"]
            )
            print(f"roadmap: {payload['docs']['roadmap']}")
            print(f"maintenance: {payload['docs']['maintenance']}")
            print(f"llms: {payload['machine_readable_summaries']['llms']}")
            print(f"llms_full: {payload['machine_readable_summaries']['llms_full']}")
            print(
                "open_source_boundary.strategy: "
                + str(payload["open_source_boundary"]["repository_strategy"])
            )
            print(
                "open_source_boundary.distribution: "
                + str(payload["open_source_boundary"]["public_distribution_name"])
            )
            print(
                "minimal_ci_baseline.path: "
                + str(payload["minimal_ci_baseline"]["path"])
            )
            print(
                "public_repo_extract_manifest.path: "
                + str(payload["public_repo_extract_manifest"]["path"])
            )
            print(
                "formal_open_source_readiness.status: "
                + str(payload["formal_open_source_readiness"]["status"])
            )
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "bundle":
        payload = _bundle_payload()
        if args.format == "text":
            print(f"schema_version: {payload['schema_version']}")
            print(f"tool: {payload['tool']}")
            print(f"version: {payload['version']}")
            print(f"language_release: {payload['language_release']}")
            print(f"status: {payload['status']}")
            print(f"license: {payload['license']}")
            print(
                "public_release.entrypoint: "
                + payload["public_release_surface"]["entrypoint"]
            )
            print(
                "public_release.readme: "
                + payload["public_release_surface"]["project_docs"]["readme"]
            )
            print(
                "open_source_boundary.strategy: "
                + str(payload["open_source_boundary"]["repository_strategy"])
            )
            print(
                "minimal_ci_baseline.path: "
                + str(payload["minimal_ci_baseline"]["path"])
            )
            print(
                "public_repo_extract_manifest.path: "
                + str(payload["public_repo_extract_manifest"]["path"])
            )
            print(
                "formal_open_source_readiness.status: "
                + str(payload["formal_open_source_readiness"]["status"])
            )
            print(f"release_check.ok: {str(payload['release_check']['ok']).lower()}")
            print(f"doctor.ok: {str(payload['doctor']['ok']).lower()}")
            print("release_check.failed_checks: " + ", ".join(payload["release_check"]["failed_checks"]))
            print("doctor.failed_checks: " + ", ".join(payload["doctor"]["failed_checks"]))
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["release_check"]["ok"] and payload["doctor"]["ok"] else 1

    if args.command == "doctor":
        payload = _doctor_payload()
        if args.format == "text":
            print(f"tool: {payload['tool']}")
            print(f"version: {payload['version']}")
            print(f"language_release: {payload['language_release']}")
            print(f"ok: {str(payload['ok']).lower()}")
            for check in payload["checks"]:
                status = "ok" if check["ok"] else "fail"
                print(f"{check['name']}: {status} ({check['detail']})")
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "vocab":
        payload = _vocab_payload()
        if args.format == "text":
            print(f"tool: {payload['tool']}")
            print(f"version: {payload['version']}")
            print(f"vocab_size: {payload['vocab_size']}")
            print(f"error_head_count: {payload['error_head_count']}")
            print("vocab: " + ", ".join(payload["vocab"]))
            print("error_heads: " + ", ".join(payload["error_heads"]))
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "examples":
        if args.name is not None:
            print(EXAMPLES[args.name])
            return 0
        payload = _examples_payload()
        if args.format == "text":
            print(f"tool: {payload['tool']}")
            print(f"version: {payload['version']}")
            print(f"example_count: {payload['example_count']}")
            for item in payload["examples"]:
                print(f"{item['name']}: {item['expr']}")
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "generation-eval":
        payload = generation_eval_payload(
            fixture_path=args.fixture,
            answers_path=args.answers_file,
        )
        payload = _generation_eval_output_payload(
            payload,
            summary_only=args.summary_only,
            failures_only=args.failures_only,
        )
        if args.format == "text":
            _print_generation_eval_text(payload)
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "preflight-fixture":
        payload = preflight_fixture_payload(args.fixture)
        if args.format == "text":
            _print_preflight_fixture_text(payload)
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "smoke":
        pytest_args = list(args.pytest_args)
        if pytest_args and pytest_args[0] == "--":
            pytest_args = pytest_args[1:]
        return _run_smoke(pytest_args)

    if args.command == "demo":
        payload = _run_demo()
        if args.format == "text":
            print(f"tool: {payload['tool']}")
            print(f"version: {payload['version']}")
            print(f"language_release: {payload['language_release']}")
            print(f"ok: {str(payload['ok']).lower()}")
            for idx, step in enumerate(payload["steps"], start=1):
                status = "ok" if step["ok"] else "fail"
                print(f"step{idx}: {status}")
                print(f"  expr: {step['expr']}")
                print(f"  result: {step['result']}")
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "host-demo":
        payload = _run_host_demo()
        if args.format == "text":
            print(f"schema_version: {payload['schema_version']}")
            print(f"tool: {payload['tool']}")
            print(f"version: {payload['version']}")
            print(f"ok: {str(payload['ok']).lower()}")
            print(f"status: {payload['status']}")
            print(f"payload_kind: {payload['payload_kind']}")
            print(f"correlation_id: {payload['correlation_id']}")
            print(f"submission_id: {payload['submission_id']}")
            print(f"node_id: {payload['node_id']}")
            _print_text_step_blocks(payload["steps"])
            for label in (
                "typed_query_result",
                "typed_submission_message",
                "typed_response",
                "typed_submission_record",
                "typed_trace",
                "write_header",
                "typed_write_header",
                "typed_snapshot",
                "typed_summary",
                "snapshot_summary",
            ):
                if label in payload:
                    _print_text_mapping_block(label, payload[label])
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "reference-host-demo":
        payload = _run_reference_host_demo()
        if args.format == "text":
            print(f"schema_version: {payload['schema_version']}")
            print(f"tool: {payload['tool']}")
            print(f"version: {payload['version']}")
            print(f"ok: {str(payload['ok']).lower()}")
            print(f"host_kind: {payload['host_kind']}")
            print(f"status: {payload['status']}")
            print(f"payload_kind: {payload['payload_kind']}")
            print(f"correlation_id: {payload['correlation_id']}")
            print(f"submission_id: {payload['submission_id']}")
            _print_text_step_blocks(payload["steps"])
            for label in (
                "typed_submission_message",
                "typed_response",
                "typed_submission_record",
                "typed_query_result",
                "typed_write_header",
                "error_response",
                "error_write_header",
            ):
                _print_text_mapping_block(label, payload[label])
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if args.command == "release-check":
        payload = _release_check_payload()
        if args.format == "text":
            print(f"tool: {payload['tool']}")
            print(f"version: {payload['version']}")
            print(f"language_release: {payload['language_release']}")
            print(f"ok: {str(payload['ok']).lower()}")
            for check in payload["checks"]:
                status = "ok" if check["ok"] else "fail"
                print(f"{check['name']}: {status} ({check['detail']})")
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    source = _read_expr(args)
    expr = parse(source)

    if args.command == "parse":
        if expr.head == "ParseError":
            _emit(expr, args.format)
            return 1
        _emit(expr, args.format)
        return 0

    if args.command == "canonicalize":
        if expr.head == "ParseError":
            print(canonicalize(expr))
            return 1
        print(canonicalize(expr))
        return 0

    if args.command == "validate":
        valid = expr.head != "ParseError" and valid_coglang(expr)
        if args.json:
            print(
                json.dumps(
                    {
                        "ok": valid,
                        "parse_error": expr.head == "ParseError",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print("true" if valid else "false")
        return 0 if valid else 1

    if args.command == "preflight":
        decision = preflight_expression(
            expr,
            budget=_preflight_budget_from_args(args),
            correlation_id=args.correlation_id,
            enabled_capabilities=args.enabled_capability,
            require_review_for_writes=not args.allow_writes_without_review,
        )
        payload = decision.to_dict()
        if args.format == "text":
            _print_preflight_text(payload)
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1 if decision.decision == "rejected" else 0

    if args.command == "execute":
        if expr.head == "ParseError":
            _emit(expr, args.format)
            return 1
        executor = PythonCogLangExecutor()
        result = executor.execute(expr)
        _emit(result, args.format)
        return 0 if not (isinstance(result, CogLangExpr) and result.head == "ParseError") else 1

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
