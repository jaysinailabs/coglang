# CogLang LightRAG Audit Bridge Companion Example

This directory contains companion example material for using CogLang as an
external audit layer around LightRAG-style entity and relationship extraction
output.

It is not an official LightRAG integration, LightRAG plugin, GraphRAG storage
backend, hosted runner, provider SDK integration, or stable protocol. The JSONL
shapes here are local example evidence only.

LightRAG is treated as an external GraphRAG system that can emit extraction
evidence. This example does not import, run, wrap, or modify LightRAG.

## What It Shows

LightRAG's extraction prompt asks the model to emit entity and relationship
tuples using a tuple delimiter. This example demonstrates a narrow local
workflow:

1. a fixture records LightRAG-style extraction tuple lines with document and
   chunk provenance
2. `lightrag_audit_bridge.py` parses each tuple into a proposed CogLang graph
   write intent
3. CogLang parses, canonicalizes, preflights, and hashes the proposed intent
4. the script writes JSONL audit records with the source tuple, provenance,
   canonical expression text, expression hash, preflight decision, and derived
   audit action
5. no LightRAG execution, graph storage write, provider call, network access, or
   HRC write envelope is performed

The output is useful as a discussion artifact: it shows how CogLang can sit
outside a GraphRAG extraction pipeline and record review evidence before
LLM-proposed entities or relationships are accepted into a knowledge graph.

## Run

From the repository root:

```powershell
python examples/lightrag_audit_bridge/lightrag_audit_bridge.py examples/lightrag_audit_bridge/fixtures/lightrag_extraction_tuples.jsonl .tmp_lightrag_audit.jsonl
```

The summary is printed to stdout. The audit records are written to the output
JSONL path.

Expected fixture behavior:

- a valid `entity` tuple is converted into a CogLang `Create["Entity", ...]`
  intent and queued for human review
- a valid `relation` tuple is converted into a CogLang `Create["Edge", ...]`
  intent and queued for human review
- a malformed `relation` tuple with an empty target entity is rejected before
  any graph write

## Boundary

This example deliberately stays outside the stable public surface:

- it does not add a `coglang` CLI command
- it does not define a normative schema or protocol
- it does not execute expressions against a host
- it does not submit HRC write envelopes
- it does not call LightRAG or depend on LightRAG packages
- it does not claim endorsement by the LightRAG project
- it does not expand HRC v0.2 frozen scope

For production use, keep the same separation: let LightRAG or another GraphRAG
system produce extraction evidence, let CogLang provide parse/preflight/canonical
review evidence, and let the host or review workflow decide whether downstream
graph writes are allowed.
