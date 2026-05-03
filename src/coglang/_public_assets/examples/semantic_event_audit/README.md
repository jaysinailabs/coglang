# CogLang Semantic Event Audit Example

This directory contains companion example material for using CogLang as a small
semantic-event audit layer around graph intents emitted by an external runner.

It is not a hosted runner, provider SDK integration, transport envelope,
observability protocol, benchmark, or HRC expansion. It does not define a stable semantic-event schema.
The JSONL shapes here are local example evidence only.

## What It Shows

The example demonstrates a narrow local workflow:

1. an external runner writes JSONL records with `event_id`, `expression`, and
   `enabled_capabilities`
2. `audit_events.py` parses and preflights each CogLang expression
3. the script writes JSONL audit records with canonical expression text,
   expression hash, preflight decision, and a derived audit action
4. no host execution, provider call, network access, or transport envelope is
   performed

The output is useful as a review artifact: it records what the runner intended,
what static preflight decided, and whether the next local action should be
`allow`, `queue_review`, or `reject`.

## Run

From the repository root:

```powershell
python examples/semantic_event_audit/audit_events.py examples/semantic_event_audit/fixtures/external_events.jsonl .tmp_semantic_event_audit.jsonl
```

The summary is printed to stdout. The audit records are written to the output
JSONL path.

Expected decisions in the fixture:

- `accepted_with_warnings` for a read-only graph query
- `requires_review` for a graph write that has write capability
- `rejected` for a graph write with only read capability

## Boundary

This example deliberately stays outside the stable public surface:

- it does not add a `coglang` CLI command
- it does not define a normative schema or protocol
- it does not execute expressions against a host
- it does not submit HRC write envelopes
- it does not add provider SDK dependencies
- it does not expand HRC v0.2 frozen scope

For production use, keep the same separation: let external systems emit
intent records, let CogLang provide parse/preflight/canonical evidence, and let
the host or review workflow decide whether execution is allowed.
