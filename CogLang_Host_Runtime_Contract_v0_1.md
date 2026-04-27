# CogLang Host Runtime Contract v0.1

**Status**: `informative companion note`
**Audience**: implementers, host runtime designers, architecture authors, and future third-party hosts
**Not part of**: the normative `CogLang v1.1.0` language-core specification

## 1. Purpose

This document answers one stable implementation question:

- the `CogLang` language layer freezes query, update, trace, and extension boundaries
- any concrete host still has to define what the host must provide

The goal is not to move application-specific architecture protocols into the language specification. The goal is to define a smaller host contract boundary:

- what the language owns
- what the host owns
- what role host bridge objects play
- what remains outside this companion contract

The current reference implementation also exposes a minimal host facade:

- `LocalCogLangHost`

That facade is not a replacement for a full host protocol. It gives external users an entry point for trying these actions without first understanding an application-specific architecture:

- execute expressions
- execute an expression in a minimal source host and submit write candidates to a target host
- execute and submit directly, then return the associated typed trace or typed query result
- capture the latest write candidate
- prepare submission messages
- submit locally
- query local write results
- export local write submission history and query-result history
- export minimal host state
- export a minimal host summary as JSON
- export request, response, submission-record, typed trace, and query-result histories as JSON, including minimal JSON exports filtered by `status`
- rebuild a local host from minimal host state
- restore a legacy state export in place on the current host instance
- export and restore legacy state JSON directly
- reset local graph state and write state explicitly
- clone an independent minimal local host copy
- restore a minimal host snapshot in place on the current host instance
- export and restore minimal host snapshot JSON directly

This facade should be treated as the reference access surface for `Host Runtime Contract v0.x`, not as the final protocol shape.

## 2. Minimal Layering

A host implementing `CogLang` should at least keep four layers distinct:

1. **Language Layer**
   - parser and validator
   - expression evaluation
   - `Core` and `Reserved` operator semantics
   - expression-level trace and error propagation
2. **Host Runtime Layer**
   - graph-read interface
   - graph-write intent intake and submission flow
   - diagnostics, observer, and capability injection
3. **Host Protocol Layer**
   - host message objects
   - submission acknowledgements
   - correlation, provenance, and retry policies
4. **Application / Architecture Layer**
   - application-side object storage and indexing
   - application-side message or task dispatch protocols
   - lifecycle objects
   - domain services and module boundaries

`CogLang v1.1.0` freezes only the first layer and gives a minimal boundary note for the second layer. It does not freeze productized protocols for the third or fourth layer.

## 3. What a Host Must Provide

### 3.1 Graph-read capability

The host must allow the executor to perform:

- node existence checks
- node attribute reads
- adjacency traversal
- soft-delete visibility checks

The language layer does not require the host to expose any specific graph database or object model, but these capabilities are required.

### 3.2 Graph-write intent intake

For `Create / Update / Delete`, the language layer freezes write intent and return contracts, not the final persistence path.

A host should support at least a two-phase model:

1. **Evaluation phase**
   - the executor evaluates normally
   - the executor collects a `WriteBundleCandidate`
2. **Submission phase**
   - the host decides whether to validate, forward, commit, reject, or roll back

This means:

- the executor can help form write candidates
- the language layer does not decide whether a write is actually committed

For `Create`, the host must also satisfy one more specific language-host interface constraint:

- if `attrs.id` is absent in node mode, a unique ID must be assigned before forming the host write request, `WriteBundleCandidate`, bundle-validation input, or equivalent host submission object
- within the same create action, the language-level return value, later references inside the same expression, and the node ID used in host bridge objects must stay consistent
- the persistence backend may still decide whether the final write is accepted, but generation of the ID adopted by the language layer must not be delayed until after a successful commit

### 3.3 Diagnostics, observer, and capability injection

The host should own:

