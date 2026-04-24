# CogLang Conformance Suite v1.1.0

## 0. Role of This Document

This document is the companion test and example document for `CogLang_Specification_v1_1_0_Draft.md`.

Its purpose is not to replace the main specification. Its purpose is to turn the following material into executable checks:

- parser / validator test groups
- minimum pass criteria for execution / trace / render
- golden examples

## 1. Scope

This file currently serves three audiences:

- authors of the `v1.1.0` specification
- implementers of CogLang parsers / validators / executors
- future regression testing and conformance review

By default, this file covers only:

- `Core`
- the minimum frozen-signature entries in `Reserved`

It does not cover:

- the full behavior of `Experimental`
- host-internal message, storage, or training implementation details
- real network behavior of external adapters

Additional notes:

- Host-specific or adapter-specific fixture suites should be maintained as **separate companion suites** and should not be mixed into the current `Core / Reserved` conformance suite.
- Such companion suites are not part of the `Core CLI` freeze commitment.

## 2. Pass Criteria

Passing this suite does not mean that an implementation is internally identical to the reference implementation. It only means that the implementation satisfies the frozen compatibility surface through externally observable behavior.

Pass criteria are evaluated in this priority order:

1. AST / canonical text consistency
2. validator diagnostic consistency
3. semantic return-value consistency
4. trace / readable render satisfaction of the minimum field requirements

If an implementation has a different internal structure but the externally observable behavior above is consistent, it is considered conformant.

## 3. Test Groups

- `PARSER`
  Lexing, application, variables, dictionaries, and zero-arity application.
- `VALIDATOR`
  Name resolution, variable positions, arity, scope, and validator diagnostic fields.
- `EXEC`
  Success paths, boundary paths, and error paths for `Core` operators.
- `ERR`
  Default propagation of error values and explicit propagation-blocking points.
- `TRACE`
  Value transparency, minimum fields, and event types for `Trace` / `Assert`.
- `RENDER`
  Stable output for canonical text and readable render.
- `EXT`
  Registry entries, profile-specific availability, uninstalled operators, and capability failures.

## 4. Golden Examples

### GE-001 `operator head` vs `term head`

**Purpose**

Verify that lowercase structured terms are valid but do not participate in default operator resolution.

**Input**

```text
Unify[f[X_, b], f[a, Y_]]
```

**Expected**

- parser succeeds
- `f` is identified as a `term head`
- operator name resolution from `§10` is not triggered
- execution result:

```text
{"X": "a", "Y": "b"}
```

**Rationale**

This is the repair anchor for a historical inconsistency in `v1.0.2`.

### GE-002 canonical text vs readable render

**Purpose**

Verify that single-line canonical text and multi-line readable render are not the same layer of object.

**Input AST**

```text
ForEach[
  Query[n_, Equal[Get[n_, "category"], "Person"]],
  p_,
  Do[
    Trace[Traverse[p_, "born_in"]],
    Update[p_, {"visited": True[]}]
  ]
]
```

**Expected**

- canonical text:

```text
ForEach[Query[n_, Equal[Get[n_, "category"], "Person"]], p_, Do[Trace[Traverse[p_, "born_in"]], Update[p_, {"visited": True[]}]]]
```

- readable render may use multi-line indentation
- both round-trip to the same AST

**Rationale**

Prevents the display layer from being treated as the semantic layer.

Additional note:

- The `category` field in this example group is only an example business field. It does not freeze a unified business classification key name for `v1.1.0`.

### GE-003 Basic success path for `Query`

**Precondition Graph**

- `einstein`, `type = Entity`, `category = "Person"`, `confidence = 1.0`
- `tesla`, `type = Entity`, `category = "Person"`, `confidence = 1.0`
- `ulm`, `type = Entity`, `category = "City"`, `confidence = 1.0`

**Input**

```text
Query[n_, Equal[Get[n_, "category"], "Person"]]
```

**Expected**

```text
List["einstein", "tesla"]
```

The return order is stably sorted by canonical node ID.

Additional note:

- This example uses `category` only to avoid conflicting with the public primary node `type`. It does not mean that the business classification field name is frozen.

### GE-004 Minimum semantics of `Query.k`

**Precondition Graph**

- `einstein`, `type = Entity`, `category = "Person"`, `confidence = 1.0`

**Input A**

```text
Query[n_, Equal[Get[n_, "category"], "Person"]]
```

**Input B**

