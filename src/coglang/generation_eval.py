from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .parser import CogLangExpr, canonicalize, parse
from .preflight import preflight_expression
from .validator import valid_coglang
from .vocab import COGLANG_VOCAB, OPAQUE_ARG_HEADS

GENERATION_EVAL_FIXTURE_SCHEMA_VERSION = "coglang-generation-eval-fixture/v0.1"
GENERATION_EVAL_RESULT_SCHEMA_VERSION = "coglang-generation-eval-result/v0.1"
DEFAULT_GENERATION_EVAL_FIXTURE = "generation_eval_minimal_v0_1.json"


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
    failure_categories: list[str]
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
            "failure_categories": list(self.failure_categories),
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
    if "defined_levels" in data and not isinstance(data["defined_levels"], list):
        raise TypeError("generation eval fixture defined_levels must be a list")
    data["path"] = str(fixture_path)
    return data


def _defined_levels_from_fixture(
    fixture: dict[str, Any],
    cases: list["GenerationEvalCase"],
) -> list[str]:
    raw_defined_levels = fixture.get("defined_levels")
    if raw_defined_levels is None:
        return sorted({case.level for case in cases}, key=_level_sort_key)
    return sorted({str(level) for level in raw_defined_levels}, key=_level_sort_key)


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
        if value.head in OPAQUE_ARG_HEADS:
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
            failure_categories=["missing_output"],
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
            failure_categories=["parse_error"],
            preflight_decision="rejected",
            parse_error=canonicalize(expr),
        )

    canonical = canonicalize(expr)
    heads = _iter_heads(expr)
    hallucinated_heads = sorted({head for head in heads if head not in COGLANG_VOCAB})
    valid = valid_coglang(expr)
    expected_head_ok = expr.head in case.expected_top_level_heads
    decision = preflight_expression(expr).decision
    failure_categories: list[str] = []
    if not valid:
        failure_categories.append("validation_error")
    if not expected_head_ok:
        failure_categories.append("top_level_head_mismatch")
    if hallucinated_heads:
        failure_categories.append("hallucinated_operator")

    return GenerationEvalCaseResult(
        case_id=case.case_id,
        level=case.level,
        prompt=case.prompt,
        output=output,
        parse_ok=True,
        canonicalize_ok=True,
        validate_ok=valid,
        expected_top_level_head_ok=expected_head_ok,
        hallucinated_heads=hallucinated_heads,
        failure_categories=failure_categories,
        preflight_decision=decision,
        canonical=canonical,
    )


def _summarize_results(results: list[GenerationEvalCaseResult]) -> dict[str, Any]:
    case_count = len(results)
    parse_ok_count = sum(1 for item in results if item.parse_ok)
    canonicalize_ok_count = sum(1 for item in results if item.canonicalize_ok)
    validate_ok_count = sum(1 for item in results if item.validate_ok)
    head_match_count = sum(1 for item in results if item.expected_top_level_head_ok)
    missing_output_count = sum(1 for item in results if item.output is None)
    hallucinated_operator_count = sum(1 for item in results if item.hallucinated_heads)

    def rate(count: int) -> float:
        return count / case_count if case_count else 0.0

    return {
        "case_count": case_count,
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
        "ok": (
            missing_output_count == 0
            and parse_ok_count == case_count
            and canonicalize_ok_count == case_count
            and validate_ok_count == case_count
            and head_match_count == case_count
            and hallucinated_operator_count == 0
        ),
    }