- observer registration
- the capability manifest
- the mapping from stage profiles to capability sets
- actual availability of extension-backed operators
- how diagnostics and traces enter the host observability system

The responsibility split should at least satisfy:

- the executor owns language-layer argument validation, semantic checks, and error-value returns that are already frozen
- the executor may return `PermissionError[...]` early based on capability or profile manifests injected by the host
- the host is the final source of truth for capability availability; even when the executor does not reject early, the host may still reject a capability during scheduling, submission, or external invocation
- if the host has staged permission packages, the `stage profile -> capability set` mapping should be decided by the host or adapter layer, not written back as `CogLang Core` semantics
- if trace or replay needs to explain why an action was allowed or rejected, the host should record the current `stage profile` and final capability set in governance-layer trace
- if the host rejects a capability, the failed request must map back to a structured `PermissionError[...]`, `ErrorReport`, or equivalent typed failure envelope instead of silently degrading

## 4. Reference Bridge Object Family

A host runtime usually needs bridge objects to carry language-level write intent into host-level submission flow.

This note uses the following object family as the reference bridge:

- `WriteBundleCandidate`
- `WriteBundleSubmissionMessage`
- `WriteBundleSubmissionResult`
- `WriteResult`
- `ErrorReport`
- `WriteBundleResponseMessage`
- `LocalWriteSubmissionRecord`
- `LocalWriteQueryResult`

Within this note, these objects:

- move language-layer write intent into host submission
- provide minimal structure for local validation, atomic replay, and typed round trips

They are **not** formal replacements for:

- application-side knowledge or message objects
- a complete host submission protocol
- a complete provenance query protocol

Inside this companion boundary, these objects should be treated as:

> a reference bridge for the host bridge layer, not as a fully frozen cross-system standard protocol.

### 4.1 Minimal `WriteBundleCandidate` fields

`WriteBundleCandidate` should at least contain these stable fields:

| Field | Type | Meaning |
|------|------|------|
| `owner` | `string` | Identifier for the current host or bridge-layer owner |
| `base_node_ids` | `string[]` | Existing and visible baseline node IDs before the candidate was formed |
| `operations` | `WriteOperation[]` | Write-intent sequence captured in top-level execution order |

Each `WriteOperation` should at least contain:

| Field | Type | Meaning |
|------|------|------|
| `op` | `string` | Write operation kind, such as `create_node / create_edge / update_node / delete_node / delete_edge` |
| `payload` | `object` | Minimal structured data for that operation |

Minimal JSON example:

```json
{
  "owner": "LocalCogLangHost",
  "base_node_ids": ["einstein"],
  "operations": [
    {
      "op": "create_node",
      "payload": {
        "id": "dog_1",
        "node_type": "Entity",
        "attrs": {
          "label": "Dog"
        }
      }
    },
    {
      "op": "create_edge",
      "payload": {
        "source_id": "einstein",
        "target_id": "dog_1",
        "relation": "knows"
      }
    }
  ]
}
```

If a host implementation uses field names such as `source_id / target_id / relation`, the call-surface aliases `from / to / relation_type` must be mapped before forming this candidate or an equivalent host write request. The mapping must not be delayed until after reference-consistency checks.

## 5. Minimal Request / Response Pair

A host runtime should have at least one structured request/response envelope pair. This note uses the following minimal pair as the bridge baseline.

### 5.1 Request side

- `WriteBundleSubmissionMessage`
  - contains `correlation_id`
  - contains `submission_id`
  - contains `candidate`
  - can export a transport-safe dict envelope

### 5.2 Response side

- `WriteBundleResponseMessage`
  - contains `correlation_id`
  - contains `submission_id`
  - contains `owner`
  - has a payload that is either `WriteResult` or `ErrorReport`

### 5.3 Positioning of this contract layer

This request/response pair is useful because it:

- lets the host avoid reading executor internals directly
- gives the bridge layer structured message pairs instead of loose dicts
- leaves a clear landing point for a more formal host-bus protocol later

