# CogLang Use Cases And Positioning v0.1

This document gives a concise, reader-facing explanation of where CogLang fits,
what it is good for, and where it should not be used.

## 1. One-Sentence Summary

CogLang is a small auditable language for LLM-generated graph operations, with
canonicalization, validation, preflight effect and budget checks, and
provider-neutral generation evaluation.

## 2. Best-Fit Scenarios

### 2.1 LLM-Generated Knowledge Graph Updates

Use CogLang when a model proposes graph operations such as creating nodes,
updating properties, traversing relations, or querying graph-backed state.

Why CogLang helps:

- generated operations are parseable language values
- canonical text can be hashed and reviewed
- write-like intent can be separated from durable host submission
- host capabilities can reject unsupported operations before execution

Example:

```powershell
coglang preflight --format text 'Create["Entity", "person:ada", {"label": "Ada Lovelace"}]'
```

### 2.2 Human-In-The-Loop Graph Write Review

Use CogLang when an AI system can suggest changes but a host or reviewer must
decide whether those changes are safe.

Why CogLang helps:

- `preflight` returns a structured decision such as accepted, requires review,
  rejected, or cannot estimate
- effect summaries distinguish read, traverse, write, delete, trace, submit,
  and external-like surfaces
- graph budget estimates make hidden cost assumptions visible
- capability checks make policy failures explicit

This is the most important public framing: CogLang is not "AI can mutate your
graph directly"; it is "AI can propose an inspectable graph operation."

### 2.3 Semantic-Event Audit Pipelines

Use CogLang when an external runner emits graph-intent events and you want a
local audit record before trusting or replaying them.

Why CogLang helps:

- external JSONL can be converted into canonical CogLang expression text
- expression hashes give stable identities for audit records
- preflight decisions can derive actions such as allow, queue review, or reject
- the audit layer does not need provider SDKs or hosted infrastructure

Evidence:

- `examples/semantic_event_audit`

### 2.4 Provider-Neutral LLM Output Evaluation

Use CogLang when you want to test generated CogLang text from any model runner
without binding the project to OpenAI, Anthropic, Ollama, or a private gateway.

Why CogLang helps:

- request records can be exported as JSON or JSONL
- any external runner can fill response records
- deterministic scoring checks parse, canonicalization, validation, expected
  top-level heads, hallucinated operators, and maturity summaries
- runner failures stay outside the scorer

Evidence:

- `CogLang_Generation_Eval_Request_Response_Contract_v0_1.md`
- `examples/generation_eval_offline_runner`

### 2.5 Constrained Generation For Local Models

Use CogLang when a local or open model should be nudged toward syntactically
valid graph-operation text.

Why CogLang helps:

- companion Lark and GBNF grammars provide starting points for constrained
  generation experiments
- grammar-constrained output can still go through parse, validate, and preflight
- examples do not make the grammar the normative parser

Evidence:

- `examples/grammar`

### 2.6 Host Runtime Boundary Experiments

Use CogLang when a host implementation or consumer wants a narrow typed
write-envelope boundary to study without taking on the whole Python runtime.

Why CogLang helps:

- HRC v0.2 has a frozen narrow typed write-envelope evidence path
- Node.js examples show non-Python consumption of schema pack and samples
- host/runtime companion assets are classified so examples are not mistaken for
  normative JSON Schema contracts

Evidence:

- `CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md`
- `CogLang_HRC_Companion_Asset_Classification_v0_1.md`
- `examples/node_host_consumer`
- `examples/node_minimal_host_runtime_stub`

## 3. Advantages

### 3.1 Auditable By Construction

CogLang keeps the model's graph intent in a structured language form instead of
an untyped natural-language instruction. That form can be parsed, canonicalized,
validated, hashed, diffed, reviewed, and replayed.

### 3.2 Errors As Values

In AI-driven graph operations, partial failure is normal. CogLang keeps failures
as explicit language values where possible, which helps downstream hosts and
review tools reason about failure instead of treating every failure as an
unstructured exception.

### 3.3 Preflight Before Trust

CogLang's static preflight path lets a host ask what an expression appears to do
before running it. Effect summaries, budget estimates, and capability checks are
first-class review objects rather than hidden implementation details.

### 3.4 Provider-Neutral Evaluation

CogLang does not need to import a model provider SDK to evaluate generated
CogLang text. It exports request records and scores response records, allowing
teams to use their existing runner, gateway, model, or manual review process.

### 3.5 Narrow Host Boundary

The host/runtime work is intentionally narrow. HRC v0.2 freezes typed
write-envelope evidence rather than claiming a complete cross-language runtime
or universal host API.

### 3.6 Local-First Validation

CogLang keeps release and contribution validation local-first. This matters for
single-maintainer and small-team projects because GitHub Actions minutes and
maintainer attention are both limited resources.

## 4. Comparison Notes

These notes are positioning aids, not superiority claims.

### CogLang And Native Graph Query Languages

Native graph query languages are still the right tool inside their native
database environment. CogLang is useful when the operation is generated by an
LLM and must be inspected, preflighted, or reviewed before host execution.

### CogLang And Agent Frameworks

Agent frameworks coordinate multi-step behavior. CogLang represents graph
operation intent and host-visible outcomes. It can sit inside an agent workflow,
but it is not a complete agent loop.

### CogLang And LLM Eval Frameworks

LLM eval frameworks often manage datasets, runs, metrics, or optimization.
CogLang provides a narrow deterministic scorer for generated CogLang text and a
provider-neutral file contract for external runners.

### CogLang And Constrained-Decoding Tools

Constrained-decoding tools reduce invalid output during generation. CogLang
still needs parse, validation, and preflight after generation because syntax
alone does not prove semantic safety or host capability support.

### CogLang And Observability Tools

Observability tools record process, service, and metric data. CogLang is for
symbolic graph intent and graph-operation audit records, not general telemetry.

## 5. Non-Goals

CogLang does not currently promise:

- production readiness for every graph database
- npm package publication
- VS Code Marketplace publication
- LSP support
- hosted playground operation
- managed OpenAI, Anthropic, Ollama, or enterprise-gateway runner
- universal benchmark claims
- stable readable-render API
- stable v1.2 effect/budget vocabulary as public language syntax

## 6. Quick Decision Table

| You need... | CogLang fit |
| --- | --- |
| Inspect LLM-generated graph operations before execution | Strong fit |
| Convert external graph-intent JSONL into audit records | Strong fit |
| Export eval requests and score model responses without provider SDKs | Strong fit |
| Constrain local model output toward graph-operation syntax | Good companion fit |
| Replace a native graph database query language | Not the goal |
| Build a full autonomous agent framework | Not the goal |
| Publish and maintain npm or marketplace packages from this repo | Not the goal |

## 7. Recommended First Try

```powershell
pip install coglang
coglang info
coglang release-check
coglang preflight --format text 'AllNodes[]'
coglang generation-eval --summary-only
```

From a source checkout:

```powershell
python examples/semantic_event_audit/audit_events.py examples/semantic_event_audit/fixtures/external_events.jsonl .tmp_semantic_event_audit.jsonl
coglang generation-eval --export-requests --request-format jsonl
node examples/node_host_consumer/consume_hrc_envelopes.mjs
```

