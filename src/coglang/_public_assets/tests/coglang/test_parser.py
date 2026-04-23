"""Parser tests for current CogLang canonical text handling.

Coverage:
  [L1] Basic parse mechanics — no crash on all 22 completeness expressions
  [L1] CogLangExpr hashability (frozen=True)
  [L2] Variable disambiguation rules (spec §3.2 rules 1-4)
  [L2] Dict literal parsing (including embedded True[]/False[])
  [L2] ParseError return on malformed input
  [L2] Roundtrip: parse(canonicalize(expr)) == expr
  [L2] canonicalize edge cases: float repr, dict key sort, zero-arg brackets
"""

import pytest

try:
    from logos.coglang.parser import CogLangExpr, CogLangVar, canonicalize, parse
    from logos.coglang.vocab import COGLANG_VOCAB
except ModuleNotFoundError:
    from coglang.parser import CogLangExpr, CogLangVar, canonicalize, parse
    from coglang.vocab import COGLANG_VOCAB


# ---------------------------------------------------------------------------
# [L1] Basic: parse does not crash on the completeness expressions
# ---------------------------------------------------------------------------

# Representative canonical-text expressions drawn from the completeness suite
_COMPLETENESS_EXPRS = [
    'Traverse["Einstein", "born_in"]',
    'ForEach[Traverse["Einstein", "awards"], prize_, Get[prize_, "name"]]',
    'Match[f[X_, b], f[a, Y_]]',
    'Create["Entity", {"confidence": 1.0, "name": "Tesla"}]',
    'Update["Tesla", {"confidence": 0.0}]',
    'Delete["Tesla"]',
    'Traverse["Einstein", "related_to"]',
    'If[Query[n_, Equal[Get[n_, "type"], "Person"]], "found", "not_found"]',
    'Unify[f[X_, b], f[a, Y_]]',
    'Unify[f[a], g[b]]',
    'ForEach[List["a", "b"], item_, Get[item_, 0]]',
    'Query[n_, Equal[Get[n_, "type"], "NonExistentType"]]',
    'Abstract[List["Einstein"]]',
    'Compose["FindBirthplace", List[person_], Traverse[person_, "born_in"]]',
    'Probe["some_rule", {}]',
    'Create["Rule", {"confidence": 0.5, "name": "TestRule"}]',
    'Send["layer_2", "activate", "attention"]',
    'Inspect["Einstein"]',
    'Send["target", "message", "broadcast"]',
    'Estimate["Traverse", List["Einstein", "born_in"]]',
    'Defer["some_problem"]',
    'Decompose["Traverse", 10]',
    'Traverse[NotFound[], "born_in"]',
    'ForEach[List[], x_, Get[x_, "name"]]',
]


@pytest.mark.L1
@pytest.mark.parametrize("src", _COMPLETENESS_EXPRS)
def test_parse_no_crash(src):
    """parse() produces a non-error CogLangExpr for every completeness expression.

    NOTE: ParseError is itself a CogLangExpr, so asserting isinstance(..., CogLangExpr)
    is NOT sufficient — it would pass even if parsing silently degraded to an error.
    This test explicitly checks head != 'ParseError'.
    """
    result = parse(src)
    assert isinstance(result, CogLangExpr), f"Expected CogLangExpr, got {type(result)!r}"
    assert result.head != "ParseError", (
        f"parse() returned ParseError for valid expression.\n"
        f"  Input:  {src!r}\n"
        f"  Result: {result!r}"
    )


@pytest.mark.L1
def test_coglang_expr_hashable():
    """CogLangExpr (no dict args) is hashable — frozen=True."""
    e1 = CogLangExpr("List", ())
    e2 = CogLangExpr("True", ())
    e3 = CogLangExpr("Traverse", ("Einstein", "born_in"))
    s = {e1, e2, e3}
    assert len(s) == 3


@pytest.mark.L1
def test_coglang_var_hashable():
    """CogLangVar is hashable — frozen=True."""
    v1 = CogLangVar("x", False)
    v2 = CogLangVar("_", True)
    assert len({v1, v2}) == 2   # two distinct vars do not collide in a set
    assert v1 in {v1, v2}       # can be retrieved from the set
    assert v2 in {v1, v2}


# ---------------------------------------------------------------------------
# [L2] Variable disambiguation (spec §3.2 ambiguity rules 1-4)
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_anon_var_rule1():
    """Rule 1: bare '_' → CogLangVar(is_anonymous=True)."""
    expr = parse('Unify[_, X_]')
    assert isinstance(expr.args[0], CogLangVar)
    assert expr.args[0].is_anonymous is True
    assert expr.args[0].name == "_"


