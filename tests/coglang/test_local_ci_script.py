from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from coglang.schema_versions import LOCAL_CI_SIMULATION_SCHEMA_VERSION


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_local_ci_module():
    path = _repo_root() / "scripts" / "local_ci.py"
    spec = importlib.util.spec_from_file_location("coglang_local_ci_test", path)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load scripts/local_ci.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_local_ci_quick_dry_run_uses_release_facing_checks():
    local_ci = _load_local_ci_module()

    payload = local_ci.run_profile("quick", dry_run=True)

    assert payload["schema_version"] == LOCAL_CI_SIMULATION_SCHEMA_VERSION
    assert local_ci.SCHEMA_VERSION == LOCAL_CI_SIMULATION_SCHEMA_VERSION
    assert payload["profile"] == "quick"
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert [step["name"] for step in payload["steps"]] == [
        "release_check",
        "smoke",
        "host_demo",
        "reference_host_demo",
    ]
    assert all(step["dry_run"] is True for step in payload["steps"])


def test_local_ci_ci_dry_run_includes_offline_contract_and_conformance():
    local_ci = _load_local_ci_module()

    payload = local_ci.run_profile("ci", dry_run=True)
    step_names = [step["name"] for step in payload["steps"]]

    assert step_names[:4] == [
        "pytest",
        "public_assets",
        "generation_eval_offline_contract",
        "bundle",
    ]
    assert step_names[-1] == "conformance_smoke"
    pytest_command = " ".join(payload["steps"][0]["command"])
    assert "pytest" in pytest_command
    assert "-q" in pytest_command
    offline_contract = payload["steps"][2]
    rendered_command = " ".join(offline_contract["command"])
    assert "generation_eval_three_case_v0_1.json" in rendered_command
    assert "mock_responses.jsonl" in rendered_command


def test_local_ci_package_dry_run_defers_artifact_install_steps():
    local_ci = _load_local_ci_module()

    payload = local_ci.run_profile("package", dry_run=True)

    assert payload["ok"] is True
    assert [step["name"] for step in payload["steps"]] == [
        "build_distributions",
        "wheel_install_validation",
        "sdist_install_validation",
    ]


def test_local_ci_stops_after_first_failed_step(monkeypatch):
    local_ci = _load_local_ci_module()
    calls: list[tuple[str, ...]] = []

    class Completed:
        def __init__(self, returncode: int) -> None:
            self.returncode = returncode

    def fake_run(command: tuple[str, ...], *, cwd: Path) -> Completed:
        calls.append(command)
        if "smoke" in command:
            return Completed(7)
        return Completed(0)

    monkeypatch.setattr(local_ci.subprocess, "run", fake_run)

    payload = local_ci.run_profile("quick")

    assert payload["ok"] is False
    assert payload["failed_step"] == "smoke"
    assert [step["name"] for step in payload["steps"]] == [
        "release_check",
        "smoke",
    ]
    assert len(calls) == 2
