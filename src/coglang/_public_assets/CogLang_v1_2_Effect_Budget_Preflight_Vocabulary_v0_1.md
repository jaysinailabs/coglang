# CogLang v1.2 Effect And Graph-Budget Preflight Vocabulary v0.1

**Status**: public design proposal
**Scope**: minimal v1.2 vocabulary candidate, not a stable specification
**Audience**: maintainers, contributors, host implementers, and AI-system builders

---

## 0. How To Read This Document

This document defines a minimal vocabulary candidate for v1.2 planning:

- `EffectSummary`
- `GraphBudget`
- `GraphBudgetEstimate`
- `PreflightDecision`
- budget-related error categories

It is intentionally small. The goal is to make CogLang's next direction concrete
enough for implementation discussion and light public communication without
claiming that the v1.1 runtime already executes these surfaces.

This document is not:

- a stable v1.2 specification
- executable v1.1 syntax
- a promise that every candidate name will ship unchanged
- a complete static analysis system
- a replacement for host policy, graph database planning, observability, or
  provenance tooling

The stable v1.1 language release remains governed by
`CogLang_Specification_v1_1_0_Draft.md`.

---

## 1. Design Goal

AI-generated graph actions need a preflight step before execution.

At minimum, a host should be able to answer:

1. What kind of effect may this expression have?
2. What capabilities does it require?
3. What graph-compute budget might it consume?
4. Is the action safe enough to run automatically?
5. Does it require review?
6. Should it be rejected before execution?
7. If rejected, what explicit value explains why?

The vocabulary below defines the smallest shared language for those answers.

---

## 2. Boundary

### 2.1 What Preflight Is

Preflight is a conservative analysis performed before execution.

It may combine:

- expression-level inspection
- host capability checks
- host graph shape information
- graph-cost estimation
- policy rules
- human-review requirements

Preflight is allowed to be incomplete. A host may say `cannot_estimate` rather
than pretending to know a cost it cannot safely estimate.

### 2.2 What Preflight Is Not

Preflight is not:

- proof that execution will succeed
- proof that the result set is complete
- a substitute for runtime budget enforcement
- a graph database query planner
- a security sandbox by itself
- a reason to hide runtime failures

Runtime must still enforce capabilities, budgets, and error behavior.

### 2.3 Recommended Representation

For v1.2 planning, this proposal recommends defining preflight artifacts first
as typed host-facing objects, not as mandatory Core expression syntax.

Reason:

- typed objects are easier for host integrations to adopt
- the v1.1 Core syntax remains stable
- implementation can mature before any candidate Head enters `Reserved` or
  `Core`

Candidate Heads such as `EffectSummary[...]` and `GraphBudget[...]` may be
reserved later, but this document does not freeze their expression syntax.

---

## 3. Minimal Object Model

### 3.1 `EffectSummary`

`EffectSummary` describes the possible effect categories of a CogLang
expression before execution.

Minimal fields:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Suggested value: `coglang-effect-summary/v0.1`. |
| `expression_hash` | string or null | yes | Hash of canonical expression when available. |
| `effects` | string array | yes | Conservative effect categories. |
| `required_capabilities` | string array | yes | Host capabilities required before execution. |
| `possible_errors` | string array | yes | Error categories that preflight can already see. |
| `confidence` | string | yes | `known`, `estimated`, or `unknown`. |
| `notes` | string array | no | Human-readable caveats. |

Minimal effect category vocabulary:

| Category | Meaning |
| --- | --- |
| `pure` | No graph or host effect is expected. |
| `graph.read` | Reads visible graph state. |
| `graph.write` | Writes graph state. |
| `graph.delete` | Performs or requests deletion semantics. |
| `graph.traverse` | Performs traversal over graph edges. |
| `graph.unify` | Performs unification or binding expansion. |
| `meta.trace` | Produces trace or diagnostic evidence. |
| `host.submit` | Submits a host write envelope or equivalent host action. |
| `host.policy` | Requires host policy evaluation. |
| `human.review` | Requires human or external approval before execution. |
| `external.tool` | Requires a tool or adapter outside the core runtime. |

Compatibility rule:

Effect summaries must be conservative. If a host is unsure whether a category
applies, it should include the category or mark confidence as `unknown`.

### 3.2 `GraphBudget`

`GraphBudget` describes host-enforced limits for graph computation.

Minimal fields:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Suggested value: `coglang-graph-budget/v0.1`. |
| `max_traversal_depth` | integer or null | no | Maximum traversal depth. |
| `max_visited_nodes` | integer or null | no | Maximum nodes visited. |
| `max_visited_edges` | integer or null | no | Maximum edges visited. |
| `max_result_count` | integer or null | no | Maximum returned result count. |
| `max_path_count` | integer or null | no | Maximum path expansions. |
| `max_recursion_depth` | integer or null | no | Maximum recursion depth. |
| `max_unification_branches` | integer or null | no | Maximum unification branches. |
| `max_intermediate_bindings` | integer or null | no | Maximum intermediate bindings. |
| `max_execution_ms` | integer or null | no | Wall-clock execution limit in milliseconds. |
| `max_memory_bytes` | integer or null | no | Host-estimated memory budget. |
| `host_cost_class` | string or null | no | Host-defined class such as `small`, `bounded`, `expensive`, or `blocked`. |

