# CogLang Readable Render Golden Example Candidates v0.1

**Status**: public governance note
**Scope**: candidate golden examples for a future readable render subsystem
**Audience**: maintainers, contributors, tooling authors, UI authors, and reviewers
**Non-goal**: implementing `to_readable()`, freezing a renderer API, or changing canonical text, parser, validator, executor, or transport behavior

---

## 0. How To Read This Document

`CogLang_Readable_Render_Boundary_v0_1.md` records the current boundary:
canonical text is the machine-facing stability anchor, readable rendering is a
human-facing display layer, and transport envelopes remain structured host data.

This document is the next step after that boundary note. It records candidate
golden examples that a future readable renderer can use as review input. These
examples are intentionally not an implementation promise.

This document does not:

- add a public renderer function
- add a CLI command or `--format readable`
- require readable text to be parseable
- change `canonicalize`
- change conformance pass criteria
- change HRC or write-bundle envelope semantics

Until a future implementation PR promotes a renderer API and tests, the only
stable text output remains canonical text.

---

## 1. Candidate Example Rules

Every candidate example in this note keeps three layers separate:

1. **AST / value shape**: the semantic object or expression being displayed.
2. **Canonical text**: the stable one-line text form used for replay, hashing,
   tests, and machine exchange.
3. **Readable render candidate**: an illustrative display shape for human
   review.

Readable render candidates in this note should be read as example expectations
for future design review, not as output produced by the current package.

Future renderer work may adjust the exact layout, but it must preserve the
invariants named here.

---

## 2. Candidate Examples

### RRG-001 Compact Expression May Stay Compact

**Purpose**

Show that readable rendering does not need to expand every expression.

**Canonical text**

```text
Equal[Get["ada", "category"], "Person"]
```

**Readable render candidate**

```text
Equal[Get["ada", "category"], "Person"]
```

**Invariants**

- The head `Equal` remains visible.
- Argument order is unchanged.
- The nested `Get[...]` call remains visible.
- The display does not imply a different comparison rule from the canonical
  expression.

### RRG-002 Multiline Display Is Not Canonical Text

**Purpose**

Make the `GE-002` conformance-suite theme concrete: canonical text and readable
render are different layers.

**Canonical text**

```text
ForEach[Query[n_, Equal[Get[n_, "category"], "Person"]], p_, Do[Trace[Traverse[p_, "born_in"]], Update[p_, {"visited": True[]}]]]
```

**Readable render candidate**

```text
ForEach[
  Query[
    n_,
    Equal[
      Get[n_, "category"],
      "Person"
    ]
  ],
  p_,
  Do[
    Trace[Traverse[p_, "born_in"]],
    Update[p_, {"visited": True[]}]
  ]
]
```

**Invariants**

- The display is allowed to use newlines and indentation.
- The display remains traceable to the same expression tree.
- The display must not become the only stored representation.
- A future renderer must not require transport consumers to parse this display
  text to recover machine data.

### RRG-003 Dictionaries Keep Stable Field Visibility

**Purpose**

Show that readable rendering must not hide dictionary fields or reorder them in
an unstable way.

**Canonical text**

```text
Update["ada", {"active": True[], "rank": 1}]
```

**Readable render candidate**

```text
Update[
  "ada",
  {
    "active": True[],
    "rank": 1
  }
]
```

**Invariants**

- Both dictionary fields remain visible.
- Field order is stable.
- Boolean values remain explicit CogLang boolean expressions.
- The display does not imply a host persistence result.

### RRG-004 Error Expressions Keep The Error Head

**Purpose**

Show that readable rendering of error values should preserve the error category
and key arguments.

**Canonical text**

```text
StubError["Send", "not implemented"]
```

**Readable render candidate**

```text
StubError[
  "Send",
  "not implemented"
]
```

**Invariants**

- The error head remains visible.
- Key arguments are not dropped or replaced by prose.
- The display does not turn an error value into a host exception.
- Additional UI annotations may be shown outside the render, but they must not
  overwrite the canonical error value.

### RRG-005 Transport Views Keep Structured Data Separate

**Purpose**

Show the expected split when a future host or UI wants to show both machine data
and human-readable display.

**Canonical text**

```text
Create["Entity", {"category": "Person", "label": "Ada"}]
```

**Readable render candidate**

```text
Create[
  "Entity",
  {
    "category": "Person",
    "label": "Ada"
  }
]
```

**Transport expectation**

If a future host-visible envelope carries a readable render, that render should
be auxiliary display data. The envelope should still preserve structured fields
and canonical text or a reference to canonical text.

**Invariants**

- The readable render is not the transport serialization.
- Machine consumers should use structured envelope fields.
- Human review can show readable render next to canonical text.
- HRC v0.2 is not expanded by this example.

---

## 3. Future Promotion Tests

A future renderer implementation should add tests that prove:

- each candidate example has the expected canonical text before rendering
- readable output is stable for the selected renderer profile
- rendering does not mutate the AST or value object
- `parse(canonicalize(expr)) == expr` still holds for supported values
- CLI default output remains canonical text unless a future public readable mode
  is explicitly added
- transport envelopes do not depend on parsing readable text

Those tests should live beside parser/CLI/transport tests according to the
surface being promoted. This document alone does not create those tests.

---

## 4. Claims To Avoid

Do not use this document to claim that:

- `to_readable()` exists
- `coglang render` exists
- `--format readable` exists
- readable output is stable release data today
- readable output is always parseable
- readable output can replace canonical text in machine paths
- HRC v0.2 includes readable-render transport semantics

Those claims require implementation, tests, release notes, and explicit public
surface promotion.

---

## 5. Review Use

This note is useful when reviewing future renderer work because it gives
maintainers concrete display shapes and invariants to compare against. A future
renderer PR should either satisfy these examples or explain why a different
stable layout is better before it changes public documentation.

The governing priority remains:

1. canonical text and structured data are authoritative for machines
2. readable render is for human inspection
3. transport envelopes stay structured
4. UI conveniences must remain traceable back to canonical text or structured
   values
