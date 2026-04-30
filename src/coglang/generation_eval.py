from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .parser import CogLangExpr, canonicalize, parse
from .preflight import preflight_expression
from .validator import valid_coglang
from .vocab import COGLANG_VOCAB

GENERATION_EVAL_FIXTURE_SCHEMA_VERSION = "coglang-generation-eval-fixture/v0.1"
GENERATION_EVAL_RESULT_SCHEMA_VERSION = "coglang-generation-eval-result/v0.1"
DEFAULT_GENERATION_EVAL_FIXTURE = "generation_eval_minimal_v0_1.json"

_OPAQUE_ARG_HEADS = frozenset({"Unify", "Match"})


@dataclass(frozen=True)
class GenerationEvalCase:
    """One offline prompt case for evaluating generated CogLang text."""

    case_id: str
    level: str
    prompt: str
    reference_expr: str
    expected_top_level_heads: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GenerationEvalCase":
        return cls(
            case_id=str(data["case_id"]),
            level=str(data["level"]),
            prompt=str(data["prompt"]),
            reference_expr=str(data["reference_expr"]),
            expected_top_level_heads=[
                str(item) for item in data.get("expected_top_level_heads", [])
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "level": self.level,
            "prompt": self.prompt,
            "reference_expr": self.reference_expr,
            "expected_top_level_heads": list(self.expected_top_level_heads),
        }


@dataclass(frozen=True)
class GenerationEvalCaseResult:
    """Deterministic score for one candidate output."""

    case_id: str
    level: str
    prompt: str
    output: str | None
    parse_ok: bool
    canonicalize_ok: bool
    validate_ok: bool
    expected_top_level_head_ok: bool
    hallucinated_heads: list[str]
    preflight_decision: str | None
    canonical: str | None = None
    parse_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "level": self.level,
            "prompt": self.prompt,
            "output": self.output,
            "parse_ok": self.parse_ok,
            "canonicalize_ok": self.canonicalize_ok,
            "validate_ok": self.validate_ok,
            "expected_top_level_head_ok": self.expected_top_level_head_ok,
            "hallucinated_heads": list(self.hallucinated_heads),
            "preflight_decision": self.preflight_decision,
            "canonical": self.canonical,
            "parse_error": self.parse_error,
        }


def default_generation_eval_fixture_path() -> Path:
    return Path(__file__).resolve().parent / "eval_fixtures" / DEFAULT_GENERATION_EVAL_FIXTURE


def load_generation_eval_fixture(path: str | Path | None = None) -> dict[str, Any]:
    fixture_path = Path(path) if path is not None else default_generation_eval_fixture_path()
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != GENERATION_EVAL_FIXTURE_SCHEMA_VERSION:
        raise ValueError("unsupported generation eval fixture schema_version")
    if not isinstance(data.get("cases"), list):
        raise TypeError("generation eval fixture must contain a cases list")
    data["path"] = str(fixture_path)
    return data


def load_generation_eval_cases(path: str | Path | None = None) -> list[GenerationEvalCase]:
    data = load_generation_eval_fixture(path)
    return [GenerationEvalCase.from_dict(dict(item)) for item in data["cases"]]


def load_generation_eval_answers(path: str | Path) -> dict[str, str]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_answers = data if isinstance(data, list) else data.get("answers", [])
    if not isinstance(raw_answers, list):
        raise TypeError("generation eval answers must be a list or contain an answers list")
    answers: dict[str, str] = {}
    for item in raw_answers:
        if not isinstance(item, dict):
            raise TypeError("generation eval answer entries must be objects")
        answers[str(item["case_id"])] = str(item["output"])
    return answers


def reference_generation_eval_answers(
    cases: list[GenerationEvalCase],
) -> dict[str, str]:
    return {case.case_id: case.reference_expr for case in cases}


def _iter_heads(value: Any) -> list[str]:
    heads: list[str] = []
    if isinstance(value, CogLangExpr):
        heads.append(value.head)
        if value.head in _OPAQUE_ARG_HEADS:
            return heads
        for arg in value.args:
            heads.extend(_iter_heads(arg))
        return heads
    if isinstance(value, dict):
        for item in value.values():
            heads.extend(_iter_heads(item))
        return heads
    if isinstance(value, (list, tuple)):
        for item in value:
            heads.extend(_iter_heads(item))
    return heads


