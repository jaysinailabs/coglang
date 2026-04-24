# CogLang M-expression parser and canonical serializer.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union


# ---------------------------------------------------------------------------
# AST node types (CogLang Specification v1.0.2, §3.2)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CogLangVar:
    """A CogLang variable.

    Examples:
        X_   → CogLangVar(name="X", is_anonymous=False)
        x_   → CogLangVar(name="x", is_anonymous=False)
        _    → CogLangVar(name="_", is_anonymous=True)

    Anonymous variable contract:
        When is_anonymous=True, name is set to "_" as a sentinel.  Downstream
        code (executor, unify backend) MUST use is_anonymous to test anonymity,
        never name == "_".  Reason: a named variable literally called "_" is
        syntactically disallowed by the spec (bare "_" is always the anon var),
        but nothing in the type system prevents constructing one manually.
        Relying on is_anonymous avoids this subtle equality trap.
    """
    name: str          # Without trailing '_' (except anonymous where name == "_")
    is_anonymous: bool  # True only when original token was bare "_"


@dataclass(frozen=True)
class CogLangExpr:
    """A CogLang M-expression node.

    Examples:
        Traverse["Einstein", "born_in"]
        → CogLangExpr(head="Traverse", args=("Einstein", "born_in"))

        NotFound[]
        → CogLangExpr(head="NotFound", args=())

    Notes:
        - args is always a tuple (frozen=True requires hashable structure).
        - If args contains a dict, the whole expr is unhashable (dicts are
          unhashable), but immutability protection still applies.
        - partial is only used for ParseError nodes; stored at construction
          time (cannot assign post-construction due to frozen=True).
    """
    head: str
    args: tuple
    partial: "CogLangExpr | None" = None

    def __post_init__(self):
        # Enforce args as tuple regardless of what caller passes (list, generator, etc).
        # frozen=True prevents direct assignment; object.__setattr__ bypasses the freeze.
        # Rationale: spec §3.5 伪代码全程用 list 构造 CogLangExpr；若不强制转换，
        # CogLangExpr("List", ["Ulm"]) != CogLangExpr("List", ("Ulm",)) 导致静默失败。
        object.__setattr__(self, "args", tuple(self.args))


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def _tokenize(s: str) -> list[str]:
    """Split a CogLang M-expression string into tokens.

    Tokens: double-quoted strings (with escapes), '[', ']', ',', '{', '}',
    ':', and bare identifier/number/symbol tokens. Whitespace is skipped.
    Quoted strings are returned WITH their surrounding double-quotes so
    _parse_tokens can distinguish them from bare identifiers.
    """
    tokens: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c in ' \t\r\n':
            i += 1
        elif c in '[],:{}':
            tokens.append(c)
            i += 1
        elif c == '"':
            # Quoted string — consume until unescaped closing quote.
            j = i + 1
            while j < n:
                if s[j] == '\\':
                    j += 2  # skip escaped character
                elif s[j] == '"':
                    j += 1
                    break
                else:
                    j += 1
            tokens.append(s[i:j])
            i = j
        else:
            # Bare token: identifier, number, '_', or sign prefix for numbers.
            j = i
            while j < n and s[j] not in ' \t\r\n[],:{}\"':
                j += 1
            tokens.append(s[i:j])
            i = j
    return tokens


# ---------------------------------------------------------------------------
# Recursive-descent parser
# ---------------------------------------------------------------------------

def _parse_dict(tokens: list[str], pos: int) -> tuple[dict, int]:
    """Parse a dict literal  { "key": value, ... }  starting at pos (after '{').

    Dict values are limited to: string, number, True[], False[]
    (per CogLang Specification §3.2 dict_lit grammar).
    Returns (dict, new_pos) where new_pos points past the closing '}'.
    """
    result: dict = {}
    # pos is right after '{'
    while pos < len(tokens) and tokens[pos] != '}':
        # Expect a quoted-string key
        if not tokens[pos].startswith('"'):
            raise _ParseFailure(f"dict key must be a quoted string, got {tokens[pos]!r}", pos)
        key = _unquote(tokens[pos])
        pos += 1
        if pos >= len(tokens) or tokens[pos] != ':':
            raise _ParseFailure("expected ':' after dict key", pos)
        pos += 1  # skip ':'
        value, pos = _parse_tokens(tokens, pos)
        result[key] = value
        if pos < len(tokens) and tokens[pos] == ',':
            pos += 1  # skip ','
    if pos >= len(tokens):
        raise _ParseFailure("unclosed dict literal '{'", pos)
    pos += 1  # skip '}'
    return result, pos


