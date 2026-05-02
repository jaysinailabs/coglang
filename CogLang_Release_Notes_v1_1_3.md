# CogLang Release Notes v1.1.3

**Status**: Python package evidence and maintenance patch
**Python distribution version**: `1.1.3`
**Language release**: `v1.1.0`
**Audience**: users trying the current package, host implementers, and reviewers
**Purpose**: publish the executable maintenance evidence added after `1.1.2` without changing language semantics

---

## 0. Release Positioning

CogLang `1.1.3` is a package-level patch release for the stable `v1.1.0`
language line.

It does not change CogLang language syntax, operator semantics, canonical text
rules, or the `v1.1.0` conformance contract.

The package version changes to `1.1.3`, while CLI metadata continues to report:

- `version`: `1.1.3`
- `language_release`: `v1.1.0`

## 1. What Changed

This release publishes the maintenance evidence added after `1.1.2`:

- `coglang preflight` and `coglang preflight-fixture` expose the candidate v1.2
  static preflight path for effect summaries, graph budgets, budget estimates,
  and preflight decisions.
- Static preflight now treats `estimated_traversal_depth` as nested `Traverse`
  depth rather than the total number of `Traverse` occurrences.
- `coglang generation-eval` packages a deterministic L1-L3 fixture for checking
  generated CogLang text against parse, canonicalization, validation, expected
  top-level heads, hallucinated operators, maturity summaries, and preflight
  decisions.
- The generation-eval maturity summary now distinguishes fixture-defined levels
  from evaluated levels, so L4-L6 are reported as unevaluated instead of implied.
- The abstract `CogLangExecutor` surface is kept minimal for second
  implementations: `execute()` and `validate()` are the required methods.
- `examples/node_host_consumer` demonstrates Node.js standard-library
  consumption of the HRC schema pack and envelope samples without importing the
  Python runtime.
- `examples/node_minimal_host_runtime_stub` demonstrates a tiny companion
  Node.js host/runtime stub for `execute`, `validate`, and typed write-envelope
  success/failure paths.
- Public governance and planning notes now record the v1.2 evolution boundary,
  the effect-budget preflight vocabulary, reserved-operator promotion criteria,
  `Send` carry-forward exit criteria, HRC companion asset classification,
  readable-render boundaries, readable-render candidate examples,
  readable-render API promotion gates, and current review-response priorities.
- Release-check and CI evidence now cover the public asset mirror, built wheel
  and sdist validation, HRC host demos, Node examples, generation-eval, and
  preflight fixtures.
- Schema version identifiers now have a central `schema_versions.py` registry
  used by Python runtime payload producers, without changing existing payload
  values.
- Readable-render golden example candidates now have a packaged JSON fixture
  that pins their canonical text and candidate display strings without adding a
  renderer API or stable readable-output claim.
- Public asset mirror maintenance now has reusable check and sync helpers so
  source/extracted trees can detect and repair mirror drift without changing the
  public release contract.
- Repository metadata now includes `.mailmap` so historical commits authored as
  `xinjingshun <xinjingshun@foxmail.com>` are attributed to
  `Jason Xin <xinjingshun@foxmail.com>` without rewriting Git history.

## 2. What Did Not Change

This release does not freeze:

- v1.2 language syntax
- `EffectSummary`, `GraphBudget`, `GraphBudgetEstimate`, or
  `PreflightDecision` as stable v1.1 syntax
- a public readable-render API
- `to_readable()`
- `coglang render`
- `--format readable`
- a benchmark claim for `generation-eval`
- a cross-language conformance program
- a network transport protocol
- a normative cross-language JSON Schema pack
- a third-party host implementation maintained outside this repository

HRC v0.2 remains frozen only for the narrow typed write-envelope surface covered
by `host-demo`, `reference-host-demo`, package tests, and companion evidence.

## 3. Recommended Checks

For a minimum user install:

```powershell
pip install coglang
coglang info
coglang release-check
coglang preflight --format text 'AllNodes[]'
coglang preflight-fixture
coglang generation-eval --summary-only
coglang execute 'Equal[1, 1]'
```

For host-runtime evidence:

```powershell
coglang host-demo
coglang reference-host-demo
node examples/node_host_consumer/consume_hrc_envelopes.mjs
node examples/node_minimal_host_runtime_stub/run_demo.mjs
```

For packaged smoke and conformance checks:

```powershell
pip install "coglang[dev]"
coglang doctor
coglang smoke
coglang conformance smoke
```

## 4. One-Sentence Summary

CogLang `1.1.3` publishes the preflight, generation-eval, Node companion
evidence, and governance-review assets added after `1.1.2`, while keeping the
stable `v1.1.0` language semantics unchanged.
