# CogLang Outlines Generation Bridge Companion Example

This directory contains companion example material for auditing CogLang
expressions produced by an Outlines-style constrained-generation runner.

It is not an official Outlines integration, Outlines plugin, model provider
adapter, hosted runner, benchmark, or stable protocol. The JSONL shapes here are
local example evidence only.

Outlines is treated as an external structured-output or constrained-generation
system that can emit candidate CogLang text. This example does not import, run, wrap, or modify Outlines.

## What It Shows

CogLang already ships companion Lark and GBNF grammar files under
[`../grammar`](../grammar). This example demonstrates the narrow post-generation
workflow that should still happen after a grammar-aware runner emits text:

1. a fixture records Outlines-style generated CogLang candidate expressions
2. `outlines_generation_bridge.py` parses each generated expression
3. CogLang validates, canonicalizes, preflights, and hashes the candidate when
   possible
4. the script writes JSONL audit records with the prompt metadata, grammar
   provenance, generated expression, canonical expression, expression hash,
   preflight decision, and derived audit action
5. no model call, Outlines execution, provider SDK, host execution, graph write,
   or HRC write envelope is performed

The output is useful as a discussion artifact: it shows how CogLang can sit
after a constrained-generation system and turn generated DSL text into review
evidence before any downstream graph or host operation is allowed.

## Run

From the repository root:

```powershell
python examples/outlines_generation_bridge/outlines_generation_bridge.py examples/outlines_generation_bridge/fixtures/outlines_generated_expressions.jsonl .tmp_outlines_generation_audit.jsonl
```

The summary is printed to stdout. The audit records are written to the output
JSONL path.

Expected fixture behavior:

- a generated `AllNodes[]` expression is accepted with warnings and allowed
- a generated `Create[...]` graph write is parsed and queued for human review
- a generated unknown head is parsed but rejected by CogLang validation
- a malformed expression is rejected before any canonical hash is assigned

## Boundary

This example deliberately stays outside the stable public surface:

- it does not add a `coglang` CLI command
- it does not define a normative schema or protocol
- it does not execute expressions against a host
- it does not submit HRC write envelopes
- it does not call Outlines or depend on Outlines packages
- it does not claim endorsement by the Outlines project
- it does not expand HRC v0.2 frozen scope

For production use, keep the same separation: let Outlines or another
grammar-aware runner generate candidate text, then run CogLang parse,
validation, preflight, canonicalization, and deterministic scoring before any
host action.