Compatibility rule:

The host owns enforcement. CogLang may describe requested or default budget
limits, but the host decides what is safe.

### 3.3 `GraphBudgetEstimate`

`GraphBudgetEstimate` describes what a host believes an expression may consume.

Minimal fields:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Suggested value: `coglang-graph-budget-estimate/v0.1`. |
| `estimated_traversal_depth` | integer or null | no | Estimated traversal depth. |
| `estimated_visited_nodes` | integer or null | no | Estimated nodes visited. |
| `estimated_visited_edges` | integer or null | no | Estimated edges visited. |
| `estimated_result_count` | integer or null | no | Estimated result count. |
| `estimated_path_count` | integer or null | no | Estimated path count. |
| `estimated_unification_branches` | integer or null | no | Estimated unification branches. |
| `estimate_confidence` | string | yes | `known`, `estimated`, `unknown`, or `not_supported`. |
| `estimator` | string | no | Host-defined estimator name or version. |
| `notes` | string array | no | Caveats about missing indexes, graph density, or unknown shape. |

Compatibility rule:

An estimate is evidence for review. It is not a guarantee.

### 3.4 `PreflightDecision`

`PreflightDecision` is the host-visible pre-execution decision.

Minimal fields:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Suggested value: `coglang-preflight-decision/v0.1`. |
| `decision` | string | yes | One of the decision values below. |
| `reasons` | string array | yes | Machine-readable reason codes. |
| `required_review` | boolean | yes | Whether execution requires review. |
| `effect_summary` | object or null | yes | `EffectSummary` object when available. |
| `budget` | object or null | yes | `GraphBudget` applied by the host. |
| `budget_estimate` | object or null | yes | `GraphBudgetEstimate` when available. |
| `possible_errors` | string array | yes | Errors that may be returned before or during execution. |
| `correlation_id` | string or null | no | Host correlation identifier. |

Decision vocabulary:

| Decision | Meaning |
| --- | --- |
| `accepted` | Host accepts automatic execution under the stated budget. |
| `accepted_with_warnings` | Host accepts execution but records caveats. |
| `requires_review` | Human or policy review is required before execution. |
| `rejected` | Host rejects execution before runtime. |
| `cannot_estimate` | Host cannot safely estimate effect or budget. |

Compatibility rule:

`accepted` does not mean execution cannot fail. Runtime still returns normal
values or explicit error values.

---

## 4. Minimal Error Categories

Budget and preflight failures should remain explicit error values.

Candidate categories:

| Error category | Meaning |
| --- | --- |
| `BudgetExceeded` | Runtime exceeded a host-enforced budget. |
| `TraversalLimitExceeded` | Traversal depth, node count, edge count, or path count exceeded the budget. |
| `ResultLimitExceeded` | Result cardinality exceeded the budget. |
| `UnificationLimitExceeded` | Unification branch or binding count exceeded the budget. |
| `PathExplosion` | Host rejected or stopped path expansion because it became unsafe. |
| `Timeout` | Runtime exceeded the execution time budget. |
| `HostCostUnsupported` | Host cannot estimate or enforce the requested cost boundary. |
| `PreflightRejected` | Host rejected the expression before execution. |
| `ReviewRequired` | Host refused automatic execution because review is required. |
| `CapabilityRequired` | Required capability is not present or not enabled. |

The exact canonical spelling is not frozen by this proposal. The important
constraint is that failures stay explicit, structured, and inspectable.

---

## 5. Minimal JSON Shapes

### 5.1 Read Query Example

Expression:

```text
Query[n_, Equal[Get[n_, "category"], "Person"]]
```

Candidate preflight object:

```json
{
  "schema_version": "coglang-preflight-decision/v0.1",
  "decision": "accepted",
  "reasons": ["effect.graph_read", "budget.within_default"],
  "required_review": false,
  "effect_summary": {
    "schema_version": "coglang-effect-summary/v0.1",
    "expression_hash": "sha256:example",
    "effects": ["graph.read"],
    "required_capabilities": ["graph.read"],
    "possible_errors": [],
    "confidence": "known"
  },
  "budget": {
    "schema_version": "coglang-graph-budget/v0.1",
    "max_traversal_depth": 1,
    "max_visited_nodes": 1000,
    "max_result_count": 100,
    "max_execution_ms": 1000,
    "host_cost_class": "bounded"
  },
  "budget_estimate": {
    "schema_version": "coglang-graph-budget-estimate/v0.1",
    "estimated_traversal_depth": 0,
    "estimated_visited_nodes": 1000,
    "estimated_result_count": 100,
    "estimate_confidence": "estimated",
    "estimator": "local-host-v0.1"
  },
  "possible_errors": [],
  "correlation_id": "preflight-example-001"
}
```

### 5.2 Write Intent Example

Expression:

```text
Update["alice", "city", "Paris"]
```

