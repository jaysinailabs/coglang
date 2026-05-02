from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from coglang.generation_eval import generation_eval_payload
from coglang.generation_eval_adapters import (
    generation_eval_request_jsonl,
    load_generation_eval_response_answers,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_generation_eval_offline_runner_writes_scorable_responses(tmp_path):
    root = _repo_root()
    script = root / "examples" / "generation_eval_offline_runner" / "mock_responses.py"
    requests_path = tmp_path / "requests.jsonl"
    responses_path = tmp_path / "responses.jsonl"
    requests_path.write_text(
        generation_eval_request_jsonl(include_reference=True),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(script), str(requests_path), str(responses_path)],
        check=True,
        cwd=root,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)
    answers = load_generation_eval_response_answers(responses_path)
    scored = generation_eval_payload(
        answers=answers,
        answer_source=str(responses_path),
    )

    assert payload["schema_version"] == (
        "coglang-generation-eval-offline-runner-demo/v0.1"
    )
    assert payload["ok"] is True
    assert payload["request_count"] == 50
    assert payload["response_count"] == 50
    assert payload["checks"] == [
        "jsonl-request-input",
        "reference-expression-present",
        "jsonl-response-output",
    ]
    assert responses_path.exists()
    assert scored["ok"] is True
    assert scored["summary"]["validate_ok_count"] == 50


def test_generation_eval_offline_runner_requires_reference_records(tmp_path):
    root = _repo_root()
    script = root / "examples" / "generation_eval_offline_runner" / "mock_responses.py"
    requests_path = tmp_path / "requests.jsonl"
    responses_path = tmp_path / "responses.jsonl"
    requests_path.write_text(generation_eval_request_jsonl(), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(script), str(requests_path), str(responses_path)],
        cwd=root,
        text=True,
        capture_output=True,
    )

    assert completed.returncode != 0
    assert "--include-reference" in completed.stderr
    assert not responses_path.exists()


def test_generation_eval_offline_runner_readme_documents_provider_boundary():
    readme = (
        _repo_root()
        / "examples"
        / "generation_eval_offline_runner"
        / "README.md"
    ).read_text(encoding="utf-8")

    assert "provider-neutral" in readme
    assert "not a model provider integration" in readme
    assert "--include-reference" in readme
    assert "--responses-file" in readme
    assert "provider SDKs" in readme