It is still not:

- a complete cross-process message protocol
- a multi-host standard
- an independent open runtime standard

### 5.4 Local query layer

If a host implements a local bridge layer, it may also keep a minimal provenance-style query capability:

- return `committed / failed / not_found` by `correlation_id`
- return `committed / failed / not_found` by `submission_id`
- return the local typed response envelope by `correlation_id`
- return one `LocalWriteSubmissionRecord` by `correlation_id` or `submission_id`
- return a typed `LocalWriteQueryResult` by `correlation_id`
- return a typed `LocalWriteQueryResult` by `submission_id`
- return a transport-safe dict form of `LocalWriteQueryResult` by `correlation_id` or `submission_id`
- return the minimal `payload_kind` directly by `correlation_id` or `submission_id`, so lightweight hosts do not need to drill into response headers; this minimal field should preferably come from the runtime bridge first
- return the minimal `write_header` directly by `correlation_id` or `submission_id`, covering `correlation_id / submission_id / status / payload_kind`, so lightweight hosts do not need to query several fields separately
- return a typed `LocalWriteHeader` directly by `correlation_id` or `submission_id`, so typed hosts do not need to reconstruct the minimal header from dict form; this typed header should preferably come from the runtime bridge first and be thinly wrapped by the host facade
- when a companion CLI or demo shows both dict `write_header` and typed `LocalWriteHeader` views, the typed header should come from the host typed query, not only reuse the dict header as an alias
- when a companion CLI or demo shows `submission-message / response / submission-record / query-result` together with `write_header`, the alignment of `correlation_id / submission_id / status / payload_kind` across public views should be part of success criteria rather than only an implicit test invariant
- when a companion CLI or demo also exposes a top-level `node_id` or equivalent primary object ID, that field should align with touched object IDs in the response payload and with object-ID views in the snapshot graph, and that alignment should be part of success criteria
- when a companion CLI or demo shows the submission-message candidate or commit plan together with a top-level `node_id`, the create-node target ID in the candidate or commit plan should also align with that top-level ID and be part of success criteria
- a companion CLI or demo should not only demonstrate the `WriteResult` happy path; if it also serves as a contract example, it should include a minimal `ErrorReport` companion step showing alignment of `payload_kind=ErrorReport`, `status=failed`, typed response, query result, and trace
- export `write_header` history directly through the host facade, including `status` filtering and minimal JSON export; corresponding dict, JSON, and history assembly should preferably come from the runtime bridge first
- export typed `LocalWriteHeader[]` directly through the host facade, including minimal JSON export and `status` filtering; the corresponding JSON wrapper should preferably come from the runtime bridge first
- return minimal JSON form of `LocalWriteQueryResult` by `correlation_id` or `submission_id`; its JSON wrapper should preferably come from the runtime bridge first
- execute `execute_and_prepare_submission_message(...)` directly through the host facade, collapsing execution and typed message preparation into one step
- execute `execute_and_prepare_submission_message_dict(...)` directly through the host facade, collapsing execution and transport-safe message preparation into one step
- read or consume the dict form of an existing `WriteBundleCandidate` directly through the host facade, or convert an existing candidate directly into a dict submission message
- execute `submit_message_dict(...)` and `submit_message_dict_and_query(...)` directly through the host facade, allowing lightweight script hosts to stay in dict form end to end
- execute `submit_*_and_query(...)` directly through the host facade, collapsing local submission and typed query into one step
- execute `execute_and_submit_to_query(...)` through a dual-host facade, collapsing source-host execution, target-host submission, and target-host typed query into one step
- execute `execute_and_submit_to_query_dict(...)` through a dual-host facade, collapsing source-host execution, target-host submission, and target-host dict query into one step
- read typed response envelopes and single request/response records directly through the host facade
- read typed response envelopes directly by `submission_id` through the host facade
- read transport-safe dict forms of single response envelopes and single submission records directly through the host facade
- read minimal JSON forms of single response envelopes and single submission records directly through the host facade; corresponding JSON wrappers should preferably come from the runtime bridge first
- read a transport-safe dict response envelope directly by `submission_id` through the host facade
- read a transport-safe dict submission record directly by `submission_id` through the host facade
- read typed submission messages directly by `correlation_id / submission_id` through the host facade
- read transport-safe dict submission messages directly by `correlation_id / submission_id` through the host facade
- read minimal JSON submission messages directly by `correlation_id / submission_id` through the host facade; the corresponding JSON wrapper should preferably come from the runtime bridge first
- read one associated typed `LocalHostTrace` directly by `correlation_id / submission_id` through the host facade
- read transport-safe dict form of `LocalHostTrace` directly by `correlation_id / submission_id` through the host facade
- read minimal JSON form of `LocalHostTrace` directly by `correlation_id / submission_id` through the host facade
- expose these trace views directly from the host facade, while keeping the underlying association logic in the runtime bridge first so hosts do not repeatedly hand-assemble request, response, record, and query-result data
- assemble single JSON queries and history JSON exports for `query-result / response / submission-message / submission-record / trace` in the runtime bridge first, then thinly wrap them in the host facade
- when a companion CLI or demo shows this object group, prefer consuming the host facade query/view interfaces over drilling into typed trace internals
- export typed response history, dict response history, and typed submission-record history directly through the host facade
- export typed submission-message history and dict submission-message history directly through the host facade
- return typed submission-message history by `status`, or export dict submission-message history filtered by `status`, directly through the host facade
- return typed response history or typed submission-record history by `status`, or export dict histories filtered by `status`, directly through the host facade
- preserve the queried `submission_id` when a `submission_id` query returns `not_found`, so lightweight hosts do not lose the lookup key
- export typed trace history and dict trace history directly through the host facade, including minimal JSON export of typed `LocalHostTrace[]` and filtering by `status`
- return typed `LocalHostTrace[]` by `status`, or export trace history filtered by `status`, directly through the host facade
- export a complete snapshot object through the host facade, including graph state, typed request/response/record histories, typed query results, and typed traces
- when typed trace exists in a snapshot but request/response/record histories are incomplete, the host may use trace as a fallback source to restore those histories
- when a snapshot has only matching request/response data and no record, the host should synthesize the minimal submission record during restore and must not append response history twice
- export typed summary and dict summary through the host facade for lightweight hosts or CLI consumers; the summary should at least include counts for request, response, record, query-result, and trace
- when a companion CLI or demo shows both `snapshot` and `summary`, its `snapshot_summary` should be rebuilt explicitly from the exported `snapshot`, not just reuse another summary payload
- when a companion CLI or demo shows `trace`, `snapshot`, and other public views together, alignment among request, response, record, and query-result views should be part of success criteria rather than only an implicit test invariant
- clear local write state explicitly through the host facade, returning to a clean request, response, and query baseline
- export local `LocalWriteQueryResult` history in insertion order
- filter and export local `LocalWriteQueryResult` by `status`
- return typed `LocalWriteQueryResult[]` directly by `status` through the host facade

