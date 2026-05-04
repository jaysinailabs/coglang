# CogLang GitNexus Audit Bridge Companion Example

This directory contains companion example material for using CogLang as an
external audit layer around GitNexus-style MCP tool-call evidence.

It is not an official GitNexus integration, GitNexus plugin, MCP transport
extension, hosted runner, GitNexus dependency, GitHub automation, or stable
protocol. The JSONL shapes here are local example evidence only.

GitNexus is treated as an external code-knowledge-graph tool. This example does
not import, run, wrap, or modify GitNexus.

## What It Shows

The example demonstrates a narrow local workflow:

1. a fixture records GitNexus-style MCP tool calls and compact result summaries
2. each record carries a CogLang expression describing the audited intent
3. `gitnexus_audit_bridge.py` parses and preflights that expression
4. the script writes JSONL audit records with canonical expression text,
   expression hash, preflight decision, GitNexus evidence summary, and a derived
   audit action
5. no GitNexus execution, host execution, provider call, network access, or HRC
   write envelope is performed

The output is useful as a discussion artifact: it shows how CogLang can sit
outside a code-knowledge-graph tool and record review evidence without making
that upstream project adopt CogLang as a core dependency.

## Run

From the repository root:

```powershell
python examples/gitnexus_audit_bridge/gitnexus_audit_bridge.py examples/gitnexus_audit_bridge/fixtures/gitnexus_tool_events.jsonl .tmp_gitnexus_audit.jsonl
```

The summary is printed to stdout. The audit records are written to the output
JSONL path.

Expected fixture behavior:

- `impact` evidence is accepted with warnings and recorded as `allow`
- `detect_changes` evidence is accepted by CogLang preflight but queued for
  review because the GitNexus-style result reports high risk
- `rename` dry-run evidence is queued for review because the audited CogLang
  intent is a graph write

## Boundary

This example deliberately stays outside the stable public surface:

- it does not add a `coglang` CLI command
- it does not define a normative schema or protocol
- it does not execute expressions against a host
- it does not submit HRC write envelopes
- it does not call GitNexus or depend on GitNexus packages
- it does not claim endorsement by the GitNexus project
- it does not expand HRC v0.2 frozen scope

For production use, keep the same separation: let GitNexus or another
code-knowledge-graph system produce tool-call evidence, let CogLang provide
parse/preflight/canonical evidence, and let the host or review workflow decide
whether downstream code changes are allowed.
