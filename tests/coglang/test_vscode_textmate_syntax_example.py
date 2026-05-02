from __future__ import annotations

import json
from pathlib import Path

from coglang.parser import parse
from coglang.validator import valid_coglang


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "CogLang_Public_Repo_Extract_Manifest_v0_1.json").exists():
            return parent
    raise AssertionError("CogLang public extract manifest not found")


def _example_root() -> Path:
    return _repo_root() / "examples" / "vscode_textmate_syntax"


def test_vscode_textmate_syntax_example_declares_companion_boundary():
    readme = (_example_root() / "README.md").read_text(encoding="utf-8")

    assert "companion example material" in readme
    assert "not a parser" in readme
    assert "not a validator" in readme
    assert "not an LSP" in readme
    assert "does not expand HRC v0.2 frozen scope" in readme


def test_vscode_textmate_syntax_manifest_and_configuration_are_valid_json():
    package = json.loads((_example_root() / "package.json").read_text(encoding="utf-8"))
    language_config = json.loads(
        (_example_root() / "language-configuration.json").read_text(encoding="utf-8")
    )
    grammar = json.loads(
        (
            _example_root()
            / "syntaxes"
            / "coglang.tmLanguage.json"
        ).read_text(encoding="utf-8")
    )

    assert package["private"] is True
    assert package["contributes"]["languages"] == [
        {
            "id": "coglang",
            "aliases": ["CogLang", "coglang"],
            "extensions": [".coglang"],
            "configuration": "./language-configuration.json",
        }
    ]
    assert package["contributes"]["grammars"] == [
        {
            "language": "coglang",
            "scopeName": "source.coglang",
            "path": "./syntaxes/coglang.tmLanguage.json",
        }
    ]
    assert language_config["brackets"] == [["[", "]"], ["{", "}"]]
    assert {"open": "\"", "close": "\"", "notIn": ["string"]} in language_config[
        "autoClosingPairs"
    ]
    assert "comments" not in language_config
    assert grammar["scopeName"] == "source.coglang"
    assert grammar["fileTypes"] == ["coglang"]
    assert "repository" in grammar


def test_vscode_textmate_syntax_grammar_contains_expected_scopes():
    grammar_text = (
        _example_root()
        / "syntaxes"
        / "coglang.tmLanguage.json"
    ).read_text(encoding="utf-8")

    assert "string.quoted.double.coglang" in grammar_text
    assert "constant.numeric.coglang" in grammar_text
    assert "variable.parameter.coglang" in grammar_text
    assert "entity.name.function.coglang" in grammar_text
    assert "punctuation.section.brackets.coglang" in grammar_text


def test_vscode_textmate_syntax_sample_expressions_parse_and_validate():
    sample = (_example_root() / "samples" / "basic.coglang").read_text(
        encoding="utf-8"
    )
    expressions = [line.strip() for line in sample.splitlines() if line.strip()]

    assert len(expressions) == 3
    for source in expressions:
        expr = parse(source)
        assert expr.head != "ParseError"
        assert valid_coglang(expr)
