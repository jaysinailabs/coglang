# CogLang Operator Catalog v1.1.0

## 0. Role of This Document

This document is the public companion catalog for `CogLang_Specification_v1_1_0_Draft.md`.

It answers three questions:

- which operators are explicitly closed in the `v1.1.0` specification set
- which operators still carry forward the `v1.0.2` compatibility position because they have not yet been migrated into the new template
- which operators must remain `Reserved / Experimental`

This document is a catalog, not the authoritative semantic source. The main specification remains authoritative for semantics. This catalog provides a status index for implementers, authors, and reviewers.

## 1. How to Read This Catalog

Entries in this catalog use three categories:

- `Explicit`
  The operator is described item by item in the `v1.1.0` main specification using the current operator template.
- `Carry-forward`
  The operator has not yet been rewritten item by item in `v1.1.0`, but continues to follow the `v1.0.2` semantics when that position does not conflict with the new main line.
- `Reserved / Experimental`
  Only the signature, direction, or status is frozen. A default implementation is not required.

If documents conflict, precedence is:

1. `CogLang_Specification_v1_1_0_Draft.md`
2. `CogLang_Migration_v1_0_2_to_v1_1_0.md`
3. `CogLang_Specification_v1_0_2.md`

## 2. Explicit Operators

The following operators are explicitly closed in the `v1.1.0` main specification.

| Operator | Status | Layer | Effect | Baseline | Notes |
|---------|--------|-------|--------|----------|-------|
| `Abstract` | `Core` | `language` | `meta` | Normal execution | Extracts and triggers prototypes only. It does not directly produce rules. |
| `Equal` | `Core` | `language` | Inherits parameter evaluation | Normal execution | Structural equality. It does not dereference node strings. |
| `Compare` | `Core` | `language` | Inherits parameter evaluation | Normal execution | Diagnostic delta. The minimal schema is frozen. |
| `Unify` | `Core` | `language` | `pure` after parameter reduction | Normal execution | Term-level and value-level unification. Error values may also be structurally matched. |
| `Match` | `Core` | `language` | Same as `Unify` | Normal execution | Exact alias of `Unify`. It must not expand into graph search. |
| `Get` | `Core` | `language` | `graph-read` | Normal execution | Three-way dispatch. It does not pierce transport or UI wrapper layers. |
| `Query` | `Core` | `language` | `graph-read` | Normal execution | Two-argument compatibility remains. The three-argument form introduces `k / mode`. |
| `AllNodes` | `Core` | `language` | `graph-read` | Normal execution | Returns a stable list of visible nodes. |
| `Traverse` | `Core` | `language` | `graph-read` | Normal execution | One-step outgoing-edge traversal. A missing start node returns `List[]`. |
| `ForEach` | `Core` | `language` | Inherits child expressions | Normal execution | Snapshot iteration. If `collection` is an error value, it returns `List[]`. |
| `Do` | `Core` | `language` | Inherits child expressions | Normal execution | Sequential container. Errors do not automatically stop later steps. |
| `If` | `Core` | `language` | Inherits the executed branch | Normal execution | Truthy branch selection. Auto-propagated error values are treated as false here. |
| `IfFound` | `Core` | `language` | Inherits the executed branch | Normal execution | Distinguishes available results from missing or failed results. `List[]` enters the then branch. |
| `Compose` | `Core` | `language` | `meta` | Normal execution | Registers dynamic operator definitions in the graph. The public return value is a registration receipt, not an internal `Operation` handle. |
| `Create` | `Core` | `language` | `graph-write` | Normal execution | Creates nodes and edges. The public node `type` is determined by the first argument. |
| `Update` | `Core` | `language` | `graph-write` | Normal execution | Covers node updates only. `confidence = 0` must use `Delete`. |
| `Delete` | `Core` | `language` | `graph-write` | Normal execution | Soft-delete only. Nodes and edges both retain history. |
| `Trace` | `Core` | `observability` | `diagnostic` | Normal execution | Value-transparent wrapper. |
| `Assert` | `Core` | `observability` | `diagnostic` | Normal execution | Non-fatal assertion. |
| `Explain` | `Reserved` | `observability` | `meta` | `StubError[...]` | Signature frozen. The plan object schema is not frozen. |

