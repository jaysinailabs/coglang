from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from coglang.schema_versions import LOCAL_CI_SIMULATION_SCHEMA_VERSION

SCHEMA_VERSION = LOCAL_CI_SIMULATION_SCHEMA_VERSION
PROFILES = ("quick", "ci", "package")
PACKAGE_TEMP_PATHS = ("build", "dist", ".tmp_ci_wheel", ".tmp_ci_sdist")


@dataclass(frozen=True)
class Step:
    name: str
    command: tuple[str, ...]

    def rendered(self) -> str:
        return " ".join(self.command)


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("pyproject.toml not found above scripts/local_ci.py")


def _python(*args: str) -> tuple[str, ...]:
    return (sys.executable, *args)


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _quick_steps() -> list[Step]:
    return [
        Step(
            "release_check",
            _python("-m", "coglang", "release-check", "--format", "text"),
        ),
        Step("smoke", _python("-m", "coglang", "smoke")),
        Step("host_demo", _python("-m", "coglang", "host-demo", "--format", "json")),
        Step(
            "reference_host_demo",
            _python("-m", "coglang", "reference-host-demo", "--format", "json"),
        ),
    ]


def _ci_steps() -> list[Step]:
    fixture = (
        "examples/generation_eval_offline_runner/fixtures/"
        "generation_eval_three_case_v0_1.json"
    )
    responses = "examples/generation_eval_offline_runner/fixtures/mock_responses.jsonl"
    return [
        Step("pytest", _python("-m", "pytest", "-q")),
        Step(
            "public_assets",
            _python("-m", "coglang", "public-assets", "--format", "text"),
        ),
        Step(
            "generation_eval_offline_contract",
            _python(
                "-m",
                "coglang",
                "generation-eval",
                "--fixture",
                fixture,
                "--responses-file",
                responses,
                "--summary-only",
            ),
        ),
        Step("bundle", _python("-m", "coglang", "bundle")),
        *_quick_steps(),
        Step("conformance_smoke", _python("-m", "coglang", "conformance", "smoke")),
    ]


def _run_step(step: Step, root: Path, *, dry_run: bool) -> dict[str, Any]:
    payload = {
        "name": step.name,
        "command": list(step.command),
        "dry_run": dry_run,
        "exit_code": 0,
        "ok": True,
    }
    print(f"==> {step.name}: {step.rendered()}", flush=True)
    if dry_run:
        return payload
    completed = subprocess.run(step.command, cwd=root)
    payload["exit_code"] = completed.returncode
    payload["ok"] = completed.returncode == 0
    return payload


def _assert_within_root(root: Path, target: Path) -> Path:
    resolved_root = root.resolve()
    resolved_target = target.resolve()
    if resolved_target == resolved_root or resolved_root not in resolved_target.parents:
        raise ValueError(f"refusing to remove path outside repository: {target}")
    return resolved_target


def _remove_path(root: Path, relative_path: str) -> dict[str, Any]:
    target = _assert_within_root(root, root / relative_path)
    if not target.exists():
        return {"path": relative_path, "removed": False}
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    return {"path": relative_path, "removed": True}


def _clean_package_artifacts(root: Path) -> list[dict[str, Any]]:
    return [_remove_path(root, relative_path) for relative_path in PACKAGE_TEMP_PATHS]


def _find_one_artifact(root: Path, pattern: str) -> Path:
    matches = sorted((root / "dist").glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"expected exactly one dist/{pattern}, found {len(matches)}")
    return matches[0]


