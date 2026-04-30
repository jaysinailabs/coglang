from __future__ import annotations

import json

from coglang.generation_eval import (
    generation_eval_payload,
    load_generation_eval_cases,
    reference_generation_eval_answers,
)


def test_default_generation_eval_fixture_has_50_cases():
    cases = load_generation_eval_cases()

    assert len(cases) == 50
    assert {case.level for case in cases} == {"L1", "L2", "L3"}
    assert all(case.reference_expr for case in cases)


def test_generation_eval_reference_outputs_score_cleanly():
    payload = generation_eval_payload()

    assert payload["ok"] is True
    assert payload["answer_source"] == "fixture_reference"
    assert payload["case_count"] == 50
    assert payload["summary"]["parse_ok_count"] == 50
    assert payload["summary"]["canonicalize_ok_count"] == 50
    assert payload["summary"]["validate_ok_count"] == 50
    assert payload["summary"]["hallucinated_operator_count"] == 0


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
    assert failed_case["hallucinated_heads"] == ["BetterEqual"]
    assert failed_case["expected_top_level_head_ok"] is False