## 3. Carry-forward Operators

The following operators have not yet been migrated item by item into the new `v1.1.0` template. They continue to follow the `v1.0.2` compatibility position when there is no direct conflict with the new main line.

### 3.1 Graph Query and Data Access

| Operator | Status | Notes |
|---------|--------|-------|
| None | - | All high-priority entries in this section have been moved to `Explicit`. |

### 3.2 Control Flow and Binding

| Operator | Status | Notes |
|---------|--------|-------|
| None | - | All high-priority entries in this section have been moved to `Explicit`. |

### 3.3 Graph Write and Definition

| Operator | Status | Notes |
|---------|--------|-------|
| None | - | All high-priority entries in this section have been moved to `Explicit`. |

### 3.4 Transitional and Peripheral Capability

| Operator | Status | Notes |
|---------|--------|-------|
| `Send` | `Carry-forward` | Continues to be treated as a transitional capability. In `P1`, the default position may be `StubError[...]`. If the cross-instance protocol, default failure shape, and minimal trace requirements are frozen before `v1.2.0`, it may be promoted into the main specification. Otherwise, it should be downgraded to `Reserved`. |

## 4. Reserved / Experimental Directions

The following directions must not be treated as stable operators that are available by default.

### 4.1 Reserved

| Direction | Status | Notes |
|-----------|--------|-------|
| `Inspect` | `Reserved` | Object-structure inspection boundaries are described, but the default implementation may remain a stub. |
| Non-default `Query.mode` | `Reserved` | A default implementation is not required. |
| Query `cost / gain` meta-reasoning interfaces | `Reserved` | Key names are reserved. The complete schema is not frozen. |
| Rule candidate envelope | `Reserved` | Reserved as a bridge point for downstream rule-induction and validation stages. |
| Rule publish / rollback chain schema | `Reserved` | Not frozen in `v1.1`. |
| Concrete surface syntax for explicitly qualified names | `Reserved` | Only the existence of the capability is frozen, not the spelling. This is an implementer-reserved capability, not ordinary teachable user syntax. |

### 4.2 Experimental

| Direction | Status | Notes |
|-----------|--------|-------|
| `Recover[...]` | `Experimental` | Does not enter the `v1.1` core syntax. |
| Stronger `InspectSelf[...]` | `Experimental` | Involves permission and self-modification boundaries. |
| Rule self-modification operator | `Experimental` | High risk. |
| Adapter-specific tightly coupled operators | `Experimental` | Depend on the host environment and should not enter the core catalog. |

### 4.3 Architecture-Owned Future Directions (Non-v1.1)

The following directions are potential architecture evolution paths for `P3/P4`. They must not be read as part of the `v1.1` schedule and do not constitute the language core catalog.

| Direction | Status | Notes |
|-----------|--------|-------|
| Restricted procedural policy execution | `Future` | Directional placeholder for `P3` only. It does not enter `v1.1`. |
| Full program execution-domain capability | `Future` | Belongs to the `P4` direction. It does not enter the `v1.1` language trunk. |
| Procedural syntax extension | `Future` | If introduced, it should first go through a profile, extension, or reserved path instead of entering `Core` directly. |

## 5. Catalog Maintenance Principles

- Update the main specification first, then update this catalog.
- `Carry-forward` is not a permanent status. Once an entry is migrated into the main specification, move it out of this section.
- If an older operator directly conflicts with the new `v1.1.0` main line, identify the conflict in the migration document before deciding whether to rewrite, downgrade, or remove it.

## 6. Carry-forward Exit Conditions

Only a small number of boundary-sensitive entries remain in `Carry-forward`. Their exit conditions are:

1. `Send`
   If the cross-instance protocol, default failure shape, and minimal trace requirements are frozen before `v1.2.0`, `Send` may be promoted into the main specification. If those boundaries are still not frozen before `v1.2.0`, it should move from `Carry-forward` to `Reserved` so that it does not remain indefinitely ambiguous.