`LocalWriteSubmissionRecord` is positioned as:

- a record of one local submission attempt's request/response pair
- a stable landing point for host debugging, tests, and later integration with a formal provenance layer

`LocalWriteQueryResult` is positioned as:

- a typed return object that combines the local query result's `status / response / record`
- a way to preserve the same mental model for later integration with formal `ProvenanceStore.query_by_correlation_id`

It is still not the formal `ProvenanceStore.query_by_correlation_id`, but it means the local bridge is no longer limited to an immediate return value from one submission.

### 5.5 Reserved collaboration surface for governance-layer hosts

If a host further uses `CogLang` as a governance, scheduling, or audit layer, it will usually need request-shaped governance actions such as:

- `request_harness_run`
- `request_snapshot_rollback`
- `pause_for_review`
- `hold`

These objects are currently better treated as:

- host runtime or adapter-layer action schemas
- orchestration objects for governance, approval, replay, or audit

They are not:

- `CogLang Core` operators
- side-effect protocols executed directly by the language layer

For these governance actions, this note currently recommends only these minimal constraints:

- action requests and actual execution results must be distinguishable
- if an action requires approval, the host should record `requires_approval` or an equivalent field explicitly
- if an action is rejected, the failure must map back to a structured typed error instead of silently falling back
- the difference between `shadow` and `live` should be represented in host governance-layer trace or diff, not by rewriting action semantic boundaries
- the real execution protocols for external harnesses, rollback executors, and tool invocation remain host-layer concerns and are not frozen by this note