def _score_case(case: GenerationEvalCase, output: str | None) -> GenerationEvalCaseResult:
    if output is None:
        return GenerationEvalCaseResult(
            case_id=case.case_id,
            level=case.level,
            prompt=case.prompt,
            output=None,
            parse_ok=False,
            canonicalize_ok=False,
            validate_ok=False,
            expected_top_level_head_ok=False,
            hallucinated_heads=[],
            preflight_decision=None,
            parse_error="missing output",
        )

    expr = parse(output)
    if expr.head == "ParseError":
        return GenerationEvalCaseResult(
            case_id=case.case_id,
            level=case.level,
            prompt=case.prompt,
            output=output,
            parse_ok=False,
            canonicalize_ok=False,
            validate_ok=False,
            expected_top_level_head_ok=False,
            hallucinated_heads=[],
            preflight_decision="rejected",
            parse_error=canonicalize(expr),
        )

    canonical = canonicalize(expr)
    heads = _iter_heads(expr)
    hallucinated_heads = sorted({head for head in heads if head not in COGLANG_VOCAB})
    valid = valid_coglang(expr)
    decision = preflight_expression(expr).decision

    return GenerationEvalCaseResult(
        case_id=case.case_id,
        level=case.level,
        prompt=case.prompt,
        output=output,
        parse_ok=True,
        canonicalize_ok=True,
        validate_ok=valid,
        expected_top_level_head_ok=expr.head in case.expected_top_level_heads,
        hallucinated_heads=hallucinated_heads,
        preflight_decision=decision,
        canonical=canonical,
    )


def score_generation_eval(
    cases: list[GenerationEvalCase],
    answers: dict[str, str],
    *,
    answer_source: str,
) -> dict[str, Any]:
    results = [_score_case(case, answers.get(case.case_id)) for case in cases]
    case_count = len(results)
    parse_ok_count = sum(1 for item in results if item.parse_ok)
    canonicalize_ok_count = sum(1 for item in results if item.canonicalize_ok)
    validate_ok_count = sum(1 for item in results if item.validate_ok)
    head_match_count = sum(1 for item in results if item.expected_top_level_head_ok)
    missing_output_count = sum(1 for item in results if item.output is None)
    hallucinated_operator_count = sum(1 for item in results if item.hallucinated_heads)

    def rate(count: int) -> float:
        return count / case_count if case_count else 0.0

    ok = (
        missing_output_count == 0
        and parse_ok_count == case_count
        and canonicalize_ok_count == case_count
        and validate_ok_count == case_count
        and head_match_count == case_count
        and hallucinated_operator_count == 0
    )

    return {
        "schema_version": GENERATION_EVAL_RESULT_SCHEMA_VERSION,
        "tool": "coglang",
        "fixture_schema_version": GENERATION_EVAL_FIXTURE_SCHEMA_VERSION,
        "answer_source": answer_source,
        "ok": ok,
        "case_count": case_count,
        "summary": {
            "missing_output_count": missing_output_count,
            "parse_ok_count": parse_ok_count,
            "parse_ok_rate": rate(parse_ok_count),
            "canonicalize_ok_count": canonicalize_ok_count,
            "canonicalize_ok_rate": rate(canonicalize_ok_count),
            "validate_ok_count": validate_ok_count,
            "validate_ok_rate": rate(validate_ok_count),
            "expected_top_level_head_ok_count": head_match_count,
            "expected_top_level_head_ok_rate": rate(head_match_count),
            "hallucinated_operator_count": hallucinated_operator_count,
        },
        "cases": [item.to_dict() for item in results],
    }


def generation_eval_payload(
    *,
    fixture_path: str | Path | None = None,
    answers_path: str | Path | None = None,
) -> dict[str, Any]:
    cases = load_generation_eval_cases(fixture_path)
    if answers_path is None:
        answers = reference_generation_eval_answers(cases)
        answer_source = "fixture_reference"
    else:
        answers = load_generation_eval_answers(answers_path)
        answer_source = str(answers_path)
    payload = score_generation_eval(cases, answers, answer_source=answer_source)
    payload["fixture_path"] = load_generation_eval_fixture(fixture_path)["path"]
    return payload
