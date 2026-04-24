# CogLang Profiles and Capabilities v1.1.0

## 0. Role of This Document

This document is a pre-release companion to `CogLang_Specification_v1_1_0_Draft.md`.

It answers three questions:

- what the `Baseline` and `Enhanced` profiles carry in `v1.1.0`
- how profile-specific availability should be written in operator entries and implementation manifests
- what minimum contract applies to capability declarations and extension-backed operators

This document does not rewrite language semantics from the main specification. If it conflicts with the main specification, the main specification takes precedence. For `v1.1.0` profile and capability boundaries, treat this document as the authoritative pre-release companion source.

Terminology boundary:

- In this document, `capability` means runtime execution ability, permission string, or manifest item.
- It does not mean any application-side taxonomy of cognitive abilities or any other domain-level capability category.
- If both meanings need to appear together, application-side capability categories and CogLang runtime capabilities should be named as separate layers.

## 1. Design Purpose

`v1.1.0` uses profiles to carry execution availability differences and controlled extension ability, instead of expanding the `Core` trunk to absorb every variation.

Profiles are intended to:

- keep `Baseline` graph-first and minimally consistent
- let `Enhanced` carry extension ability that is not yet suitable for `Core`
- let implementers distinguish frozen language semantics from optional implementation-provided ability packages

A profile is not a new language layer and not a new AST kind. It only affects:

- `Baseline Availability`
- capability checks
- the default callable capability set
- the scope of conformance assertions

## 2. Profile Overview

### 2.1 `Baseline`

`Baseline` is the default baseline profile for `v1.1.0`.

It carries:

- the graph-first main chain
- minimal composition ability
- the basic error model
- basic observability
- the minimum `Core` conformance requirements from the main specification

The goal of `Baseline` is not to maximize feature count. Its goal is to keep the graph main chain stable.

### 2.2 `Enhanced`

`Enhanced` is an enhanced profile layered on top of `Baseline`.

It carries:

- non-default query modes
- `Reserved` abilities with frozen signatures but no required default implementation
- controlled extension-backed operators
- external abilities guarded by capabilities
- enhanced execution abilities that are still not suitable for the `Core` trunk

The goal of `Enhanced` is not to replace `Baseline`. It carries extensions without changing `Core` semantics.

## 3. Profile Relationship Constraints

The relationship between `Baseline` and `Enhanced` must satisfy these constraints:

- `Enhanced` **MUST** preserve compatibility with the `Baseline` compatibility surface.
- `Enhanced` **MUST NOT** rewrite the specified semantics of existing `Core` operators.
- If an ability is available only in `Enhanced`, its operator entry **MUST** explicitly state the profile condition.
- `Baseline` **SHOULD NOT** carry high-risk, strongly host-coupled, or architecture-level protocol abilities.
- `Enhanced` may provide stronger abilities, but those abilities do not automatically become graph entries, program execution domain features, or public knowledge-layer objects.

## 4. Capability Allocation

### 4.1 Required `Baseline` Abilities

The following abilities should be treated as the minimum `Baseline` ability set:

- `Abstract`
- `Equal`
- `Compare`
- `Unify`
- `Match`
- `Get`
- the default `mode` of `Query`
- `AllNodes`
- `Traverse`
- `ForEach`
- `Do`
- `If`
- `IfFound`
- `Compose`
- `Create`
- `Update`
- `Delete`
- `Trace`
- `Assert`

The following basic models are also included:

- four-layer representation model
- errors as values
- explicit graph-write boundary
- default priority for name resolution
- minimum contract for `Readable Render`

### 4.2 `Enhanced` Abilities

Within the current version boundary, the following abilities belong to `Enhanced`:

- non-default `Query.mode`
- `Explain`
- `Inspect`
- meta-reasoning interfaces related to query `cost / gain`
- extension-backed operators
- external abilities guarded by capabilities
- stronger profile-specific debugging and meta-observation interfaces

### 4.3 Minimum Operator by Profile Matrix

This table closes the ambiguity where profile-specific availability is described only locally but not summarized in one matrix. If this table conflicts with a specific operator entry in the main specification, the main specification takes precedence.

| Operator / Ability | Profile Baseline | Profile Enhanced |
| --- | --- | --- |
| `Abstract` | normal execution | normal execution |
| `Equal` | normal execution | normal execution |
| `Compare` | normal execution | normal execution |
| `Unify` | normal execution | normal execution |
| `Match` | normal execution | normal execution |
| `Get` | normal execution | normal execution |
| `Query` with omitted `options` or `mode="default"` | normal execution | normal execution |
| `Query` with non-default `mode` | `StubError["Query", "mode", ...]` | profile-specific / implementation-defined |
| `AllNodes` | normal execution | normal execution |
| `Traverse` | normal execution | normal execution |
| `ForEach` | normal execution | normal execution |
| `Do` | normal execution | normal execution |
| `If` | normal execution | normal execution |
| `IfFound` | normal execution | normal execution |
| `Compose` | normal execution | normal execution |
| `Create` | normal execution | normal execution |
| `Update` | normal execution | normal execution |
| `Delete` | normal execution | normal execution |
| `Trace` | normal execution | normal execution |
| `Assert` | normal execution | normal execution |
| `Explain` | `StubError["Explain", ...]` | normal execution |
| `Inspect` | `StubError["Inspect", ...]` | profile-specific / implementation-defined |
| `Send` | `StubError["Send", ...]` | profile-specific / implementation-defined |
| extension-backed operator | `PermissionError[...]` or `StubError[...]` | profile-specific / capability-gated |