@pytest.mark.L2
def test_named_var_rule2_lowercase():
    """Rule 2: 'x_' (lowercase + trailing _) → CogLangVar(name='x')."""
    expr = parse('ForEach[List[], x_, Get[x_, "name"]]')
    bindvar = expr.args[1]
    assert isinstance(bindvar, CogLangVar)
    assert bindvar.name == "x"
    assert bindvar.is_anonymous is False


@pytest.mark.L2
def test_named_var_rule2_uppercase():
    """Rule 2: 'X_' (uppercase + trailing _) → CogLangVar(name='X')."""
    expr = parse('Unify[f[X_, b], f[a, Y_]]')
    inner = expr.args[0]  # f[X_, b]
    assert isinstance(inner.args[0], CogLangVar)
    assert inner.args[0].name == "X"
    assert inner.args[0].is_anonymous is False


@pytest.mark.L2
def test_underscore_prefix_is_const_atom():
    """'_name' (leading _ but not trailing _) → const_atom, NOT a variable."""
    # Rule 2 requires trailing underscore; '_node' has a leading underscore only.
    expr = parse('Traverse[_node, "born_in"]')
    # _node → const_atom (rule 4), returned as the string "_node"
    assert expr.args[0] == "_node"
    assert not isinstance(expr.args[0], CogLangVar)


@pytest.mark.L2
def test_bare_head_is_zero_arg_expr():
    """Rule 4 then top-level: bare 'NotFound' → CogLangExpr('NotFound', ())."""
    result = parse("NotFound")
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_zero_arg_with_brackets():
    """Explicit 'NotFound[]' → CogLangExpr('NotFound', ())."""
    result = parse("NotFound[]")
    assert result == CogLangExpr("NotFound", ())


# ---------------------------------------------------------------------------
# [L2] Dict literal parsing
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_dict_simple():
    """Basic dict literal is parsed into a Python dict."""
    expr = parse('Create["Entity", {"name": "Tesla", "confidence": 1.0}]')
    d = expr.args[1]
    assert isinstance(d, dict)
    assert d["name"] == "Tesla"
    assert d["confidence"] == 1.0


@pytest.mark.L2
def test_dict_key_order_preserved_in_parse():
    """Dict keys are preserved as Python dicts (order irrelevant for equality)."""
    expr = parse('Update["n", {"b": 2, "a": 1}]')
    d = expr.args[1]
    assert d == {"a": 1, "b": 2}


# ---------------------------------------------------------------------------
# [L2] ParseError return
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_parse_error_unclosed_bracket():
    """Unclosed bracket → CogLangExpr('ParseError', (...), partial=...)."""
    result = parse('Traverse["Einstein",')
    assert result.head == "ParseError"
    assert result.partial is not None
    assert result.partial.head == "Traverse"


@pytest.mark.L2
def test_parse_error_empty_string():
    """Empty string → ParseError."""
    result = parse("")
    assert result.head == "ParseError"


# ---------------------------------------------------------------------------
# [L2] Roundtrip: parse(canonicalize(expr)) == expr
# ---------------------------------------------------------------------------

_ROUNDTRIP_CASES = [
    CogLangExpr("Traverse", ("Einstein", "born_in")),
    CogLangExpr("List", ()),
    CogLangExpr("NotFound", ()),
    CogLangExpr("True", ()),
    CogLangExpr("False", ()),
    CogLangExpr(
        "ForEach",
        (
            CogLangExpr("List", ()),
            CogLangVar("x", False),
            CogLangExpr("Get", (CogLangVar("x", False), "name")),
        ),
    ),
    CogLangExpr(
        "Unify",
        (
            CogLangExpr("f", (CogLangVar("X", False), "b")),
            CogLangExpr("f", ("a", CogLangVar("Y", False))),
        ),
    ),
]


@pytest.mark.L2
@pytest.mark.parametrize("expr", _ROUNDTRIP_CASES)
def test_roundtrip(expr):
    """parse(canonicalize(expr)) == expr."""
    s = canonicalize(expr)
    assert parse(s) == expr, f"Roundtrip failed for {s!r}"


# ---------------------------------------------------------------------------
# [L2] canonicalize edge cases
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_canonicalize_float():
    """Float uses repr() format (cross-platform roundtrip safety)."""
    assert canonicalize(0.1) == repr(0.1)
    assert canonicalize(3.14) == repr(3.14)


