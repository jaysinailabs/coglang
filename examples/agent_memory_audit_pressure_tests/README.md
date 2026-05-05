# Agent Memory Audit Pressure Tests

This directory contains companion pressure-test material for a possible future
CogLang host-side application: auditable agent memory operations.

It is not a language proposal, RFC, conformance suite, HRC extension, host
implementation, Locus/STTP integration, or commitment to add new operators. The
fixture records here are internal scenario pressure tests: they use current
CogLang v1.1.0 expressions to measure recurring expression cost, then keep
proposed after-shapes as text-only candidate evidence.

## Scenario

The target application shape is intentionally narrow:

- agents store durable memory records after work sessions
- memory writes carry provenance back to source interaction events and agents
- recall operations need reviewable read evidence and read-set tracking
- maintenance workflows backfill embeddings or clean expired memory
- guarded updates need stale-read protection before write execution

## What It Tests

The fixture currently covers five pressure cases:

1. memory write with explicit provenance edges
2. recall with read-set tracking pressure
3. embedding backfill transform pressure
4. retention cleanup pressure
5. stale-read guarded update pressure

Each case records:

- current v1.1.0 expression text
- expected canonical text
- expected current preflight decision and effect summary
- proposed after-shape as text only
- candidate track and promotion risk
- a conformance-test sketch for future proposal work

## Run

From the repository root:

```powershell
python examples/agent_memory_audit_pressure_tests/agent_memory_audit_pressure_tests.py examples/agent_memory_audit_pressure_tests/fixtures/agent_memory_audit_pressure_tests_v0_1.json .tmp_agent_memory_audit_pressure_results.jsonl
```

The summary is printed to stdout. Per-case results are written to the output
JSONL path.

## Boundary

- No new parser or validator behavior is introduced.
- Proposed after-shapes are not added to `COGLANG_VOCAB`.
- Proposed after-shapes are not claimed to be valid current CogLang.
- No HRC v0.2 frozen scope is expanded.
- No host execution, graph write, memory write, provider call, or transport
  envelope is performed.
- The fixture is evidence for later Discussion or focused governance proposals,
  not a replacement for those proposals.
