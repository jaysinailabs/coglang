# CogLang Maintenance Policy

**Status**: public project status and maintenance policy  
**Scope**: maintenance modes, freeze conditions, and archive/transfer expectations  
**Audience**: contributors, adopters, and maintainers who need to understand what happens if project velocity changes

---

## Why This File Exists

Open-source users need more than a feature list.

They also need to know:

- whether the project is actively moving
- what “maintenance mode” would mean here
- how the project would communicate a slowdown, freeze, transfer, or archive

This file exists to make those expectations explicit.

---

## Current Mode

`CogLang` is currently in:

- `active experimental maintenance`

That means:

- the project is still evolving
- the maintainers are still willing to tighten contracts and improve public documentation
- readers should treat stability claims as coming from release and contract docs, not from feature velocity alone

---

## Maintenance Modes

### 1. Active Experimental Maintenance

This is the current mode.

Typical work includes:

- spec/runtime/conformance alignment
- CLI and documentation improvements
- host contract tightening
- carefully chosen additions that fit the language boundary

This mode does not imply rapid feature growth.

### 2. Maintenance Mode

If the project moves into maintenance mode, the default expectation becomes:

- bug fixes
- documentation clarifications
- compatibility-preserving contract work
- conformance corrections

What usually stops in this mode:

- large language-surface expansion
- new subsystems without strong maintainer support
- roadmap items that require sustained implementation bandwidth

### 3. Compatibility Freeze

If the project moves into compatibility freeze, the expectation becomes:

- published surfaces remain available as reference material
- only minimal compatibility or correctness fixes are likely
- roadmap work is effectively paused

This mode is intended to preserve trust for existing readers and integrators, even if active evolution has stopped.

### 4. Transfer Or Archive

If the project can no longer be actively maintained, maintainers should prefer one of two explicit outcomes:

- transfer to new maintainers
- archive with the status made explicit

Silent abandonment is the least desirable outcome.

---

## Possible Triggers For Maintenance Or Freeze

The following do not automatically force a transition, but they are examples of conditions that may trigger a public reassessment:

- sustained lack of maintainer capacity
- sustained absence of meaningful community use or contribution
- a decision that the remaining roadmap no longer justifies active language evolution
- emergence of a broadly adopted alternative that serves the same practical role well enough that `CogLang` no longer has a distinct maintenance case

If such a reassessment happens, the project should say so plainly rather than leaving contributors to guess.

---

## What Maintainers Owe The Community

If project status changes materially, maintainers should update:

- `README.md`
- `ROADMAP.md`
- `MAINTENANCE.md`
- the latest release note or status note

The important thing is not to promise constant velocity.

The important thing is to make status changes legible.

---

## What This Means For Contributors

If the project is in active experimental maintenance:

- contributions that tighten contracts, tests, docs, and host boundaries are usually the safest fit

If the project is in maintenance mode:

- contributions should assume a more conservative acceptance bar

If the project is in compatibility freeze:

- contributors should expect very limited scope unless maintainers explicitly reopen a line of work

---

## Relationship To Other Docs

Use these documents together:

- `CogLang_Release_Notes_v1_1_0_pre.md`: what is currently promised
- `ROADMAP.md`: what the project is trying to move toward
- `MAINTENANCE.md`: how project status may change if velocity or maintainer capacity changes

---

## One-Sentence Summary

`CogLang` aims to be explicit not only about what it is building, but also about how it would slow down, freeze, transfer, or archive if active development can no longer be sustained.
