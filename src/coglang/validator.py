# CogLang expression validator.
from __future__ import annotations

from .parser import CogLangExpr
from .vocab import COGLANG_VOCAB

# Heads whose arguments are opaque Prolog terms, not CogLang expressions.
# Unify[f[X_, b], f[a, Y_]] is a valid CogLang expression; the nested f[...] are
# Prolog functor terms (data), not CogLang sub-expressions.  Applying vocab
# validation recursively to those args would incorrectly reject all Unify/Match
# expressions that use non-trivial patterns (i.e., all real-world usage).
#
# Design note: this is a semantic distinction between "CogLang program position"
# (must be in vocab) and "Prolog data position" (arbitrary functor structure).
# The parser represents both as CogLangExpr because M-expression syntax is
# identical; the validator is the layer that knows which positions are which.
_OPAQUE_ARG_HEADS: frozenset[str] = frozenset({"Unify", "Match"})

_SPECIAL_FORM_ARITIES: dict[str, frozenset[int]] = {
    "Do": frozenset({1}),
    "If": frozenset({3}),
    "IfFound": frozenset({4}),
    "ForEach": frozenset({3}),
    "Compose": frozenset({3}),
    "Assert": frozenset({1, 2}),
    "Query": frozenset({2, 3}),
}


def _has_valid_arity(expr: CogLangExpr) -> bool:
    allowed = _SPECIAL_FORM_ARITIES.get(expr.head)
    if allowed is None:
        return True
    if expr.head == "Do":
        return len(expr.args) >= 1
    return len(expr.args) in allowed


def valid_coglang(
    expr: CogLangExpr,
    vocab: frozenset[str] = COGLANG_VOCAB,
    graph=None,
) -> bool:
    """Validate a CogLang expression against the vocabulary.

    Rules:
    1. head must be in the static vocab, OR in the graph as a COMPOSE-registered
       Operation node (dynamic extension via Compose[]).
    2. Argument positions are unconstrained (no vocab check on args).
    3. Nested CogLangExpr arguments are validated recursively, EXCEPT for
       heads in _OPAQUE_ARG_HEADS (Unify, Match) whose args are Prolog terms.

    Args:
        expr:  The expression to validate.
        vocab: Static vocabulary set (default: COGLANG_VOCAB).
        graph: Optional NetworkX DiGraph for COMPOSE-registered operations.
               If provided, an unknown head is accepted if it is a node of
               type "Operation" in the graph.

    Returns:
        True if the expression is valid, False otherwise.
    """
    if expr.head not in vocab:
        # Check dynamic operations registered via Compose.
        if graph is not None and expr.head in graph.nodes:
            if graph.nodes[expr.head].get("type") != "Operation":
                return False
        else:
            return False

    if not _has_valid_arity(expr):
        return False

    # Unify/Match args are Prolog terms (opaque data).  Do not recurse into them.
    if expr.head in _OPAQUE_ARG_HEADS:
        return True

    for arg in expr.args:
        if isinstance(arg, CogLangExpr) and not valid_coglang(arg, vocab, graph):
            return False

    return True