@pytest.mark.L2
def test_canonicalize_int():
    """Integer without decimal point."""
    assert canonicalize(42) == "42"
    assert canonicalize(0) == "0"


@pytest.mark.L2
def test_canonicalize_dict_key_sort():
    """Dict keys are sorted alphabetically."""
    result = canonicalize({"b": 1, "a": 2})
    assert result == '{"a": 2, "b": 1}'


@pytest.mark.L2
def test_canonicalize_zero_arg_brackets():
    """Zero-arg expressions always include []."""
    assert canonicalize(CogLangExpr("NotFound", ())) == "NotFound[]"
    assert canonicalize(CogLangExpr("True", ())) == "True[]"
    assert canonicalize(CogLangExpr("List", ())) == "List[]"


@pytest.mark.L2
def test_canonicalize_string_escaping():
    """Strings with special chars are properly escaped."""
    assert canonicalize('say "hello"') == r'"say \"hello\""'
    assert canonicalize("back\\slash") == r'"back\\slash"'


@pytest.mark.L2
def test_canonicalize_var():
    """CogLangVar canonical form."""
    assert canonicalize(CogLangVar("x", False)) == "x_"
    assert canonicalize(CogLangVar("X", False)) == "X_"
    assert canonicalize(CogLangVar("_", True)) == "_"


@pytest.mark.L2
def test_canonicalize_bool_before_int():
    """Python bool is canonicalized as True[]/False[], not 1/0."""
    assert canonicalize(True) == "True[]"
    assert canonicalize(False) == "False[]"


# ---------------------------------------------------------------------------
# [L1] Vocab integrity
# ---------------------------------------------------------------------------

@pytest.mark.L1
def test_vocab_size():
    """COGLANG_VOCAB has exactly 49 built-in Heads.

    This acts as a change-detector: if someone adds or removes a Head without
    updating the spec, this test will fail and force an explicit decision.
    """
    assert len(COGLANG_VOCAB) == 49, (
        f"Expected 49 Heads in COGLANG_VOCAB, got {len(COGLANG_VOCAB)}. "
        "If you intentionally changed the vocab, update this assertion and "
        "bump CogLang_Specification version."
    )


# ---------------------------------------------------------------------------
# [L2] Roundtrip with dict args
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_roundtrip_with_dict_args():
    """parse(canonicalize(expr)) == expr for expressions containing dict args."""
    expr = CogLangExpr("Create", ("Entity", {"confidence": 1.0, "name": "Tesla"}))
    s = canonicalize(expr)
    result = parse(s)
    assert result == expr, f"Roundtrip failed for {s!r}\nGot: {result!r}"


@pytest.mark.L2
def test_roundtrip_nested_dict():
    """Dict with multiple sorted keys roundtrips correctly."""
    expr = CogLangExpr("Update", ("node_1", {"confidence": 0.5, "active": 1, "name": "X"}))
    s = canonicalize(expr)
    result = parse(s)
    assert result == expr, f"Roundtrip failed.\nGot: {result!r}"


@pytest.mark.L2
def test_canonicalize_ignores_partial_field():
    """canonicalize() serializes only head+args; partial metadata is not included.

    Rationale: partial is debug metadata for Encoder training signal extraction,
    not a semantic value. canonicalize output must be parse()-able, and parse()
    cannot reconstruct partial from a string — this is intentional and expected.
    """
    err = CogLangExpr(
        "ParseError",
        ("unclosed_bracket", 5),
        partial=CogLangExpr("Traverse", ("Einstein",)),
    )
    s = canonicalize(err)
    assert s == 'ParseError["unclosed_bracket", 5]'
    recovered = parse(s)
    assert recovered.head == "ParseError"
    assert recovered.partial is None  # partial is lost in serialization — expected


# ---------------------------------------------------------------------------
# [L1] R-1 regression: args are always tuple regardless of construction
# ---------------------------------------------------------------------------

@pytest.mark.L1
def test_args_coerced_to_tuple_from_list():
    """CogLangExpr.__post_init__ coerces list args to tuple (R-1 fix)."""
    expr_list = CogLangExpr("List", ["Ulm"])
    expr_tuple = CogLangExpr("List", ("Ulm",))
    assert expr_list == expr_tuple
    assert type(expr_list.args) is tuple
    assert type(expr_tuple.args) is tuple
