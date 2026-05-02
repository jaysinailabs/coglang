from pathlib import Path

from coglang.parser import parse
from coglang.validator import valid_coglang


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "CogLang_Public_Repo_Extract_Manifest_v0_1.json").exists():
            return parent
    raise AssertionError("CogLang public extract manifest not found")


def test_constrained_generation_grammar_examples_are_companion_material():
    root = _repo_root()
    readme = (root / "examples" / "grammar" / "README.md").read_text(
        encoding="utf-8"
    )
    lark = (root / "examples" / "grammar" / "coglang.lark").read_text(
        encoding="utf-8"
    )
    gbnf = (root / "examples" / "grammar" / "coglang.gbnf").read_text(
        encoding="utf-8"
    )

    assert "companion example material" in readme
    assert "not a normative parser" in readme
    assert "valid_coglang" in readme
    assert "start: expr" in lark
    assert "root ::= ws expr ws" in gbnf


def test_grammar_readme_examples_parse_and_validate():
    examples = [
        'Query[n_, Equal[Get[n_, "category"], "Person"]]',
        'Create["Entity", {"active": True[], "id": "ada"}]',
    ]

    for source in examples:
        expr = parse(source)
        assert expr.head != "ParseError"
        assert valid_coglang(expr)
