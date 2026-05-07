# CogLang AI Operator Guide

Status: public AI/operator entry point
Audience: AI coding agents, maintainers, and reviewers working in this repository
Authority: routing and operating guidance only; executable tests, release-check, specifications, and release notes remain authoritative
Scope: preserves CogLang boundaries while helping AI agents work safely and efficiently
Stability: valid for the stable `v1.1.0` language line and source package `1.1.5`
Read after: `README.md`

CogLang is an independent open-source project. Treat this file as an operating
index, not a hidden specification and not a substitute for the public contract
documents.

## Project Boundary

CogLang is a graph-first intermediate language for LLM-proposed graph
operations. Its public value is inspectable intent: parse, canonicalize,
validate, preflight, review, hash, trace, and replay graph operations before a
host trusts them.

Keep these boundaries explicit:

- Stable language core: `v1.1.0`.
- Python package version may move independently from the language release.
- HRC v0.2 is frozen only for the narrow typed write-envelope evidence path.
- Node, grammar, editor, bridge, and pressure-test examples are companion evidence.
- Future v1.2 notes are proposals unless executable evidence and release decisions promote them.
- External project pressure belongs first in adapters, host bridges, policy packs, fixtures, or examples, not in CogLang Core.

## Authority Order

When files disagree, prefer evidence in this order:

1. runnable tests, fixtures, and example outputs
2. `coglang release-check --format text`
3. stable specification, conformance suite, operator catalog, and release notes
4. HRC freeze and companion asset classification documents
5. README, ADOPTING, CONTRIBUTING, ROADMAP, and MAINTENANCE
6. proposal, promotion, announcement, and outreach material

Do not promote roadmap or proposal text into stable behavior without an
explicit implementation and review step.

## First Commands

From a source checkout with the console script installed:

```powershell
coglang release-check --format text
coglang smoke
python scripts/local_ci.py --profile quick
```

If `coglang` is not on `PATH`, use the module entry point:

```powershell
python -m coglang release-check --format text
python -m coglang smoke
```

In this Windows checkout, the local virtual environment form is:

```powershell
.\.venv\Scripts\python.exe -m coglang release-check --format text
.\.venv\Scripts\python.exe scripts\local_ci.py --profile quick
```

Do not trigger remote GitHub Actions by default. The project is local-first
because maintainer remote CI minutes are limited.

## Change-Type Gates

Use the smallest gate set that matches the change.

Documentation entry or routing changes:

```powershell
python -m coglang public-assets --format text
python -m coglang release-check --format text
git diff --check
```

Parser, validator, vocabulary, or language semantics:

```powershell
python -m pytest tests/coglang/test_parser.py tests/coglang/test_validator.py tests/coglang/test_graph_ops.py tests/coglang/test_preflight.py
python -m coglang release-check --format text
```

Executor or unification behavior:

```powershell
python -m pytest tests/coglang/test_executor_interface.py tests/coglang/test_unify.py tests/coglang/test_graph_ops.py
python -m coglang smoke
```

Host or HRC boundary:

```powershell
python -m pytest tests/coglang/test_local_host.py tests/coglang/test_node_host_consumer.py tests/coglang/test_node_minimal_host_runtime_stub.py
python -m coglang host-demo --format text
python -m coglang reference-host-demo --format text
python -m coglang release-check --format text
```

Packaging, public extract, or mirrored public assets:

```powershell
python -m pytest tests/coglang/test_open_source_extract.py tests/coglang/test_public_assets_mirror.py tests/coglang/test_package_asset_audit_script.py
python -m coglang public-assets --format text
python -m coglang release-check --format text
```

Before release preparation:

```powershell
python scripts/local_ci.py --profile quick
python scripts/local_ci.py --profile package
```

## Documentation Roles

Use the public docs this way:

- `ADOPTING.md`: human decision entry point.
- `AGENTS.md`: AI/operator entry point.
- `README.md`: public index and shortest first-run path.
- `CogLang_Quickstart_v1_1_0.md`: first-pass user guide.
- `CogLang_Specification_v1_1_0_Draft.md`: language semantics.
- `CogLang_Conformance_Suite_v1_1_0.md`: executable language examples.
- `CogLang_Operator_Catalog_v1_1_0.md`: operator status and surface.
- `CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md`: frozen HRC v0.2 evidence scope.
- `CogLang_HRC_Companion_Asset_Classification_v0_1.md`: formal versus companion HRC assets.
- `ROADMAP.md`: direction, not a release contract.
- `MAINTENANCE.md`: project status and slowdown/freeze policy.

Private `.private/` notes can help continuity, but do not treat them as public
contract material.

## Do Not

- Do not expand parser or vocabulary because a pressure test suggests an elegant idea.
- Do not expand HRC v0.2 without a dedicated evidence path and scope decision.
- Do not present companion examples as SDKs, normative schemas, hosted products, or platform commitments.
- Do not add provider SDK dependencies to Core for generation evaluation.
- Do not make broad CLI refactors unless a clear boundary is identified.
- Do not move public documents casually; this project depends on stable paths.
- Do not touch `.claude/` unless explicitly asked.

## Preferred Next-Step Shape

When continuing work, prefer:

1. one small adoption or evidence problem
2. one scoped patch
3. focused tests
4. `release-check`
5. `git diff --check`
6. a commit that can be reverted cleanly

The healthiest project direction is external-use evidence, not more speculative
language surface.
