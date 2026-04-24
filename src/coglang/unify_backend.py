# CogLang unification backend.
# DL-012: janus-swi (SWI-Prolog unify_with_occurs_check/2) as primary backend;
#         PythonUnifyBackend (Robinson unification, ~80 lines) as fallback.
# SWI_HOME_DIR must be normalized before any optional janus_swi import. Do not
# invent a platform-specific default; users should provide the value when needed.
import os

if "SWI_HOME_DIR" in os.environ:
    os.environ["SWI_HOME_DIR"] = os.environ["SWI_HOME_DIR"].strip()

import warnings
from abc import ABC, abstractmethod
from typing import Any, Union

from .parser import CogLangExpr, CogLangVar


# ---------------------------------------------------------------------------
# Prolog term conversion (helper for JanusUnifyBackend)
# ---------------------------------------------------------------------------

def _quote_prolog_atom(s: str) -> str:
    """Return s as a single-quoted Prolog atom string.

    Single-quoting handles PascalCase heads (which would be Prolog variables
    without quotes) and any atom that contains special characters.
    """
    escaped = s.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def _coglang_to_prolog_str(expr: Any, _anon: "list[int] | None" = None) -> str:
    """Recursively convert a CogLang value to a Prolog term *string*.

    Conversion rules:
    - CogLangVar (named)     → Prolog variable (first letter uppercased)  [SCC-U1]
    - CogLangVar (anonymous) → _AnonN  (N incremented per occurrence so
                               each anonymous var is a distinct Prolog var;
                               starts with '_' so janus excludes it from
                               the result dict)                           [SCC-U7]
    - CogLangExpr zero-arity → quoted Prolog atom
    - CogLangExpr non-zero   → quoted_functor(arg, ...)
    - str                    → quoted Prolog atom
    - bool                   → true / false (Prolog atoms, checked before int)
    - int                    → numeric literal
    - float                  → repr(x)
    """
    if _anon is None:
        _anon = [0]

    if isinstance(expr, CogLangVar):
        if expr.is_anonymous:
            _anon[0] += 1
            return f"_Anon{_anon[0]}"          # starts with _ → excluded by janus
        # Named variable: ensure first letter is uppercase (Prolog convention)
        name = expr.name
        return name[0].upper() + name[1:]

    if isinstance(expr, CogLangExpr):
        head_atom = _quote_prolog_atom(expr.head)
        if not expr.args:
            return head_atom                    # zero-arity: just the atom
        args_str = ", ".join(
            _coglang_to_prolog_str(a, _anon) for a in expr.args
        )
        return f"{head_atom}({args_str})"

    if isinstance(expr, bool):                 # bool must precede int (bool ⊂ int)
        return "true" if expr else "false"

    if isinstance(expr, int):
        return str(expr)

    if isinstance(expr, float):
        return repr(expr)

    if isinstance(expr, str):
        return _quote_prolog_atom(expr)

    # Fallback: stringify as a quoted atom
    return _quote_prolog_atom(str(expr))


# ---------------------------------------------------------------------------
# Robinson unification helpers (PythonUnifyBackend)
# ---------------------------------------------------------------------------

def _var_key(var: CogLangVar) -> str:
    """Canonical dict key for a named CogLangVar: first letter uppercased, no '_'.

    Matches the Prolog variable name convention used by the janus backend so
    both backends produce identical dict keys (SCC-U5).
    """
    name = var.name
    return name[0].upper() + name[1:]


def _apply_subst(term: Any, bindings: dict) -> Any:
    """Apply bindings to term, following variable chains to their fixpoint.

    Returns the most-resolved form of term reachable under bindings.
    Does NOT mutate bindings.
    """
    if isinstance(term, CogLangVar):
        if term.is_anonymous:
            return term                         # anonymous var is never bound
        key = _var_key(term)
        if key in bindings:
            return _apply_subst(bindings[key], bindings)
        return term
    if isinstance(term, CogLangExpr):
        new_args = tuple(_apply_subst(a, bindings) for a in term.args)
        return CogLangExpr(term.head, new_args)
    return term                                 # str / int / float — atomic


