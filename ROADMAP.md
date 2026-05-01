# CogLang Roadmap

**Status**: public roadmap
**Scope**: direction layer, not stability guarantees
**Audience**: readers, implementers, and contributors who want to know where `CogLang` is going next

---

## How To Read This File

This file is intentionally not a release contract.

Use the docs this way:

- `CogLang_Release_Notes_v1_1_0.md`: what is currently promised
- `ROADMAP.md`: what is currently prioritized or being explored
- `MAINTENANCE.md`: how the project may slow down, freeze, transfer, or archive

This roadmap does not promise dates.

It separates three levels:

- `In Progress`: work currently being pushed forward
- `Next`: work that has been chosen as likely next, but is not yet complete
- `Exploring`: long-range directions that are intentionally non-binding

---

## Stable v1.1.0 Release Status

The current stable release line is `v1.1.0`.

That status is not a date promise. It means the project is now focused on keeping the public language surface, package metadata, release artifacts, and documentation aligned for the stable `v1.1.0` release line.

For `v1.1.0`, the project should keep the following surfaces aligned:

- a clear package/version/tag convention that users can understand without reading internal notes
- a release path decision for source-only GitHub releases versus package-index publication
- stronger Host Runtime Contract closure, especially around multi-host expectations
- enough public examples that users can try the core language and host boundary without relying on private context
- no unresolved public documentation contradictions between README, release notes, roadmap, install guide, and machine-readable summaries

The stable release line is intentionally scoped to the language, public CLI, conformance, package metadata, and public documentation. Host Runtime Contract v0.2 and multi-host ecosystem work remain roadmap items, not completed stable-platform commitments.

### Version And Tag Convention

Public language release tags use language labels: `v1.1.0-pre.N` for historical GitHub-only pre-releases and `v1.1.0` for the stable language line.

The stable `v1.1.0` language release initially aligned the Python distribution version to `1.1.0`. Later `1.1.x` Python package patch releases may update packaging or documentation while keeping `language_release = v1.1.0`. Earlier pre-release packages may keep artifact versions such as `0.1.x`; do not infer stable language status from those pre-release package versions alone.

The stable `v1.1.0` release path is PyPI publication through Trusted Publishing. The project should not use long-lived PyPI API tokens for normal releases.

---

## Review Response Work Plan

Recent review feedback is being handled as a sequence of small, reviewable
changes. The current priority order is:

1. `1.1.3` release preparation.
   Align `pyproject.toml`, release notes, README/PyPI-facing text,
   machine-readable summaries, package data, manifest metadata, and
   release-check expectations for the repository features added after `1.1.2`.
2. Reader routing and documentation density.
   Keep the README first screen oriented around a 30-second reader guide, then
   move larger governance reorganization only if the public extract and package
   asset paths can stay clear.
3. Preflight and generation-eval clarity.
   Add an obviously accepted preflight example, clarify traversal estimate
   semantics, and make generation-eval report evaluated versus unevaluated
   maturity levels.
4. Readable-render executable anchors.
   Convert RRG candidate examples into a small fixture that pins canonical text
   anchors before any renderer API or CLI mode is implemented.
5. Schema-version registry.
   Centralize schema-version string constants and add a release-check entry so
   future schema bumps have one reviewable registration point.
6. Public asset generation ergonomics.
   Explore whether `_public_assets/` can eventually be derived during build or
   release preparation, reducing manual mirror churn without weakening package
   verification.

The governance framework is now strong enough for a first external host
implementation review. The most useful external contribution would be a host
or consumer maintained outside the core runtime repository, evaluated against
the existing HRC companion/formal boundary.

---

## In Progress

### 1. Host Runtime Contract v0.2 tightening

Current priority is to keep turning the host bridge from a helpful reference layer into a more reviewable contract surface.

This includes:

- clearer acceptance boundaries for `Host Runtime Contract` `§5.4`
- stronger alignment between `host-demo`, public views, and typed local query objects
- a minimal `reference-host-demo` path that consumes the typed write-envelope JSON without inheriting `LocalCogLangHost`
- more explicit handling of failed writes, `ErrorReport`, and correlated local traces

Contributions in this area are especially welcome.

### 2. Conformance and contract evidence

`CogLang` relies on executable examples more than prose alone.

Current work continues to focus on:

- turning key semantics into golden examples
- keeping spec, runtime, and CLI output aligned
- reducing places where contract claims are only implied, rather than tested
- keeping the minimal `generation-eval` fixture useful as executable evidence for AI-produced CogLang text, without presenting it as a benchmark claim

Contributions in this area are especially welcome.

### 3. Public project surface for standalone open source use

If `CogLang` is read as an independent open-source project, it needs a clearer public surface than “the language docs happen to exist”.

