from __future__ import annotations

import json

import coglang.generation_eval as generation_eval_module
from coglang.generation_eval import (
    generation_eval_payload,
    load_generation_eval_cases,
    reference_generation_eval_answers,
)
from coglang.vocab import OPAQUE_ARG_HEADS


def test_generation_eval_uses_shared_opaque_argument_metadata():
    assert generation_eval_module.OPAQUE_ARG_HEADS is OPAQUE_ARG_HEADS


def test_default_generation_eval_fixture_has_50_cases():
    cases = load_generation_eval_cases()

    assert len(cases) == 50
    assert {case.level for case in cases} == {"L1", "L2", "L3"}
    assert all(case.reference_expr for case in cases)


def test_generation_eval_reference_outputs_score_cleanly():
    payload = generation_eval_payload()
    level_summary = payload["level_summary"]

    assert payload["ok"] is True
    assert payload["answer_source"] == "fixture_reference"
    assert payload["case_count"] == 50
    assert payload["summary"]["parse_ok_count"] == 50
    assert payload["summary"]["canonicalize_ok_count"] == 50
    assert payload["summary"]["validate_ok_count"] == 50
    assert payload["summary"]["hallucinated_operator_count"] == 0
    assert payload["summary"]["failure_category_counts"] == {}
    assert payload["failure_case_count"] == 0
    assert payload["failure_cases"] == []
    assert payload["maturity"] == {
        "evaluated_levels": ["L1", "L2", "L3"],
        "passed_levels": ["L1", "L2", "L3"],
        "contiguous_passed_levels": ["L1", "L2", "L3"],
        "highest_contiguous_level": "L3",
        "blocked_level": None,
    }
    assert set(level_summary) == {"L1", "L2", "L3"}
    assert sum(item["case_count"] for item in level_summary.values()) == 50
    assert level_summary["L1"]["case_count"] == 18
    assert level_summary["L2"]["case_count"] == 16
    assert level_summary["L3"]["case_count"] == 16
    assert all(item["ok"] is True for item in level_summary.values())


def test_generation_eval_detects_hallucinated_operator(tmp_path):
    cases = load_generation_eval_cases()
    answers = reference_generation_eval_answers(cases)
    answers["L1-001"] = "BetterEqual[1, 1]"
    answers_path = tmp_path / "answers.json"
    answers_path.write_text(
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

    payload = generation_eval_payload(answers_path=answers_path)
    failed_case = next(item for item in payload["cases"] if item["case_id"] == "L1-001")

    assert payload["ok"] is False
    assert payload["summary"]["parse_ok_count"] == 50
    assert payload["summary"]["validate_ok_count"] == 49
    assert payload["summary"]["hallucinated_operator_count"] == 1
    assert payload["summary"]["failure_category_counts"] == {
        "hallucinated_operator": 1,
        "top_level_head_mismatch": 1,
        "validation_error": 1,
    }
    assert payload["failure_case_count"] == 1
    assert payload["failure_cases"] == [
        {
            "case_id": "L1-001",
            "level": "L1",
            "failure_categories": [
                "validation_error",
                "top_level_head_mismatch",
                "hallucinated_operator",
            ],
            "hallucinated_heads": ["BetterEqual"],
            "parse_error": None,
        }
    ]
    assert payload["level_summary"]["L1"]["ok"] is False
    assert payload["level_summary"]["L1"]["validate_ok_count"] == 17
    assert payload["level_summary"]["L2"]["ok"] is True
    assert payload["level_summary"]["L3"]["ok"] is True
    assert payload["maturity"]["passed_levels"] == ["L2", "L3"]
    assert payload["maturity"]["contiguous_passed_levels"] == []
    assert payload["maturity"]["highest_contiguous_level"] == "L0"
    assert payload["maturity"]["blocked_level"] == "L1"
    assert failed_case["hallucinated_heads"] == ["BetterEqual"]
    assert failed_case["failure_categories"] == [
        "validation_error",
        "top_level_head_mismatch",
        "hallucinated_operator",
    ]
    assert failed_case["expected_top_level_head_ok"] is False


def test_generation_eval_categorizes_missing_and_parse_errors(tmp_path):
    cases = load_generation_eval_cases()
    answers = reference_generation_eval_answers(cases)
    answers.pop("L1-001")
    answers["L1-002"] = "Equal[1, 1"
    answers_path = tmp_path / "answers.json"
    answers_path.write_text(
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

    payload = generation_eval_payload(answers_path=answers_path)
    missing_case = next(item for item in payload["cases"] if item["case_id"] == "L1-001")
    parse_case = next(item for item in payload["cases"] if item["case_id"] == "L1-002")

    assert payload["ok"] is False
    assert payload["summary"]["missing_output_count"] == 1
    assert payload["summary"]["parse_ok_count"] == 48
    assert payload["summary"]["failure_category_counts"] == {
        "missing_output": 1,
        "parse_error": 1,
    }
    assert payload["failure_case_count"] == 2
    assert [
        (item["case_id"], item["failure_categories"])
        for item in payload["failure_cases"]
    ] == [
        ("L1-001", ["missing_output"]),
        ("L1-002", ["parse_error"]),
    ]
    assert payload["level_summary"]["L1"]["missing_output_count"] == 1
    assert payload["level_summary"]["L1"]["parse_ok_count"] == 16
    assert payload["maturity"]["highest_contiguous_level"] == "L0"
    assert payload["maturity"]["blocked_level"] == "L1"
    assert missing_case["failure_categories"] == ["missing_output"]
    assert parse_case["failure_categories"] == ["parse_error"]


def test_generation_eval_maturity_requires_contiguous_level_success(tmp_path):
    cases = load_generation_eval_cases()
    answers = reference_generation_eval_answers(cases)
    answers["L2-001"] = "BetterQuery[n_]"
    answers_path = tmp_path / "answers.json"
    answers_path.write_text(
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

    payload = generation_eval_payload(answers_path=answers_path)

    assert payload["level_summary"]["L1"]["ok"] is True
    assert payload["level_summary"]["L2"]["ok"] is False
    assert payload["level_summary"]["L3"]["ok"] is True
    assert payload["maturity"]["passed_levels"] == ["L1", "L3"]
    assert payload["maturity"]["contiguous_passed_levels"] == ["L1"]
    assert payload["maturity"]["highest_contiguous_level"] == "L1"
    assert payload["maturity"]["blocked_level"] == "L2"
