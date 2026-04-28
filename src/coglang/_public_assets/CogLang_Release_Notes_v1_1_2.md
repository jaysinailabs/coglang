# CogLang Release Notes v1.1.2

**Status**: Python package host-contract evidence patch
**Python distribution version**: `1.1.2`
**Language release**: `v1.1.0`
**Audience**: users evaluating CogLang's host-runtime boundary
**Purpose**: add second-host evidence and record the HRC v0.2 frozen typed write-envelope scope without changing language semantics

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
- `CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md` records the HRC v0.2 frozen
  typed write-envelope scope, evidence, non-scope, and compatibility policy.
- Public docs and LLM retrieval summaries now list the new host demo and HRC
  final freeze record.

## 2. What Did Not Change

This release does not freeze:

- a network transport protocol
- an external database persistence contract
- a normative cross-language JSON Schema pack
- a third-party host implementation maintained outside this repository
- final `KnowledgeMessage` cross-service standardization
- capability-manifest negotiation

The HRC v0.2 record is frozen only for the narrow typed write-envelope surface
covered by `host-demo`, `reference-host-demo`, and the package tests. It is not
a final frozen multi-host standard.

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

CogLang `1.1.2` adds a minimal second-host demo and freezes the narrow HRC v0.2
typed write-envelope surface while keeping the stable `v1.1.0` language
semantics unchanged.
