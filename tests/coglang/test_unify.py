"""Tests for CogLang unification backends.

Coverage:
  [L1]  Backends instantiable; factory returns a UnifyBackend instance
  [L1]  Factory returns JanusUnifyBackend when janus-swi is available
        (skipped when the local Janus / SWI-Prolog ABI is incompatible)
  [L2]  Basic variable binding — analogue of completeness tests 03 / 07
  [L2]  All incompatible-term cases return NotFound[] (SCC-U6)
  [L2]  Occurs check — Unify[X_, f[X_]] → NotFound[] (SCC-U3)
  [L2]  Return dict keys have no trailing '_' (SCC-U2)
  [L2]  Anonymous variable: matches anything, absent from result dict (SCC-U7)
  [L2]  Dual-backend consistency: same result for same input (SCC-U5)
        (janus side skipped when Janus is unavailable or ABI-incompatible)

Local Janus availability is probed once at collection time because some
incompatible builds can terminate the process at import time.
"""
import pytest

from coglang.parser import CogLangExpr, CogLangVar
from coglang.unify_backend import (
    JanusUnifyBackend,
    PythonUnifyBackend,
    UnifyBackend,
    _janus_available,
    get_unify_backend,
)

# ---------------------------------------------------------------------------
# Probe janus availability once at collection time (subprocess — safe).
# This avoids crashing pytest when janus-swi has a C-level exit on import.
# ---------------------------------------------------------------------------

_JANUS_OK: bool = _janus_available()
_skip_janus = pytest.mark.skipif(
    not _JANUS_OK,
    reason="janus-swi not available or ABI-incompatible with the local SWI-Prolog runtime",
)

# Shared backend instances — construction never imports janus_swi (safe).
_python = PythonUnifyBackend()

# _BOTH: backends to parametrize over. Janus included only when probe passes.
_BOTH = [pytest.param(_python, id="python")]
if _JANUS_OK:
    _BOTH.append(pytest.param(JanusUnifyBackend(), id="janus"))


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------

def _expr(head: str, *args) -> CogLangExpr:
    return CogLangExpr(head, args)


def _var(name: str) -> CogLangVar:
    """Named CogLang variable (e.g. X_ in source → CogLangVar(name='X'))."""
    return CogLangVar(name=name, is_anonymous=False)


def _anon() -> CogLangVar:
    """Anonymous CogLang variable (_)."""
    return CogLangVar(name="_", is_anonymous=True)


# ---------------------------------------------------------------------------
# L1: smoke — backends importable and instantiable
# ---------------------------------------------------------------------------

@pytest.mark.L1
def test_python_backend_instantiable():
    """PythonUnifyBackend() can be constructed without error."""
    b = PythonUnifyBackend()
    assert isinstance(b, PythonUnifyBackend)


@pytest.mark.L1
def test_janus_backend_instantiable():
    """JanusUnifyBackend() can be constructed (no janus import at __init__)."""
    b = JanusUnifyBackend()
    assert isinstance(b, JanusUnifyBackend)


@pytest.mark.L1
def test_factory_returns_unify_backend():
    """get_unify_backend() always returns a UnifyBackend instance."""
    backend = get_unify_backend()
    assert isinstance(backend, UnifyBackend)


@pytest.mark.L1
@_skip_janus
def test_factory_returns_janus_when_available():
    """get_unify_backend() returns JanusUnifyBackend when janus-swi is available.

    Skipped when the local janus-swi build is unavailable or ABI-incompatible
    with the installed SWI-Prolog runtime.
    """
    backend = get_unify_backend()
    assert isinstance(backend, JanusUnifyBackend)


# ---------------------------------------------------------------------------
# L2: basic variable binding
# Analogue of completeness tests 03 (Match) and 07 (Unify)
# ---------------------------------------------------------------------------

@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_basic_variable_binding(backend):
    """Unify[f[X_, b], f[a, Y_]] → {"X": "a", "Y": "b"}."""
    pattern = _expr("f", _var("X"), "b")
    target = _expr("f", "a", _var("Y"))
    result = backend.unify(pattern, target)
    assert result == {"X": "a", "Y": "b"}


@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_single_variable_binding(backend):
    """Unify[X_, a] → {"X": "a"} (variable unifies with atom)."""
    result = backend.unify(_var("X"), "a")
    assert result == {"X": "a"}


@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_ground_unification_succeeds(backend):
    """Unify[f[a], f[a]] → {} (ground success, no variable bindings)."""
    result = backend.unify(_expr("f", "a"), _expr("f", "a"))
    assert result == {}


@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_lowercase_variable_name(backend):
    """Unify[x_, a] → {"X": "a"} (lowercase var name uppercased in result key)."""
    result = backend.unify(_var("x"), "a")
    # Key must be "X" (first letter uppercased), not "x" (SCC-U1 + SCC-U2)
    assert result == {"X": "a"}


# ---------------------------------------------------------------------------
# L2: incompatible terms → NotFound[] (SCC-U6)
# Analogue of completeness test 08
# ---------------------------------------------------------------------------

