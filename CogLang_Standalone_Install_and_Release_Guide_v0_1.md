# CogLang Standalone Install and Release Guide v0.1

**Status**: pre-release companion document
**Audience**: users, implementers, and release maintainers trying `CogLang` as a standalone language component for the first time
**Purpose**: explain how to install, verify, and try `CogLang` with minimal setup, and clarify the boundary between "publicly trialable" and "fully standalone release"

---

## 0. What This Document Covers

The current pre-release distribution path is still source-based installation.
When readers only inspect the source tree, they can usually find where the code lives, but it is less obvious how to try `CogLang` first as an independent language core.

This document answers four practical questions:

1. How to install and run `CogLang` today
2. Which commands to run first after installation
3. What the current minimum standalone tool surface includes
4. What is still missing before a fully standalone release

---

## 1. Current Minimum Installation Path

The minimum supported path is still **installing from source**:

```powershell
pip install -e .
```

After installation, the following entry point should be available:

```powershell
coglang info
```

Notes:

- `CogLang` already provides an independent console script named `coglang`.
- It is not yet published through a package index such as PyPI.

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

In the current source-distribution shape, these two version meanings should be read separately:

- `version` reflects the installed distribution metadata version.
- `language_release` reflects the public `CogLang` language/specification label.

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

This should pass in the current pre-release source distribution.
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

### 2.5 Minimum Consistency Path

```powershell
coglang conformance smoke
```

### 2.6 Minimum End-to-End Example

```powershell
coglang demo
```

### 2.7 Host Integration Guidance

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
- `execute`
- `conformance`
- `repl`
- `info`
- `manifest`
- `bundle`
- `doctor`
- `vocab`
- `examples`
- `smoke`
- `demo`
- `host-demo`
- `release-check`

This means `CogLang` is no longer only a specification plus a reference runtime. It also has a minimum tool surface that can be tried independently.
If help output shows additional reference commands, those commands do not automatically become stable public commitments.

---

## 4. Recommended Public Positioning

Current suitable terms:

- `experimental`
- `pre-release`
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

1. a language project published through a package index
2. a reference implementation fully decoupled from the current source-distribution shape
3. a standalone release product with formal release automation
4. a stable platform validated across multiple hosts

Keep "trialable" strictly separate from "fully standalone and mature."

---

## 6. Remaining Gaps Before a Fully Standalone Release

The most realistic next gaps are:

1. **Package-index publication**
   Let users install it without cloning the repository first.
2. **Release metadata and version cadence**
   Make package publication, artifact validation, and language-release labels easier to follow.
3. **More stable Host Runtime Contract**
   Lower the integration cost for external hosts.
4. **At least one non-reference host demo**
   Show that this is not a private in-project DSL.
5. **More complete release automation**
   For example, wheel/sdist verification, release smoke path, and version cadence guidance.

---

## 7. Recommended Trial Sequence

If you only want to verify that `CogLang` can run independently, use these five steps:

1. `pip install -e .`
2. `coglang bundle`
3. `coglang smoke`
4. `coglang demo`
5. `coglang conformance smoke`

If all five steps pass, continue with:

- `CogLang_Quickstart_v1_1_0.md`
- `CogLang_Specification_v1_1_0_Draft.md`
- `CogLang_Host_Runtime_Contract_v0_1.md`
- `CogLang_Release_Notes_v1_1_0_pre.md`

---

## 8. One-Sentence Summary

`CogLang` now has a minimum standalone install path, command entry point, consistency run, and release artifact check.
That is enough for experimental public trial use, but not enough to claim that standalone release maturity is complete.