```text
Query[n_, Equal[Get[n_, "category"], "Person"], {"k": 0, "mode": "default"}]
```

**Input C**

```text
Query[n_, Equal[Get[n_, "category"], "Person"], {"k": 2, "mode": "default"}]
```

**Input D**

```text
Query[n_, Equal[Get[n_, "category"], "Person"], {"k": 1, "mode": 7}]
```

**Expected**

- A/B/C all succeed
- all three result sets are identical:

```text
List["einstein"]
```

- D returns:

```text
TypeError["Query", "mode", ...]
```

**Rationale**

Locks down the default two-argument form, the independent semantics of `k`, and the dynamic type constraint on `mode`.

### GE-005 `Abstract` only extracts and triggers prototypes

**Input**

```text
Abstract[List["case_a", "case_b", "case_c"]]
```

**Expected**

Returns a structured summary object with at least:

```text
{
  "cluster_id": ...,
  "instance_count": 3,
  "prototype_ref": ...,
  "equivalence_class_ref": ...,
  "selection_basis": ...,
  "triggered": True[] | False[]
}
```

It also satisfies:

- does not directly return a rule object
- does not directly write to the primary graph
- does not replace `Encoder -> Logic Engine -> draft/promote`

### GE-006 Value transparency of `Trace`

**Input**

```text
Trace[Traverse["einstein", "born_in"]]
```

**Expected**

- the semantic return value is exactly identical to direct execution of `Traverse["einstein", "born_in"]`
- trace records at least:
  `expr_id`
  `parent_id`
  `canonical_expr`
  `result_summary`
  `duration_ms`
  `effect_class`

### GE-007 Non-fatal semantics of `Assert`

**Input**

```text
Do[
  Assert[False[], "missing invariant"],
  "continued"
]
```

**Expected**

- does not throw a host exception
- does not convert to a CogLang runtime error
- returns:

```text
"continued"
```

- a structured assertion / anomaly event appears in trace / observer output
- the event can be traced back at least to:
  `condition = False[]`
  `message = "missing invariant"`
  `passed = False[]`

### GE-008 `ParseError` and `partial_ast`

**Input**

```text
Traverse["Einstein",
```

**Expected**

- returns the canonical error expression:

```text
ParseError["unclosed_bracket", position]
```

- the diagnostic object or transport envelope exposes `partial_ast` or `partial_ast_ref`
- `partial_ast` points to the recovered `Traverse[...]` prefix structure

### GE-009 Unresolved name is not `ParseError`

**Input**

```text
NoSuchOperator["x"]
```

**Expected**

- parser succeeds
- validator fails
- diagnostic fields include at least:
  `head`
  `attempted_resolution_scopes`
  `source_span`
  `diagnostic_code`
- this issue is not represented as `ParseError[...]`

### GE-010 Public labeling of the `Operation` internal artifact

**Precondition**

The implementation uses an internal `Operation` node to carry the result of `Compose`.

**Input**

```text
Compose["FindBirthplace", List[person_], Traverse[person_, "born_in"]]
```

**Expected**

- the public semantic return value contains at least:

```text
{
  "operator_name": "FindBirthplace",
  "scope": "graph-local"
}
```

- an executor-internal `Operation` carrier may be generated internally
- if the implementation also keeps an internal definition handle, it may only appear in diagnostics / transport / management interfaces and must not replace the public return contract above
- public documentation, management UI, trace, or render must not mislabel it as a public primary node type
- the public knowledge-node type terminology remains:
  `Entity / Concept / Rule / Meta`

### GE-011 Sole source of public node `type` in `Create`

**Input A**

```text
Create["Entity", {"id": "tesla_01", "label": "Tesla"}]
```

**Input B**

```text
Create["Entity", {"id": "tesla_02", "type": "Person"}]
```

**Expected**

- A succeeds and returns:

```text
"tesla_01"
```

- B returns:

```text
TypeError["Create", "attrs", ...]
```

- for the node created by A, the public primary type must be `Entity`
- `attrs["type"]` must not continue to be used as a business classification field

### GE-012 Edge call-surface alias and public return value

**Precondition Graph**

- `einstein` exists and is visible
- `ulm` exists and is visible

**Input**

```text
Create["Edge", {"from": "einstein", "to": "ulm", "relation_type": "born_in"}]
```

**Expected**

- succeeds and returns:

```text
List["einstein", "born_in", "ulm"]
```