def _venv_install_and_validate_steps(venv_dir: Path, artifact: Path) -> list[Step]:
    python = str(_venv_python(venv_dir))
    return [
        Step(f"{venv_dir.name}_create", _python("-m", "venv", str(venv_dir))),
        Step(
            f"{venv_dir.name}_upgrade_pip",
            (python, "-m", "pip", "install", "--upgrade", "pip"),
        ),
        Step(
            f"{venv_dir.name}_install",
            (python, "-m", "pip", "install", "pytest", "pytest-cov", str(artifact)),
        ),
        Step(
            f"{venv_dir.name}_manifest",
            (python, "-m", "coglang", "manifest", "--format", "json"),
        ),
        Step(
            f"{venv_dir.name}_release_check",
            (python, "-m", "coglang", "release-check", "--format", "json"),
        ),
        Step(f"{venv_dir.name}_smoke", (python, "-m", "coglang", "smoke")),
        Step(f"{venv_dir.name}_host_demo", (python, "-m", "coglang", "host-demo")),
        Step(
            f"{venv_dir.name}_reference_host_demo",
            (python, "-m", "coglang", "reference-host-demo"),
        ),
    ]


def _package_steps_after_build(root: Path) -> list[Step]:
    wheel = _find_one_artifact(root, "*.whl")
    sdist = _find_one_artifact(root, "*.tar.gz")
    return [
        *_venv_install_and_validate_steps(root / ".tmp_ci_wheel", wheel),
        *_venv_install_and_validate_steps(root / ".tmp_ci_sdist", sdist),
    ]


def run_profile(profile: str, *, dry_run: bool = False, clean: bool = True) -> dict[str, Any]:
    root = _repo_root()
    executed_steps: list[dict[str, Any]] = []
    cleanup: list[dict[str, Any]] = []

    if profile == "quick":
        steps = _quick_steps()
    elif profile == "ci":
        steps = _ci_steps()
    elif profile == "package":
        if clean and not dry_run:
            cleanup = _clean_package_artifacts(root)
        steps = [
            Step("build_distributions", _python("-m", "build", "--sdist", "--wheel"))
        ]
    else:
        raise ValueError(f"unsupported local CI profile: {profile}")

    for step in steps:
        result = _run_step(step, root, dry_run=dry_run)
        executed_steps.append(result)
        if not result["ok"]:
            break

    if profile == "package" and (dry_run or all(item["ok"] for item in executed_steps)):
        package_steps = (
            [
                Step("wheel_install_validation", ("<after-build>", "validate", "dist/*.whl")),
                Step(
                    "sdist_install_validation",
                    ("<after-build>", "validate", "dist/*.tar.gz"),
                ),
            ]
            if dry_run
            else _package_steps_after_build(root)
        )
        for step in package_steps:
            result = _run_step(step, root, dry_run=dry_run)
            executed_steps.append(result)
            if not result["ok"]:
                break

    ok = all(item["ok"] for item in executed_steps)
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": "coglang-local-ci",
        "profile": profile,
        "ok": ok,
        "dry_run": dry_run,
        "clean": clean,
        "cleanup": cleanup,
        "step_count": len(executed_steps),
        "failed_step": next(
            (item["name"] for item in executed_steps if not item["ok"]),
            None,
        ),
        "steps": executed_steps,
    }


def _print_text(payload: dict[str, Any]) -> None:
    print(f"schema_version: {payload['schema_version']}")
    print(f"tool: {payload['tool']}")
    print(f"profile: {payload['profile']}")
    print(f"ok: {str(payload['ok']).lower()}")
    print(f"dry_run: {str(payload['dry_run']).lower()}")
    print(f"step_count: {payload['step_count']}")
    if payload["failed_step"] is not None:
        print(f"failed_step: {payload['failed_step']}")
    for step in payload["steps"]:
        status = "ok" if step["ok"] else "fail"
        print(f"{step['name']}: {status} ({' '.join(step['command'])})")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run local CI simulation profiles without triggering GitHub Actions.",
    )
    parser.add_argument("profile", nargs="?", choices=PROFILES)
    parser.add_argument("--profile", dest="profile_option", choices=PROFILES)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the selected command sequence without running it.",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not remove package-profile build and temp venv artifacts first.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the final summary.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    profile = args.profile_option or args.profile or "quick"
    payload = run_profile(profile, dry_run=args.dry_run, clean=not args.no_clean)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_text(payload)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
