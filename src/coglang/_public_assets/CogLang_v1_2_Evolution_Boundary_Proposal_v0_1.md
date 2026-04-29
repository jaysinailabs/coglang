# CogLang v1.2 Evolution Boundary Proposal v0.1

**Status**: public design proposal  
**Scope**: v1.2 evolution boundary and planning discipline, not a release contract  
**Audience**: maintainers, contributors, host implementers, and AI-system builders

---

## 0. How To Read This Document

This document records a planning decision:

CogLang should preserve the stable `v1.1.0` language commitments while widening
its long-term identity enough to serve future AI systems that need auditable
semantic actions, not only direct graph queries and updates.

This document is not:

- a new stable specification
- a v1.2 release checklist
- a promise that every candidate surface will ship
- permission to break the `v1.1.0` canonical syntax, Core operator semantics, or
  error model

The practical intent is to avoid two failure modes:

- over-freezing CogLang as a small LLM-to-graph-query DSL
- expanding CogLang into a general-purpose scripting language

The target middle path is:

> CogLang remains a small, auditable semantic-action intermediate language, with
> graph-shaped state as its primary substrate and bounded host contracts as its
> safety boundary.

---

## 1. Current Constraint Audit

The current public documents contain strong constraints. Most of them are
healthy; a few should be reinterpreted before v1.2 planning.

### 1.1 Constraints That Should Remain Hard

The following constraints should remain hard project law.

#### Canonical Text Remains The Stability Anchor

Canonical M-expression text must remain the authoritative representation for:

- storage
- hashing
- diffing
- replay
- conformance
- examples
- AI learning material

Readable render can improve, but it must not replace canonical text.

#### Errors Remain Values

Failure must remain an explicit value-level result, not hidden host exceptions,
silent `null`-like values, or out-of-band status codes.

This is especially important for AI-generated input because partial failure is
normal and must remain inspectable.

#### Existing Core Compatibility Must Not Be Broken In v1.x

`v1.x` can add new surfaces, profiles, and Reserved capabilities, but it should
not change the meaning of existing Core operators.

Breaking changes belong in a future major language line with migration notes.

#### Raw Opaque Payloads Do Not Enter Expressions

Large opaque payloads should normally be represented by host-owned references
plus metadata, not embedded directly in CogLang expressions.

Examples:

- tensor bytes
- media bytes
- model artifacts
- database-native opaque handles
- large binary blobs

This keeps expressions inspectable, hashable, diffable, and replayable.

#### CogLang Does Not Own Graph Execution Infrastructure

CogLang should not become a distributed graph compute engine.

It may define:

- cost and budget vocabulary
- preflight result shapes
- effect summaries
- standard budget error values
- host-visible safety envelopes

It should not own:

- graph storage
- distributed query planning
- index selection
- GPU scheduling
- cluster-level execution

### 1.2 Constraints That Need Reframing

Some existing wording is correct for `v1.1.0`, but too narrow if treated as a
permanent identity boundary.

#### Reframe "Graph-First Execution Language"

`graph-first` should remain true, but it should not mean "only graph query and
graph update operators matter."

For v1.2 planning, a better framing is:

> CogLang is a semantic-action intermediate language whose primary substrate is
> graph-shaped state.

This keeps the graph kernel central while allowing related AI-action surfaces:

- tool-call preflight for graph-like actions
- agent memory write review
- provenance and responsibility links
- review bundles
- bounded semantic-action orchestration
- host policy evidence

#### Reframe Procedural Composition

Current procedural composition exists to support graph semantics. That remains
right for Core, but future AI systems also need bounded orchestration around
semantic actions.

Acceptable future orchestration:

- conditional approval paths
- bounded retry or repair shells
- review-before-write sequences
- rollback request envelopes
- budget preflight followed by execute-or-reject
- policy branch records

Still out of scope:

- unbounded loops
- arbitrary filesystem or network IO in the language core
- background services
- general package/module systems
- human-oriented scripting convenience as a primary goal

The line is not "no orchestration." The line is "bounded semantic-action
orchestration, not general scripting."

#### Reframe Profiles

Profiles should remain unable to rewrite Core. However, profiles should become
more than a loose availability label.

For v1.2, a profile should be allowed to become a formal extension contract
pack, containing:

- capability vocabulary
- operator availability
- schema or shape references
- conformance examples
- default failure behavior
- trace and review-bundle expectations

This lets CogLang evolve without forcing every future AI-action surface into
Core.

#### Reframe Schema Avoidance

CogLang should not become a schema definition language. That boundary remains
valid.

However, AI-generated actions often need to reference host shapes before
execution. v1.2 should therefore allow schema-aware references without turning
CogLang into the schema system itself.

Candidate direction:

- `SchemaRef[...]`
- `ShapeRef[...]`
- host-provided shape summaries in review bundles
- shape mismatch errors as values