- the implementation may internally map this to `source_id / target_id / relation`
- this internal naming difference must not change the public call surface or return semantics

### GE-013 Structural equality for `Equal`

**Input A**

```text
Equal[f[a, b], f[a, b]]
```

**Input B**

```text
Equal[f[a, b], f[a, c]]
```

**Expected**

- A returns:

```text
True[]
```

- B returns:

```text
False[]
```

- `f` must be handled as a `term head` and must not trigger name resolution from `§10`
- comparison is based on structural equality, not wrapper objects or render-text equality

### GE-014 Minimum delta schema for `Compare`

**Input A**

```text
Compare["hello", "hello"]
```

**Input B**

```text
Compare[f[a, b], f[a, c]]
```

**Expected**

- A returns:

```text
{}
```

- B returns:

```text
{"arg1": {"expected": "b", "actual": "c"}}
```

- differences in application argument positions must use `argN` names
- equality must return an empty dictionary, not another empty value

### GE-015 Same-name variable consistency in `Unify`

**Input A**

```text
Unify[f[X_, X_], f[a, a]]
```

**Input B**

```text
Unify[f[X_, X_], f[a, b]]
```

**Expected**

- A returns:

```text
{"X": "a"}
```

- B returns:

```text
NotFound[]
```

- same-name named variables must represent the same logical variable

### GE-016 Structural matching of error values in `Unify`

**Input**

```text
Unify[TypeError[X_, _, _, _], TypeError["Get", "source", "expected dict/List/string", 7]]
```

**Expected**

```text
{"X": "Get"}
```

Additional requirements:

- `TypeError[...]` is a normal target term that can be structurally matched in `Unify`
- it must not automatically propagate outward again merely because it is an error value

### GE-017 `Match` is an exact alias of `Unify`

**Input A**

```text
Match[f[X_, b], f[a, Y_]]
```

**Input B**

```text
Unify[f[X_, b], f[a, Y_]]
```

**Expected**

- A returns:

```text
{"X": "a", "Y": "b"}
```

- B returns:

```text
{"X": "a", "Y": "b"}
```

- the parser / validator / execution observable results of both forms must be identical

### GE-018 Default stub for `Explain` in `Baseline`

**Preconditions**

- the current implementation declares support for `Baseline`
- it does not additionally declare an enhanced implementation of `Explain`

**Input**

```text
Explain[Query[n_, True[]]]
```

**Expected**

- returns:

```text
StubError["Explain", ...]
```

- the call must not be degraded into an unresolved name
- the call must not masquerade as `ParseError[...]`
- at least one `meta` or `stub` event is left behind

**Rationale**

Locks down the minimum behavior for `Reserved` entries whose signatures are frozen while the default baseline may use stubs.

### GE-019 Capability denied for an extension-backed operator

**Preconditions**

- the runtime registry contains an entry for `ExtFetch[uri]`
- the entry name has been resolved
- the entry requires the `external_io` capability
- the current manifest has not granted `external_io`

**Input**

```text
ExtFetch["dummy://resource"]
```

**Expected**

- returns:

```text
PermissionError["ExtFetch", "external_io"]
```

- must not fall back to unresolved name
- must not return `ParseError[...]`
- must not actually attempt to access the external resource
- trace / diagnostics should show a capability-denied event

**Rationale**

Locks down the failure shape for "name resolved but capability insufficient" and prevents it from being confused with uninstalled implementations or unresolved names.

### GE-020 Name resolved but implementation not installed

**Preconditions**

- the runtime registry contains metadata for an `ExtRank[input]` entry
- name resolution can hit that entry
- the corresponding execution implementation is not installed or is currently unavailable

**Input**

```text
ExtRank["sample"]
```

**Expected**

- returns:

```text
StubError["ExtRank", "operator_unavailable"]
```

- must not be classified as an unresolved name
- must not be classified as `ParseError[...]`
- this path must be distinguishable from the "not resolved at all" case in `GE-009`

**Rationale**

Locks down the minimum failure behavior for an extension-backed operator when it is resolved but not executable.

### GE-021 `If` handling of auto-propagating error values in the condition branch

**Input**

```text
If[Get[1, "type"], "then", "else"]
```

**Expected**

- returns:

```text
"else"
```

- the auto-propagating error value produced in `condition` must not keep auto-propagating outward
- trace must distinguish `condition_result_kind = error` from `branch_taken = else`

**Rationale**

