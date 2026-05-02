# CogLang Release Notes v1.1.4

**Status**: Python package maintenance patch
**Python distribution version**: `1.1.4`
**Language release**: `v1.1.0`
**Audience**: users, release maintainers, and reviewers
**Purpose**: align post-`1.1.3` release governance and release-check evidence without changing language semantics

---

## 0. Release Positioning

CogLang `1.1.4` is a package-level maintenance patch for the stable `v1.1.0`
language line.

It does not change CogLang language syntax, operator semantics, canonical text
rules, or the `v1.1.0` conformance contract.

The package version changes to `1.1.4`, while CLI metadata continues to report:

- `version`: `1.1.4`
- `language_release`: `v1.1.0`

## 1. What Changed

- `coglang release-check` now includes a `public_assets_mirror` gate in source
  and public-extract layouts, using the existing mirror checker to fail when
  exact package-data mirror files are missing or drift from their root sources.
- Installed package mode treats the source/mirror comparison as not applicable,
  so wheel and sdist users are not asked to compare files that are not present
  outside the packaged `_public_assets/` tree.
- The release-check text and JSON output now make public asset mirror coverage
  explicit.
- The v1.1.3 GitHub Release and PyPI Trusted Publishing completion are recorded
  in the roadmap and standalone install/release guide.
- The standalone install/release guide now lists the current public CLI surface,
  including preflight, generation-eval, host-demo, and reference-host-demo.

## 2. What Did Not Change

This release does not freeze:

- v1.2 language syntax
- a public readable-render API
- a benchmark claim for `generation-eval`
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

For packaged smoke and conformance checks:

```powershell
pip install "coglang[dev]"
coglang doctor
coglang smoke
coglang conformance smoke
```

For source checkout release-gate validation:

```powershell
python -m pytest
python -m coglang release-check --format text
```

## 4. One-Sentence Summary

CogLang `1.1.4` makes public asset mirror drift a first-class `release-check`
gate and records the completed `1.1.3` publication path, while keeping stable
`v1.1.0` language semantics unchanged.
