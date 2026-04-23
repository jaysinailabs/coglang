# CogLang Roadmap

**Status**: public roadmap  
**Scope**: direction layer, not stability guarantees  
**Audience**: readers, implementers, and contributors who want to know where `CogLang` is going next

---

## How To Read This File

This file is intentionally not a release contract.

Use the docs this way:

- `CogLang_Release_Notes_v1_1_0_pre.md`: what is currently promised
- `ROADMAP.md`: what is currently prioritized or being explored
- `MAINTENANCE.md`: how the project may slow down, freeze, transfer, or archive

This roadmap does not promise dates.

It separates three levels:

- `In Progress`: work currently being pushed forward
- `Next`: work that has been chosen as likely next, but is not yet complete
- `Exploring`: long-range directions that are intentionally non-binding

---

## In Progress

### 1. Host Runtime Contract v0.2 tightening

Current priority is to keep turning the host bridge from a helpful reference layer into a more reviewable contract surface.

This includes:

- clearer acceptance boundaries for `Host Runtime Contract` `§5.4`
- stronger alignment between `host-demo`, public views, and typed local query objects
- more explicit handling of failed writes, `ErrorReport`, and correlated local traces

Contributions in this area are especially welcome.

### 2. Conformance and contract evidence

`CogLang` relies on executable examples more than prose alone.

Current work continues to focus on:

- turning key semantics into golden examples
- keeping spec, runtime, and CLI output aligned
- reducing places where contract claims are only implied, rather than tested

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

The next step is to make their promotion path easier to understand:

- what evidence is required before promotion
- which operators are blocked on host-side capability work
- which parts are still informative rather than contractual

Contributions in this area are especially welcome.

### 5. Second independent host example

`CogLang` already has a local reference host path. A next priority is to make its host story easier to trust outside that single path.

The likely next step is:

- a second minimal host example with weaker assumptions
- a clearer demonstration that `CogLang` can be integrated without inheriting the entire reference runtime shape

Contributions in this area are especially welcome.

### 6. Readable render as a more explicit subsystem

`canonical text` is currently the stability anchor.

A likely next step is to separate the human-facing rendering story more cleanly:

- clearer readable rendering rules
- clearer boundaries between canonical form, readable form, and transport envelopes
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
