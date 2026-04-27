# CogLang Release Notes v1.1.0

**Status**: stable language release
**Version label**: `v1.1.0`
**Python distribution version**: `1.1.0`
**Audience**: users, implementers, host integrators, and contributors
**Purpose**: define the public commitments and non-commitments for CogLang v1.1.0

---

## 0. Release Positioning

CogLang v1.1.0 is a stable language release and reference implementation for a graph-first intermediate language designed for LLM-generated graph queries and updates.

It is intended to sit between a language model and a graph-backed host, so generated operations can be parsed, validated, inspected, traced, and denied before they are allowed to affect a host system.

This release aligns three public version surfaces:

- GitHub release tag: `v1.1.0`
- Python distribution version: `1.1.0`
- CLI `language_release`: `v1.1.0`

## 1. What This Release Commits To

CogLang v1.1.0 commits to the following public surfaces:

- The canonical M-expression language form documented in `CogLang_Specification_v1_1_0_Draft.md`.
- The public CLI entry point `coglang`.
- The documented command surface exposed through `coglang info`, `coglang manifest`, `coglang bundle`, `coglang smoke`, and `coglang release-check`.
- The executable conformance cases documented in `CogLang_Conformance_Suite_v1_1_0.md` and covered by the test suite.
- Error-as-value behavior for documented language operators.
- Profile and capability boundaries documented in `CogLang_Profiles_and_Capabilities_v1_1_0.md`.
- Operator status and call-surface summaries documented in `CogLang_Operator_Catalog_v1_1_0.md`.
- A local reference host bridge and Host Runtime Contract v0.x materials for reviewable host integration experiments.
- English-first public documentation, with Chinese companion translations where provided.
- Apache-2.0 licensing for the public repository.

## 2. What This Release Does Not Commit To

CogLang v1.1.0 does not claim the following:

- It is not a general-purpose programming language.
- It is not a schema definition language.
- It is not a replacement for Cypher, SPARQL, GQL, or any native graph database query language in that system's native setting.
- It does not claim benchmark superiority over other graph languages.
- It does not expose Python internal modules as a stable public API unless that surface is explicitly documented.
- It does not freeze a complete multi-host runtime standard.
- It does not promise a mature extension ecosystem, LSP integration, or IDE support in this release.

## 3. Stability Scope

The stable v1.1.0 commitment applies to:

- language syntax and canonicalization behavior documented for the current release
- documented operator semantics and conformance examples
- public CLI command names and documented JSON payload shapes
- release metadata paths used by `manifest`, `bundle`, and `release-check`
- public documentation boundaries and non-goals

The stable v1.1.0 commitment does not apply to:

- private helper functions
- internal Python module layout
- experimental or reserved operators beyond their documented status
- future Host Runtime Contract v0.2+ decisions
- unreleased ecosystem tooling

## 4. Upgrade Notes From v1.1.0-pre

The stable release keeps the pre-release language target and closes the public release metadata gap:

- `COGLANG_LANGUAGE_RELEASE` changes from `v1.1.0-pre` to `v1.1.0`.
- The Python package version changes from `0.1.0` to `1.1.0`.
- The active release notes document changes from `CogLang_Release_Notes_v1_1_0_pre.md` to `CogLang_Release_Notes_v1_1_0.md`.
- PyPI publication uses Trusted Publishing and does not require a long-lived PyPI API token.
- GitHub-only pre-release tags remain historical source releases and should not be backfilled to PyPI.

## 5. Installation

For the stable release artifact:

```powershell
pip install coglang
coglang manifest
coglang release-check
```

For source development:

```powershell
pip install -e .[dev]
python -m pytest
```

## 6. Release Checklist

A release artifact should pass:

- `python -m pytest`
- `python -m build`
- fresh virtual environment wheel installation
- `coglang manifest`
- `coglang release-check`
- `coglang smoke`

The public release workflow publishes only stable `v*` tags whose tag name matches the Python distribution version.

## 7. One-Sentence Summary

CogLang v1.1.0 is a stable language and CLI release for auditable LLM-generated graph operations, with clear public boundaries around what is stable, what remains host-contract work, and what is intentionally out of scope.
