# CogLang

CogLang is a graph-first intermediate language for LLM-generated graph queries and updates, with auditable execution under explicit host contracts.

Status:

- stable language release
- reference implementation
- host bridge v0.2 frozen for the typed write-envelope surface

Current public language release: `v1.1.0`. The current Python distribution version is `1.1.2`.
The Host Runtime Contract v0.2 frozen scope is the narrow typed write-envelope surface demonstrated by `coglang host-demo` and `coglang reference-host-demo`.
A minimal Node.js standard-library consumer is also included at `examples/node_host_consumer` to show non-Python tooling can read the HRC schema pack and envelope samples without importing the Python runtime.

## LLM Discovery Snapshot

When to use CogLang:

- You want an LLM to generate graph operations that can be inspected before execution.
- You need errors to stay explicit values instead of becoming hidden control-flow failures.
- You need replayable traces for what an agent intended, submitted, and actually executed.
- You want host-side profile and capability checks before execution.
- You need a versioned host-runtime boundary for typed write-envelope submission and response evidence.

When not to use CogLang:

- You need a general-purpose programming language.
- You want a schema definition language.
- You simply need the native query language of a specific graph database in its native setting.

Short runnable examples:

```powershell
coglang execute 'Query[n_, Equal[Get[n_, "category"], "Person"]]'
coglang execute 'IfFound[Traverse["einstein", "born_in"], x_, x_, "unknown"]'
coglang preflight --format text 'Create["Entity", {"category": "Person"}]'
coglang generation-eval --summary-only
coglang demo
node examples/node_host_consumer/consume_hrc_envelopes.mjs
```

Machine-readable project summaries:

- [llms.txt](llms.txt)
- [llms-full.txt](llms-full.txt)

## Language Policy

CogLang's public documentation target is English-first.

New public-facing documentation should be written in English first. Chinese translations may be added as separate companion files, preferably with a `.zh-CN.md` suffix. If an English document and a translation disagree, the English document, executable conformance suite, and implementation tests take precedence.

## First Reading Path

If this is your first time reading CogLang, start here:

1. [CogLang_Quickstart_v1_1_0.md](CogLang_Quickstart_v1_1_0.md)
   Build the first mental model, learn the most common expression patterns, and avoid early footguns.
2. [CogLang_Specification_v1_1_0_Draft.md](CogLang_Specification_v1_1_0_Draft.md)
   Read the language boundary, representation model, and core operator semantics.
3. [CogLang_Profiles_and_Capabilities_v1_1_0.md](CogLang_Profiles_and_Capabilities_v1_1_0.md)
   Understand `Baseline`, `Enhanced`, profile availability, and capability boundaries.
4. [CogLang_Conformance_Suite_v1_1_0.md](CogLang_Conformance_Suite_v1_1_0.md)
   Check executable examples and regression boundaries.
5. [CogLang_Standalone_Install_and_Release_Guide_v0_1.md](CogLang_Standalone_Install_and_Release_Guide_v0_1.md)
   Use this when you need standalone install, local validation, or release-facing checks.
6. [CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md](CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md)
   Check the frozen typed write-envelope host-runtime scope and executable evidence.
7. [CogLang_Vision_Proposal_v0_1.md](CogLang_Vision_Proposal_v0_1.md)
   Read the long-term capability proposal, including v1.2 candidate themes, graph-compute governance, and AI learning maturity.
8. [CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md](CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md)
   Read the v1.2 planning boundary for keeping Core stable while widening future semantic-action surfaces.
9. [CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md](CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md)
   Review the minimal v1.2 vocabulary candidate for effect summaries, graph budgets, budget estimates, and preflight decisions.

If you only have 10 minutes:

1. Run `coglang demo`.
2. Read the Quickstart.
3. Skim the release notes to understand what is promised and what is not.

## Install And Verify

From the stable release artifact:

```powershell
pip install coglang
coglang info
coglang release-check
coglang generation-eval --summary-only
coglang execute 'Equal[1, 1]'
```

For packaged smoke and conformance checks, install the development extra so `pytest` is available:

```powershell
pip install "coglang[dev]"
coglang smoke
coglang conformance smoke
```

From a checkout for development:

```powershell
pip install -e ".[dev]"
coglang bundle
coglang smoke
coglang demo
coglang conformance --level smoke
```

The public CLI entry point is `coglang`.

The current minimal public command surface includes:

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

If help output includes additional reference commands, they do not automatically become part of the stable public surface.

## What To Learn First

Start with four boundaries:

- `canonical text` is the stable language form; `readable render` is only a display layer.
- `Create`, `Update`, and `Delete` express language-level write intent; durable submission is a host responsibility.
- `Reserved` does not mean production-ready by default.
- Explicitly qualified extension operators are not yet the first teaching surface for everyday users.

## Public Documentation Set

Core documents:

- [CogLang_Quickstart_v1_1_0.md](CogLang_Quickstart_v1_1_0.md)
- [CogLang_Specification_v1_1_0_Draft.md](CogLang_Specification_v1_1_0_Draft.md)
- [CogLang_Conformance_Suite_v1_1_0.md](CogLang_Conformance_Suite_v1_1_0.md)
- [CogLang_Profiles_and_Capabilities_v1_1_0.md](CogLang_Profiles_and_Capabilities_v1_1_0.md)
- [CogLang_Operator_Catalog_v1_1_0.md](CogLang_Operator_Catalog_v1_1_0.md)