@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_different_head_returns_notfound(backend):
    """Unify[f[a], g[b]] → NotFound[] (different functor)."""
    result = backend.unify(_expr("f", "a"), _expr("g", "b"))
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_different_arity_returns_notfound(backend):
    """Unify[f[a, b], f[a]] → NotFound[] (different arity)."""
    result = backend.unify(_expr("f", "a", "b"), _expr("f", "a"))
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_constant_clash_returns_notfound(backend):
    """Unify[f[a], f[b]] → NotFound[] (constant clash)."""
    result = backend.unify(_expr("f", "a"), _expr("f", "b"))
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_atom_vs_compound_returns_notfound(backend):
    """Unify[a, f[a]] → NotFound[] (atom vs compound)."""
    result = backend.unify("a", _expr("f", "a"))
    assert result == CogLangExpr("NotFound", ())


# ---------------------------------------------------------------------------
# L2: occurs check (SCC-U3)
# ---------------------------------------------------------------------------

@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_occurs_check_direct(backend):
    """Unify[X_, f[X_]] → NotFound[] (circular structure — occurs check)."""
    result = backend.unify(_var("X"), _expr("f", _var("X")))
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_occurs_check_nested(backend):
    """Unify[X_, f[g[X_]]] → NotFound[] (occurs check via nested structure)."""
    result = backend.unify(_var("X"), _expr("f", _expr("g", _var("X"))))
    assert result == CogLangExpr("NotFound", ())


# ---------------------------------------------------------------------------
# L2: return key format — no trailing '_' (SCC-U2)
# ---------------------------------------------------------------------------

@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_return_key_no_trailing_underscore(backend):
    """Result dict keys must NOT contain a trailing '_'.

    CogLangVar X_ has name='X' (parser strips the trailing _), so the result
    key must be 'X' not 'X_'. executor uses Get[bindings, "X"] — any trailing _
    would cause silent NotFound[] (test_07 would fail).
    """
    result = backend.unify(_var("X"), "hello")
    assert isinstance(result, dict), f"Expected dict, got {result!r}"
    for key in result:
        assert not key.endswith("_"), (
            f"Key {key!r} has trailing underscore — executor Get[] would miss it"
        )
    assert "X" in result
    assert result["X"] == "hello"


# ---------------------------------------------------------------------------
# L2: anonymous variable (SCC-U7)
# ---------------------------------------------------------------------------

@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_anonymous_var_matches_anything(backend):
    """f[_, b] unifies with f[anything, b] — anonymous var is a wildcard."""
    result = backend.unify(
        _expr("f", _anon(), "b"),
        _expr("f", "anything", "b"),
    )
    assert isinstance(result, dict), (
        f"Expected dict (success), got {result!r}"
    )


@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_anonymous_var_not_in_result_dict(backend):
    """Anonymous _ must NOT appear as a key in the result dict."""
    result = backend.unify(
        _expr("f", _anon(), "b"),
        _expr("f", "a", "b"),
    )
    assert isinstance(result, dict)
    for key in result:
        assert not key.startswith("_"), (
            f"Anonymous var placeholder {key!r} leaked into result dict"
        )


@pytest.mark.L2
@pytest.mark.parametrize("backend", _BOTH)
def test_multiple_anonymous_vars_independent(backend):
    """Each _ occurrence matches independently — f[_, _] unifies with f[a, b]."""
    result = backend.unify(
        _expr("f", _anon(), _anon()),
        _expr("f", "a", "b"),
    )
    assert isinstance(result, dict), (
        f"Expected dict (success), got {result!r}"
    )


# ---------------------------------------------------------------------------
# L2: dual-backend consistency (SCC-U5)
# Janus side skipped when unavailable (TD-003).
# ---------------------------------------------------------------------------

@pytest.mark.L2
@_skip_janus
def test_dual_backend_consistency_basic_binding():
    """JanusUnifyBackend and PythonUnifyBackend return identical result on success."""
    pattern = _expr("f", _var("X"), "b")
    target = _expr("f", "a", _var("Y"))
    janus = JanusUnifyBackend()
    assert janus.unify(pattern, target) == _python.unify(pattern, target)


@pytest.mark.L2
@_skip_janus
def test_dual_backend_consistency_failure():
    """Both backends return the same NotFound[] on unification failure."""
    janus = JanusUnifyBackend()
    j_result = janus.unify(_expr("f", "a"), _expr("g", "b"))
    p_result = _python.unify(_expr("f", "a"), _expr("g", "b"))
    assert j_result == p_result == CogLangExpr("NotFound", ())


@pytest.mark.L2
@_skip_janus
def test_dual_backend_consistency_occurs_check():
    """Both backends agree on occurs-check failure."""
    janus = JanusUnifyBackend()
    j_result = janus.unify(_var("X"), _expr("f", _var("X")))
    p_result = _python.unify(_var("X"), _expr("f", _var("X")))
    assert j_result == p_result == CogLangExpr("NotFound", ())
