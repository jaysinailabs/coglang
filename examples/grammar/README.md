# CogLang Constrained-Generation Grammar Examples

**Status**: companion example material
**Scope**: syntax-shaped generation only, not a normative parser or semantic validator

This directory provides small grammar files for constrained generation tools:

- [coglang.lark](coglang.lark): Lark-style grammar for CogLang M-expression shape.
- [coglang.gbnf](coglang.gbnf): GBNF-style grammar for llama.cpp-compatible grammar consumers.

These files are intentionally examples. The authoritative implementation remains:

1. `coglang.parser.parse`
2. `coglang.validator.valid_coglang`
3. the public specification and conformance tests

Use the grammars to reduce malformed model output, then still parse and validate
the generated expression:

```python
from coglang.parser import parse
from coglang.validator import valid_coglang

candidate = 'Query[n_, Equal[Get[n_, "category"], "Person"]]'
expr = parse(candidate)
assert expr.head != "ParseError"
assert valid_coglang(expr)
```

The grammars describe M-expression syntax, not host policy. They do not prove
that a generated expression is safe to execute, within graph budget, or allowed
by a host capability manifest. For effect and budget checks, run:

```powershell
coglang preflight --format text 'Query[n_, Equal[Get[n_, "category"], "Person"]]'
```

## Boundary

- These files are companion constrained-generation assets.
- They are not part of the frozen `v1.1.0` language contract.
- They are not a replacement for `parse` and `valid_coglang`.
- They do not expand HRC v0.2 frozen scope.
- `Unify` and `Match` arguments remain opaque data positions; validate the
  top-level CogLang expression after generation.

## Notes For Tool Adapters

Tool-specific APIs change faster than the grammar shape. Adapters should load
one of these grammar files, generate a candidate string, and then run the
normal CogLang parser and validator before using the expression.
