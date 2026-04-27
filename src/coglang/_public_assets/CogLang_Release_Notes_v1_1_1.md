# CogLang Release Notes v1.1.1

**Status**: Python package documentation patch
**Python distribution version**: `1.1.1`
**Language release**: `v1.1.0`
**Audience**: users installing CogLang from PyPI for the first time
**Purpose**: correct first-run installation guidance without changing language semantics

---

## 0. Release Positioning

CogLang `1.1.1` is a package-level patch release for the stable `v1.1.0` language line.

It does not change the CogLang language surface, operator semantics, conformance suite, or Host Runtime Contract posture.

The package version changes to `1.1.1`, while CLI metadata continues to report:

- `version`: `1.1.1`
- `language_release`: `v1.1.0`

## 1. What Changed

This release corrects public first-run documentation in the PyPI package and README:

- The minimum PyPI install verification path now uses `coglang info`, `coglang release-check`, and `coglang execute 'Equal[1, 1]'`.
- `coglang smoke`, `coglang doctor`, and packaged conformance checks now explicitly require `pytest`, normally installed through `pip install "coglang[dev]"`.
- Quickstart status wording now reflects the stable release posture rather than pre-release wording.

## 2. What Did Not Change

This release does not change:

- parser behavior
- validator behavior
- executor behavior
- canonical text rules
- documented operator semantics
- public language release label
- PyPI Trusted Publishing policy

## 3. Recommended Install Checks

For a minimum user install:

```powershell
pip install coglang
coglang info
coglang release-check
coglang execute 'Equal[1, 1]'
```

For packaged smoke and conformance checks:

```powershell
pip install "coglang[dev]"
coglang doctor
coglang smoke
coglang conformance smoke
```

## 4. One-Sentence Summary

CogLang `1.1.1` fixes PyPI first-run guidance so users do not run pytest-backed smoke checks before installing the development extra.
