# CogLang Send Carry-Forward Exit Matrix v0.1

**Status**: public governance note
**Scope**: evidence matrix for deciding whether `Send` leaves `Carry-forward`
**Audience**: maintainers, contributors, host implementers, and reviewers evaluating cross-instance capability work

---

## 0. How To Read This Document

`Send` is currently the only meaningful `Carry-forward` operator entry. The
operator catalog says it may be promoted only if the cross-instance protocol,
default failure shape, and minimal trace requirements are frozen before the
target version boundary. Otherwise, it should move to `Reserved`.

This document applies `CogLang_Reserved_Operator_Promotion_Criteria_v0_1.md` to
`Send`. It does not implement `Send`, freeze a transport protocol, introduce a
cross-instance runtime, or make `Send` available by default.

The practical decision is narrower:

- if the evidence below becomes public and executable, `Send` can be reviewed for
  promotion into a more stable specification surface
- if the evidence remains missing, `Send` should be downgraded from
  `Carry-forward` to `Reserved` so that the catalog does not preserve indefinite
  ambiguity

---

## 1. Current Status

| Field | Current position |
| --- | --- |
| Operator | `Send` |
| Current status | `Carry-forward` |
| Current Baseline behavior | `StubError["Send", ...]` |
| Current Enhanced behavior | profile-specific / implementation-defined |
| Current implementation requirement | none |
| Current Core status | not Core |
| Current promotion condition | freeze cross-instance protocol, default failure shape, and minimal trace requirements before the target version boundary |
| Default outcome if evidence is missing | downgrade to `Reserved` |

`Send` should not be treated as a stable everyday authoring surface while these
fields remain unfrozen.

## 2. Current Executable Evidence

The repository currently provides only narrow executable evidence around `Send`:

| Surface | Current evidence | Interpretation |
| --- | --- | --- |
| Parser / vocabulary | `Send[...]` is a recognized head. | Name recognition only; not a stable send protocol. |
| Executor | The default execution path returns `StubError["Send", ...]`. | Confirms unsupported behavior, not normal execution. |
| Preflight | `Send` is classified as a host submission effect and requires host submission capability. | Capability/effect classification only; not a runtime success contract. |
| Conformance suite | No success or failure conformance examples for real cross-instance dispatch. | Blocks promotion. |
| Release notes | No stable `Send` release promise. | Blocks claims of user-facing stability. |

This evidence is enough to justify keeping `Send` visible as a transitional
entry. It is not enough to promote it.

---

## 3. Exit Decision Matrix

| Evidence area | Required for promotion | Current state | Decision pressure |
| --- | --- | --- | --- |
| Cross-instance protocol | Stable request/response shape, addressing model, delivery expectation, correlation identity, timeout behavior, and retry boundary. | Not frozen. | Blocks promotion. |
| Default failure shape | Explicit value returned for unavailable peer, denied capability, invalid target, transport failure, timeout, and unsupported profile. | Not frozen. | Blocks promotion. |
| Minimal trace requirements | Minimum trace fields for source expression, target endpoint or peer reference, correlation ID, status, timing, and returned value or error. | Not frozen. | Blocks promotion. |
| Capability boundary | Stable capability strings for cross-instance execution and external I/O, with denied-by-default behavior where appropriate. | Partly named as capability categories, not frozen for `Send`. | Blocks default availability. |
| Profile availability | Baseline and Enhanced behavior matrix, including missing implementation and denied capability paths. | Baseline stub and Enhanced implementation freedom are documented. | Supports reserved status, not promotion. |
| Conformance evidence | Golden examples for success, unsupported path, capability denied path, timeout/failure path, and trace recording. | Not present. | Blocks promotion. |
| Host ownership | Clear split between language expression semantics and host-owned transport, policy, security, and delivery behavior. | Directionally stated by project governance, not specific to `Send`. | Blocks Core promotion. |
| Security review | Permission, identity, spoofing, replay, and data-leakage boundaries documented for cross-instance use. | Not present. | Blocks promotion. |

Promotion requires every blocking row to move from `Not frozen` or `Not present`
to public specification, examples, and tests.

---

## 4. Candidate Outcomes

### 4.1 Promote

`Send` can be considered for promotion only when:

- the cross-instance protocol is described in a public contract document
- default failure values are stable and executable
- minimum trace fields are stable
- capability checks produce explicit `PermissionError[...]` values where
  appropriate
- missing implementation produces explicit `StubError[...]`
- conformance tests cover success and failure paths
- documentation explains which behavior belongs to language semantics and which
  belongs to host transport

Promotion does not automatically mean `Baseline` normal execution. It may still
mean a profile-specific surface if the host boundary remains too strong for
Core.

### 4.2 Reserve

`Send` should move to `Reserved` if any of these remain true at the target
version boundary:

- cross-instance protocol is still host-specific
- failure shape is still only informative
- trace requirements are still incomplete
- capability strings are not stable
- no conformance examples exist
- the feature mainly describes host transport rather than language semantics

Reserved status keeps the name and direction visible without implying default
availability.

### 4.3 Remove

Removal is appropriate only if `Send` conflicts with the `v1.x` language line or
if the project decides cross-instance dispatch should live entirely outside the
operator catalog.

Removal is not the default recommendation. The current default recommendation is
to preserve the direction as `Reserved` if promotion evidence is not ready.

---

## 5. Minimum Promotion Artifact Set

A promotion PR should include at least:

1. A specification or host-contract section defining `Send` syntax, validation,
   return contract, effect class, determinism, baseline availability,
   observability, and compatibility status.
2. A profile/capability matrix showing `Baseline`, `Enhanced`, missing
   implementation, and denied capability behavior.
3. A small schema or structured example set for cross-instance request/response
   and trace data if those are outside canonical expression syntax.
4. Golden examples for:
   - successful send
   - unavailable peer
   - denied capability
   - unsupported profile
   - timeout or transport failure
   - trace record with correlation identity
5. Tests proving ordinary `Core` operators keep their existing behavior when
   `Send` is unavailable.
6. README, `llms.txt`, `llms-full.txt`, operator catalog, release notes, package
   data, public extract, and release-check updates when the public surface
   changes.

---

## 6. Non-Goals

This matrix does not:

- define a network protocol
- require any executor to implement cross-instance dispatch
- make `Send` part of `Core`
- make `Enhanced` equivalent to a distributed runtime profile
- freeze peer identity, delivery, retry, timeout, or authentication semantics
- claim that HRC v0.2 covers cross-instance dispatch

The goal is to make the exit from `Carry-forward` explicit before the project
decides whether to promote or downgrade `Send`.
