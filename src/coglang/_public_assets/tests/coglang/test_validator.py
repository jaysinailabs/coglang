"""Validator tests for valid_coglang() on current CogLang expressions.

Coverage:
  [L2] Static vocab: known Head → True
  [L2] Static vocab: unknown Head → False
  [L2] Recursive validation of nested expressions
  [L2] COMPOSE dynamic registration via mock graph
"""

import pytest

try:
    from logos.coglang.parser import CogLangExpr, parse
    from logos.coglang.validator import valid_coglang
    from logos.coglang.vocab import COGLANG_VOCAB
    _PARSER_MODULE = "logos.coglang.parser"
except ModuleNotFoundError:
    from coglang.parser import CogLangExpr, parse
    from coglang.validator import valid_coglang
    from coglang.vocab import COGLANG_VOCAB
    _PARSER_MODULE = "coglang.parser"


# ---------------------------------------------------------------------------
# [L2] Static vocab checks
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_known_head_traverse():
    """Traverse is in COGLANG_VOCAB → valid."""
    expr = CogLangExpr("Traverse", ("Einstein", "born_in"))
    assert valid_coglang(expr) is True


@pytest.mark.L2
def test_known_head_unify():
    """Unify is in COGLANG_VOCAB → valid (using List args, which are valid heads)."""
    # Note: Unify[f[X_, b], f[a, Y_]] uses Prolog functors ('f') that are NOT in
    # COGLANG_VOCAB; valid_coglang correctly rejects those nested exprs.
    # Here we use List[...] which IS in the vocab to verify Unify itself validates.
    expr = CogLangExpr("Unify", (CogLangExpr("List", ("a",)), CogLangExpr("List", ("b",))))
    assert valid_coglang(expr) is True


@pytest.mark.L2
def test_known_head_list():
    """List is in COGLANG_VOCAB → valid."""
    assert valid_coglang(CogLangExpr("List", ())) is True


@pytest.mark.L2
def test_unify_with_prolog_functor_args_valid():
    """Unify[f[X_, b], f[a, Y_]] is valid — Prolog functor args are opaque data.

    'f' is not in COGLANG_VOCAB, but in Unify/Match argument position it is
    term data rather than a top-level CogLang operator. valid_coglang() must
    accept this or it will incorrectly reject normal Unify/Match expressions.
    """
    if _PARSER_MODULE == "logos.coglang.parser":
        from logos.coglang.parser import parse as _parse
    else:
        from coglang.parser import parse as _parse
    # Via parse (the main code path Encoder will use)
    expr = _parse('Unify[f[X_, b], f[a, Y_]]')
    assert valid_coglang(expr) is True, (
        "valid_coglang() rejected Unify with Prolog functor args. "
        "Opaque term arguments in Unify/Match should not be treated as unknown operators."
    )
    # Also Match (alias)
    expr2 = _parse('Match[f[X_, b], f[a, Y_]]')
    assert valid_coglang(expr2) is True


@pytest.mark.L2
def test_unknown_head_no_graph():
    """Unknown head without graph → False."""
    expr = CogLangExpr("FooBar", ("x",))
    assert valid_coglang(expr) is False


@pytest.mark.L2
def test_unknown_head_empty_string():
    """Empty-string head → False."""
    expr = CogLangExpr("", ())
    assert valid_coglang(expr) is False


# ---------------------------------------------------------------------------
# [L2] Nested validation
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_nested_valid():
    """Nested valid expressions → True."""
    inner = CogLangExpr("Traverse", ("Einstein", "born_in"))
    outer = CogLangExpr("If", (inner, "yes", "no"))
    assert valid_coglang(outer) is True


@pytest.mark.L2
def test_nested_invalid_inner():
    """Outer valid but inner invalid → False."""
    bad_inner = CogLangExpr("Unknown_Op", ("x",))
    outer = CogLangExpr("If", (bad_inner, "yes", "no"))
    assert valid_coglang(outer) is False


@pytest.mark.L2
def test_error_head_valid():
    """Error heads (e.g. NotFound) are in COGLANG_VOCAB → valid."""
    assert valid_coglang(CogLangExpr("NotFound", ())) is True
    assert valid_coglang(CogLangExpr("TypeError", ("msg",))) is True
    assert valid_coglang(CogLangExpr("StubError", ("Abstract",))) is True


@pytest.mark.L2
@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ('If[True[], "yes"]', False),
        ('IfFound[NotFound[], r_, "fallback"]', False),
        ('Query[n_]', False),
        ('ForEach[List[]]', False),
        ('Compose["Op", List[n_]]', False),
        ('Assert[]', False),
        ('Do[]', False),
        ('If[True[], "yes", "no"]', True),
        ('IfFound[NotFound[], r_, "then", "else"]', True),
        ('Query[n_, True[]]', True),
        ('ForEach[List[], x_, x_]', True),
        ('Compose["MyOp", List[n_], n_]', True),
        ('Assert[True[]]', True),
        ('Do[True[]]', True),
    ],
)
def test_special_form_arity_validation(source, expected):
    """Special-form arity drift should be rejected at validator time."""
    assert valid_coglang(parse(source)) is expected


# ---------------------------------------------------------------------------
# [L2] COMPOSE dynamic registration via mock graph
# ---------------------------------------------------------------------------

class _MockGraph:
    """Minimal stand-in for nx.DiGraph with node attr access."""

    def __init__(self, nodes: dict[str, dict]):
        self._nodes = nodes

    @property
    def nodes(self):
        return self._nodes


@pytest.mark.L2
def test_compose_registered_operation_valid():
    """Head registered as Operation node in graph → valid."""
    graph = _MockGraph({"FindBirthplace": {"type": "Operation"}})
    expr = CogLangExpr("FindBirthplace", ("Einstein",))
    assert valid_coglang(expr, COGLANG_VOCAB, graph) is True


@pytest.mark.L2
def test_compose_registered_wrong_type_invalid():
    """Head exists in graph but type != 'Operation' → invalid."""
    graph = _MockGraph({"FindBirthplace": {"type": "Entity"}})
    expr = CogLangExpr("FindBirthplace", ("Einstein",))
    assert valid_coglang(expr, COGLANG_VOCAB, graph) is False


@pytest.mark.L2
def test_compose_not_in_graph_invalid():
    """Head not in static vocab and not in graph → False."""
    graph = _MockGraph({})
    expr = CogLangExpr("NotRegistered", ("x",))
    assert valid_coglang(expr, COGLANG_VOCAB, graph) is False