def _unquote(token: str) -> str:
    """Convert a quoted-string token  "hello \"world\""  to a Python str.

    INTERNAL USE ONLY — assumes token was produced by _tokenize().
    _tokenize() guarantees that escape sequences are well-formed (no
    truncated backslash at end-of-string) and that the only escape sequences
    present are \\" and \\\\.  The two-pass replace is correct ONLY under
    that assumption: replacing \\" → " first, then \\\\ → \\ cannot produce
    spurious results because _tokenize() never emits \\\\" in the token.

    Do NOT call _unquote() on arbitrary strings from external sources — use
    a proper single-scan decoder instead to avoid O(n²) and correctness issues.
    """
    inner = token[1:-1]
    return inner.replace('\\"', '"').replace('\\\\', '\\')


class _ParseFailure(Exception):
    """Internal exception carrying a reason string and position."""
    def __init__(self, reason: str, pos: int, partial: "CogLangExpr | None" = None):
        super().__init__(reason)
        self.reason = reason
        self.pos = pos
        self.partial = partial


def _parse_tokens(tokens: list[str], pos: int) -> tuple[Any, int]:
    """Recursive-descent parser over a token list.

    Returns (node, new_pos).

    Ambiguity resolution rules (priority 1→4, CogLang Specification §3.2):
      1. token == "_"                     → CogLangVar(is_anonymous=True)
      2. token ends with "_", len > 1     → CogLangVar(is_anonymous=False)
      3. next token is "["                → parse as Head[arglist]
      4. otherwise                        → const_atom or number or string
    """
    if pos >= len(tokens):
        raise _ParseFailure("unexpected end of input", pos)

    token = tokens[pos]

    # --- Quoted string ---
    if token.startswith('"'):
        return _unquote(token), pos + 1

    # --- Dict literal ---
    if token == '{':
        return _parse_dict(tokens, pos + 1)

    # --- Rule 1: anonymous variable ---
    if token == '_':
        return CogLangVar(name="_", is_anonymous=True), pos + 1

    # --- Rule 2: named variable (ends with '_', length > 1) ---
    if token.endswith('_') and len(token) > 1:
        return CogLangVar(name=token[:-1], is_anonymous=False), pos + 1

    # --- Number: integer or float (may start with '-') ---
    if token.lstrip('-').replace('.', '', 1).isdigit() and token not in ('', '-', '.'):
        try:
            if '.' in token:
                return float(token), pos + 1
            else:
                return int(token), pos + 1
        except ValueError:
            pass  # fall through to head/atom logic

    # --- Rule 3: followed by '[' → head expression ---
    if pos + 1 < len(tokens) and tokens[pos + 1] == '[':
        head = token
        pos += 2  # skip head and '['
        args: list = []
        while pos < len(tokens) and tokens[pos] != ']':
            arg, pos = _parse_tokens(tokens, pos)
            args.append(arg)
            if pos < len(tokens) and tokens[pos] == ',':
                pos += 1  # skip ','
        if pos >= len(tokens):
            raise _ParseFailure(
                "unclosed_bracket",
                pos,
                partial=CogLangExpr(head, tuple(args)),
            )
        pos += 1  # skip ']'
        return CogLangExpr(head, tuple(args)), pos

    # --- Rule 4: const_atom (bare identifier or zero-arg head) ---
    # A bare token like "NotFound" (no following '[') is a const_atom;
    # per spec it is equivalent to NotFound[] → treated as head with no args.
    # But only if it looks like a valid PascalCase/identifier head.
    # For truly bare lowercase atoms (e.g. 'a', 'b' in Unify patterns) we
    # return the string as-is (const_atom).
    return token, pos + 1


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(s: str) -> CogLangExpr:
    """Parse a CogLang M-expression string into an AST.

    On success returns a CogLangExpr.
    On failure returns CogLangExpr("ParseError", (reason, pos), partial=...).

    Examples:
        parse('Traverse["Einstein", "born_in"]')
        → CogLangExpr("Traverse", ("Einstein", "born_in"))

        parse('ForEach[List[], x_, Get[x_, "name"]]')
        → CogLangExpr("ForEach", (
              CogLangExpr("List", ()),
              CogLangVar(name="x", is_anonymous=False),
              CogLangExpr("Get", (CogLangVar("x", False), "name"))
          ))
    """
    try:
        tokens = _tokenize(s)
        if not tokens:
            return CogLangExpr("ParseError", ("empty_input", 0))
        node, pos = _parse_tokens(tokens, 0)
        if pos != len(tokens):
            return CogLangExpr(
                "ParseError",
                ("trailing_tokens", pos),
                partial=node if isinstance(node, CogLangExpr) else None,
            )
        # Top-level must be a CogLangExpr (not a bare atom/var/literal).
        if not isinstance(node, CogLangExpr):
            # Bare atom at top level → wrap as zero-arg expression if head-like.
            if isinstance(node, str) and node[:1].isupper():
                return CogLangExpr(node, ())
            return CogLangExpr("ParseError", ("not_an_expression", 0))
        return node
    except _ParseFailure as exc:
        return CogLangExpr("ParseError", (exc.reason, exc.pos), partial=exc.partial)
    except Exception as exc:  # noqa: BLE001
        return CogLangExpr("ParseError", (str(exc), 0))