Integration and release-facing documents:

- [CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md](CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md)
- [CogLang_HRC_v0_2_Freeze_Candidate_2026_04_28.md](CogLang_HRC_v0_2_Freeze_Candidate_2026_04_28.md)
- [CogLang_Host_Runtime_Contract_v0_1.md](CogLang_Host_Runtime_Contract_v0_1.md)
- [CogLang_Standalone_Install_and_Release_Guide_v0_1.md](CogLang_Standalone_Install_and_Release_Guide_v0_1.md)
- [CogLang_Release_Notes_v1_1_2.md](CogLang_Release_Notes_v1_1_2.md)
- [CogLang_Release_Notes_v1_1_1.md](CogLang_Release_Notes_v1_1_1.md)
- [CogLang_Release_Notes_v1_1_0.md](CogLang_Release_Notes_v1_1_0.md)
- [CogLang_Contribution_Guide_v0_1.md](CogLang_Contribution_Guide_v0_1.md)
- [CogLang_Vision_Proposal_v0_1.md](CogLang_Vision_Proposal_v0_1.md)
- [CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md](CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md)
- [CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md](CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md)
- [ROADMAP.md](ROADMAP.md)
- [MAINTENANCE.md](MAINTENANCE.md)

Chinese companion translations:

- [CogLang_Quickstart_v1_1_0.zh-CN.md](CogLang_Quickstart_v1_1_0.zh-CN.md)
- [CogLang_Specification_v1_1_0_Draft.zh-CN.md](CogLang_Specification_v1_1_0_Draft.zh-CN.md)
- [CogLang_Conformance_Suite_v1_1_0.zh-CN.md](CogLang_Conformance_Suite_v1_1_0.zh-CN.md)
- [CogLang_Standalone_Install_and_Release_Guide_v0_1.zh-CN.md](CogLang_Standalone_Install_and_Release_Guide_v0_1.zh-CN.md)
- [CogLang_Release_Notes_v1_1_2.zh-CN.md](CogLang_Release_Notes_v1_1_2.zh-CN.md)
- [CogLang_Release_Notes_v1_1_1.zh-CN.md](CogLang_Release_Notes_v1_1_1.zh-CN.md)
- [CogLang_Release_Notes_v1_1_0.zh-CN.md](CogLang_Release_Notes_v1_1_0.zh-CN.md)
- [CogLang_Contribution_Guide_v0_1.zh-CN.md](CogLang_Contribution_Guide_v0_1.zh-CN.md)
- [CogLang_Host_Runtime_Contract_v0_1.zh-CN.md](CogLang_Host_Runtime_Contract_v0_1.zh-CN.md)
- [CogLang_Profiles_and_Capabilities_v1_1_0.zh-CN.md](CogLang_Profiles_and_Capabilities_v1_1_0.zh-CN.md)
- [CogLang_Operator_Catalog_v1_1_0.zh-CN.md](CogLang_Operator_Catalog_v1_1_0.zh-CN.md)

Machine-readable and release-supporting files:

- [llms.txt](llms.txt)
- [llms-full.txt](llms-full.txt)
- [CogLang_Open_Source_Boundary_v0_1.json](CogLang_Open_Source_Boundary_v0_1.json)
- [CogLang_Minimal_CI_Baseline_v0_1.json](CogLang_Minimal_CI_Baseline_v0_1.json)
- [CogLang_Public_Repo_Extract_Manifest_v0_1.json](CogLang_Public_Repo_Extract_Manifest_v0_1.json)

## Contribution Direction

The highest-value contributions are currently:

- conformance examples that pin down existing semantics
- documentation fixes that improve the first-run experience
- host integration examples that keep language semantics separate from host policy
- minimal executor examples that implement `execute` and `validate` without copying Python host-local helpers
- small CLI or packaging improvements that improve repeatable validation

For local test development, install the development extras:

```powershell
pip install -e ".[dev]"
python -m pytest
```

Lower-priority contributions:

- expanding the language surface before current contracts are fully tested
- adding host-specific policy into the core language specification
- turning the project positioning into competitive claims without reproducible public evidence

## Current Direction

Use the project documents this way:

- [CogLang_Release_Notes_v1_1_2.md](CogLang_Release_Notes_v1_1_2.md): latest Python package patch notes.
- [CogLang_Release_Notes_v1_1_0.md](CogLang_Release_Notes_v1_1_0.md): stable language release commitments.
- [CogLang_Vision_Proposal_v0_1.md](CogLang_Vision_Proposal_v0_1.md): long-term capability proposal, not a release contract.
- [CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md](CogLang_v1_2_Evolution_Boundary_Proposal_v0_1.md): v1.2 planning boundary for semantic-action evolution, not a stable specification.
- [CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md](CogLang_v1_2_Effect_Budget_Preflight_Vocabulary_v0_1.md): minimal v1.2 vocabulary candidate for effect and graph-budget preflight, not executable v1.1 syntax.
- [CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md](CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md): host-runtime contract v0.2 frozen scope and evidence.
- [CogLang_HRC_v0_2_Freeze_Candidate_2026_04_28.md](CogLang_HRC_v0_2_Freeze_Candidate_2026_04_28.md): prior freeze-candidate review record.
- [ROADMAP.md](ROADMAP.md): what is prioritized or being explored.
- [MAINTENANCE.md](MAINTENANCE.md): how the project may slow down, freeze, transfer, or archive.

The roadmap is intentionally not a release contract and does not promise dates.