Candidate preflight object:

```json
{
  "schema_version": "coglang-preflight-decision/v0.1",
  "decision": "requires_review",
  "reasons": ["effect.graph_write", "policy.review_required"],
  "required_review": true,
  "effect_summary": {
    "schema_version": "coglang-effect-summary/v0.1",
    "expression_hash": "sha256:example",
    "effects": ["graph.write", "host.policy", "human.review"],
    "required_capabilities": ["graph.write"],
    "possible_errors": ["CapabilityRequired", "ReviewRequired"],
    "confidence": "known"
  },
  "budget": {
    "schema_version": "coglang-graph-budget/v0.1",
    "max_visited_nodes": 1,
    "max_result_count": 1,
    "max_execution_ms": 1000,
    "host_cost_class": "small"
  },
  "budget_estimate": {
    "schema_version": "coglang-graph-budget-estimate/v0.1",
    "estimated_visited_nodes": 1,
    "estimated_result_count": 1,
    "estimate_confidence": "known",
    "estimator": "local-host-v0.1"
  },
  "possible_errors": ["ReviewRequired"],
  "correlation_id": "preflight-example-002"
}
```

### 5.3 Unbounded Traversal Example

Expression:

```text
Traverse["root", "related"]
```

Candidate preflight object when the host cannot bound the expansion:

```json
{
  "schema_version": "coglang-preflight-decision/v0.1",
  "decision": "cannot_estimate",
  "reasons": ["budget.traversal_unbounded", "host.index_unknown"],
  "required_review": true,
  "effect_summary": {
    "schema_version": "coglang-effect-summary/v0.1",
    "expression_hash": "sha256:example",
    "effects": ["graph.read", "graph.traverse", "human.review"],
    "required_capabilities": ["graph.read"],
    "possible_errors": ["HostCostUnsupported", "TraversalLimitExceeded"],
    "confidence": "estimated",
    "notes": ["host cannot bound edge fanout for relation 'related'"]
  },
  "budget": {
    "schema_version": "coglang-graph-budget/v0.1",
    "max_traversal_depth": 1,
    "max_visited_nodes": 1000,
    "max_visited_edges": 5000,
    "max_execution_ms": 1000,
    "host_cost_class": "blocked"
  },
  "budget_estimate": {
    "schema_version": "coglang-graph-budget-estimate/v0.1",
    "estimate_confidence": "unknown",
    "estimator": "local-host-v0.1",
    "notes": ["missing degree statistics"]
  },
  "possible_errors": ["HostCostUnsupported"],
  "correlation_id": "preflight-example-003"
}
```

---

## 6. Host Responsibilities

A host that claims support for this vocabulary should:

1. parse and canonicalize the expression before preflight when possible
2. compute or receive an `EffectSummary`
3. apply a host-owned `GraphBudget`
4. estimate cost when supported
5. return `cannot_estimate` when cost cannot be bounded safely
6. require review for writes or high-risk effects when policy says so
7. enforce the budget at runtime
8. return explicit error values when limits are exceeded
9. include correlation identifiers in traces or review bundles

A host should not:

- treat preflight as proof of success
- silently truncate results without an explicit value
- execute a rejected expression
- downgrade capability failures into partial success
- claim support for budget enforcement if runtime limits are not actually
  enforced

---

## 7. AI Generation Guidance

For AI-generated CogLang, the model should learn to produce or request preflight
evidence when an action may be expensive or destructive.

Useful generation patterns:

- Ask for preflight before graph writes.
- Ask for preflight before traversal over unknown relations.
- Use explicit small budgets for examples.
- Treat `cannot_estimate` as a reason to ask for clarification or review.
- Treat budget failures as repairable errors, not hidden failures.

Anti-patterns:

- generating writes without review context
- using open-ended traversal without a budget
- assuming a host can estimate every graph cost
- treating `accepted` as proof that runtime cannot fail
- hiding budget failures in natural-language explanations

---

## 8. Minimal Acceptance Bar For v1.2 Work

This vocabulary should not be promoted from design proposal to Reserved surface
until the project has:

- at least one typed helper or schema seed for the JSON shapes
- at least one local-host preflight demo
- tests for accepted, requires-review, rejected, and cannot-estimate decisions
- tests for at least one budget-exceeded error value
- documentation that separates host estimate from runtime enforcement
- examples suitable for `llms-full.txt`

It should not enter Core until:

- semantics are normative
- parser / validator / executor impact is clear
- conformance examples exist
- host responsibility boundaries are frozen
- migration notes explain how v1.1 users should treat the new surfaces

---

## 9. Decision Summary

The minimal v1.2 preflight vocabulary should begin with host-facing typed
objects:

- `EffectSummary`
- `GraphBudget`
- `GraphBudgetEstimate`
- `PreflightDecision`

These objects give CogLang a concrete next capability: before an AI-generated
graph action runs, the host can describe likely effects, budget limits, cost
confidence, review requirements, and rejection reasons.

This is the smallest practical step from "auditable graph expression" toward
"auditable AI semantic-action preflight" without expanding CogLang into a
general-purpose runtime.
