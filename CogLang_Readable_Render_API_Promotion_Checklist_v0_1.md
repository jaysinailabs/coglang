# CogLang Readable Render API Promotion Checklist v0.1

Status: public governance note.

Scope: evidence and decision checklist for promoting readable render work from
boundary and candidate examples into a public API or CLI mode.

Audience: maintainers, contributors, tooling authors, UI authors, and reviewers.

This document does not implement a renderer. It does not add `to_readable()`,
does not add a CLI readable mode, and does not change canonical text, parsing,
validation, execution, or host-runtime transport semantics.

## 0. How To Read This Checklist

`CogLang_Readable_Render_Boundary_v0_1.md` records the public boundary between
canonical text, display-only readable rendering, and structured transport
envelopes.

`CogLang_Readable_Render_Golden_Example_Candidates_v0_1.md` records candidate
display examples and invariants for future renderer work. Those examples are
not stable renderer output.

This checklist is the gate between candidate examples and implementation. A
future change may use it to propose, implement, and test a readable render API,
but this document does not create that API.

If a draft language document names `to_readable()` or an equivalent readable
render hook as a desired reference feature, treat that as future-facing guidance
until the API proposal, implementation, and tests in this checklist are
accepted.

## 1. Promotion States

The readable render work should move through explicit states:

1. Boundary documented: done by
   `CogLang_Readable_Render_Boundary_v0_1.md`.
2. Candidate examples documented: done by
   `CogLang_Readable_Render_Golden_Example_Candidates_v0_1.md`.
3. API proposal accepted: not done.
4. Implementation added: not done.
5. Public CLI mode added: not done.

Skipping a state requires an explicit reviewer decision and release-note entry.

## 2. Required API Decisions

Before an implementation is promoted, reviewers should decide:

- API name and location: for example `to_readable()` versus a renderer object,
  and whether the public import surface belongs in `coglang.__init__`.
- Accepted input values: `CogLangExpr`, `CogLangVar`, lists, dictionaries,
  primitives, errors as values, and parse-error values.
- Return type: normally `str`, with any profile or option object specified
  before release.
- Stability promise: whether stability is profile-specific, version-specific,
  or explicitly best-effort.
- Parseability policy: whether readable text is display-only, parseable in a
  subset, or never promised as parser input.
- Ordering and formatting policy: dictionary key order, booleans, strings,
  numbers, escaped characters, and reserved words.
- Multiline policy: indentation, line-break thresholds, collection wrapping,
  and nested expression wrapping.
- Error handling: how renderer failures, parse errors, partial values, and
  unsupported host-owned values are represented.
- Mutation policy: rendering must not mutate input expressions or containers.
- Relationship to existing output: canonical text remains the stability anchor;
  JSON and repr-style outputs remain separate surfaces.

## 3. Required Test Evidence

An implementation PR should include focused tests proving:

- candidate examples either become executable fixtures or remain explicitly
  non-executable documentation examples;
- `canonicalize()` output is unchanged for all existing examples;
- `parse(canonicalize(expr))` invariants remain unchanged for supported inputs;
- rendering does not mutate input expressions, lists, dictionaries, or values;
- existing CLI defaults keep their current canonical, JSON, or text behavior;
- any new CLI mode has explicit help text, manifest entries, release-check
  coverage, and CLI output tests;
- host-runtime transport envelopes do not depend on readable text for machine
  interpretation;
- package data, public extract metadata, and release-check gates are updated
  only when a new public surface is deliberately added.

## 4. CLI Promotion Gates

There is no public readable render CLI mode by default.

If a future PR adds one, it must decide:

- whether the public surface is a new command, an explicit `--format` value, or
  an option on an existing command;
- how help text distinguishes canonical text from readable display text;
- how `coglang manifest`, `coglang bundle`, and `coglang release-check` expose
  the new surface;
- which existing CLI outputs remain byte-for-byte unchanged;
- which public docs and release notes explain the new behavior.

Existing CLI defaults must not change as a side effect of adding readable
rendering.

## 5. Host And Transport Gates

Readable text is auxiliary display material unless a later contract says
otherwise.

Structured fields, typed envelopes, canonical text, and explicit status values
remain the machine-readable anchors. HRC v0.2 is not expanded by readable render
work unless a future HRC document says so directly.

## 6. Claims To Avoid Until Promotion

Do not claim that:

- `to_readable()` exists;
- `coglang render` exists;
- `--format readable` exists;
- readable output is stable release data;
- readable output can replace canonical text in machine paths;
- readable output is always parseable;
- HRC v0.2 includes readable-render transport semantics;
- current release-check gates prove renderer behavior.

## 7. Review Checklist

Before merging any implementation PR, reviewers should confirm:

- the API decision list above is answered in the PR or referenced design note;
- candidate examples have either executable tests or a documented reason to
  remain non-executable;
- parser, canonicalizer, validator, executor, and transport behavior changes
  are either absent or explicitly justified;
- tests cover both direct API calls and any new CLI surface;
- packaging, public extract, README, roadmap, `llms.txt`, `llms-full.txt`, and
  release notes are updated when the public surface changes;
- no release-facing text implies readable render stability before the stability
  promise is accepted.
