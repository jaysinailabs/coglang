# CogLang Release Notes v1.1.5

**Status**: Python package maintenance patch
**Python distribution version**: `1.1.5`
**Language release**: `v1.1.0`
**Audience**: users, release maintainers, host implementers, and reviewers
**Purpose**: publish the local-first validation and AI-first developer-experience maintenance batch without changing language semantics

---

## 0. Release Positioning

CogLang `1.1.5` is a package-level maintenance patch for the stable `v1.1.0`
language line.

It does not change CogLang language syntax, operator semantics, canonical text
rules, or the `v1.1.0` conformance contract.

The package version changes to `1.1.5`, while CLI metadata continues to report:

- `version`: `1.1.5`
- `language_release`: `v1.1.0`

## 1. What Changed

This release publishes the source-maintenance batch accumulated after `1.1.4`:

- The public GitHub `ci` workflow is now manually triggered to conserve Actions
  minutes, with local validation expected before remote evidence is requested.
- `scripts/local_ci.py` provides `quick`, `ci`, and `package` local simulation
  profiles for release-check, smoke, HRC host demos, and wheel/sdist install
  validation.
- `examples/grammar` provides companion Lark and GBNF grammar examples for
  constrained generation. These files reduce malformed model output but do not
  replace `parse` or `valid_coglang`.
- `coglang generation-eval` now supports provider-neutral request export and
  response-file scoring, so external model runners can be evaluated without
  adding provider SDK dependencies. The record shape is now documented in
  `CogLang_Generation_Eval_Request_Response_Contract_v0_1.md`.
- `examples/generation_eval_offline_runner` provides a no-provider three-case
  dry run for the generation-eval request/response file contract.
- `examples/vscode_textmate_syntax` provides a private, local-installable
  VS Code/TextMate syntax companion for `.coglang` files. It is editor-only
  companion material, not a parser, validator, LSP, formatter, renderer, or
  normative grammar.
- `examples/node_host_consumer` now includes a private npm scaffold for local
  `npm test` and `npm pack --dry-run` checks. It remains example packaging
  evidence, not a published JavaScript SDK or second CogLang runtime API.
- `coglang release-check`, public extract tests, package data, machine-readable
  summaries, and public asset mirrors now cover these new companion examples
  and local-first validation assets.

## 2. What Did Not Change

This release does not freeze:

- v1.2 language syntax
- a public readable-render API
- a benchmark claim for `generation-eval`
- a normative constrained-generation grammar
- a VS Code extension Marketplace release
- a published npm package or stable JavaScript SDK
- a cross-language conformance program
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
coglang execute 'Equal[1, 1]'
```

For source checkout validation before spending remote workflow minutes:

```powershell
python -m pytest
python scripts/local_ci.py --profile quick
python scripts/local_ci.py --profile package
```

For companion Node and editor-package dry runs:

```powershell
npm --prefix examples/node_host_consumer test
npm --prefix examples/node_host_consumer run pack:dry
Push-Location examples/vscode_textmate_syntax
npm pack --dry-run
Pop-Location
```

## 4. One-Sentence Summary

CogLang `1.1.5` packages the local-first validation workflow and the first
AI-first developer-experience companion assets while keeping stable `v1.1.0`
language semantics unchanged.
