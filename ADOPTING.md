# Adopting CogLang

Status: public adoption decision brief
Audience: human decision-makers, technical evaluators, and integration owners
Authority: routing and summary only; release notes, specifications, conformance tests, and `coglang release-check` remain authoritative
Scope: helps decide whether to evaluate CogLang, which path to try first, and where the current risks are
Stability: describes the stable `v1.1.0` language line and active experimental maintenance posture
Read after: `README.md`

This document is the human decision entry point for CogLang. It is intentionally
shorter than the specification and governance notes.

CogLang is a small auditable intermediate language for LLM-proposed graph
operations. It is useful when a model or external runner can propose graph
queries or updates, but a host system still needs to parse, canonicalize,
validate, preflight, review, hash, and replay the intent before trusting it.

## Quick Decision

Continue evaluating CogLang if you need at least one of these:

- inspect LLM-generated graph operations before execution
- keep write-like graph intent reviewable before durable host submission
- produce replayable audit records for what an agent intended and what a host accepted
- reject unsupported graph operations through profile, capability, or budget checks
- score generated CogLang text from any model runner without binding CogLang to a provider SDK
- study a narrow typed write-envelope host boundary without adopting the Python runtime

Stop early if you need one of these instead:

- a general-purpose programming language
- a schema definition language
- a replacement for Cypher, Gremlin, SPARQL, or another native graph query language in its native setting
- a full agent framework
- a hosted product or managed model gateway
- a published JavaScript SDK, VS Code Marketplace extension, or stable readable-render API

## Current Commitments

The public language line is stable at `v1.1.0`.

The current Python source package version is `1.1.6`. Package release notes
define what is available from PyPI; source HEAD may be prepared before a remote
release workflow is triggered.

The Host Runtime Contract v0.2 frozen scope is narrow: typed write-envelope
submission and response evidence demonstrated by `coglang host-demo` and
`coglang reference-host-demo`. Node examples are companion evidence, not a
published SDK or a promise that the main project will maintain a JavaScript
runtime.

The project is in active experimental maintenance. That means contracts,
examples, documentation, and host boundaries may be tightened, but stable
language semantics should not expand casually.

## Five-Minute Trial

From an installed package:

```powershell
pip install coglang
coglang info
coglang release-check
coglang preflight --format text 'AllNodes[]'
coglang execute 'Equal[1, 1]'
```

From a source checkout before the console script is on `PATH`, use the module
entry point:

```powershell
python -m coglang info
python -m coglang release-check --format text
python examples/readme_end_to_end_audit/readme_end_to_end_audit.py
```

If this checkout has a local virtual environment, the equivalent Windows
PowerShell form is:

```powershell
.\.venv\Scripts\python.exe -m coglang release-check --format text
```

## Adoption Paths

### 1. Eval Path

Use this when you already have a model runner and want deterministic scoring of
generated CogLang text.

Start with:

```powershell
coglang generation-eval --export-requests --request-format jsonl
coglang generation-eval --responses-file responses.jsonl --summary-only
```

Read:

- `CogLang_Generation_Eval_Request_Response_Contract_v0_1.md`
- `examples/generation_eval_offline_runner`

Boundary:

CogLang exports prompt records and scores returned records. It does not import
OpenAI, Anthropic, Ollama, or private gateway SDKs.

### 2. Audit Path

Use this when an external system emits graph-intent records and you want a local
preflight audit layer before trusting or replaying them.

Start with:

```powershell
python examples/semantic_event_audit/audit_events.py examples/semantic_event_audit/fixtures/external_events.jsonl .tmp_semantic_event_audit.jsonl
```

Read:

- `examples/semantic_event_audit`
- `CogLang_Use_Cases_and_Positioning_v0_1.md`

Boundary:

The example converts external graph intent into local audit records. It is not
a hosted runner, stable semantic-event schema, transport envelope, provider SDK
integration, or HRC v0.2 expansion.

### 3. Host Path

Use this when a host or consumer wants to inspect a narrow typed write-envelope
surface without inheriting the Python runtime.

Start with:

```powershell
coglang host-demo --format text
coglang reference-host-demo --format text
npm --prefix examples/node_host_consumer test
```

Read:

- `CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md`
- `CogLang_HRC_Companion_Asset_Classification_v0_1.md`
- `examples/node_host_consumer`
- `examples/node_minimal_host_runtime_stub`

Boundary:

HRC v0.2 is frozen only for the narrow typed write-envelope evidence path.
Companion schemas and examples are not automatically normative cross-language
contracts.

## Risk Checklist

Before depending on CogLang, check:

- whether your need fits Eval, Audit, or Host path
- whether stable `v1.1.0` semantics are enough without v1.2 proposals
- whether your host can own durable graph writes and policy enforcement
- whether provider-neutral files are acceptable instead of direct SDK integration
- whether companion examples are enough, or a real integration contribution is needed
- whether your team can evaluate local evidence with `coglang release-check`

## Where To Go Next

For a first technical pass:

1. Run `python examples/readme_end_to_end_audit/readme_end_to_end_audit.py`.
2. Read `CogLang_Quickstart_v1_1_0.md`.
3. Read the path-specific document above.
4. Run `coglang release-check --format text`.

For a contribution:

1. Read `CONTRIBUTING.md`.
2. Open an issue before large host or consumer work.
3. Keep proposed language or HRC expansion out of Core until there is executable evidence.
