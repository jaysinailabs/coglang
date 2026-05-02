from __future__ import annotations

import json

import pytest

from coglang.generation_eval import (
    generation_eval_payload,
    load_generation_eval_cases,
    reference_generation_eval_answers,
)
from coglang.generation_eval_adapters import (
    GENERATION_EVAL_OUTPUT_INSTRUCTIONS,
    generation_eval_request_batch_payload,
    generation_eval_request_jsonl,
    generation_eval_response_answers_payload,
    load_generation_eval_response_answers,
)


def test_generation_eval_request_batch_exports_provider_neutral_records():
    payload = generation_eval_request_batch_payload()
    first_request = payload["requests"][0]

    assert payload["schema_version"] == "coglang-generation-eval-request-batch/v0.1"
    assert payload["fixture_schema_version"] == "coglang-generation-eval-fixture/v0.1"
    assert payload["response_schema_version"] == (
        "coglang-generation-eval-response-batch/v0.1"
    )
    assert payload["case_count"] == 50
    assert payload["include_reference"] is False
    assert payload["response_contract"]["required_fields"] == ["case_id", "output"]
    assert first_request["case_id"] == "L1-001"
    assert first_request["instructions"] == GENERATION_EVAL_OUTPUT_INSTRUCTIONS
    assert first_request["expected_top_level_heads"] == ["Equal"]
    assert "reference_expr" not in first_request


def test_generation_eval_request_batch_can_include_references():
    payload = generation_eval_request_batch_payload(include_reference=True)
    first_request = payload["requests"][0]

    assert payload["include_reference"] is True
    assert first_request["reference_expr"] == "Equal[1, 1]"


def test_generation_eval_request_jsonl_exports_one_record_per_case():
    text = generation_eval_request_jsonl()
    records = [json.loads(line) for line in text.splitlines()]

    assert len(records) == 50
    assert records[0]["case_id"] == "L1-001"
    assert records[0]["instructions"] == GENERATION_EVAL_OUTPUT_INSTRUCTIONS
    assert "reference_expr" not in records[0]


def test_generation_eval_response_loader_accepts_jsonl_output(tmp_path):
    responses_path = tmp_path / "responses.jsonl"
    responses_path.write_text(
        "\n".join(
            [
                json.dumps({"case_id": "L1-001", "output": "Equal[1, 1]"}),
                json.dumps({"case_id": "L1-002", "text": "NotEqual[1, 2]"}),
                json.dumps({"case_id": "L1-003", "completion": "GreaterThan[2, 1]"}),
            ]
        ),
        encoding="utf-8",
    )

    assert load_generation_eval_response_answers(responses_path) == {
        "L1-001": "Equal[1, 1]",
        "L1-002": "NotEqual[1, 2]",
        "L1-003": "GreaterThan[2, 1]",
    }


def test_generation_eval_response_loader_accepts_json_response_batch(tmp_path):
    responses_path = tmp_path / "responses.json"
    responses_path.write_text(
        json.dumps(
            {
                "responses": [
                    {"case_id": "L1-001", "output": "Equal[1, 1]"},
                    {"case_id": "L1-002", "output": "NotEqual[1, 2]"},
                ]
            }
        ),
        encoding="utf-8",
    )

    payload = generation_eval_response_answers_payload(responses_path)

    assert payload["schema_version"] == "coglang-generation-eval-response-batch/v0.1"
    assert payload["answer_count"] == 2
    assert payload["answers"] == [
        {"case_id": "L1-001", "output": "Equal[1, 1]"},
        {"case_id": "L1-002", "output": "NotEqual[1, 2]"},
    ]


def test_generation_eval_response_loader_accepts_top_level_json_list(tmp_path):
    responses_path = tmp_path / "responses.json"
    responses_path.write_text(
        json.dumps([{"case_id": "L1-001", "output": "Equal[1, 1]"}]),
        encoding="utf-8",
    )

    assert load_generation_eval_response_answers(responses_path) == {
        "L1-001": "Equal[1, 1]"
    }


def test_generation_eval_response_loader_rejects_missing_output(tmp_path):
    responses_path = tmp_path / "responses.json"
    responses_path.write_text(
        json.dumps({"responses": [{"case_id": "L1-001"}]}),
        encoding="utf-8",
    )

    with pytest.raises(KeyError, match="missing output"):
        load_generation_eval_response_answers(responses_path)


def test_generation_eval_response_loader_rejects_object_without_records(tmp_path):
    responses_path = tmp_path / "responses.json"
    responses_path.write_text(json.dumps({"schema_version": "demo"}), encoding="utf-8")

    with pytest.raises(TypeError, match="must contain a responses list"):
        load_generation_eval_response_answers(responses_path)


def test_generation_eval_scores_loaded_external_responses(tmp_path):
    cases = load_generation_eval_cases()
    reference_answers = reference_generation_eval_answers(cases)
    responses_path = tmp_path / "responses.jsonl"
    responses_path.write_text(
        "\n".join(
            json.dumps({"case_id": case_id, "output": output})
            for case_id, output in reference_answers.items()
        ),
        encoding="utf-8",
    )

    answers = load_generation_eval_response_answers(responses_path)
    payload = generation_eval_payload(
        answers=answers,
        answer_source=str(responses_path),
    )

    assert payload["ok"] is True
    assert payload["answer_source"] == str(responses_path)
    assert payload["summary"]["validate_ok_count"] == 50
