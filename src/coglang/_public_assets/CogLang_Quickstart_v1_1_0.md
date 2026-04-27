# CogLang Quickstart v1.1.0

**Status**: stable release companion document
**Audience**: First-time CogLang users and implementers
**Scope**: Covers only the most common and stable `Baseline` forms
**Out of scope**: Full `Reserved / Experimental` capabilities, explicit qualified names for extension operators, host bridging, write-intent, and persistence-backend details

---

## 0. What This Document Is For

Use this document as a first-pass guide for getting started.

It answers three practical questions:

1. Which patterns to learn first when writing CogLang for the first time
2. Which forms can be relied on now, and which forms should be avoided for now
3. Where to go next for the authoritative definitions after writing a first valid expression

For formal semantics and related boundaries, see:

- **Complete semantics and frozen posture**: `CogLang_Specification_v1_1_0_Draft.md`
- **Profile / capability boundaries**: `CogLang_Profiles_and_Capabilities_v1_1_0.md`
- **Executable examples and regression constraints**: `CogLang_Conformance_Suite_v1_1_0.md`
- **Standalone installation and release trial path**: `CogLang_Standalone_Install_and_Release_Guide_v0_1.md`

If you want to first confirm that the installed package and the recommended minimal public entry points are available, run:

```powershell
coglang info
coglang release-check
coglang parse 'Equal[1, 1]'
coglang validate 'Equal[1, 1]'
coglang execute 'Equal[1, 1]'
coglang manifest
coglang vocab
coglang examples
coglang demo
```

For `doctor`, `smoke`, and packaged conformance checks, install the development extra first so `pytest` is available:

```powershell
pip install "coglang[dev]"
coglang doctor
coglang smoke
coglang conformance smoke
```

Under the current stable release posture, `release-check` should pass. If it fails, the usual cause is that the installed package or release metadata is incomplete.

---

## 1. Why CogLang Exists

For a first mental model, read `CogLang` as this:

`CogLang` is a **graph-first intermediate language** designed for parse determinism, canonicalization, and inspectable LLM-generated graph operations under an auditable host contract.

It currently makes several explicit design choices:

1. It uses a stable `M-expression / canonical text` form instead of relying on a freer surface syntax.
The reason: parsing, normalization, and inspectable generated structure come first; more elaborate syntax can come later.
2. It treats errors as values instead of making evaluation failure an automatic exception-style interruption.
The reason: in AI-driven graph operations, partial failure and locally unavailable results are normal conditions, not exceptional ones.
3. It keeps `profile / capability` close to the language boundary instead of leaving the host to infer them later.
The reason: extensions and hosts should explicitly declare what they require so a host can reject unsafe or unsuitable actions before execution.

It also has clear non-goals:

- It is not a general-purpose programming language
- It is not a schema definition language
- It does not try to replace other graph query languages in their native scenarios

If you need a mature general-purpose language ecosystem, a complete application framework, or a native query experience for a specific system, this Quickstart is not that kind of entry point.

---

## 2. Minimal Mental Model

For a first pass, remember five things:

1. CogLang is a **graph-first intermediate language**. Learn queries, conditionals, and tracing before extension syntax.
2. The form you normally write is **canonical text**. `readable render` is a more human-readable display form, not a separate syntax.
3. `Baseline` is the entry point for ordinary users. `Reserved` is not a capability to rely on by default.
4. `Create / Update / Delete` freeze **language-level write intent**. They do not mean that an executor directly writes to a particular persistence backend.
5. Explicit qualified names for extension operators are not part of the first teachable syntax set. Do not rely on them when starting out.

---

## 3. Minimal Example Graph Assumed Below

The examples below assume a minimal example graph:

- `einstein`
  `type = Entity`
  `category = "Person"`
  `label = "Einstein"`
- `tesla`
  `type = Entity`
  `category = "Person"`
  `label = "Tesla"`
- `ulm`
  `type = Entity`
  `category = "City"`
  `label = "Ulm"`
- One edge:
  `einstein -[born_in]-> ulm`

This matches the basic examples in the conformance suite, with the fields commonly used while reading made explicit here.

---

## 4. The First 4 Expression Types To Learn

### 4.1 Get a Field

```text
Get["einstein", "label"]
```