Current work continues to focus on:

- clearer public positioning
- clearer non-goals
- more explicit documentation for what is stable, what is directional, and what is exploratory

Contributions in this area are especially welcome.

---

## Next

### 4. Reserved operator upgrade conditions

Some `Reserved / Experimental` capabilities already have stable signatures or placeholder behavior, but they are not yet part of the default everyday surface.

`CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md` now records the public
evidence bar for moving a `Carry-forward`, `Reserved`, or `Experimental` entry
toward a more stable surface.

`CogLang_Send_Carry_Forward_Exit_Matrix_v0_1.md` applies that evidence bar to
`Send`, the remaining meaningful `Carry-forward` entry, and records what would
be needed for promotion versus downgrade to `Reserved`.

The next step is to use those criteria notes when reviewing specific candidates:

- what evidence is required before promotion
- which operators are blocked on host-side capability work
- which parts are still informative rather than contractual

Contributions in this area are especially welcome.

### 5. Host evidence hardening

`CogLang` now has both the richer `LocalCogLangHost` demo and a minimal `reference-host-demo` path. HRC v0.2 is frozen for the narrow typed write-envelope surface covered by those in-repository examples.

The repository also includes experimental Node.js examples: one standard-library
consumer for HRC schema/envelope samples, and one minimal host/runtime stub that
exercises tiny `execute` / `validate` and typed write-envelope success/failure
paths. These examples are companion evidence, not an expansion of the HRC v0.2
frozen scope.

The companion/formal asset decision is recorded in
`CogLang_HRC_Companion_Asset_Classification_v0_1.md`. Public CI now runs the
frozen HRC evidence commands, `coglang host-demo` and
`coglang reference-host-demo`, against both built distribution paths. The likely
next step is:

- eventually, a host example maintained outside the core runtime repository

Contributions in this area are especially welcome.

### 6. Readable render as a more explicit subsystem

`canonical text` is currently the stability anchor.

`CogLang_Readable_Render_Boundary_v0_1.md` records the first public boundary
between canonical text, display-only readable rendering, and structured
transport envelopes.

`CogLang_Readable_Render_Golden_Example_Candidates_v0_1.md` now records
candidate display examples and invariants for future renderer work without
freezing a renderer API.

`CogLang_Readable_Render_API_Promotion_Checklist_v0_1.md` now records the
API, CLI, host/transport, packaging, and test gates that must be answered before
candidate examples are promoted into implementation.

The next implementation step is to draft or accept a small API proposal only
after those gates are answered:

- a small `to_readable()` or equivalent API proposal
- tests proving canonicalization, parsing, and transport envelopes are unchanged
- CLI/API documentation only if a public readable mode is deliberately added
- less ambiguity for tooling and UI consumers

Contributions in this area are especially welcome.

---

## Exploring

### 7. LSP and editor support

Longer-term, `CogLang` would benefit from lightweight authoring support:

- syntax-aware editing
- canonicalization-aware formatting
- fast validation feedback

This is a direction, not a commitment.

Contributions in this area are especially welcome.

### 8. Richer profile and capability tooling

The current `profile / capability` story is already important, but tooling around it is still minimal.

Longer-term exploration includes:

- stronger manifest tooling
- clearer extension declarations
- better host-side rejection and diagnostics before execution

This is a direction, not a commitment.

Contributions in this area are especially welcome.

### 9. Cross-host conformance kits

`CogLang` becomes more useful as more than one host can run the same expectations.

Longer-term exploration includes:

- portable conformance bundles
- host-neutral fixtures
- easier evidence that the language core survives outside any single runtime

This is a direction, not a commitment.

Contributions in this area are especially welcome.

### 10. Semantic-event audit examples

`CogLang` fits naturally as a semantic-event audit layer for AI systems that
produce graph operations.

Longer-term exploration includes small, runnable examples for:

- agent memory or RAG knowledge-graph write preflight
- OpenTelemetry sidecar metadata carrying canonical CogLang intent
- MCP or tool-wrapper preflight for graph operations
- human review artifacts showing canonical expression, planned graph diff,
  capability requirements, and host-visible outcome

This is a direction, not a commitment. These examples should complement agent
frameworks, tool protocols, and observability stacks rather than replace them.

Contributions in this area are especially welcome.

---

## Not What This File Is For

This file is not intended to be:

- a performance scorecard
- a competitive comparison table
- a promise that all listed work will ship
- a calendar

If a capability is not already committed in a release note or contract document, treat it as direction rather than guarantee.

---

## One-Sentence Summary

The roadmap for `CogLang` is to make it more stable as an auditable graph-first intermediate language, while keeping direction and vision explicit without turning either into accidental release promises.
