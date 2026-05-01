# CogLang Reserved Operator Promotion Criteria v0.1

**Status**: public governance note
**Scope**: evidence required before `Carry-forward`, `Reserved`, or `Experimental` entries can move toward a more stable surface
**Audience**: maintainers, contributors, implementers, and reviewers evaluating operator-surface changes

---

## 0. How To Read This Document

This document explains the evidence bar for promoting non-Core operator
surfaces. It does not add a new operator, change `v1.1.0` Core semantics, or
make any `Reserved / Experimental` entry available by default.

The authoritative semantic source remains
`CogLang_Specification_v1_1_0_Draft.md`. The operator catalog remains the
status index. This note records the review discipline that should sit between
roadmap interest and a specification change.

Promotion is allowed only when the evidence is public, reproducible, and narrow
enough to preserve the existing compatibility story:

- canonical M-expression text remains the stability anchor
- errors remain explicit values
- `Enhanced` does not rewrite `Baseline` or `Core`
- host-specific behavior stays behind profiles, capabilities, examples, or
  host contracts unless it is deliberately promoted through specification and
  conformance work

---

## 1. Current Non-Core Buckets

The current catalog has three non-Core buckets that need different treatment.

| Bucket | Meaning | Default action without enough evidence |
| --- | --- | --- |
| `Carry-forward` | A legacy or transitional entry has not yet been rewritten into the current `v1.1.0` template. | Rewrite, explicitly downgrade to `Reserved`, or remove ambiguity before it becomes permanent. |
| `Reserved` | A name, direction, signature, or bridge point is held for future work, but default execution is not required. | Keep `StubError[...]`, profile-specific availability, or implementation-defined behavior explicit. |
| `Experimental` | A high-risk or immature direction exists only as exploratory material. | Keep outside default surfaces; normally move through `Reserved` before any stronger status. |

`Future` directions are not promotion candidates by default. They first need a
profile, extension, host-contract, or reserved entry that can be reviewed on its
own evidence.

---

## 2. Required Evidence Checklist

Every promotion proposal should include these evidence categories.

### 2.1 Candidate Scope

State:

- the exact operator or direction name
- current status and proposed target status
- target layer: `Core`, `Enhanced`, extension-backed, host-contract companion,
  or documentation-only
- whether the name is frozen
- whether the signature is frozen
- whether any schema, envelope, or readable rendering shape is still informative
  rather than contractual

### 2.2 Semantic Freeze

Define:

- normal execution behavior
- default missing-implementation behavior
- capability-denied behavior
- failure value shape
- interaction with canonical text
- interaction with existing error propagation rules
- whether the behavior depends on host state, external I/O, cross-instance
  messaging, or self-modification

If the proposal cannot write these fields without implementation-specific
language, it should not move into `Core`.

### 2.3 Profile And Availability Matrix

Provide a profile matrix at least as explicit as:

| Profile | Required behavior |
| --- | --- |
| `Baseline` | `normal execution`, `StubError[...]`, or `PermissionError[...]` |
| `Enhanced` | `normal execution`, `StubError[...]`, `PermissionError[...]`, or explicitly profile-specific behavior |

`Enhanced` may add availability. It must not reinterpret an omitted option,
change a `Core` default, or make existing `Baseline` behavior mean something
else.

### 2.4 Capability And Extension Contract

If the entry is capability-gated or extension-backed, document:

- stable capability strings
- denied-by-default behavior
- required manifest fields
- missing implementation error
- capability denied error
- default-enabled profiles
- whether an extension can be absent without making the implementation
  non-conformant

Permission failure must remain explicit. Silent degradation is not acceptable
evidence.

### 2.5 Conformance And Golden Examples

Promotion needs executable evidence, not only prose.

Minimum test evidence should cover:

- parse and canonicalization behavior when syntax is involved
- normal execution or the required stub/error value
- capability denied behavior
- missing implementation versus installed implementation, when extension-backed
- `Baseline` and `Enhanced` consistency for existing `Core` operators
- at least one negative case that preserves explicit error values

If the feature affects host envelopes, include host-level success and failure
examples without widening the language-core claim.

### 2.6 Host And Security Boundary

Any proposal involving cross-instance communication, external I/O, host policy,
self-inspection, self-modification, rule publishing, rollback, or adapter-specific
behavior must state:

- which behavior belongs to language semantics
- which behavior belongs to host contract or companion examples
- which identifiers or envelopes are stable
- which trace or provenance fields are required
- which security or permission failure shape is required

Unfrozen host behavior should block `Core` promotion.

### 2.7 Documentation And Release Surface

Accepted promotion work must update the public surface in a consistent order:

1. main specification or profile/host-contract document
2. conformance and regression tests
3. operator catalog
4. migration or release notes, if behavior changed
5. README, `llms.txt`, `llms-full.txt`, manifest/package data, and public extract
   assets when the new document or surface is public

The release-check surface should fail if a newly public governance or contract
document is missing from the packaged assets.

---

## 3. Status-Specific Gates

### 3.1 `Send`

`Send` is the remaining meaningful `Carry-forward` entry.

Before promotion, it needs public evidence for:

- cross-instance protocol
- default failure shape
- minimal trace requirements
- capability or permission behavior
- conformance examples for success and failure

If those boundaries remain unfrozen before the target version boundary, `Send`
should move to `Reserved` rather than stay indefinitely ambiguous.

### 3.2 `Explain`

`Explain` has a frozen name and a reserved observability role, but the plan
object schema is not frozen.

Promotion requires:

- a minimal result schema
- profile-specific availability rules
- behavior when no planner is installed
- examples proving that explanation does not change the value of the wrapped or
  analyzed expression

### 3.3 `Inspect`, Non-default `Query.mode`, And Query Cost/Gain Interfaces

These entries depend on profile, capability, and host boundaries.

Promotion requires:

- explicit profile availability
- stable capability strings where needed
- `StubError[...]` or `PermissionError[...]` behavior for unsupported paths
- evidence that ordinary default `Query[...]` behavior is unchanged
- clear separation between informative host estimates and contractual language
  values

### 3.4 Preset Shortcut Heads

`Instantiate`, `Probe`, `Explore`, `Estimate`, `Decompose`, `Defer`, `Resume`,
and `Merge` are reserved shortcut heads, not promoted Core semantics.

Promotion requires:

- a stable signature
- a defined return value or error value
- evidence that the shortcut is not only host UI convenience
- conformance cases covering both supported and unsupported behavior

### 3.5 Rule Candidate And Publish/Rollback Surfaces

Rule candidate envelopes and publish/rollback chains are bridge points for
future rule-induction workflows.

Promotion requires:

- stable envelope fields
- review and trace requirements
- rollback failure shape
- host ownership boundaries
- public examples that avoid binding a single reference host lifecycle into the
  language core

### 3.6 Qualified Extension Names

Concrete syntax for explicitly qualified names remains implementer-reserved.

Promotion requires:

- spelling rules
- canonicalization rules
- collision behavior
- extension lookup behavior
- failure values for unavailable or denied extensions

This is not ordinary teachable user syntax until those rules are stable.

### 3.7 Experimental High-Risk Directions

`Recover[...]`, stronger `InspectSelf[...]`, rule self-modification, and
adapter-specific tightly coupled operators should normally pass through
`Reserved` first.

Direct promotion is blocked unless the proposal can prove:

- bounded behavior
- explicit permission failure
- no hidden host exceptions
- no silent mutation of rules or policy
- conformance coverage for denied and unsupported paths

---

## 4. Review Outcomes

Maintainers should close each promotion review with one of these outcomes:

- `promote`: evidence is sufficient, docs and tests are updated, and the target
  status is explicit
- `reserve`: the direction is worth keeping but default behavior remains
  `StubError[...]`, `PermissionError[...]`, or profile-specific
- `keep experimental`: the direction is still exploratory or too risky
- `downgrade`: a carry-forward or ambiguous entry becomes `Reserved`
- `remove`: the entry conflicts with the current language line or no longer has
  a clear role

The decision should identify the missing evidence if the result is not
`promote`.

---

## 5. Non-Goals

This document does not:

- define new stable syntax
- promise a `v1.2` feature list
- require every implementation to support `Enhanced`
- turn host-specific examples into language-core behavior
- replace conformance tests with prose

The goal is narrower: make promotion review predictable enough that `Core`,
`Reserved`, and `Experimental` remain meaningful compatibility tiers.
