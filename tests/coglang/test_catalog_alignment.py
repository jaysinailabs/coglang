import re
from pathlib import Path

from coglang import COGLANG_OPERATOR_HEADS, COGLANG_VOCAB, ERROR_HEADS

CATALOG_PATH = (
    Path(__file__).resolve().parents[2] / "CogLang_Operator_Catalog_v1_1_0.md"
)
OPERATOR_ROW_RE = re.compile(
    r"^\|\s*`(?P<head>[A-Z][A-Za-z0-9]*)`\s*\|\s*`(?P<status>[^`|]+)`\s*\|"
)
CATALOG_OPERATOR_STATUSES = frozenset({"Core", "Reserved", "Carry-forward"})


def _catalog_operator_statuses() -> dict[str, str]:
    statuses: dict[str, str] = {}
    for line in CATALOG_PATH.read_text(encoding="utf-8").splitlines():
        match = OPERATOR_ROW_RE.match(line)
        if not match:
            continue
        head = match.group("head")
        status = match.group("status")
        if status not in CATALOG_OPERATOR_STATUSES:
            continue
        statuses[head] = status
    return statuses


def test_operator_catalog_covers_static_operator_heads():
    catalog_heads = set(_catalog_operator_statuses())

    assert catalog_heads == set(COGLANG_OPERATOR_HEADS)


def test_operator_catalog_heads_are_static_vocab_heads():
    catalog_heads = set(_catalog_operator_statuses())

    assert catalog_heads <= set(COGLANG_VOCAB)


def test_static_operator_heads_exclude_value_and_error_heads():
    assert COGLANG_OPERATOR_HEADS <= COGLANG_VOCAB
    assert COGLANG_OPERATOR_HEADS.isdisjoint(ERROR_HEADS)
    assert "List" in COGLANG_VOCAB
    assert "List" not in COGLANG_OPERATOR_HEADS
    assert "Entity" in COGLANG_VOCAB
    assert "Entity" not in COGLANG_OPERATOR_HEADS
