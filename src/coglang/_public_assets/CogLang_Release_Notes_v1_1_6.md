# CogLang Release Notes v1.1.6

**Status**: Python package maintenance patch
**Python distribution version**: `1.1.6`
**Language release**: `v1.1.0`
**Audience**: users, release maintainers, host implementers, downstream experiment maintainers, and reviewers
**Purpose**: publish the Rosetta-driven runtime and documentation maintenance patch without changing language semantics

---

## 0. Release Positioning

CogLang `1.1.6` is a package-level maintenance patch for the stable `v1.1.0`
language line.

It does not change CogLang language syntax, canonical text rules, or the
`v1.1.0` conformance contract.

The package version changes to `1.1.6`, while CLI metadata continues to report:

- `version`: `1.1.6`
- `language_release`: `v1.1.0`

## 1. Why This Patch Exists

This release responds to concrete downstream feedback from a model-to-model
communication experiment that used CogLang as a symbolic relay and executable
evidence layer.

The feedback exposed three practical integration issues:

- host-runtime write-envelope names were easy to mistake for callable CogLang
  expression heads;
- `Unify[]` and `Match[]` could leak a Python `IndexError` on wrong arity
  instead of returning a CogLang error value;
- downstream prompts and tests needed a public way to enumerate executable
  expression heads without relying on private executor internals.

## 2. What Changed

- `Unify` and `Match` now return a CogLang error value for wrong arity:
  `TypeError[head, "arity", "expected 2 args"]`.
- `LocalCogLangHost.available_operators()` returns executable expression heads
  for the host's current executor.
- `LocalCogLangHost.operator_inventory()` returns executable heads, eager
  dispatch heads, special forms, user-defined heads, and host API-only names as
  separate categories.
- `coglang info --operators` exposes the same operator inventory through the
  CLI in JSON or text form.
- Public docs now explicitly classify `WriteBundleCandidate`,
  `WriteBundleSubmissionMessage`, and `WriteResult` as host API-only typed
  envelope names, not `Do[...]`-callable expression operators.
- Public asset mirrors and package data include the updated release-facing docs
  and this release note.

## 3. What Did Not Change

This release does not:

- promote `WriteBundleCandidate`, `WriteBundleSubmissionMessage`, or
  `WriteResult` into executable CogLang expression heads;
- change the `Create / Update / Delete` graph-write language surface;
- expand HRC v0.2 beyond the narrow typed write-envelope evidence path;
- add provider SDK dependencies;
- change parser syntax, canonical serialization, or stable `v1.1.0`
  conformance examples;
- publish a new JavaScript SDK, VS Code Marketplace extension, or multi-host
  runtime standard.

Downstream senders should continue to express write intent with ordinary
CogLang graph-write operators such as `Create / Update / Delete`, then use a
host API such as `LocalCogLangHost.execute_with_candidate(...)` or
`prepare_submission_message(...)` to inspect or submit the captured typed
envelope.

## 4. Recommended Checks

For a minimum user install:

```powershell
pip install coglang
coglang info
coglang info --operators
coglang release-check
coglang execute 'Equal[1, 1]'
```

For source checkout validation before spending remote workflow minutes:

```powershell
python -m pytest
python scripts/local_ci.py --profile quick
python scripts/local_ci.py --profile package
```

For downstream prompt regression checks:

```python
from coglang import LocalCogLangHost

host = LocalCogLangHost()
assert {"Create", "Query", "Trace"}.issubset(host.available_operators())
assert "WriteBundleCandidate" in host.operator_inventory()["host_api_only"]
assert "WriteBundleCandidate" not in host.available_operators()
```

## 5. One-Sentence Summary

CogLang `1.1.6` packages a downstream-driven maintenance patch that preserves
the stable `v1.1.0` language line while fixing `Unify` / `Match` arity errors
and making executable operator discovery explicit.
