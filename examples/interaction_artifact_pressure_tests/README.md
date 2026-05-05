# Interaction Artifact Graph Pressure Tests

This directory contains companion pressure-test material for a possible future
CogLang host-side application: an interaction/artifact graph for AI-assisted
software work.

It is not a language proposal, RFC, conformance suite, HRC extension, host
implementation, or commitment to add new operators. The fixture records here are
internal scenario pressure tests: they use current CogLang v1.1.0 expressions to
measure recurring expression cost, then keep proposed after-shapes as text-only
candidate evidence.

## Scenario

The target application shape is intentionally narrow:

- graph nodes are mostly interaction events and durable outputs
- provenance edges connect events, agents, and outputs
- decisions, dependencies, plans, risks, and progress are treated as projections
  instead of first-class ontology expansion
- multiple AI agents and human reviewers read before acting and write after
  acting

## What It Tests

The fixture currently covers five pressure cases:

1. causal ancestors along a named relation
2. revision chain traversal
3. manual provenance writes around a durable output
4. a strict-provenance profile pressure case where current v1.1.0 cannot reject
   missing provenance by profile
5. reviewer point-of-view projection pressure

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
python examples/interaction_artifact_pressure_tests/interaction_artifact_pressure_tests.py examples/interaction_artifact_pressure_tests/fixtures/interaction_artifact_pressure_tests_v0_1.json .tmp_interaction_artifact_pressure_results.jsonl
```

The summary is printed to stdout. Per-case results are written to the output
JSONL path.

## Boundary

- No new parser or validator behavior is introduced.
- Proposed after-shapes are not added to `COGLANG_VOCAB`.
- Proposed after-shapes are not claimed to be valid current CogLang.
- No HRC v0.2 frozen scope is expanded.
- No host execution, graph write, or transport envelope is performed.
- The fixture is evidence for later Discussion or focused governance proposals,
  not a replacement for those proposals.
