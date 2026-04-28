# CogLang HRC v0.2 Final Freeze Record

**Date**: 2026-04-28
**Status**: `frozen`
**Scope**: typed host-runtime write envelopes and in-repository host evidence
**Not a language release**: this record does not change `CogLang v1.1.0`
language-core commitments.

## Decision

`Host Runtime Contract v0.2` is frozen for the typed write-envelope surface
implemented and tested in this repository.

This is a narrow host-runtime freeze. It means the public package now treats the
current typed submission, response, result, error-report, local record,
query-result, and write-header shapes as stable review targets for `1.x`
package-level host integration work.

It does not claim that CogLang has a broad third-party host ecosystem yet. It
also does not freeze a network protocol, an external database protocol, or a
normative cross-language JSON Schema pack.

## Frozen Scope

The frozen HRC v0.2 scope covers these typed objects and invariants:

- `WriteOperation`
- `WriteBundleCandidate`
- `WriteBundleSubmissionMessage`
- `WriteBundleResponseMessage`
- `WriteResult`
- `ErrorReport`
- `LocalWriteSubmissionRecord`
- `LocalWriteQueryResult`
- `LocalWriteHeader`
- preservation of `correlation_id`
- preservation of `submission_id`
- `committed`, `failed`, and `not_found` local status semantics
- success and failure response-envelope behavior for local/reference hosts

The frozen scope also covers the executable behavior demonstrated by:

- `coglang host-demo`
- `coglang reference-host-demo`

## Evidence

`coglang host-demo` exercises the richer `LocalCogLangHost` path:

- a write-producing expression is executed
- the write candidate is submitted to a target host
- typed submission, response, record, query-result, trace, snapshot, summary,
  and write-header views agree
- invalid write submission returns an `ErrorReport` envelope

`coglang reference-host-demo` exercises a smaller host path:

- it does not depend on `LocalCogLangHost`
- it consumes `WriteBundleSubmissionMessage` JSON
- it returns a typed `WriteBundleResponseMessage`
- it exposes query-result, write-header, submission-record, graph-state, and
  `ErrorReport` behavior

The frozen decision is backed by the local release-gate commands:

```powershell
coglang host-demo
coglang reference-host-demo
coglang smoke
python -m pytest
python -m build --sdist --wheel
```

Release publication should still use normal GitHub CI and PyPI Trusted
Publishing checks. A CI failure is a release blocker; it is not a scope expansion
for HRC v0.2 unless it exposes a contradiction in the frozen surface.

## Explicit Non-Scope

HRC v0.2 does not freeze:

- a network transport protocol
- an external database persistence contract
- a normative cross-language JSON Schema pack
- a third-party host implementation maintained outside this repository
- final `KnowledgeMessage` cross-service standardization
- capability-manifest negotiation
- schema promotion rules beyond the current companion-pack posture
- LSP, IDE, package-index automation, or ecosystem integrations

The schema files under `internal_schemas/host_runtime/v0.1/` remain recommended
companion material. They are useful for reviewing the current object shapes, but
this freeze does not make them a normative JSON Schema export surface.

## Compatibility Policy

Within the `1.x` package line, changes inside the frozen HRC v0.2 scope should
be additive or explicitly compatibility-preserving.

Breaking changes to the frozen scope require:

- a successor HRC version
- release notes that identify the break
- migration guidance for host implementers
- tests that pin the new behavior

## Relationship to the Candidate Record

This record promotes
`CogLang_HRC_v0_2_Freeze_Candidate_2026_04_28.md` to final frozen status for the
narrow typed write-envelope surface described above.

The candidate record remains useful as historical review context, but this file
is the current public HRC v0.2 status record.