The schema remains host-owned. CogLang carries inspectable references and
preflight evidence.

---

## 2. Future AI Assumptions

The following assumptions should guide v1.2 planning.

### 2.1 AI Systems Are Moving From Text To Action

AI systems increasingly:

- call tools
- modify memory
- update knowledge graphs
- coordinate with other agents
- produce structured plans
- submit actions to hosts
- require audit trails

CogLang should focus on the semantic-action layer between model output and host
execution.

### 2.2 Tool Protocols Need Semantic Payloads

Tool protocols can expose tools, schemas, and resources to models. They do not
by themselves define a canonical semantic-action language for graph-shaped
intent.

CogLang should complement tool protocols by acting as the payload that says:

- what the model intended
- what graph-shaped state may be read or changed
- what capabilities are required
- what budget may be consumed
- what review evidence should be shown before execution

### 2.3 Observability Needs Canonical Action Sidecars

Tracing systems can record events, spans, tool calls, and exceptions. CogLang
should not replace them.

CogLang should provide canonical semantic sidecars:

- expression text
- expression hash
- effect summary
- capability requirements
- budget estimate
- review decision
- error values
- host submission identifiers

### 2.4 Provenance Needs Compact Action Evidence

Provenance models can describe entities, activities, agents, responsibility, and
derivation. CogLang should not replace a provenance standard.

CogLang should provide compact action evidence that can be linked into
provenance records:

- who or what proposed an action
- what canonical expression was proposed
- what host reviewed it
- what capability or budget gate accepted or rejected it
- what result or error value was produced

### 2.5 AI Learning Is A Product Surface

CogLang is designed to be generated by AI systems. Therefore, learnability by
models is not only documentation quality; it is part of the project surface.

v1.2 planning should treat prompt-to-expression generation, repair, validation,
and host-aware review generation as measurable surfaces.

---

## 3. Proposed v1.2 Identity

The recommended v1.2 identity is:

> CogLang is an auditable semantic-action intermediate language for AI-generated
> operations over graph-shaped state, host tools, and reviewable execution
> envelopes.

This identity keeps the graph substrate central but leaves room for:

- tool protocol integration
- agent memory writes
- review bundles
- provenance links
- budget preflight
- profile-based domain packs
- AI generation maturity tests

It does not make CogLang:

- a general-purpose programming language
- a database engine
- a distributed graph compute system
- a replacement for tool protocols
- a replacement for tracing or provenance systems
- a full schema language

---

## 4. Core And Extension Boundary

v1.2 should distinguish three layers more explicitly.

### 4.1 Stable Core Kernel

The Core kernel should remain small:

- canonical expression syntax
- parser / validator / executor consistency
- graph read and graph write intent
- structural values
- explicit errors
- traceable execution
- existing Core operator semantics

Core should grow only when a capability is broadly useful, semantically frozen,
and covered by conformance.

### 4.2 Reserved Semantic-Action Surfaces

Reserved surfaces should carry likely future commitments without freezing every
implementation detail.

The strongest v1.2 candidates are:

- `EffectSummary`
- `GraphBudget`
- `ReviewBundle`
- `SchemaRef` or `ShapeRef`
- `ProvenanceRef`
- `ToolPreflightEnvelope`
- profile manifest formalization

These should be defined as candidate surfaces first, then promoted only after
examples and tests exist.

### 4.3 Profile Contract Packs

Profiles should become formal enough to support real extension ecosystems.

A profile contract pack should include:

- profile name
- capability strings
- supported operators
- required host evidence
- default failure values
- review-bundle fields
- conformance examples
- compatibility statement with the Core kernel

Candidate future profiles:

- `Baseline`
- `Enhanced`
- `ToolPreflight`
- `AgentMemory`
- `Provenance`
- `BudgetedGraph`

These names are not frozen by this proposal.

---

## 5. Candidate v1.2 Reserved Surfaces

### 5.1 `EffectSummary`

Purpose:

Describe possible effects before execution.

Candidate fields:

- reads
- writes
- deletes
- traversal
- unification
- external tool use
- host capability requirement
- human review requirement
- possible error categories

Boundary:

An effect summary is conservative evidence, not a proof of complete runtime
behavior.

### 5.2 `GraphBudget`

Purpose:

Keep AI-generated graph operations computationally reachable.

Candidate fields:

- max traversal depth
- max visited nodes
- max visited edges
- max path count
- max result count
- max recursion depth
- max unification branches
- max intermediate bindings
- max execution time
- host-specific cost class

Boundary:

The host enforces the budget. CogLang defines vocabulary and standard failure
shapes.

### 5.3 `ReviewBundle`

Purpose:

Make inspect-before-execute concrete.

Candidate fields:

- canonical expression
- readable explanation
- effect summary
- graph budget
- planned graph diff
- required capabilities
- risk flags
- host policy decision
- correlation identifiers
- expected success envelope
- possible `ErrorReport`

