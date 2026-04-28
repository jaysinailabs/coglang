# CogLang Release Notes v1.1.2

**Status**: Python package host-contract evidence patch
**Python distribution version**: `1.1.2`
**Language release**: `v1.1.0`
**Audience**: users evaluating CogLang's host-runtime boundary
**Purpose**: add second-host evidence and record the HRC v0.2 freeze-candidate scope without changing language semantics

---

## 0. Release Positioning

CogLang `1.1.2` is a package-level patch release for the stable `v1.1.0`
language line.

It does not change CogLang language syntax, operator semantics, canonical text
rules, or the `v1.1.0` conformance contract.

The package version changes to `1.1.2`, while CLI metadata continues to report:

- `version`: `1.1.2`
- `language_release`: `v1.1.0`

## 1. What Changed

This release adds public, executable evidence for host-runtime review:

- `coglang reference-host-demo` demonstrates a minimal second host path that
  consumes `WriteBundleSubmissionMessage` JSON and returns
  `WriteBundleResponseMessage` without depending on `LocalCogLangHost`.
- `ReferenceTransportHost` is exported as a small reference host implementation
  for typed write-envelope submission and local query/header lookup.
- `CogLang_HRC_v0_2_Freeze_Candidate_2026_04_28.md` records the HRC v0.2
  freeze-candidate scope, evidence, non-scope, and promotion criteria.
- Public docs and LLM retrieval summaries now list the new host demo and HRC
  freeze-candidate record.

## 2. What Did Not Change

This release does not freeze:

- a network transport protocol
- an external database persistence contract
- a normative cross-language JSON Schema pack
- a third-party host implementation maintained outside this repository
- final `KnowledgeMessage` cross-service standardization
- capability-manifest negotiation

The HRC v0.2 record is a `freeze-candidate`, not a final frozen multi-host
standard. Promotion to `frozen` still requires public CI and maintainer review.

## 3. Recommended Checks

For a minimum user install:

```powershell
pip install coglang
coglang info
coglang release-check
coglang execute 'Equal[1, 1]'
```

For host-runtime evidence:

```powershell
coglang host-demo
coglang reference-host-demo
```

For packaged smoke and conformance checks:

```powershell
pip install "coglang[dev]"
coglang doctor
coglang smoke
coglang conformance smoke
```

## 4. One-Sentence Summary

CogLang `1.1.2` adds a minimal second-host demo and an HRC v0.2 freeze-candidate
decision record while keeping the stable `v1.1.0` language semantics unchanged.