def _failure_category_counts(
    results: list[GenerationEvalCaseResult],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        for category in result.failure_categories:
            counts[category] = counts.get(category, 0) + 1
    return dict(sorted(counts.items()))


def _level_summary(
    results: list[GenerationEvalCaseResult],
) -> dict[str, dict[str, Any]]:
    return {
        level: _summarize_results([item for item in results if item.level == level])
        for level in sorted({item.level for item in results})
    }


def _level_sort_key(level: str) -> tuple[int, str]:
    if len(level) >= 2 and level[0] == "L" and level[1:].isdigit():
        return int(level[1:]), level
    return 10_000, level


def _maturity_summary(
    level_summary: dict[str, dict[str, Any]],
    *,
    defined_levels: list[str] | None = None,
) -> dict[str, Any]:
    evaluated_levels = sorted(level_summary, key=_level_sort_key)
    defined_level_set = set(defined_levels or evaluated_levels)
    defined_level_set.update(evaluated_levels)
    sorted_defined_levels = sorted(defined_level_set, key=_level_sort_key)
    unevaluated_levels = [
        level for level in sorted_defined_levels if level not in level_summary
    ]
    passed_levels = [
        level for level in evaluated_levels if level_summary[level]["ok"] is True
    ]
    contiguous_passed_levels: list[str] = []
    blocked_level: str | None = None
    for level in evaluated_levels:
        if level_summary[level]["ok"] is True:
            contiguous_passed_levels.append(level)
            continue
        blocked_level = level
        break
    return {
        "defined_levels": sorted_defined_levels,
        "evaluated_levels": evaluated_levels,
        "unevaluated_levels": unevaluated_levels,
        "passed_levels": passed_levels,
        "contiguous_passed_levels": contiguous_passed_levels,
        "highest_contiguous_level": (
            contiguous_passed_levels[-1] if contiguous_passed_levels else "L0"
        ),
        "highest_contiguous_evaluated_level": (
            contiguous_passed_levels[-1] if contiguous_passed_levels else "L0"
        ),
        "next_unevaluated_level": (
            unevaluated_levels[0] if unevaluated_levels else None
        ),
        "blocked_level": blocked_level,
        "evaluation_complete": not unevaluated_levels,
        "maturity_claim_scope": (
            "defined_levels_complete"
            if not unevaluated_levels
            else "evaluated_fixture_levels_only"
        ),
    }


def _failure_case_summaries(
    results: list[GenerationEvalCaseResult],
) -> list[dict[str, Any]]:
    return [
        {
            "case_id": result.case_id,
            "level": result.level,
            "failure_categories": list(result.failure_categories),
            "hallucinated_heads": list(result.hallucinated_heads),
            "parse_error": result.parse_error,
        }
        for result in results
        if result.failure_categories
    ]


def score_generation_eval(
    cases: list[GenerationEvalCase],
    answers: dict[str, str],
    *,
    answer_source: str,
    defined_levels: list[str] | None = None,
) -> dict[str, Any]:
    results = [_score_case(case, answers.get(case.case_id)) for case in cases]
    summary = _summarize_results(results)
    failure_category_counts = _failure_category_counts(results)
    summary["failure_category_counts"] = failure_category_counts
    level_summary = _level_summary(results)
    failure_cases = _failure_case_summaries(results)

    return {
        "schema_version": GENERATION_EVAL_RESULT_SCHEMA_VERSION,
        "tool": "coglang",
        "fixture_schema_version": GENERATION_EVAL_FIXTURE_SCHEMA_VERSION,
        "answer_source": answer_source,
        "ok": summary["ok"],
        "case_count": summary["case_count"],
        "summary": summary,
        "level_summary": level_summary,
        "maturity": _maturity_summary(level_summary, defined_levels=defined_levels),
        "failure_case_count": len(failure_cases),
        "failure_cases": failure_cases,
        "cases": [item.to_dict() for item in results],
    }


def generation_eval_payload(
    *,
    fixture_path: str | Path | None = None,
    answers_path: str | Path | None = None,
) -> dict[str, Any]:
    fixture = load_generation_eval_fixture(fixture_path)
    cases = [GenerationEvalCase.from_dict(dict(item)) for item in fixture["cases"]]
    defined_levels = _defined_levels_from_fixture(fixture, cases)
    if answers_path is None:
        answers = reference_generation_eval_answers(cases)
        answer_source = "fixture_reference"
    else:
        answers = load_generation_eval_answers(answers_path)
        answer_source = str(answers_path)
    payload = score_generation_eval(
        cases,
        answers,
        answer_source=answer_source,
        defined_levels=defined_levels,
    )
    payload["fixture_path"] = fixture["path"]
    return payload