Notes:

- `Enhanced` must not change the frozen specified semantics of any `Core` operator that already exists in `Baseline`.
- In `Enhanced`, `Query[...]` with omitted `options` still defaults to `mode="default"`. `Enhanced` must not reinterpret omitted `mode` as another default execution strategy.
- `profile-specific / implementation-defined` is allowed only for abilities already marked by the main specification or catalog as `Reserved`, `Carry-forward`, or extension-backed.

### 4.4 `v1.1` Out-of-Scope Directions

The following directions should not be frozen early as `Baseline` abilities or default `Enhanced` abilities in `v1.1`, even if they may be needed in the future:

- procedural syntax extension
- general-purpose `Recover[...]`
- syntactic sugar aimed at human handwritten convenience
- high-risk adapter-specific abilities with strong host coupling
- full program execution domain abilities

If these directions continue, they should enter `Reserved / Experimental` status or a later version.

The future directions listed in this section only prevent accidental expansion of the `v1.1` boundary. They are not a near-term roadmap.

## 5. Writing `Baseline Availability`

The `Baseline Availability` field in the main specification may contain only:

- `normal execution`
- `StubError[...]`
- `PermissionError[...]`
- `Profile <name>: ...`

When availability depends on a profile, use this form:

```text
Baseline Availability:
Profile Baseline: StubError["Explain", ...]
Profile Enhanced: normal execution
```

If the profile-specific form is used, the companion document or manifest **MUST** formally define that profile.

## 6. Minimum Fields for a Capability Manifest

An implementation that supports capability checks should provide at least these fields:

| Field | Requirement |
| --- | --- |
| `profile_name` | Name of the current implementation profile |
| `capabilities` | Stable string set of available capabilities |
| `extensions` | Installed extensions or registry entry identifiers |
| `default_enabled` | Extensions enabled by default |
| `denied_by_default` | Capabilities denied by default |
| `version` | Version of the manifest itself |

Minimal example:

```json
{
  "profile_name": "Enhanced",
  "capabilities": ["graph_write", "trace_write", "external_io"],
  "extensions": ["query.mode.rank", "meta.explain"],
  "default_enabled": ["meta.explain"],
  "denied_by_default": ["external_io"],
  "version": "v1.1.0"
}
```

## 7. Capability String Constraints

`v1.1.0` does not freeze the complete capability vocabulary, but it requires:

- capability names **MUST** be stable strings.
- the same implementation must not reuse the same capability name for incompatible semantics.
- the profile manifest **MUST** publish precise capability strings.
- failed capability checks **MUST** return `PermissionError[...]` and must not silently degrade.

Implementations should at least be able to distinguish:

- `graph_write`
- `trace_write`
- `external_io`
- `cross_instance`
- `self_modify`

## 8. Minimum Contract for Extension-backed Operators

An extension-backed operator is an operator whose execution ability is provided by a registry, plugin, or external adapter.

Each extension-backed operator must at least declare:

- whether its name is frozen
- whether its signature is frozen
- the profiles where it is available by default
- the required capabilities
- the error returned when no implementation is installed
- the error returned when capability is denied
- whether it is an enhanced ability outside `Baseline`

Minimal contract example:

```text
Operator: Explain
Status: Reserved
Layer: observability
Profiles:
- Profile Baseline: StubError["Explain", ...]
- Profile Enhanced: normal execution
Capabilities:
- none
On missing implementation:
- StubError["Explain", ...]
On capability denied:
- PermissionError["Explain", ...]
```

## 9. Minimum Conformance Requirements

If an implementation declares support for `Enhanced`, its conformance tests should at least add:

- profile-specific availability tests
- capability denied tests
- split tests for missing extension vs installed extension
- shared `Core` behavior consistency tests between `Baseline` and `Enhanced`

If an implementation declares only `Baseline`, it must not be considered non-conformant with `v1.1.0` merely because it does not implement `Enhanced` abilities.

## 10. Relationship to Future Extensions

This document defines only the profile and capability boundaries for `v1.1.0`.

It does not mean that:

- `v1.1.0` has introduced procedural syntax.
- `v1.1.0` has committed to a program execution domain.
- `Enhanced` is equivalent to any future procedural layer.

Stronger procedural abilities should be carried through:

- new profiles
- `Reserved / Experimental` entries
- an extension registry
- companion-document extensions

They should not be introduced by rewriting the current `Core` trunk.