def _occurs(var_key: str, term: Any, bindings: dict) -> bool:
    """Return True if the variable (identified by var_key) occurs in term.

    Applies bindings before checking so that chains are correctly resolved.
    Used for Robinson occurs check to prevent infinite terms.
    """
    term = _apply_subst(term, bindings)
    if isinstance(term, CogLangVar) and not term.is_anonymous:
        return _var_key(term) == var_key
    if isinstance(term, CogLangExpr):
        return any(_occurs(var_key, a, bindings) for a in term.args)
    return False


def _python_unify(
    pattern: Any,
    target: Any,
    bindings: "dict | None" = None,
) -> "dict | None":
    """Robinson first-order unification with occurs check.

    Returns:
        dict:  updated bindings (NEW dict, never mutates the input) on success.
               May be empty ({}) for ground-term success.
        None:  if unification fails (head mismatch, arity mismatch, constant
               clash, or occurs-check violation).

    Variable keys: canonical form (first letter uppercase, no trailing '_'),
    matching janus backend output (SCC-U5).
    """
    if bindings is None:
        bindings = {}

    p = _apply_subst(pattern, bindings)
    t = _apply_subst(target, bindings)

    # --- Named variable on the pattern side ---
    if isinstance(p, CogLangVar) and not p.is_anonymous:
        p_key = _var_key(p)
        # Trivial case: same variable on both sides
        if isinstance(t, CogLangVar) and not t.is_anonymous and _var_key(t) == p_key:
            return bindings
        # Occurs check: binding X to f(X) would create an infinite term
        if _occurs(p_key, t, bindings):
            return None
        return {**bindings, p_key: t}

    # --- Named variable on the target side ---
    if isinstance(t, CogLangVar) and not t.is_anonymous:
        t_key = _var_key(t)
        if _occurs(t_key, p, bindings):
            return None
        return {**bindings, t_key: p}

    # --- Anonymous variables match anything without binding ---
    if isinstance(p, CogLangVar) and p.is_anonymous:
        return bindings
    if isinstance(t, CogLangVar) and t.is_anonymous:
        return bindings

    # --- Both compound terms: structural unification ---
    if isinstance(p, CogLangExpr) and isinstance(t, CogLangExpr):
        if p.head != t.head or len(p.args) != len(t.args):
            return None                         # different functor or arity
        current = bindings
        for p_arg, t_arg in zip(p.args, t.args):
            current = _python_unify(p_arg, t_arg, current)
            if current is None:
                return None
        return current

    # --- Atomic equality (str / int / float) ---
    if p == t:
        return bindings

    return None                                 # incompatible atomic values


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------

class UnifyBackend(ABC):
    """Abstract interface for CogLang UNIFY / MATCH operations."""

    @abstractmethod
    def unify(self, pattern: Any, target: Any) -> "Union[dict, CogLangExpr]":
        """Attempt to unify pattern and target.

        Returns:
            dict: {variable_name: bound_value, ...} on success.
                  Keys have no trailing '_'; may be empty for ground unification.
            CogLangExpr("NotFound", ()): on unification failure.
        """
        ...


# ---------------------------------------------------------------------------
# Primary backend: janus-swi (SWI-Prolog unify_with_occurs_check/2)
# ---------------------------------------------------------------------------