Locks down the semantic boundary most likely to drift in automated systems: error values are treated as false values in `If`, but this is not the same as silently swallowing trace.

### GE-022 `IfFound` dispatch for `NotFound[]`, error values, and `List[]`

**Input A**

```text
IfFound[NotFound[], x_, x_, "fallback"]
```

**Expected A**

- returns `"fallback"`

**Input B**

```text
IfFound[List[], x_, x_, "fallback"]
```

**Expected B**

- returns `List[]`

**Rationale**

Locks down the layering between `IfFound` and `If`: `NotFound[]` and auto-propagating error values enter `else`, while `List[]` is not an error value.

### GE-023 Stable mapping and result preservation in `ForEach`

**Input**

```text
ForEach[List["a", "b"], x_, Equal[x_, x_]]
```

**Expected**

- returns:

```text
List[True[], True[]]
```

- result order must match the input snapshot order
- trace must show a snapshot size of `2`

**Rationale**

Locks down the minimum stability of `ForEach`: one evaluation snapshot, item-by-item mapping, and no order drift.

### GE-024 Sequential execution and non-automatic abort in `Do`

**Input**

```text
Do[
  Get[1, "type"],
  Trace["still_runs"]
]
```

**Expected**

- returns:

```text
"still_runs"
```

- the return value of `Do` must be the result of the last executed subexpression, not an aggregation of all step results
- the error value produced by the first subexpression must not automatically abort the second subexpression
- trace must show that both steps were executed

**Rationale**

Locks down the boundary in `Do` that implementers are most likely to accidentally "fix" into exception-style interruption.

### GE-025 Default stub for `Inspect` in `Baseline`

**Input**

```text
Inspect["einstein"]
```

**Expected**

- returns:

```text
StubError["Inspect", "einstein"]
```

- trace must leave a `stub` or `meta` class event
- the `Inspect` stub must not trigger a graph write

**Rationale**

Locks down the minimum reliability of `Inspect` as a `Reserved` entry: signature freeze, default failure-shape freeze, and observability requirement freeze.

### GE-026 Bind-and-continue idiom for `IfFound`

**Input**

```text
IfFound[
  Get["einstein", "label"],
  label_,
  List[label_, Equal[label_, "Einstein"]],
  "missing"
]
```

**Expected**

- returns:

```text
List["Einstein", True[]]
```

- the result of `Get["einstein", "label"]` must be bound to `label_`
- `thenExpr` must be evaluated only when binding succeeds
- trace must show `branch_taken = then`

**Rationale**

Locks down `IfFound` as the official bind-and-continue idiom in current `v1.1.0` without changing the no-between-step-binding semantics of `Do`.

### GE-027 Visibility and stable order of `AllNodes`

**Precondition Graph**

- `einstein`, `type = Entity`, `confidence = 1.0`
- `tesla`, `type = Entity`, `confidence = 1.0`
- `ghost`, `type = Entity`, `confidence = 0`

**Input**

```text
AllNodes[]
```

**Expected**

```text
List["einstein", "tesla"]
```

- the result must not contain `ghost`
- result order must be stable; by default it is ascending by canonical node ID

**Rationale**

Locks down the default visibility and stable sorting of `AllNodes`, avoiding implementations that re-expose soft-deleted / hidden nodes.

### GE-028 Success path of `Update` and rejection of `confidence = 0`

**Precondition Graph**

- `einstein`, `type = Entity`, `label = "Einstein"`, `confidence = 1.0`

**Input A**

```text
Update["einstein", {"label": "Albert Einstein"}]
```

**Expected A**

- returns:

```text
True[]
```

- subsequent execution of:

```text
Get["einstein", "label"]
```

  must return:

```text
"Albert Einstein"
```

**Input B**

```text
Update["einstein", {"confidence": 0}]
```

**Expected B**

- returns:

```text
TypeError["Update", "changes", "use Delete for soft-delete", ...]
```

**Rationale**

Locks down both the normal field-overwrite path of `Update` and the hard boundary that `confidence = 0` must not be used to simulate deletion.

### GE-029 Soft-delete and idempotence of `Delete`

**Precondition Graph**

- `tesla`, `type = Entity`, `confidence = 1.0`

**Input A**

```text
Delete["tesla"]
```

**Expected A**

- returns:

```text
"tesla"
```

**Input B**

```text
Delete["tesla"]
```

**Expected B**

- returns:

```text
NotFound[]
```