Boundary:

The review bundle is a host-facing artifact. It should not add new hidden
semantics to the expression itself.

### 5.4 `SchemaRef` / `ShapeRef`

Purpose:

Let expressions or review bundles reference host-owned shape information.

Candidate examples:

```text
SchemaRef["kg://schema/person-v1"]
ShapeRef["memory://shape/user-preference-v1"]
```

Boundary:

CogLang references shape evidence but does not become the schema definition
language.

### 5.5 `ProvenanceRef`

Purpose:

Link CogLang actions to provenance or lineage systems.

Candidate examples:

```text
ProvenanceRef["prov://bundle/2026-04-29/action-17"]
```

Boundary:

CogLang carries compact action evidence and stable links. Provenance systems own
the broader provenance graph.

### 5.6 `ToolPreflightEnvelope`

Purpose:

Wrap a CogLang semantic action for use inside a tool protocol or agent
framework.

Candidate fields:

- tool name
- canonical expression
- required capabilities
- effect summary
- graph budget
- approval status
- host policy result
- correlation identifiers

Boundary:

CogLang does not replace the tool protocol. It supplies the reviewable semantic
payload.

### 5.7 Formal Profile Manifest

Purpose:

Make profile support machine-readable and testable.

Candidate fields:

- profile name
- language release
- supported operators
- capability strings
- denied-by-default capabilities
- review-bundle support
- graph-budget support
- schema-ref support
- conformance level

Boundary:

A profile manifest must not claim Core compatibility unless Core semantics are
preserved.

---

## 6. Bounded Orchestration Rule

v1.2 should explicitly allow bounded semantic-action orchestration.

Allowed:

- review-before-execute
- preflight-then-execute
- policy branch records
- error-guided repair attempts with explicit limits
- rollback request envelopes
- bounded approval workflows

Not allowed in Core:

- unbounded loops
- arbitrary IO
- general modules
- background tasks
- unrestricted tool chaining
- general-purpose scripting convenience

The test should be:

> Can this orchestration be represented as reviewable semantic-action evidence
> with bounded host responsibilities?

If yes, it can be explored through Reserved surfaces or profiles. If no, it
belongs outside CogLang.

---

## 7. Promotion Gates

No v1.2 candidate should enter Core merely because it is useful.

### 7.1 Experimental To Reserved

A candidate may become Reserved when:

- the name is stable enough to teach
- the owning layer is clear
- the minimum signature is documented
- default failure values are defined
- trace or review evidence is described
- at least one runnable example exists

### 7.2 Reserved To Core

A candidate may become Core only when:

- semantics are normative and complete
- the reference implementation passes conformance tests
- parser / validator / executor impact is implemented
- error values and permission boundaries are frozen
- AI-generation examples are stable
- at least one host-facing example demonstrates the boundary
- migration and compatibility notes are updated

### 7.3 Profile Pack Acceptance

A profile pack may be accepted without entering Core when:

- it preserves Core semantics
- it has a capability manifest
- denied capabilities fail explicitly
- host responsibilities are documented
- examples are runnable
- conformance or smoke tests exist

---

## 8. Recommended v1.2 Planning Order

The next planning pass should avoid designing everything at once.

Recommended order:

1. `EffectSummary`
2. `GraphBudget`
3. `ReviewBundle`
4. formal profile manifest
5. `ToolPreflightEnvelope`
6. `SchemaRef` / `ShapeRef`
7. `ProvenanceRef`

Reason:

Effect and budget preflight are the smallest surfaces that directly improve
AI-generated graph action safety. Review bundles make them visible to humans and
policy engines. Profile manifests then make extension claims testable.

Tool, schema, and provenance integrations should follow after the core review
path is coherent.

---

## 9. Documentation Impact

If this proposal is accepted for v1.2 planning, the following documents should
eventually be updated:

- `ROADMAP.md`: add v1.2 boundary and planning order
- `CogLang_Vision_Proposal_v0_1.md`: cross-link this boundary proposal
- `CogLang_Profiles_and_Capabilities_v1_1_0.md`: prepare profile pack language
- `CogLang_Operator_Catalog_v1_1_0.md`: reserve candidate surface names only
  after names are intentionally chosen
- `CogLang_Specification_v1_1_0_Draft.md`: do not edit stable v1.1 semantics
  unless a future v1.2 draft branch is opened
- `llms.txt` and `llms-full.txt`: expose the direction without treating it as a
  release promise

---

## 10. Decision Summary

CogLang should not loosen its core invariants. It should loosen the way its
future identity is described.

The durable center is:

- canonical text
- errors as values
- graph-shaped semantic actions
- host-reviewed execution
- explicit capability and budget boundaries
- profile-based extension pressure

The v1.2 direction is:

> Keep the Core kernel stable, make semantic-action preflight explicit, and let
> formal profiles carry future AI-action domains without turning CogLang into a
> general scripting language.