class JanusUnifyBackend(UnifyBackend):
    """Unification via SWI-Prolog's unify_with_occurs_check/2 through janus-swi.

    Advantages over PythonUnifyBackend:
    - Correct occurs check guaranteed by SWI-Prolog's built-in implementation.
    - Same janus channel can be reused for a future full Prolog backend.

    Requires:
    - SWI-Prolog installed at the path set in SWI_HOME_DIR.
    - janus-swi package installed in the active venv.
    """

    def unify(self, pattern: Any, target: Any) -> "Union[dict, CogLangExpr]":
        import janus_swi

        # Share anon_counter across both sides so each occurrence of _ gets a
        # distinct Prolog variable name (e.g. _Anon1 in pattern, _Anon2 in target).
        _anon: list[int] = [0]
        pattern_str = _coglang_to_prolog_str(pattern, _anon)
        target_str = _coglang_to_prolog_str(target, _anon)
        goal = f"unify_with_occurs_check({pattern_str}, {target_str})"

        try:
            result = janus_swi.query_once(goal)
        except Exception:
            # Unexpected Prolog exception → treat as unification failure
            return CogLangExpr("NotFound", ())

        if not result.get('truth', False):
            return CogLangExpr("NotFound", ())

        # Exclude 'truth' metadata and anonymous-var placeholders (keys starting
        # with '_' are not emitted by janus per SWI-Prolog convention, but filter
        # defensively in case future janus versions change behaviour).
        bindings: dict = {
            k: v
            for k, v in result.items()
            if k != 'truth' and not k.startswith('_')
        }
        return bindings


# ---------------------------------------------------------------------------
# Fallback backend: pure-Python Robinson unification
# ---------------------------------------------------------------------------

class PythonUnifyBackend(UnifyBackend):
    """Pure-Python Robinson unification with occurs check.

    Fallback when janus-swi is unavailable. Produces the same return format
    as JanusUnifyBackend so the executor is backend-agnostic (SCC-U5).
    """

    def unify(self, pattern: Any, target: Any) -> "Union[dict, CogLangExpr]":
        result = _python_unify(pattern, target)
        if result is None:
            return CogLangExpr("NotFound", ())
        return result


# ---------------------------------------------------------------------------
# Factory function (with safe subprocess probe)
# ---------------------------------------------------------------------------

# TD-003:
#   janus-swi 1.5.2 was compiled against SWI-Prolog 9.x ABI.
#   The installed SWI-Prolog 10.0.2 has ABI swipl-abi-2-68-*, which causes
#   _swipl.initialize() to call C-level exit() — uncatchable by Python's
#   try/except.  A subprocess probe is the only safe detection method.
#   Fix: rebuild janus-swi from source against the installed SWI-Prolog headers
#   before enabling Janus.

_JANUS_AVAILABLE_CACHE: "bool | None" = None


def _janus_available() -> bool:
    """Return True if janus-swi can initialize without crashing the process.

    janus-swi initialization failure triggers a C-level exit() that cannot be
    caught by Python's exception handling.  We probe in a subprocess so that
    a crash there does not kill the calling process.  Result is cached after
    the first call.
    """
    global _JANUS_AVAILABLE_CACHE
    if _JANUS_AVAILABLE_CACHE is None:
        import subprocess
        import sys
        try:
            result = subprocess.run(
                [sys.executable, '-c',
                 'import janus_swi; print("ok")'],
                capture_output=True,
                timeout=10,
            )
            _JANUS_AVAILABLE_CACHE = (
                result.returncode == 0 and b'ok' in result.stdout
            )
        except Exception:
            _JANUS_AVAILABLE_CACHE = False
    return _JANUS_AVAILABLE_CACHE


def get_unify_backend() -> UnifyBackend:
    """Return the best available UnifyBackend.

    Probes janus-swi in a subprocess first (safe against C-level exit on
    ABI mismatch — see TD-003).  Falls back to PythonUnifyBackend when janus
    is unavailable.
    """
    if _janus_available():
        return JanusUnifyBackend()
    warnings.warn(
        "janus-swi not available (see TD-003); using PythonUnifyBackend. "
        "Fix: rebuild janus-swi against SWI-Prolog 10.0.2 before enabling the optional Janus backend.",
        RuntimeWarning,
        stacklevel=2,
    )
    return PythonUnifyBackend()
