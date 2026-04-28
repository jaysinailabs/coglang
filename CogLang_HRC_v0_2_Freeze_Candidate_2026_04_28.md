# CogLang HRC v0.2 Freeze Candidate Decision Record

**Date**: 2026-04-28
**Status**: `freeze-candidate`
**Scope**: host-runtime write envelopes and in-repository host evidence
**Not a language release**: this record does not change `CogLang v1.1.0`
language-core commitments.

## Decision

`Host Runtime Contract v0.2` is ready to be treated as a freeze candidate for
the typed write-envelope surface and the two in-repository host evidence paths.

This is not yet a final multi-host ecosystem standard. It is a narrower
candidate decision: the current contract is stable enough for maintainers and
host implementers to review against executable evidence before it is promoted
to `frozen`.

## Candidate Freeze Scope

The candidate scope covers:

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
- success and failure response envelope behavior for local/reference hosts

The candidate scope also covers the executable behavior demonstrated by:

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

Local verification commands for this candidate are:

```powershell
coglang host-demo
coglang reference-host-demo
coglang smoke
python -m pytest
python -m build --sdist --wheel
```

## Explicit Non-Scope

This candidate does not freeze:

- a network transport protocol
- an external database persistence contract
- a normative cross-language JSON Schema pack
- a third-party host implementation maintained outside this repository
- final `KnowledgeMessage` cross-service standardization
- capability-manifest negotiation
- schema promotion rules beyond the current companion-pack posture
- LSP, IDE, package-index automation, or ecosystem integrations

The existing schema files under `internal_schemas/host_runtime/v0.1/` remain
recommended companion material. They are useful for reviewing the current object
shapes, but this candidate does not make them a normative JSON Schema export
surface.

## Promotion Criteria

This candidate can be promoted from `freeze-candidate` to `frozen` after:

- the branch containing this record passes public CI
- `host-demo` and `reference-host-demo` remain part of smoke-facing tests
- no critical contradiction is found between the HRC note, public docs, and
  typed runtime behavior
- maintainers explicitly update this record or add a successor record with
  status `frozen`

## Rationale

The project now has two executable host paths instead of only one local host
facade. That is enough to review the typed write-envelope boundary without
pretending that a broad third-party host ecosystem already exists.

The candidate keeps the claim narrow: it freezes the parts that are executable
and tested, and defers the parts that still need external implementation
experience.