- subsequent execution of:

```text
AllNodes[]
```

  must no longer contain `tesla`

**Rationale**

Locks down the soft-delete semantics, idempotence, and default visibility consequences of `Delete`.

### GE-030 Result preservation for body errors in `ForEach`

**Input**

```text
ForEach[List["einstein", "missing"], x_, Get[x_, "label"]]
```

**Expected**

- returns:

```text
List["Einstein", NotFound[]]
```

- `NotFound[]` in the second position must be preserved in the result list
- the first successful item must not be erased because the second item is missing
- the full iteration must not abort early

**Rationale**

Locks down the "preserve per-item results" semantics of `ForEach`, avoiding implementations that convert body errors back into global failure.

### GE-031 Three-way dispatch for `Get`: `Dict / List / node_attr`

**Input A**

```text
Get[{"name": "Einstein"}, "name"]
```

**Expected A**

```text
"Einstein"
```

**Input B**

```text
Get[List["a", "b"], 1]
```

**Expected B**

```text
"b"
```

**Input C**

```text
Get["einstein", "label"]
```

**Expected C**

```text
"Einstein"
```

**Input D**

```text
Get[List["a"], "name"]
```

**Expected D**

```text
TypeError["Get", "key", ...]
```

**Rationale**

Locks down the three-way runtime dispatch of `Get`, `0-based` list indexing, and the error semantics of validating the key type only after dispatch is determined.

### GE-032 Unique allocation and return consistency for default IDs in `Create`

**Precondition Graph**

- `einstein` exists and is visible

**Input**

```text
IfFound[
  Create["Entity", {"label": "Dog"}],
  dog_id_,
  Create["Edge", {"from": "einstein", "to": dog_id_, "relation_type": "knows"}],
  False[]
]
```

**Expected**

- the whole expression succeeds
- the final return value is:

```text
List["einstein", "knows", "<allocated_id>"]
```

- `<allocated_id>` must be the unique ID allocated to the node created in this execution
- that ID must remain consistent across the language-level node return value, later references inside the same expression, and the internal write candidate
- the implementation must not delay allocating and backfilling that ID until after persistent commit succeeds

**Rationale**

Locks down the frozen semantics of `Create` when `attrs.id` is missing: the unique ID must be allocated before the internal write request is formed, and it becomes the shared identifier for later references in the same expression.

### GE-033 Alias normalization in `Create["Edge", ...]` occurs before internal reference validation

**Precondition Graph**

- `einstein` exists and is visible

**Input**

```text
Do[
  Create["Entity", {"id": "dog_1", "label": "Dog"}],
  Create["Edge", {"from": "einstein", "to": "dog_1", "relation_type": "knows"}]
]
```

**Expected**

- the whole expression succeeds
- the final return value is the result of the last step:

```text
List["einstein", "knows", "dog_1"]
```

- if the implementation has internal field mapping, key normalization, or an equivalent call-surface conversion step, these steps must occur before any internal reference-consistency check, host commit validation, or local referential-integrity check
- the public freeze is the timing constraint that "mapping occurs before any internal reference-consistency check", not any particular host-internal field name or bridge-object implementation
- behavior where the public call surface is valid but fails only because the implementation has not yet completed call-surface normalization is not allowed

**Rationale**

Locks down the timing constraint between edge call-surface aliases and internal commit objects, preventing implementations from performing field mapping too late and breaking local reference consistency.

## 5. Minimum Regression Set

After each specification change, at least the following examples should be regressed:

- `GE-001`
- `GE-002`
- `GE-003`
- `GE-004`
- `GE-005`
- `GE-006`
- `GE-007`
- `GE-008`
- `GE-009`
- `GE-010`
- `GE-011`
- `GE-012`
- `GE-013`
- `GE-014`
- `GE-015`
- `GE-016`
- `GE-017`
- `GE-018`
- `GE-019`
- `GE-020`
- `GE-021`
- `GE-022`
- `GE-023`
- `GE-024`
- `GE-025`
- `GE-026`
- `GE-027`
- `GE-028`
- `GE-029`
- `GE-030`
- `GE-031`
- `GE-032`
- `GE-033`

## 6. Extension Notes

This file will continue to grow as `v1.1.0` converges, but the growth principle should stay restrained:

- prefer examples that prove semantic boundaries
- do not pile up many similar examples to create an illusion of coverage
- do not write host-internal implementation details into golden examples