# ---------------------------------------------------------------------------
# Canonical serializer (CogLang Specification v1.0.2 §2.7 + §3.2b)
# ---------------------------------------------------------------------------

def canonicalize(expr: Union[CogLangExpr, CogLangVar, str, int, float, dict, bool]) -> str:
    """Convert a CogLang AST node to its canonical string representation.

    Rules (CogLang Specification §2.7):
    - Head[arg1, arg2] — no space between Head and [
    - Arguments separated by ", " (comma + one space)
    - Strings in double-quotes; internal " escaped as \", internal \\ as \\\\
    - Integers without decimal point (42 not 42.0)
    - Floats with repr() format for cross-platform roundtrip safety
    - Zero-arg expressions always include brackets: NotFound[], True[], False[]
    - CogLangVar: name + "_"; anonymous always outputs "_"
    - Dict keys sorted alphabetically; colon followed by one space
    - Single line, no newlines

    Roundtrip guarantee: parse(canonicalize(expr)) == expr for any valid CogLang value.

    Known limitation — dict values should be CogLang values, not raw Python bools:
        canonicalize({"active": True})  → '{"active": True[]}'
        parse('...{"active": True[]}...').args[1]  → {"active": CogLangExpr("True", ())}
        Original Python bool True ≠ CogLangExpr("True", ()) → roundtrip breaks.
    Callers creating attribute dicts must use CogLangExpr("True", ()) / CogLangExpr("False", ())
    for boolean values, not Python bool literals.  The spec (§3.2 dict_lit grammar) defines
    dict values as  string | number | True[] | False[]  where True[]/False[] are CogLang exprs.
    """
    # bool must be checked before int (bool is a subclass of int).
    if isinstance(expr, bool):
        return "True[]" if expr else "False[]"
    if isinstance(expr, CogLangVar):
        return "_" if expr.is_anonymous else f"{expr.name}_"
    if isinstance(expr, CogLangExpr):
        args_str = ", ".join(canonicalize(a) for a in expr.args)
        return f"{expr.head}[{args_str}]"
    if isinstance(expr, str):
        escaped = expr.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(expr, int):
        return str(expr)
    if isinstance(expr, float):
        return repr(expr)
    if isinstance(expr, dict):
        pairs = ", ".join(
            f'"{k}": {canonicalize(v)}' for k, v in sorted(expr.items())
        )
        return "{" + pairs + "}"
    raise TypeError(f"Cannot canonicalize: {type(expr)!r}")