### 5.6 Current position of the schema companion pack

The current `Host Runtime Contract` has a schema companion pack covering:

- `header / result / error / response`
- `query-result / submission-record / trace`
- `summary`

It is paired with:

- `schema-pack.json`
- a sample payload pack
- minimal versioning and reference rules
- a `candidate / seed_only` promotion boundary
- the candidate object's minimal field surface and the boundary around detail fields that are easiest to over-promote

The better current position for this material is:

- it is already sufficient as a **recommended companion** for `HRC v0.2`
- it is not a default freeze blocker for `HRC v0.2`
- it is not a formal cross-host JSON Schema export surface

This means:

- host implementers who want to understand the minimal object shapes of the current reference bridge should prioritize reading this schema pack
- whether a host implementation passes a `v0.2` freeze discussion should not default to depending on whether a full-pack schema has already been published externally
- some object-view items in the `Freeze Checklist` may be classified as `schema-assisted`, but that classification is currently for reading and triaging freeze materials; it should not automatically become a per-object shape commitment in the `HRC` body
- `LocalHostSnapshot`, third-party host stub interoperability, and a more formal export strategy remain decisions for later versions

In short, the current schema companion pack is:

> companion material recommended for reading and comparison alongside `HRC v0.2`, not a freeze blocker for `v0.2` itself.

## 6. Minimum Requirements for Host Implementers

If you are implementing a third-party host, you should at least:

- accept `WriteBundleCandidate` or an equivalent write-intent object
- decide whether to commit, reject, or defer submission
- return a structured success or failure result
- preserve `correlation_id`
- preserve a stable `submission_id`
- distinguish language-level `ErrorExpr` from host submission failure

If a host cannot satisfy these requirements, it may be able to execute some expressions, but it is not yet an integrable `CogLang` host.

## 7. Still Unfrozen

This note intentionally does not freeze:

- the final `KnowledgeMessage` schema
- the cross-service submission protocol for `WriteBundle`
- the standard query interface for `ProvenanceStore.query_by_correlation_id`
- formal action schemas for external harnesses, rollback, or tool invocation
- standard enumeration and cross-host naming for `stage profile`
- the owning-module enumeration table
- multi-host interoperability format
- the release boundary for an independent reference runtime

These topics should be handled by architecture documents, implementation documents, or future versions of the host contract.

## 8. Relationship to Other Documents

The public repository currently ships these directly reviewable companion documents and schema assets:

- Language semantics: `CogLang_Specification_v1_1_0_Draft.md`
- Profiles and capabilities: `CogLang_Profiles_and_Capabilities_v1_1_0.md`
- Standalone install and trial path: `CogLang_Standalone_Install_and_Release_Guide_v0_1.md`
- Public release boundary: `CogLang_Release_Notes_v1_1_0.md`
- Public roadmap: `ROADMAP.md`
- Schema companion pack: `internal_schemas/host_runtime/v0.1/schema-pack.json`

Migration notes, schema-promotion notes, and HRC v0.2 freeze decision records are not part of the current stable language release. Until they are published, they should be treated as future release-gate material rather than public commitments.
