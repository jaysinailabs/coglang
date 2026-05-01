# CogLang HRC Companion Asset Classification v0.1

**Status**: public governance note
**Scope**: classification of host-runtime assets as frozen HRC v0.2 contract,
companion evidence, historical record, or implementation detail
**Non-goal**: expanding the HRC v0.2 frozen scope

## 1. Purpose

`CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md` freezes a narrow host-runtime
surface for typed write envelopes and the in-repository behavior demonstrated by
the Python host demos.

This document makes the surrounding asset status explicit so package users and
contributors can tell which files are formal review targets and which files are
supporting evidence.

It does not change `CogLang v1.1.0`, introduce a new host-runtime version, make
the schema pack normative, or promote the Node examples into required
implementations.

## 2. Classification Summary

| Asset | Classification | Stability meaning |
| --- | --- | --- |
| `CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md` | Formal status record | Current public source of truth for the frozen HRC v0.2 scope. |
| Typed write-envelope objects and invariants listed in the final freeze record | Frozen package-level host-runtime surface | Compatibility-preserving changes are expected within the `1.x` package line. |
| `coglang host-demo` | Frozen evidence path | Demonstrates the richer local host behavior covered by the frozen scope. |
| `coglang reference-host-demo` | Frozen evidence path | Demonstrates the smaller reference-host behavior covered by the frozen scope. |
| `CogLang_HRC_v0_2_Freeze_Candidate_2026_04_28.md` | Historical review record | Useful context, but no longer the current status record. |
| `CogLang_Host_Runtime_Contract_v0_1.md` | Public host-contract context | Describes the host-runtime direction and earlier minimal contract language; not a replacement for the HRC v0.2 final freeze record. |
| `internal_schemas/host_runtime/v0.1/*.json` | Companion schema material | Useful for reviewing current object shapes, but not a normative JSON Schema export surface. |
| `internal_schemas/host_runtime/v0.1/examples/*.json` | Companion sample material | Useful examples for package and consumer checks, not independent contract definitions. |
| `examples/node_host_consumer` | Companion consumer evidence | Shows non-Python consumption of existing schema/sample assets without requiring a Node host implementation. |
| `examples/node_minimal_host_runtime_stub` | Companion implementation evidence | Shows a minimal non-Python host/runtime stub against existing typed envelope paths without expanding HRC v0.2. |
| HRC-related tests | Release and regression evidence | Pin the current package behavior; they do not create new public scope unless the corresponding public status record says so. |

## 3. Formal Frozen Surface

The formal HRC v0.2 frozen surface is the surface named by the final freeze
record:

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

The executable evidence paths for that surface are:

- `coglang host-demo`
- `coglang reference-host-demo`

Release checks may rely on those paths as frozen evidence. They should not infer
additional frozen behavior from nearby examples, schema files, or implementation
helpers unless a future HRC status record explicitly promotes that behavior.

## 4. Companion Assets

Companion assets help users inspect, test, and reproduce the frozen surface. They
are intentionally useful, but they are not the same as the formal frozen
contract.

### 4.1 Schema Pack

The files under `internal_schemas/host_runtime/v0.1/` are companion schema
material.

They can be used to:

- review current object shapes
- validate in-repository samples
- help non-Python consumers understand the current envelope structure
- support public release smoke checks

They do not freeze:

- a normative JSON Schema export surface
- schema publication or version-negotiation rules
- a cross-language conformance program
- a transport protocol

When the schema pack labels a schema as `candidate`, that label means future
promotion triage, not current formal HRC v0.2 status. Current candidate schemas
include:

- `ErrorReport`
- `LocalHostSummary`
- `LocalWriteHeader`
- `WriteBundleResponseMessage`
- `WriteResult`

Current seed-only schemas include:

- `LocalWriteQueryResult`
- `LocalWriteSubmissionRecord`
- `LocalWriteTrace`
- `WriteBundleCandidate`
- `WriteBundleSubmissionMessage`
- `WriteOperation`

Neither label changes the final freeze record. In particular,
`LocalHostSummary`, `LocalWriteTrace`, and any snapshot-style helper view remain
companion evidence unless a successor HRC version explicitly promotes them.

### 4.2 Node Consumer

`examples/node_host_consumer` is companion evidence that a standard-library Node
script can consume the existing schema pack and envelope samples.

It does not freeze:

- a JavaScript or TypeScript runtime API
- a package name for non-Python tooling
- third-party schema distribution
- a required Node implementation path

### 4.3 Node Minimal Host Runtime Stub

`examples/node_minimal_host_runtime_stub` is companion evidence that a small
non-Python host/runtime stub can exercise existing typed write-envelope
success/failure paths.

It does not freeze:

- a required host implementation architecture
- network behavior
- cross-instance dispatch
- `Send` behavior
- capability negotiation

## 5. Historical And Context Documents

`CogLang_HRC_v0_2_Freeze_Candidate_2026_04_28.md` remains useful review context,
but the final freeze record supersedes it for current status.

`CogLang_Host_Runtime_Contract_v0_1.md` remains public host-runtime context. It
should be read as background and earlier contract language unless a specific
section is explicitly restated by the final freeze record or a successor HRC
record.

## 6. Release Review Use

Release review may check that:

1. the final freeze record is present
2. `host-demo` succeeds
3. `reference-host-demo` succeeds
4. the companion schema pack and examples remain package-visible
5. Node companion examples continue to run as examples
6. public manifest and package data continue to expose the classification
   document

Those checks preserve the public review surface. They do not promote companion
assets into formal frozen contract status.

## 7. Boundaries

This classification does not freeze:

- a network transport protocol
- an external database persistence contract
- a normative cross-language JSON Schema pack
- a third-party host implementation maintained outside this repository
- final `KnowledgeMessage` cross-service standardization
- capability-manifest negotiation
- schema promotion rules beyond the companion posture
- `Send` or any cross-instance dispatch behavior
- LSP, IDE, package-index automation, or ecosystem integrations

Future work may promote more host-runtime material, but that requires a
successor HRC record, release notes, migration guidance, and tests that identify
the new frozen surface explicitly.