Expected result:

```text
"Einstein"
```

This form is the simplest way to build the intuition that a node ID plus a property key yields a value.

### 4.2 Query Nodes

```text
Query[n_, Equal[Get[n_, "category"], "Person"]]
```

Expected result:

```text
List["einstein", "tesla"]
```

For now, learn only two things here:

- `n_` is a binding variable
- `Query` returns a result list, not objects automatically inserted into the graph

### 4.3 Branch on Found Values

```text
IfFound[Traverse["einstein", "born_in"], x_, x_, "unknown"]
```

Expected result:

```text
List["ulm"]
```

Do not read `IfFound` as "an empty list goes to else."

The frozen posture is:

- `NotFound[]` goes to `else`
- Automatically propagated error values also go to `else`
- `List[]` does not automatically switch to `else`

If a value produced by one step needs to be passed to a later step, the official `v1.1.0` form is the bind-and-continue pattern `IfFound[expr, v_, thenExpr, elseExpr]`. Do not expect `Do` to automatically preserve intermediate values.

### 4.4 Add Tracing

```text
Trace[Traverse["einstein", "born_in"]]
```

Expected result:

```text
List["ulm"]
```

And:

- The semantic return value is the same as without `Trace`
- The corresponding execution event appears in trace / observer output

This form matters because it lets you inspect execution without changing the evaluation result.

---

## 5. The First Common Pitfalls

### 5.1 Do Not Put Business Categories in Public `type`

This older form should no longer be taught:

```text
Create["Entity", {"id": "tesla_02", "type": "Person"}]
```

The reason is not that "Person" is unimportant. The reason is:

- Public node `type` is reserved for `Entity / Concept / Rule / Meta`
- Business categories should go into other fields, such as `category`

### 5.2 Do Not Treat `Reserved` as Default Production Capability

`Explain` and `Inspect` have frozen signatures and default failure shapes, but they are still not the default entry point for ordinary users.

The first expression set should rely on:

- `Get`
- `Query`
- `Traverse`
- `If`
- `IfFound`
- `Trace`
- `Assert`

### 5.3 Do Not Treat Extension Qualified Names as Ready Syntax

The specification currently freezes only that explicit qualified names may exist. It does not freeze a concrete delimiter that ordinary users can write.

This means:

- Implementers can reserve this capability for extensions
- Ordinary users should not learn it as stable syntax

### 5.4 Do Not Read Language-Level Write Intent as Direct Write Permission

You can learn:

```text
Create["Entity", {"id": "tesla_01", "label": "Tesla"}]
```

But you should not infer from that expression that:

- The executor must directly write to a fixed backend
- The host-mediated persistence submission path is absent
- The language return value is the same thing as an architectural commit object

The language layer freezes expression semantics. The architecture layer freezes the commit path.

This also does not mean the executor "does nothing." Within the `v1.1.0` frozen boundary, the host runtime is responsible for pre-allocating IDs, forming a host-mediated persistence request, and mapping the commit result back to the language-level return value.

---

## 6. What To Avoid When Starting Out

If your goal is only to learn the first set of valid expressions, do not start with:

- `Explain`
- `Inspect`
- Non-default `Query.mode`
- Query `cost / gain` meta-reasoning interfaces
- extension-backed operators
- Explicit qualified names for extension operators

These capabilities belong to the second set of topics, not the first mental model.

---

## 7. Where To Go Next

If you understand the four expression types above, continue by role.

### 7.1 Ordinary Users

Read next:

1. `CogLang_Specification_v1_1_0_Draft.md`
   Start with `Four-layer representation model`, `Core operators`, and `Error model`.
2. `CogLang_Conformance_Suite_v1_1_0.md`
   Focus on `GE-003`, `GE-004`, `GE-006`, `GE-007`, `GE-021`, and `GE-022`.

### 7.2 Implementers

Read next:

1. `CogLang_Specification_v1_1_0_Draft.md`
2. `CogLang_Conformance_Suite_v1_1_0.md`
3. `CogLang_Migration_v1_0_2_to_v1_1_0.md`

---

## 8. One-Sentence Summary

When starting out, treat CogLang as:

**A graph-first intermediate language where you learn `Baseline`, queries, and conditionals first, and leave extensions and architecture details for later.**
