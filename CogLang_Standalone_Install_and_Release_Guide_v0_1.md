# CogLang Standalone Install and Release Guide v0.1

**Status**: stable release companion document
**Audience**: users, implementers, and release maintainers trying `CogLang` as a standalone language component for the first time
**Purpose**: explain how to install, verify, and try `CogLang` with minimal setup, and clarify the boundary between stable language release and host-ecosystem roadmap work

---

## 0. What This Document Covers

The stable `v1.1.0` distribution path is PyPI publication through Trusted Publishing.
When readers only inspect the source tree, they can usually find where the code lives, but it is less obvious how to try `CogLang` first as an independent language core.

This document answers four practical questions:

1. How to install and run `CogLang` today
2. Which commands to run first after installation
3. What the current minimum standalone tool surface includes
4. What remains roadmap work beyond the stable language release

---

## 1. Current Minimum Installation Path

The stable release artifact is installed from PyPI:

```powershell
pip install coglang
```

After installation, the following entry point should be available:

```powershell
coglang info
```

Notes:

- `CogLang` already provides an independent console script named `coglang`.
- Stable releases are published through PyPI Trusted Publishing, not long-lived API tokens.

For source development, use:

```powershell
pip install -e ".[dev]"
```

The stable `v1.1.0` language release initially aligned the Python distribution version to the language release (`1.1.0` for tag `v1.1.0`). Later `1.1.x` Python distribution patches may update packaging or documentation while keeping `language_release = v1.1.0`.

Pre-release tags such as `v1.1.0-pre.0` remain GitHub-only unless a later release decision explicitly changes that policy.

---

## 2. Minimum Post-Install Acceptance Path

After installation, run the checks in this order.

### 2.1 Metadata and Command Entry Point

```powershell
coglang info
```

This should report:

- the current distribution version
- the current language release label
- available commands
- the conformance suite name

In the stable release shape, these two version meanings are aligned. In historical pre-release or source-development shapes, they should still be read separately:

- `version` reflects the installed distribution metadata version.
- `language_release` reflects the public `CogLang` language/specification label.

For stable `v1.1.0`, the initial stable release intentionally converged these two layers: the GitHub tag was `v1.1.0`, the Python package version was `1.1.0`, and `language_release` reported `v1.1.0`. Later package-only patch releases may report a Python package version such as `1.1.1` while continuing to report `language_release = v1.1.0`.

### 2.2 Environment Self-Check

```powershell
coglang doctor
```

This should check:

- Python version
- temporary directory access
- the minimum parse / validate / execute path
- whether `pytest` is available

### 2.3 Minimum Release Artifact Check

```powershell
coglang release-check
```

This should pass in the stable release artifact and in source-development checkouts.
It does not claim that every language capability is complete. It checks that the minimum release artifacts are present, including:

- `pyproject.toml`
- `LICENSE`
- distribution metadata
- console script declaration
- runtime entry integrity
- primary Specification / Quickstart / Conformance / Host Runtime Contract documents
- public entry documents: `README / ROADMAP / MAINTENANCE / llms.txt / llms-full.txt`

### 2.4 Single Release Summary for Scripts and CI

```powershell
coglang bundle
```

This combines the following layers into one summary:

- `manifest`
- `release-check`
- `doctor`

If you are wiring `CogLang` into scripts, CI, or a minimum release flow, prefer this summary instead of parsing several command outputs separately.

The current machine-readable payloads for `manifest` / `bundle` may still expose implementation metadata.
For public usage, treat `entrypoints.recommended = "coglang"` as the supported entry point instead of treating implementation module paths as the public main entry.

### 2.5 Source-Checkout Public Asset Mirror Maintenance

For maintainers working in a source checkout or materialized public extract,
this helper checks whether exact public files and their packaged
`_public_assets/` mirrors are aligned:

```powershell
coglang public-assets
```

To repair exact file mirrors after editing public documents, run:

```powershell
coglang public-assets --sync
```

This is a source-checkout maintenance helper. It is not part of the minimum
stable runtime command surface, and it does not replace `release-check`.

### 2.6 Minimum Consistency Path

```powershell
coglang conformance smoke
```

### 2.7 Minimum End-to-End Example

```powershell
coglang demo
```

### 2.8 Host Integration Guidance

If you are integrating `CogLang` from a host implementer's perspective, do not use this install guide as the source for reference-implementation internals.
Use this document instead:

- `CogLang_Host_Runtime_Contract_v0_1.md`

This guide only keeps the minimum public install, command, and trial paths.

---

## 3. Current Minimum Standalone Tool Surface

The current recommended standalone tool entry points are:

- `parse`
- `canonicalize`
- `validate`
- `preflight`
- `preflight-fixture`
- `execute`
- `conformance`
- `repl`
- `info`
- `manifest`
- `bundle`
- `doctor`
- `vocab`
- `examples`
- `generation-eval`
- `smoke`
- `demo`
- `host-demo`
- `reference-host-demo`
- `release-check`

This means `CogLang` is no longer only a specification plus a reference runtime. It also has a minimum tool surface that can be tried independently.
If help output shows additional reference commands, those commands do not automatically become stable public commitments.

---

## 4. Recommended Public Positioning

Current suitable terms:

- `stable language release`
- `reference implementation`
- `language core + host bridge`

Current unsuitable terms:

- mature standalone language platform
- complete host-independent runtime
- stable extension ecosystem
- multi-host consistent release product

---

## 5. What It Is Not Yet

Even though `CogLang` can already be installed and tried, it is still not:

1. a general-purpose programming language
2. a stable multi-host runtime standard
3. a mature extension ecosystem
4. a platform validated across multiple independent hosts

Keep "stable language release" strictly separate from "fully standalone and mature platform."

---

## 6. Stable v1.1.0 Release Policy

Stable `v1.1.0` is the first target where package-index publication should be part of the normal release path.

The release policy is:

- GitHub pre-releases such as `v1.1.0-pre.0` are source-only and should not be backfilled to PyPI.
- The stable GitHub tag is `v1.1.0`.
- The initial stable Python distribution version is `1.1.0`; package-only patch releases may use later `1.1.x` Python distribution versions.
- PyPI publishing should use Trusted Publishing from GitHub Actions.
- Normal releases should not use long-lived PyPI API tokens.
- The publishing workflow must verify that the tag and `pyproject.toml` package version match before uploading artifacts.

PyPI Trusted Publishing is configured for:

- PyPI project: `coglang`
- GitHub repository: `jaysinailabs/coglang`
- Workflow filename: `publish.yml` (the workflow file lives at `.github/workflows/publish.yml` in this repository)
- Environment name: `pypi`

The checked-in publish workflow is intentionally inert for ordinary pushes. It only runs on matching Git tags and refuses to publish non-stable tags or mismatched package versions.

The `1.1.3` package release exercised this path end to end, and later
`1.1.x` package patches should continue to use the same path:

- a stable `v1.1.x` tag triggered Trusted Publishing
- GitHub Actions built and validated the wheel before upload
- PyPI received both the wheel and sdist
- a GitHub Release exists for the tag and uses the package release notes
- post-publish verification installed the released `coglang[dev]==1.1.x` from PyPI and ran `release-check` plus `smoke`

---

## 7. Remaining Gaps After Package v1.1.x

The most realistic next gaps are now:

1. **External host or consumer review**
   Accept or link a first host or consumer maintained outside the core runtime repository.
2. **More stable Host Runtime Contract**
   Lower the integration cost for external hosts.
3. **Public asset generation ergonomics**
   Reduce manual `_public_assets/` mirror churn without weakening package verification.
4. **More complete release automation**
   For example, release notes generation and repeatable GitHub Release creation.

---

## 8. Recommended Trial Sequence

If you only want to verify that `CogLang` can run independently from PyPI, use this minimum path:

1. `pip install coglang`
2. `coglang info`
3. `coglang release-check`
4. `coglang execute 'Equal[1, 1]'`

For packaged smoke and conformance checks, install the development extra first:

1. `pip install "coglang[dev]"`
2. `coglang smoke`
3. `coglang demo`
4. `coglang conformance smoke`

If these checks pass, continue with:

- `CogLang_Quickstart_v1_1_0.md`
- `CogLang_Specification_v1_1_0_Draft.md`
- `CogLang_Host_Runtime_Contract_v0_1.md`
- `CogLang_Release_Notes_v1_1_0.md`

---

## 9. One-Sentence Summary

`CogLang` now has a stable language release path, command entry point, consistency run, and release artifact check.
That is enough for stable language use, while multi-host maturity and ecosystem tooling remain explicit roadmap work.
