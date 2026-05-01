from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

from coglang.parser import canonicalize, parse
from coglang.schema_versions import READABLE_RENDER_GOLDEN_CANDIDATES_SCHEMA_VERSION
from coglang.validator import valid_coglang


def _fixture_payload() -> dict[str, Any]:
    fixture_path = files("coglang").joinpath(
        "eval_fixtures/readable_render_golden_candidates_v0_1.json"
    )
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def test_readable_render_golden_candidate_fixture_is_non_renderer_anchor():
    payload = _fixture_payload()

    assert payload["schema_version"] == READABLE_RENDER_GOLDEN_CANDIDATES_SCHEMA_VERSION
    assert payload["name"] == "readable-render-golden-candidates-v0.1"
    assert payload["status"] == "candidate-fixture"
    assert payload["renderer_api_status"] == "not_implemented"
    assert payload["stable_claim"] == "canonical_text_anchor_only"
    assert payload["source_document"] == (
        "CogLang_Readable_Render_Golden_Example_Candidates_v0_1.md"
    )


def test_readable_render_golden_candidates_pin_canonical_text():
    payload = _fixture_payload()
    cases = payload["cases"]

    assert [case["case_id"] for case in cases] == [
        "RRG-001",
        "RRG-002",
        "RRG-003",
        "RRG-004",
        "RRG-005",
    ]
    expected_top_level_heads = {
        "RRG-001": "Equal",
        "RRG-002": "ForEach",
        "RRG-003": "Update",
        "RRG-004": "StubError",
        "RRG-005": "Create",
    }
    for case in cases:
        expr = parse(case["canonical_text"])
        assert canonicalize(expr) == case["canonical_text"]
        assert valid_coglang(expr) is True
        assert expr.head == case["expected_top_level_head"]
        assert case["expected_top_level_head"] == expected_top_level_heads[case["case_id"]]
        assert case["readable_render_candidate"]
        assert case["invariants"]


def test_readable_render_candidates_do_not_create_a_renderer_contract():
    payload = _fixture_payload()
    cases = payload["cases"]

    assert cases[0]["readable_render_candidate"] == cases[0]["canonical_text"]
    assert cases[0]["readable_render_is_canonical_text"] is True
    assert all(
        "\n" in case["readable_render_candidate"]
        for case in cases
        if case["case_id"] != "RRG-001"
    )
    assert all(
        case["readable_render_is_canonical_text"] is False
        for case in cases
        if case["case_id"] != "RRG-001"
    )
    assert "transport_expectation" in cases[-1]
