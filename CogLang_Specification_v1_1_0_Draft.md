# CogLang Language Specification

**Version: v1.1.0-pre**
**Status: pre-release state (the filename temporarily retains `Draft` for compatibility with existing references)**
**Position: authoritative main document for the current CogLang specification set; intended for implementation, conformance, external trials, and cross-host alignment**

---

## 0. Role of This Document

This document is the pre-release main specification for CogLang `v1.1.0`. It carries forward:

- The frozen core syntax, evaluation semantics, and error semantics from `v1.0.2`
- Requirements for extension mechanisms, meta-reasoning, observability, query interfaces, and rule bridging under the current architecture boundaries
- Reserved capabilities that need language-level declaration ahead of time, while leaving implementation details unfrozen by this version of the main text

This document is no longer used as a "chapter skeleton draft". For the current stage, it should be treated as:

- The pre-release authoritative source for the language surface, evaluation semantics, error model, and expression-level observability
- The primary basis for companion docs, conformance, migration documents, and host integration references
- The judgment baseline for later convergence of `Reserved / Experimental` capabilities and implementation alignment

---

## 1. Specification Status and Versioning Strategy

### 1.1 Document Nature

This specification distinguishes two kinds of content:

- **Normative**: implementations, tests, training data, and compatibility judgments must comply with it
- **Informative**: design motivation, examples, non-binding explanation, and future direction

The body text should explicitly use the following terms:

- `MUST`
- `SHOULD`
- `MAY`
- `RESERVED`
- `EXPERIMENTAL`

If an Informative description in the body conflicts with a Normative rule, the Normative rule takes precedence.

### 1.1.1 Compatibility Surfaces

CogLang compatibility is not a single dimension. It includes at least the following five surfaces:

1. **Parser surface**: whether text can be parsed into an AST
2. **Validator surface**: whether an expression is a valid CogLang program
3. **Execution surface**: whether executors implement semantics and error behavior consistently
4. **Rendering surface**: whether readable rendering and trace presentation remain stable
5. **Canonical serialization surface**: whether canonical serialization remains stable

Compatibility statements in the specification **SHOULD** state the affected surface explicitly.

Unless otherwise specified:

- For `Core` capabilities, compatibility means at least that the `parser / validator / execution` surfaces are not broken
- If a change affects the `rendering` or `canonical serialization` surface, the body text **MUST** say so explicitly

### 1.1.2 Computational Scope and Language Identity

In `v1.1.0`, `CogLang` **MUST** be understood as:

- A graph-first execution language
- An AI-specific semantic interface
- A language that supports procedural composition, but does not target general-purpose programming

This specification only freezes:

- The language surface and canonical serialization
- Minimum consistency requirements for parser / validator / execution
- Expression-level observability and extension boundaries

This specification does **not** directly freeze:

- The canonical status or field responsibilities of application-side exchange objects
- The physical storage shape of persistence backends
- The classification scheme for message or task dispatch protocols
- The full lifecycle object model for rule candidates, publication, and rollback

"Graph-first" means:

- The core public object model is centered on graph nodes, edges, rule objects, and their auditable results
- The introduction of control flow, structural values, and composition capabilities primarily serves graph queries, graph updates, rule triggering, pre-validation representation, and observable execution

"Supports procedural composition" means:

- Capabilities such as `If / Do / ForEach / Compose / List / Dict` can be used to organize local execution processes
- The main purpose of these capabilities is to support the main graph semantics path, not to expand `CogLang` into a general-purpose scripting language for humans to write by hand

Therefore, if a new capability mainly serves:

- Syntactic convenience for human hand-writing comfort
- Alignment with traditional general-purpose language surfaces
- Large-scale general runtime capability unrelated to the main graph semantics path

Then that capability **SHOULD NOT** enter `Core` directly without a clear graph-first rationale.

### 1.2 Version Evolution Principles

The freeze of `v1.0.2` applies only during the P0 dependency period and is not a permanent freeze.

The goals of `v1.1.0` are:

- Keep the `v1.0.2` core semantics stable
- Introduce the structured extension points required by the current stage
- Establish clear boundaries for Reserved / Experimental capabilities

The primary goal of `v1.1.0` is not to expand the freedom of the CogLang surface syntax. Instead, it is to make:

- Language semantics
- Extension boundaries
- Human-readable interfaces
- Interface contracts for executor / runtime bridge / trace

share one consistent judgment standard in the same specification.

### 1.2.1 Version Numbering Rules

This specification uses the following version semantics:

- `v1.0.x`: errata versions; only compatible fixes, disambiguation, and missing clarifications are allowed
- `v1.x`: backward-compatible extensions; new `Reserved` / `Experimental` / new `Core` capabilities are allowed, but existing `Core` must not be broken
- `v2.x`: breaking changes are allowed; migration documentation and compatibility notes are required

### 1.3 Three-Tier Feature System

CogLang features are divided into three tiers:

| Tier | Meaning | Compatibility commitment |
|------|---------|--------------------------|
| `Core` | Frozen core language capability | Name and semantics are stable |
| `Reserved` | Reserved and callable, but semantics or implementation are not fully frozen | Name is stable; semantics may converge |
| `Experimental` | Capability under exploration | Name and semantics may both change |

### 1.4 Feature Promotion Rules

#### `Experimental -> Reserved`

For a capability to be promoted from `Experimental` to `Reserved`, it must satisfy at least:

- Frozen name: the operator name or abstract capability name is fixed
- Fixed owning layer: it is clear which layer it belongs to among `language / executor / runtime_bridge / observability / adapter`
- Fixed minimum signature: argument count, argument roles, and default error behavior are clear
- Validation-stage failure forms and runtime default failure behavior are both clear
- Trace strategy is clear: whether it needs to enter the reasoning trace, and what the minimum recorded fields are

#### `Reserved -> Core`

For a capability to be promoted from `Reserved` to `Core`, it must satisfy at least:

- Normative semantics are complete and do not depend on key branches being "left for implementers to decide"
- At least one reference implementation passes conformance tests
- The impact on parser / validator / executor / readable render has been implemented
- Error semantics, permission boundaries, and observability fields are frozen
- The training and data-generation pipeline has a stable canonical form

#### Breaking Change Window

The following changes are considered breaking changes:

- Signature changes to an existing `Core` operator
- Structural changes to `Core` error expressions
- Changes to canonical serialization
- Changes to the name semantics of a frozen Head
- Structural changes in readable render that cause humans to lose location information

Breaking changes are allowed only:

- During the `-draft` stage
- And only when migration notes and golden examples are updated at the same time

For any released non-draft version, every breaking change must be accompanied by a new version number and migration documentation.

#### Linkage Requirements for Companion Assets

Once any of the following content enters `Reserved` or `Core`, the corresponding assets must be updated at the same time:

- conformance suite
- operator catalog
- migration documents
- rendering / UI contract
- training data specification, if the training format is affected

---

## 2. Terms and Consistency Conventions

This section defines stable terms used in the body text.

| Term | Meaning |
|------|---------|
| `expression` | A syntactic CogLang expression |
| `Head` | The symbol name at the head position of an expression in the AST, used for name resolution |
| `operator head` | A Head that starts with an uppercase letter and can participate in operator name resolution |
| `term head` | A Head that starts with a lowercase letter and is used to represent structured terms or patterns |
| `AST` | The parsed internal structured representation; the authoritative object for execution semantics |
| `canonical text` | The unique canonical serialization form, used for training data, storage, and regression tests |
| `readable render` | Stable text generated for human presentation; it is not required to be a canonical spelling |
| `transport envelope` | A structured wrapper for trace, UI, and cross-component transport |
| `primitive` | A core operation that cannot be derived from other operations |
| `built-in` | An operation whose semantics are provided natively by the executor; special-form or native type dispatch is a common implementation approach, not a requirement |
| `shortcut` | A common pattern preconfigured to reduce generation difficulty |
| `ABSTRACT` | Module/mechanism spelling used in architecture documents; unless version migration notes state otherwise, the canonical Head on the current language surface remains `Abstract` |
| `extension-backed operator` | An operator implemented by a registry or external adapter |
| `graph-read` | An effect category that reads the graph but does not modify it |
| `graph-write` | An effect category that modifies the graph, rule layer, or persistent state |
| `meta` | Operations on meta-layer objects such as execution plans, costs, and rule state |
| `diagnostic` | An effect category used only for trace, assertions, diagnostics, and rendering |
| `external` | An effect category that depends on external plugins, external systems, or external knowledge sources |
| `deterministic` | The result should be exactly the same under the same input and the same state |
| `graph-state-dependent` | The result depends on the current graph state |
| `model-dependent` | The result depends on a model or learned component |
| `implementation-defined` | The specification permits the implementation to decide details, but those details must be documented |

Unless otherwise specified:

- `Head` refers to the name at the syntax layer
- `operator` refers to a callable capability after name resolution
- `operator head` and `term head` share the same applicative syntax shape, but only the former enters the default operator resolution process

The same name may map to different operator implementations at different runtime layers, but the `Head` in its AST is still a single syntax object.

---

## 3. Representation-Layer Model

### 3.1 Four Representation Layers

CogLang specification objects must be divided into four layers:

1. **AST / internal semantic object**
2. **Canonical Text / canonical serialization**
3. **Readable Render / human-readable presentation**
4. **Transport Envelope / wrapper for trace, UI, and cross-component transport**

### 3.2 Four-Layer Conversion Constraints

#### `AST <-> Canonical Text`

`AST` and `canonical text` must satisfy lossless round-trip:

- `parse(canonical_text(expr)) == expr`
- `canonical_text(parse(text))` must produce the unique canonical form

Here, "equal" means **structurally equal**, ignoring source spans, render hints, and transport-only metadata.

If a textual spelling can be accepted by the parser but is not canonical, the pretty-printer must normalize it to the canonical form.

#### `AST -> Readable Render`

The goal of `readable render` is to help humans understand, not to replace the canonical form. Therefore:

- `readable render` is not required to be directly parseable back into the same AST
- The same AST under the same render profile must nevertheless produce stable output
- `readable render` must not introduce semantic information that is not present in the AST
- If readable render is embedded in a trace or UI envelope, it must preserve location information traceable back to the original AST node

#### `AST -> Transport Envelope`

`transport envelope` is used for UI, trace, and cross-component communication. Its minimum responsibilities are:

- Carry the original AST or a reference locatable to the AST
- Carry canonical text or a reference to it
- Optionally carry readable render
- Carry auxiliary fields related to the current execution, such as trace / source / capability / confidence

`transport envelope` is not part of CogLang core syntax; it is a structured wrapper for the runtime and presentation layers.

#### UI Noise-Reduction Rules

When presenting to humans, it is allowed to:

- Collapse long lists
- Hide default values
- Show structural summaries instead of complete subtrees

However, the following information must not be lost:

- Head name
- Argument positional relationships
- Error type
- Traceable references to rules / trace / source

### 3.3 CogLang Semantic Objects

CogLang semantic objects are graph structures and ASTs, not token sequences.

Therefore:

- The authoritative exchange object between the executor and the host runtime bridge should be an AST or equivalent structured object, not a prompt token stream
- Token order belongs only to the serialization layer and does not determine graph semantics in reverse
- LLM-facing prompt wrappers and termination tokens such as `<|end_coglang|>` are not part of CogLang core semantics

This specification assumes the following boundaries by default:

- **Language boundary**: `AST`, canonical form, error semantics, operator semantics
- **Rendering boundary**: readable render, UI presentation, trace readable summary
- **Runtime boundary**: runtime bridge / host transport / adapter envelope fields and capability checks

If a piece of information belongs only to the runtime boundary, it should not be forcibly promoted to a core syntax component because of UI or trace needs.

---

## 4. Lexical Structure and Syntax

### 4.1 Lexical Rules

The `v1.1.0` canonical surface of CogLang freezes only the minimal lexical set and does not reserve specific delimiters in advance for future qualified-name syntax.

#### Identifiers and Variables

- `operator head`: starts with an uppercase letter, followed by letters, digits, or `_`, and must not end with `_`
- `term head` / `atom`: starts with a lowercase letter, followed by letters, digits, or `_`, and must not end with `_`
- Named variable: starts with a letter, followed by letters, digits, or `_`, and ends with a single trailing `_`
- Anonymous wildcard: the single character `_`

Therefore, `Traverse` is a valid `operator head`, `f` is a valid `term head`, `person_` is a valid named variable, and `Traverse_` is not a valid `operator head`.

#### String Literals

- Enclosed in double quotes
- The canonical surface supports at least the `\"` and `\\` escapes
- Extra escape sequences such as newline and tab may be supported by implementations, but the canonical serializer must output them stably

#### Numbers

- Decimal integers and decimal floating-point numbers are supported
- A leading `+` is not allowed
- The canonical form of an integer has no decimal point

#### Reserved Symbols

`[ ] { } , : "`

These symbols are used respectively for:

- application delimiters
- dictionary literals
- argument separators
- key-value separators
- string delimiters

#### Whitespace, Newlines, and Comments

- In canonical text, whitespace only acts as a separator outside string literals
- Multiple whitespace characters must not affect the AST
- Comments are not part of the `v1.1.0` canonical surface

If a host tool supports comments, it may only treat them as a non-canonical input convenience; comments must be stripped before canonical serialization and conformance testing.

### 4.2 Syntax Rules

The minimum EBNF for `v1.1.0` is:

```ebnf
expression      ::= application
                  | atom
                  | string_literal
                  | number_literal
                  | named_variable
                  | wildcard
                  | dict_literal ;

application     ::= head_symbol "[" [arguments] "]" ;
arguments        ::= expression { "," expression } ;

head_symbol      ::= operator_head | term_head ;
operator_head    ::= upper_letter { letter | digit | "_" } ;
term_head        ::= lower_letter { letter | digit | "_" } ;
atom             ::= term_head ;
named_variable   ::= identifier_core "_" ;
wildcard         ::= "_" ;
identifier_core  ::= letter { letter | digit | "_" } ;

dict_literal     ::= "{" [dict_entries] "}" ;
dict_entries     ::= dict_entry { "," dict_entry } ;
dict_entry       ::= string_literal ":" expression ;
```

Supplemental constraints:

- Both `operator head` and `term head` can syntactically form an `application`
- Only `operator head` participates by default in the operator name resolution defined in `§10`
- `term head` and `atom` are used to represent structured terms, patterns, or data items; whether they may appear at a given argument position is determined by the entry for the outer operator
- `True[]`, `False[]`, `NotFound[]`, and similar forms are zero-argument `application`s

This definition explicitly fixes the historical conflict in `v1.0.2` between the "uppercase Head rule" and structured-term examples such as `Unify[f[a], ...]`: a lowercase `term head` is valid, but it is not an executable operator by default.

### 4.3 Canonical Form

Canonical text is the unique canonical serialization form of a single AST.

`v1.1.0` freezes the following canonical rules:

1. There is no space between `Head` and `[`
2. Arguments are separated by `, `
3. Applications always spell out square brackets explicitly, and zero-argument applications must also be written as `Head[]`
4. Strings use double quotes; the canonical serializer must stably escape internal quotes and backslashes
5. Dictionaries use JSON-style `{}`, with one space after a colon and one space after a comma
6. Dictionary keys are stably sorted in lexicographic order
7. Canonical text is always a single line

For numbers:

- Integers must be output in decimal form without a decimal point
- Non-integers must be output in a stable decimal form that the implementation can round-trip

Multiline text is not canonical text. This specification defines the handling rules for "multiline sequential input" as follows:

- If a host allows one text segment to contain multiple top-level expressions
- It must be explicitly lowered to a sequence container before entering the AST / validator
- Under the default semantics of `v1.1.0`, that sequence container is `Do[...]`

Therefore, multiline input is a host input convenience, not a new core syntax structure.

### 4.4 Readable Render

Readable Render is stable presentation for humans. It is not required to be a unique spelling, but it must be generated stably.

The recommended baseline line-wrapping rules are:

- Single-line expressions may be displayed directly in canonical style
- Multiline expressions use 2-space indentation
- Multiline applications use a stable layout with each argument on its own line
- Multiline dictionaries use a stable layout with each key-value pair on its own line

Readable Render should prioritize inspectability for the following scenarios:

- Deeply nested `Do / ForEach / If / IfFound / Query`
- Diagnostic logs from `Trace` and `Assert`
- Partial structure display for `ParseError`

Readable Render may share token order with canonical text, but it must not be required to remain single-line and must not be used to define AST equality.

---

## 5. Evaluation Model and Effect System

### 5.1 Evaluation Order

Unless a `Special Form` entry specifies otherwise, CogLang uses **inside-out, left-to-right eager evaluation**.

The default rules are:

1. Evaluate the innermost nested expressions first
2. Evaluate the arguments of the same application one by one from left to right
3. When an argument evaluates to an automatically propagated error value, a normal operator immediately propagates that value

#### Special Forms

The following operators have frozen special evaluation rules:

| Special Form | Evaluation Rule |
|-------------|----------|
| `If[cond, thenExpr, elseExpr]` | Eagerly evaluate `cond` first, then evaluate only one branch |
| `IfFound[expr, bindVar_, thenExpr, elseExpr]` | Eagerly evaluate `expr` first, then evaluate only one branch based on the result |
| `ForEach[collection, bindVar_, body]` | Evaluate `collection` once to obtain a snapshot; evaluate `body` on the bound AST in each iteration |
| `Do[e1, e2, ...]` | Evaluate each expression from left to right, rather than evaluating all arguments before invocation |
| `Compose[name, params, body]` | Evaluate `name` and `params` first; store `body` as an AST and do not execute it at definition time |
| `Assert[condition, message]` | Evaluate `condition` first; evaluate `message` only when an assertion failure needs to be recorded |
| `Query[bindVar_, condition, options?]` | Treat `bindVar_` as a binding site and do not evaluate it first; evaluate `condition` in each candidate node's binding environment; evaluate `options` first |

All operators not listed in the table above must follow the default eager rules.

#### Binding and Scope

- Binding variables of `ForEach`, `IfFound`, and `Query` are valid only in the evaluation context of the corresponding body / condition
- A binding variable MUST NOT be referenced after it leaves its scope
- The `v1.1.x` baseline profile does not allow reusing the same binding variable name in nested binding scopes; validators must reject such forms to avoid capture ambiguity

#### Snapshot Semantics

The `collection` of `ForEach` MUST be fully evaluated once before iteration begins. Subsequent iterations execute against that snapshot; side effects such as `Create / Update / Delete` in the body MUST NOT write back in a way that affects collection members not yet consumed in the current iteration.

#### Evaluation of Multiline Sequential Input

If a host accepts multiline top-level input and lowers it to `Do[...]`, those lines are evaluated in the same left-to-right order as `Do`, without introducing additional program-block semantics.

### 5.2 Error Propagation and Recovery Boundaries

Errors in CogLang are values, not host exceptions. Unless an operator entry specifies otherwise, a normal operator that receives an error value as an argument **MUST directly propagate that error value** and MUST NOT continue executing its body semantics.

This specification currently freezes the following set of error values as "automatically propagated error values":

- `NotFound[]`
- `TypeError[...]`
- `PermissionError[...]`
- `ParseError[...]`
- `StubError[...]`
- `RecursionError[...]`

`List[]` is not an error value. It may be judged false by some operators, but that truthiness semantics MUST NOT be mistaken for error-propagation semantics.

Only two categories of mechanisms may form a "recovery boundary":

- Operators explicitly defined by the language as error branch points, error absorption points, or non-fatal diagnostic points
- Host-level recovery wrappers explicitly declared by a profile

The propagation blockers explicitly identified by the current specification include `If`, `IfFound`, `Do`, and `ForEach`; their specific branching or absorption semantics are governed by their operator entries.

`v1.1.0` does not introduce a new general-purpose `Recover[...]` core syntax. If a later version needs one, it must explicitly align with this section's automatic propagation rules rather than implicitly overriding them.

Unless an entry is explicitly declared as `graph-write`, a normal successful return only means "this execution produced a result" and **MUST NOT** be interpreted as "this result should automatically enter the graph". Procedural intermediate state, local containers, and short-lived results remain in the execution context by default; the authoritative rules for graph persistence boundaries are in `§6.2`.

### 5.3 Effect Categories

Each operator must be annotated with one or a combination of the following effect categories:

- `pure`
- `graph-read`
- `graph-write`
- `meta`
- `diagnostic`
- `external`

### 5.4 Determinism Categories

Each operator must be annotated with one of the following determinism categories:

- `deterministic`
- `graph-state-dependent`
- `model-dependent`
- `implementation-defined`

---

## 6. Core Types and Data Model

### 6.1 Core Value Types

CogLang's minimum core value types are:

| Type | Description |
|------|------|
| `String` | UTF-8 text value; node IDs, relation names, error reasons, labels, and similar values may all fall into this type |
| `Number` | Integer or floating-point number; whether an implementation-level distinction between integers and floats is retained may be refined by a profile |
| `Bool` | Canonical Boolean value; corresponds to `True[]` / `False[]` on the canonical surface |
| `List` | Ordered sequence; preserves element order |
| `Dict` | Key-value mapping; keys must be strings |
| `ErrorExpr` | Legal CogLang expression represented with an error Head; see §8 |

Additional constraints:

- Every value must have canonical text and readable render
- The order of a `List` has semantic meaning; the key order of a `Dict` has no semantic meaning, but canonical serialization must be stable
- `ErrorExpr` is not a host exception wrapper, but a normal value category that expressions can consume
- This version does not introduce independent `Null` or `Maybe` core syntax; absence semantics remain represented by error values such as `NotFound[]` or by explicit structures

### 6.2 Graph Objects

Graph objects that the CogLang runtime can read and write are divided into nodes and edges. They belong first to the raw structure layer, and only secondarily may be wrapped by the specification layer or output layer.

#### Explicit Graph-Write Boundary and Prohibition on Implicit Graphification

Writing to the graph **MUST** be treated as an explicit semantic action, not as a default side effect.

Unless an operator's Normative entry explicitly declares that it includes `graph-write` semantics, evaluation of that operator **MUST NOT**:

- Create new public graph nodes or edges
- Automatically promote local intermediate values to public knowledge objects
- Automatically persist temporary results from an execution into the graph
- Automatically publish execution-time internal artifacts as shareable rules or public nodes

Therefore, the following objects **MUST** remain in the execution context by default and MUST NOT be automatically graphified:

- Local binding values
- Intermediate list / dictionary results
- Short-lived products of procedural steps such as aggregation, filtering, reduction, and sorting
- Auxiliary fields carried in trace / diagnostic / envelope data
- Temporary processed results returned by adapters or extension implementations
- Executor-internal artifacts, such as internal `Operation` carriers

If an implementation wants to persist, publish, or include a category of results in graph lifecycle management, it **MUST** do so explicitly through one of the following mechanisms:

- Invoke a frozen `graph-write` operator
- Invoke a later `Reserved / Experimental` operator that is explicitly declared to have graph-write semantics
- Enter a documented host-side explicit publication flow that is compatible with this specification

"Successful execution" and "entering the graph" are not synonyms. Unless an entry states otherwise, successful return of procedural intermediate state **MUST NOT** be interpreted as "should be written to the graph".

#### Nodes

The minimum stable fields of a node are:

| Field | Requirement |
|------|------|
| `id` | Globally unique identifier |
| `type` | Node type label |
| `confidence` | `float[0,1]` |
| `provenance` | Source annotation or a reference to it |
| `created_at` | Creation time or an equivalent temporal marker |
| `updated_at` | Most recent update time or an equivalent temporal marker |

Under the current public baseline of `v1.1.0`, the primary node types of the public knowledge graph are frozen as:

- `Entity`
- `Concept`
- `Rule`
- `Meta`

The following fields are reserved as recommended extension fields:

- `label`
- `embedding`
- `origin_generation`
- `trust_source`

#### Edges

The minimum stable fields of an edge are:

| Field | Requirement |
|------|------|
| `source_id` | Source node ID |
| `target_id` | Target node ID |
| `relation` | Relation type |
| `confidence` | `float[0,1]` |
| `provenance` | Source annotation or a reference to it |

The following fields are reserved as recommended extension fields:

- `evidence`
- `origin_generation`
- `trust_source`
- `created_at`
- `updated_at`

Both nodes and edges use soft-delete semantics: objects with `confidence = 0` remain in the raw structure layer but do not participate in normal query results by default.

#### `Rule` Nodes and Executor-Internal `Operation` Carriers

`Rule` is a first-class node type in the public knowledge graph, used to carry rule objects that have been validated, traced, or are pending promotion.

`Operation` nodes appeared in `v1.0.2` as dynamic operator carriers; `v1.1.0` preserves the validity of this executor-internal representation, but no longer defines it as part of the primary types of the public knowledge graph. If an implementation continues to use `Operation` nodes to carry `Compose` results, they must satisfy the following requirements:

- They are treated as executor-internal artifacts, not as a public knowledge node category
- They MUST NOT be confused with the public classifications `Entity / Concept / Rule / Meta`
- When exposed externally, they should explicitly mark their internal identity through readable render, diagnostics, or management interfaces

### 6.3 Result Envelope

CogLang's **semantic return value** must be distinguished from its **outer result envelope**.

- The semantic return value is the CogLang value directly returned by an operator according to its entry
- The result envelope is a wrapper object used by the transport / UI / debugging layer to carry additional metadata

The specification does not require every operator to return an envelope; however, when an envelope is used, it must follow these minimum field names:

| Field | Requirement |
|------|------|
| `value` | Semantically authoritative return value |
| `metadata` | Structured additional information |
| `trace_ref` | Reference to the related trace entry or trace session; may be omitted if there is no trace |

The following fields reserve only their key names in `v1.1.0`; their full schemas are not frozen:

- `confidence`
- `cost`
- `gain`

That is:

- `value / metadata / trace_ref` are the shared core fields of the result envelope
- `confidence` is a common execution / inference-side extension field, not a minimum field that must always be present in every transport / UI envelope
- UI / diagnostic fields such as `source_span / diagnostic_code` are handled by transport envelope contracts and are not directly incorporated into this entry's shared core fields
- Application-side query result exchange objects may have richer result schemas; they are not the result envelope defined by this entry. This entry freezes only the minimum shared fields for expression execution results, not application-side query result schemas

Envelope constraints are:

- An envelope MUST NOT rewrite the semantics of `value`
- Fields in `metadata` may be extended, but MUST NOT override the meaning of the minimum field names
- When an operator itself already returns a structured object, that object remains the semantic return value and should not be automatically treated as an envelope

---

## 7. Operator 规范

### 7.1 条目模板

每个 operator 条目固定写以下 **7 个核心项**：

1. **状态**：`Core / Reserved / Experimental`
2. **所属层**：`language / executor / runtime_bridge / observability / adapter`
3. **语法与签名**
4. **Validator Constraints**
5. **返回契约**
6. **语义**
7. **Baseline Availability**

并固定写以下 **4 个补充项**：

- **效果类别**
- **确定性类别**
- **可观测性要求**
- **兼容性承诺**

#### 条目书写规则

- `Core` operator 的“语义”必须是完整 Normative 描述，不能只写设计意图
- `Reserved` operator 必须至少冻结签名、验证约束、默认失败行为、trace 要求
- `Experimental` operator 可以保留实现自由度，但仍必须声明效果类别与权限边界
- 若一个 operator 依赖外部实现，其条目必须显式说明“名称已冻结”与“行为未冻结”是否同时成立
- `Validator Constraints` 只描述语法、参数个数、变量位置、名称解析、以及可静态判定的字面量约束；表达式求值后的动态类型不匹配必须写入“返回契约”或“语义”，不得混写为 validator 失败
- 对透明包装器或条件式包装器，确定性类别可以声明为“继承被包装表达式”；若其诊断事件或元数据编码仍保留实现自由度，必须在“语义”或“可观测性要求”中显式说明

#### Baseline Availability 的判定

本项描述的是**通过验证后的运行时基线可用性**，不覆盖 parser 或 validator 阶段的拒绝。

`Baseline Availability` 只允许使用以下三种形式：

- **正常执行**
- **`StubError[...]`**
- **`PermissionError[...]`**

不允许写成“由实现决定”或“可能不可用”。

若该可用性依赖 profile，条目必须写成 `Profile <name>: ...` 的形式，且 profile 名称必须在伴随文档或 manifest 中定义。

#### 后续程序层能力的准入原则

当后续版本考虑引入更强的程序层能力时，其进入 `Core` 前 **SHOULD** 至少满足以下条件：

- 该能力对图查询、图更新、规则触发、验证前表示、或可观测执行具有直接支撑作用
- 其核心语义可以在不依赖特定宿主实现技巧的前提下被稳定冻结
- 它不会把临时中间态、局部容器或一次性算法步骤默认提升为图谱对象
- 它不是主要为了对齐传统通用语言表面，或提高人类手写舒适度而引入
- 它不能更自然地被实现为 `Reserved`、`Experimental`、`extension-backed operator`、或 profile 特定能力

若某项能力主要承担：

- 列表 / 字典上的复杂规约、聚合、排序、过滤
- 强宿主耦合的本地算法、外部系统调用、或工具链桥接
- 仅服务于单次执行而不形成稳定知识对象的局部处理步骤

则它 **SHOULD** 先以 profile 扩展、注册表条目、或 `Reserved / Experimental` 条目存在，而不是直接扩大 `Core` 主干。

### 7.2 Core Operators

#### `Abstract`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Abstract[instances]
```

**Validator Constraints**：

- 必须且仅接受一个参数
- `instances` 必须是合法 CogLang 表达式

**返回契约**：

成功时返回一个结构化结果对象：

```text
{
  "cluster_id": str,
  "instance_count": int,
  "prototype_ref": str,
  "equivalence_class_ref": str,
  "selection_basis": str | Dict[...],
  "triggered": True[] | False[]
}
```

失败时：

- `instances` 求值后不是列表：`TypeError["Abstract", "instances", ...]`
- 名称与参数通过验证但当前 profile 不支持：`StubError["Abstract", ...]`

空列表输入必须返回一个非触发摘要对象；`triggered = False[]` 是合法正常结果，不是错误。

**语义**：

`Abstract` 的语义是对一组实例进行原型提取与触发判定。它：

- 接收一批待抽象的实例
- 先形成等价类或候选聚类，再形成该批实例对应的 prototype / cluster 表示
- 判断该模式是否达到“足够成熟，可以触发后续归纳”的阈值
- 返回本次抽象结果的结构化摘要

主规范只冻结 `triggered` 的字段类型与语义边界，不冻结具体阈值、具体聚类算法或具体触发启发式；这些实现起步建议应写入 companion / implementation note，而不是写入本条的规范正文。

`Abstract` 必须保留两类 provenance：

- 等价类成员列表的可追溯引用
- 代表选择或原型形成依据的可追溯说明

`Abstract` 不得因为形成代表或原型而删除、覆盖、或隐式合并原始实例；它只能为后续规范化、归纳、或解释层操作提供触发摘要。

`Abstract` **不**直接生成规则候选，**不**执行 Logic Engine 验证，**不**直接写入草稿图谱或主图谱。规则生成与验证属于后续流水线：

`Abstract -> Encoder -> Logic Engine -> draft/promote`

**Baseline Availability**：正常执行
**效果类别**：`meta`
**确定性类别**：`model-dependent`
**可观测性要求**：

- 必须记录 `cluster_id`
- 必须记录 `instance_count`
- 必须记录 `prototype_ref`
- 必须记录 `equivalence_class_ref`
- 必须记录 `selection_basis`
- 必须记录 `triggered`

**兼容性承诺**：

- `Abstract[instances]` 这一签名在 `v1.1.x` 内冻结
- 返回值中的六个最小字段在 `v1.1.x` 内冻结
- prototype 的内部编码与具体训练后端仍可演化

#### `Equal`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Equal[a, b]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `a` 与 `b` 都必须是合法 CogLang 表达式
- `Equal` 不引入新的绑定变量位，也不承担名称解析扩展语义
- 动态类型差异不属于 validator 失败；它们属于运行时比较语义的一部分

**返回契约**：

- `a` 或 `b` 的求值结果为自动传播错误值时：原样传播该错误值
- 两侧值结构相等时：返回 `True[]`
- 两侧值结构不相等时：返回 `False[]`
- `Equal` 不因“值类型不同”而返回 `TypeError[...]`；异类正常值之间的比较结果就是 `False[]`

**语义**：

`Equal` 是普通 eager operator，不是 `special form`。

`Equal` 比较的是语义值的结构相等，而不是 source text、readable render 或 transport envelope 的文本相等。这里的“结构相等”沿用 `§3.2` 的全局定义：忽略 source span、render hint 与 transport-only metadata。

具体规则如下：

- 字符串按字面值比较
- 数字按数值比较
- `True[] / False[]` 按布尔值比较
- `List` 的长度必须相同，元素按位置递归比较；列表顺序具有语义意义
- `Dict` 的键集合必须相同，每个键对应值递归比较；键顺序不具有语义意义
- 结构化项 / application 的 `Head` 必须相同、参数个数必须相同、参数按位置递归比较

`Equal` 不消费自动传播错误值；若调用方需要对错误表达式做结构化匹配，应使用 `Unify` 或等价的显式检视机制。

若某个字符串恰好是节点 ID，`Equal` 也只把它当字符串值；不得隐式解引用图节点。

`Equal` 用于布尔判断和控制流，不承担差异解释职责；差异解释属于 `Compare`。

**Baseline Availability**：正常执行
**效果类别**：继承 `a` 与 `b` 的求值效果并集
**确定性类别**：继承 `a` 与 `b`；在两侧值固定后，相等判断本身必须是 `deterministic`
**可观测性要求**：

- 必须记录 `comparison_kind = equal`
- 必须记录 `result = True[] | False[]`

**兼容性承诺**：

- `Equal[a, b]` 的二参数签名在 `v1.1.x` 内冻结
- “结构相等返回 `True[]`，否则 `False[]`” 在 `v1.1.x` 内冻结
- `List` 的顺序敏感、`Dict` 的键顺序不敏感，这两条在 `v1.1.x` 内冻结
- `Equal` 不自动穿透 transport / UI 包装、不自动解引用节点字符串，这两条在 `v1.1.x` 内冻结

#### `Compare`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Compare[a, b]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `a` 与 `b` 都必须是合法 CogLang 表达式
- `Compare` 不引入绑定变量位，也不承担名称解析扩展语义
- 动态类型差异不属于 validator 失败；它们属于运行时差异构造语义的一部分

**返回契约**：

- `a` 或 `b` 的求值结果为自动传播错误值时：原样传播该错误值
- 两侧值结构相等时：返回空字典 `{}`
- 两侧值不相等时：返回描述结构差异的 `Dict`
- `Compare` 不因“值类型不同”而返回 `TypeError[...]`；异类正常值之间的差异仍以差异字典表达

**语义**：

`Compare` 是普通 eager operator，不是 `special form`。

`Compare` 比较的是语义值结构，而不是 source text、readable render 或 transport envelope。其输出是诊断性 delta，不是布尔值；控制流应使用 `Equal`，不是 `Compare`。

`v1.1.x` 中冻结的最小 delta 规则如下：

- 完全相等：返回 `{}`
- 原子值不相等，或结构类型/形状不同：返回 `{"expected": a, "actual": b}`
- 两侧都是同一 `Head` 且参数个数相同的 application：只为不相等的参数位置生成子差异，键名使用 `arg0`、`arg1`、`arg2` ...
- 两侧都是等长 `List`：只为不相等的位置生成子差异，键名使用 `index0`、`index1`、`index2` ...
- 两侧都是 `Dict`：只为不相等或缺失的键生成子差异；缺失一侧可用 `NotFound[]` 作为 `expected` 或 `actual`

`Compare` 不消费自动传播错误值；若调用方需要对错误表达式做结构化匹配，应使用 `Unify` 或等价的显式检视机制。

因此，`Compare[f[a, b], f[a, c]]` 的稳定结果应为：

```text
{"arg1": {"expected": "b", "actual": "c"}}
```

若某个字符串恰好是节点 ID，`Compare` 也只把它当字符串值；不得隐式解引用图节点，不得扩展成图谱级 diff。

delta 的键顺序不具有语义意义，但 canonical 序列化必须稳定。

`Compare` 的递归展开深度继承执行环境的通用递归限制；若实现对过深嵌套结构设置保护上限，则超限时必须返回 `RecursionError["Compare", ...]`，而不是爆栈、静默截断或返回部分 delta。

**Baseline Availability**：正常执行
**效果类别**：继承 `a` 与 `b` 的求值效果并集
**确定性类别**：继承 `a` 与 `b`；在两侧值固定后，delta 构造本身必须是 `deterministic`
**可观测性要求**：

- 必须记录 `comparison_kind = compare`
- 必须记录 `delta_is_empty = True[] | False[]`

**兼容性承诺**：

- `Compare[a, b]` 的二参数签名在 `v1.1.x` 内冻结
- “相等返回 `{}`，不等返回差异字典” 在 `v1.1.x` 内冻结
- 叶子差异使用 `{"expected": ..., "actual": ...}` 的最小结构在 `v1.1.x` 内冻结
- application 参数位使用 `argN` 命名、列表位置使用 `indexN` 命名的规则在 `v1.1.x` 内冻结
- `Compare` 不自动穿透 transport / UI 包装、不自动解引用节点字符串，这两条在 `v1.1.x` 内冻结

#### `Unify`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Unify[pattern, target]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `pattern` 与 `target` 都必须是合法 CogLang 表达式
- `pattern` 与 `target` 内允许出现 `term head` application、`atom`、命名变量、匿名通配符 `_`、字典字面量，以及 canonical value form，如 `List[...]`、`True[]`、`False[]`、`NotFound[]`、`TypeError[...]`
- `term head` 在 `Unify` 的两个参数中必须被解释为结构化项，而不是可执行 operator
- 若宿主启用了自由变量检查，则 `Unify` 必须是显式例外：两个参数中未被外层绑定上下文解析的命名变量，必须被视为本次合一调用的局部合一变量，而不是验证失败

**返回契约**：

- 可合一时：返回变量绑定字典 `{"X": value, ...}`
- 可合一但没有任何命名变量需要输出时：返回 `{}`
- 不可合一时：返回 `NotFound[]`
- `_` 只匹配，不绑定，不得出现在返回字典中
- `TypeError[...]`、`PermissionError[...]`、`NotFound[]` 等自动传播错误值在 `Unify` 中是可被匹配的正常目标项，不得因为它们是错误值就再次自动向外传播

返回字典的键名必须是命名变量去掉尾部 `_` 后的标识符核心。

**语义**：

`Unify` 的语义是对两棵 canonical value / term tree 计算最一般合一子 `MGU`。

同名命名变量在两侧和同一侧都代表同一个逻辑变量；若其约束不能同时满足，则结果为 `NotFound[]`。

`_` 匹配任意子树，但永不进入绑定结果。

`Unify[f[X_, b], f[a, Y_]]` 这类写法在 `v1.1.0` 中继续合法，其合法性依赖于小写 `f` 被明确归类为 `term head`，属于结构化项，不走默认 operator 解析。

`Unify` 是项级 / 值级结构匹配，不是图级搜索；需要在图中找满足条件的节点时，应使用 `Query` 而不是 `Unify`。

在默认 eager 语义下，参数中的普通可执行子表达式可先规约为其 canonical value；但进入合一步骤后，匹配只看结果树的结构，不再触发内部 `Head` 的再次解析或执行。

**Baseline Availability**：正常执行
**效果类别**：继承 `pattern` 与 `target` 规约阶段的效果；合一步骤本身为 `pure`
**确定性类别**：继承 `pattern` 与 `target` 的规约确定性；在给定两棵规范值树后，合一结果必须是 `deterministic`
**可观测性要求**：

- 必须记录 `unify_outcome = success | not_found`
- 必须记录绑定结果大小

**兼容性承诺**：

- `Unify[pattern, target]` 的二参数签名在 `v1.1.x` 内冻结
- 成功返回绑定字典、失败返回 `NotFound[]` 的二分返回形态在 `v1.1.x` 内冻结
- 返回字典的键名去尾部 `_` 的规则在 `v1.1.x` 内冻结
- `term head` 在 `Unify` 中作为结构化项参与匹配、而不参与默认 operator 解析，这一点在 `v1.1.x` 内冻结
- 自动传播错误值可被 `Unify` 结构化匹配、而不是再次自动传播，这一点在 `v1.1.x` 内冻结

#### `Match`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Match[pattern, target]
```

**Validator Constraints**：

- 与 `Unify` 完全相同
- `Match` 不引入独立的 pattern grammar；它直接继承 `Unify` 对 `term head`、命名变量、`_`、canonical value form 的解释规则

**返回契约**：

- 与 `Unify` 完全相同
- 可合一时返回绑定字典；不可合一时返回 `NotFound[]`；`_` 不进入返回结果

**语义**：

`Match` 是 `Unify` 的精确别名，语义、返回形态、错误匹配能力、以及 `operator head / term head` 的解释规则都必须与 `Unify` 保持完全一致。

保留 `Match` 的原因是它更接近用户直觉；保留 `Unify` 的原因是它与逻辑 / 形式方法术语一致。

`Match / Unify` 做的是项级匹配，不是图级 pattern search；图级命中检索仍属于 `Query`。

**Baseline Availability**：正常执行
**效果类别**：与 `Unify` 完全相同
**确定性类别**：与 `Unify` 完全相同
**可观测性要求**：

- 与 `Unify` 完全相同
- trace 中可额外记录 `alias_of = "Unify"`

**兼容性承诺**：

- `Match[pattern, target]` 在 `v1.1.x` 内必须保持为 `Unify[pattern, target]` 的精确别名
- 不允许在 `v1.1.x` 内把 `Match` 演化成更宽的图模式查询、正则匹配、或近似匹配接口
- `Match` 与 `Unify` 的返回形态、键名规则、以及错误匹配行为不得漂移

#### `Get`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Get[source, key]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `source` 与 `key` 都必须是合法 CogLang 表达式
- `Get` 的分派属于运行时语义，不把 `source` 或 `key` 的动态类型约束写成 validator 失败

**返回契约**：

- `source` 或 `key` 的求值结果为自动传播错误值时：原样传播该错误值
- `source` 求值为 `Dict` 且 `key` 求值为字符串时：返回对应键值；键不存在时返回 `NotFound[]`
- `source` 求值为 `List[...]` 且 `key` 求值为整数时：按 `0-based` 索引返回元素；索引越界时返回 `NotFound[]`
- `source` 求值为字符串节点 ID 且 `key` 求值为字符串时：返回该节点的对应属性值；节点不存在、节点不可见、或属性不存在时返回 `NotFound[]`
- `source` 求值为其他正常值时：`TypeError["Get", "source", ...]`
- 分派已确定但 `key` 类型与该分派不匹配时：`TypeError["Get", "key", ...]`

**语义**：

`Get` 是普通 eager operator，不是 `special form`。

`Get` 的运行时分派顺序冻结为：

1. `Dict`
2. `List`
3. 字符串节点 ID

`Get` 统一承载“字典取键 / 列表取索引 / 节点属性读取”这三类常用访问，不拆分为多个核心 operator。

`Get` 的规范输入对象是 canonical CogLang 值。`transport envelope`、`readable render`、宿主诊断对象等外层包装不得被 `Get` 规范性穿透读取；宿主若有包装，必须先解包再进入 CogLang 求值。

**Baseline Availability**：正常执行
**效果类别**：`graph-read`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录 `dispatch_branch = dict | list | node_attr`
- 必须记录 `result_kind = hit | not_found | type_error`

**兼容性承诺**：

- `Get[source, key]` 的二参数签名在 `v1.1.x` 内冻结
- 三路分派模型在 `v1.1.x` 内冻结
- “键不存在 / 索引越界 / 属性不存在 / 节点不存在或不可见返回 `NotFound[]`” 在 `v1.1.x` 内冻结
- 列表索引的 `0-based` 规则在 `v1.1.x` 内冻结

#### `Query`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Query[bindVar_, condition]
Query[bindVar_, condition, options]
```

其中二参数形式等价于：

```text
Query[bindVar_, condition, {"k": 1, "mode": "default"}]
```

**Validator Constraints**：

- 只允许 2 个或 3 个参数
- `bindVar_` 必须是变量
- `condition` 必须是合法 CogLang 表达式
- 若提供第三个参数，其位置必须是合法 CogLang 表达式
- 名称未解析、变量位置非法等问题属于验证失败，不进入执行阶段

**返回契约**：

- 成功命中：`List[node_id, ...]`
- 无命中：`List[]`
- 第三个参数求值后若不是字典：`TypeError["Query", "options", ...]`
- `options["k"]` 求值后若不是非负整数或字符串 `"inf"`：`TypeError["Query", "k", ...]`
- `options["mode"]` 求值后若不是字符串：`TypeError["Query", "mode", ...]`
- 条件求值失败：传播底层错误值

返回的节点列表必须采用稳定顺序；除非条目另有说明，默认使用节点 ID 的 canonical 升序。

**语义**：

`Query` 在所有可见节点中搜索满足 `condition` 的节点。其核心语义继承 `v1.0.2` 的“绑定变量 + 条件表达式”模型，但 `v1.1.0` 为查询接口增加了独立的 `k` 与 `mode` 字段。

- `k` 表示 `condition` 求值时允许使用的图扩展深度上界，默认 `1`
- `mode` 表示执行策略，默认 `"default"`
- `k` 与 `mode` 是两个独立维度，不得被实现耦合成单一隐式参数

`k` 的最小语义约束如下：

- `k = 0`：只允许节点局部属性判断，不允许图邻接扩展
- `k = 1`：允许直接邻居级访问
- `k = N`：允许最多 `N` 跳的图扩展
- `k = "inf"`：取消固定跳数上界，但仍受 profile 预算与权限约束

如果 `condition` 只引用节点局部属性，则不同 `k` 不得改变其结果集。

在 `Core` 语义中，`mode = "default"` 是唯一要求实现的默认模式。无论当前实现声明 `Baseline` 还是 `Enhanced`，当调用者省略第三参数，或显式给出 `{"mode": "default"}` 时，都必须落到该默认模式。非默认模式属于保留扩展点，可由 profile 或运行时注册表补充。

空结果 `List[]` 表示“执行成功但没有命中”，不得与执行错误混同。

`Query` 的结果是 canonical 内部表示的一部分；任何面向 `delta+` 默认路径的人类可读渲染，都是其外层接口契约，而不是 `Query` 核心语法的一部分。

**Baseline Availability**：正常执行
**效果类别**：`graph-read`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录 `condition` 的 canonical 形式
- 必须记录 `k`
- 必须记录 `mode`
- 必须记录结果计数与耗时

**兼容性承诺**：

- 二参数形式在 `v1.1.x` 内保持有效
- `options` 中 `k` / `mode` 这两个键在 `v1.1.x` 内冻结
- 非默认 `mode` 的具体集合不在本条目冻结

#### `AllNodes`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
AllNodes[]
```

**Validator Constraints**：

- 不接受任何参数

**返回契约**：

- 成功：`List[node_id, ...]`
- 空图：`List[]`

返回顺序必须稳定；除非条目另有说明，默认使用节点 ID 的 canonical 升序。

**语义**：

`AllNodes` 返回所有可见节点的 ID 列表。这里的“可见”指：

- 节点 `confidence > 0`
- 节点未被当前 profile 隐藏

`AllNodes` 是查询族的基础构件，不承担额外的筛选、排序策略选择或执行模式切换。

**Baseline Availability**：正常执行
**效果类别**：`graph-read`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录结果计数与耗时

**兼容性承诺**：

- `AllNodes[]` 的无参数签名在 `v1.1.x` 内冻结

#### `Traverse`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Traverse[node, relation]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `node` 与 `relation` 必须是合法 CogLang 表达式

**返回契约**：

- 成功命中：`List[node_id, ...]`
- 无命中、起点不存在、或起点不可见：`List[]`
- `node` 求值后不是字符串：`TypeError["Traverse", "node", ...]`
- `relation` 求值后不是字符串：`TypeError["Traverse", "relation", ...]`
- 底层参数求值若得到自动传播错误值：原样传播该错误值

返回的节点列表必须采用稳定顺序；除非条目另有说明，默认使用目标节点 ID 的 canonical 升序。

**语义**：

`Traverse` 从起点节点出发，沿所有关系类型等于 `relation` 的**可见出边**进行一步遍历，返回所有可见目标节点的 ID 列表。

“可见”至少要求：

- 边 `confidence > 0`
- 目标节点 `confidence > 0`
- 边与目标节点未被当前 profile 隐藏

`Traverse` 不负责反向遍历。若要表达“哪些节点通过某关系指向当前节点”，应使用 `Query` 或等价图搜索在外层表达。

`Traverse` 将“起点不存在”视为“没有可见邻居”，而不是权限错误或解析错误。

**Baseline Availability**：正常执行
**效果类别**：`graph-read`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录起点节点 ID 或其摘要
- 必须记录 `relation`
- 必须记录结果计数与耗时

**兼容性承诺**：

- `Traverse[node, relation]` 的二参数签名在 `v1.1.x` 内冻结
- “起点不存在返回 `List[]`” 在 `v1.1.x` 内冻结
- “仅遍历可见出边，不含反向遍历” 在 `v1.1.x` 内冻结

#### `ForEach`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
ForEach[collection, bindVar_, body]
```

**Validator Constraints**：

- 必须且仅接受 3 个参数
- `collection` 与 `body` 必须是合法 CogLang 表达式
- `bindVar_` 必须是合法变量位
- `bindVar_` 只在 `body` 的求值作用域内有效；越界引用属于验证失败
- 在嵌套绑定作用域中重用同名 `bindVar_` 属于验证失败

**返回契约**：

- `collection` 求值为 `List[v1, ..., vn]` 时：返回 `List[r1, ..., rn]`
- `collection` 求值为自动传播错误值时：返回 `List[]`
- `collection` 求值为非列表的正常值时：`TypeError["ForEach", "collection", ...]`

每个 `ri` 是将第 `i` 个元素绑定到 `bindVar_` 后求值 `body` 的结果；若某次迭代产生错误值，该错误值保留在对应结果位置，不导致整轮迭代提前终止。

**语义**：

`ForEach` 是冻结的 `special form`。它先对 `collection` 求值一次得到快照，再按快照顺序逐个求值 `body`。

核心约束如下：

- `collection` 只在迭代开始前求值一次
- `body` 在每次迭代时使用当前元素的绑定环境求值
- `bindVar_` 的作用域严格限定在 `body` 内
- body 中的副作用不得回写改变当前轮次尚未消费的快照成员

若执行环境在某轮 `body` 中使显式写图动作生效，则后续迭代里的图查询可以观察到这些已生效变更；但这种可见性不得回溯改变本轮开始前已经冻结的 `collection` 快照成员与迭代顺序。

`ForEach` 是显式传播阻断点：当 `collection` 本身为错误值时，它返回 `List[]` 而不是继续自动传播该错误值。

**Baseline Availability**：正常执行
**效果类别**：继承 `collection` 与 `body` 的效果并集
**确定性类别**：继承 `collection` 与 `body`；迭代顺序本身必须稳定
**可观测性要求**：

- 必须记录快照大小
- 必须记录迭代顺序
- 必须记录结果计数与耗时

**兼容性承诺**：

- `ForEach[collection, bindVar_, body]` 的三参数签名在 `v1.1.x` 内冻结
- 快照语义在 `v1.1.x` 内冻结
- `collection` 为错误值时返回 `List[]` 的行为在 `v1.1.x` 内冻结

#### `Do`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Do[expr1, expr2, expr3, ...]
```

**Validator Constraints**：

- 必须至少接受 1 个参数
- 每个参数都必须是合法 CogLang 表达式
- `Do` 本身不引入新的绑定变量位；绑定与作用域由内部 operator 自身处理

**返回契约**：

- 成功时返回最后一个子表达式的求值结果
- 前序子表达式的返回值被丢弃，但其副作用保留
- 某一步返回自动传播错误值时，`Do` 不自动中止；后续步骤继续执行
- 若最后一个子表达式返回错误值，则 `Do` 返回该错误值
- `Do` 不返回“所有步骤结果的聚合列表”；除非最后一个子表达式自身返回 `List[...]` 或其他聚合值

**语义**：

`Do` 是冻结的 `special form`。它按从左到右顺序逐个求值子表达式，不做“先求完所有参数再调用”的 eager 展开。

`Do` 表达的是顺序执行容器，而不是依赖链恢复器。若要根据前一步结果决定后续控制流，必须显式使用 `If`、`IfFound`、`ForEach` 等结构，而不是依赖 `Do` 的隐式短路。

若宿主接受多行顶层输入，并将其降格为 `Do[...]`，其规范语义等同于本条目的从左到右顺序执行，而不是引入额外块语义。

**Baseline Availability**：正常执行
**效果类别**：继承其子表达式效果并集
**确定性类别**：继承其子表达式序列；求值顺序本身必须确定为从左到右
**可观测性要求**：

- 必须记录步骤数
- 必须记录步骤顺序
- 必须记录最终返回值摘要

**兼容性承诺**：

- `Do[e1, e2, ...]` 的从左到右顺序求值在 `v1.1.x` 内冻结
- “`Do` 返回最后一个已求值子表达式的结果，而不是全部中间结果” 在 `v1.1.x` 内冻结
- “前序步骤出错不自动中止后续步骤” 在 `v1.1.x` 内冻结
- “多行顶层输入可降格为 `Do[...]`，但不构成额外块语义” 在 `v1.1.x` 内冻结

#### `If`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
If[condition, thenExpr, elseExpr]
```

**Validator Constraints**：

- 必须且仅接受 3 个参数
- `condition`、`thenExpr`、`elseExpr` 都必须是合法 CogLang 表达式
- `If` 本身不引入新的绑定变量位；绑定与作用域仅由其内部子表达式中的其他 operator 自身处理

**返回契约**：

- 先求值 `condition`
- 若 `condition` 的结果为真值：返回 `thenExpr` 的求值结果
- 若 `condition` 的结果为假值：返回 `elseExpr` 的求值结果
- `condition` 的结果若属于自动传播错误值集合：不继续自动向外传播，而是按假值处理并进入 `elseExpr`
- 被执行分支若返回错误值：原样返回该错误值
- 未被执行的分支不得求值，其潜在副作用与错误不得发生

**语义**：

`If` 是冻结的 `special form`。它先 eager 求值 `condition`，随后只求值一个分支。

`v1.1.x` 中冻结的假值集合为：

- `False[]`
- `NotFound[]`
- `List[]`
- `0`
- `0.0`
- `""`
- `§8` 定义的自动传播错误值

除上述假值外，其他所有合法 CogLang 值都判定为真。

`If` 区分的是“真/假”，不是“有结果/无结果”。因此 `List[]` 在 `If` 中是假，但它不是错误值；这一点必须与 `IfFound` 的语义保持分层。

`If` 是显式传播阻断点，但不是通用错误恢复器；需要按“缺失/出错”分流时，应使用 `IfFound` 而不是复用 `If`。

**Baseline Availability**：正常执行
**效果类别**：继承 `condition` 与被执行分支的效果并集
**确定性类别**：继承 `condition` 与被执行分支；分支选择本身必须确定
**可观测性要求**：

- 必须记录 `condition_result_kind`
- 必须记录 `branch_taken = then | else`

**兼容性承诺**：

- `If[condition, thenExpr, elseExpr]` 的三参数签名在 `v1.1.x` 内冻结
- “仅执行一个分支”的 `special form` 语义在 `v1.1.x` 内冻结
- 本条目定义的假值判定表在 `v1.1.x` 内冻结
- “自动传播错误值在 `If` 中按假值处理” 在 `v1.1.x` 内冻结

#### `IfFound`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
IfFound[expr, bindVar_, thenExpr, elseExpr]
```

**Validator Constraints**：

- 必须且仅接受 4 个参数
- `expr`、`thenExpr`、`elseExpr` 必须是合法 CogLang 表达式
- `bindVar_` 必须是合法变量位，且仅在 `thenExpr` 的求值作用域内有效
- `bindVar_` 在 `elseExpr` 或外层作用域中的越界引用属于验证失败
- 在嵌套绑定作用域中重用同名 `bindVar_` 属于验证失败

**返回契约**：

- 若 `expr` 求值结果既不是 `NotFound[]` 也不是自动传播错误值，则将结果绑定到 `bindVar_`，返回 `thenExpr` 的求值结果
- 若 `expr` 求值结果为 `NotFound[]` 或自动传播错误值，则返回 `elseExpr` 的求值结果
- `List[]` 不是错误值；`expr -> List[]` 时，必须进入 `thenExpr` 分支
- `thenExpr` 或 `elseExpr` 自身求值失败时，传播对应底层错误值

**语义**：

`IfFound` 是冻结的 `special form`。它先 eager 求值 `expr`，然后只求值一个分支。

`IfFound` 区分的是“结果可用”与“缺失/出错”，不是“真/假”。因此：

- `NotFound[]` 进入 `elseExpr`
- 自动传播错误值进入 `elseExpr`
- `List[]` 进入 `thenExpr`

`IfFound` 是显式恢复边界：它不让 `expr` 的缺失值或错误值继续自动向外传播，而是把控制权交给 `elseExpr`。

`IfFound` 也是当前 `v1.1.0` 中正式冻结的 bind-and-continue 惯用法：当 `expr` 产出的是后续步骤需要消费的值时，调用者可以使用 `IfFound[expr, v_, thenExpr, elseExpr]` 将该值显式绑定进 `thenExpr`，而不改变 `Do` “只负责顺序执行、不负责步间绑定”的语义。该惯用法不把 `IfFound` 重新定义为通用顺序构件，但它是当前发布版表达“先产值、后消费”链条的官方写法。

**Baseline Availability**：正常执行
**效果类别**：继承 `expr` 与被执行分支的效果并集
**确定性类别**：继承 `expr` 与被执行分支
**可观测性要求**：

- 必须记录 `branch_taken = then | else`
- 必须记录 `source_expr_result_kind = normal | not_found | error`

**兼容性承诺**：

- `IfFound[expr, bindVar_, thenExpr, elseExpr]` 的四参数签名在 `v1.1.x` 内冻结
- `List[]` 进入 `thenExpr` 分支的行为在 `v1.1.x` 内冻结
- 自动传播错误值集合由 `§8` 统一定义；本条目只消费该集合，不单独扩展

#### `Compose`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Compose[name, params, body]
```

**Validator Constraints**：

- 必须且仅接受 3 个参数
- `name` 必须是与 `operator head` 兼容的字符串字面量
- `params` 必须是字面量形态的 `List[var1_, var2_, ...]`
- `params` 内的变量名必须互不重复，且不得使用匿名 `_`
- `body` 必须是合法 CogLang 表达式
- `body` 的验证上下文必须显式加入 `params` 中声明的变量，以及当前被注册的 operator 名称自身，以支持递归定义

**返回契约**：

- 成功：返回最小 registration receipt，对外至少包含：

```text
{
  "operator_name": <string>,
  "scope": "graph-local"
}
```

- `name` 不是与 `operator head` 兼容的字符串字面量：验证失败
- `params` 不是由互不重复命名变量组成的字面量列表：验证失败
- 若 `name` 与静态内置 operator 或同一图动态作用域中的既有定义冲突：`TypeError["Compose", "name", "operator already exists or reserved", ...]`
- 当前 profile 不允许图动态定义：`PermissionError["Compose", "capability denied", ...]`

实现可以在 transport / diagnostics / 管理 API 中附带内部 definition handle，但该 handle 不是公开语义返回值的一部分。

**语义**：

`Compose` 是冻结的 `special form`。它读取字面量 `name` 与 `params`，但**不**在定义时执行 `body`；`body` 以 AST 形式存储为图动态 operator 定义。

成功后，该定义进入 `§10` 的“图内动态 operator 定义”层。`Compose` 只负责注册图内动态定义；名称解析顺序、注册表扩展、外部 adapter 与 capability 约束由 `§10` 统一规定。

`Compose` 不等同于通用插件注册接口，也不负责冻结运行时注册表或外部 adapter 的行为。

`Compose` 的规范语义是“注册图动态 operator 定义”，而不是“创建公开知识节点”。实现可以使用 executor-internal `Operation` 载体承载该定义，但这类载体不应被误当成公开知识图谱主类型。

定义出的 operator 可以递归调用自身。默认 baseline profile 必须至少支持递归深度 100；超限时返回 `RecursionError[...]`。

**Baseline Availability**：正常执行
**效果类别**：`meta`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录 `registered_name`
- 必须记录 `param_count`
- 必须记录目标作用域为 `graph-local`
- 必须记录 `registration_outcome`

**兼容性承诺**：

- `Compose[name, params, body]` 的三参数签名在 `v1.1.x` 内冻结
- `name` 为字符串字面量、`params` 为命名变量字面量列表的约束在 `v1.1.x` 内冻结
- “`body` 在定义时不执行” 在 `v1.1.x` 内冻结
- “静态内置定义不可被 `Compose` 覆盖” 在 `v1.1.x` 内冻结
- “默认 baseline profile 的递归深度下限为 100” 在 `v1.1.x` 内冻结

#### `Create`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Create[nodeType, attrs]
Create["Edge", attrs]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `nodeType` 与 `attrs` 都必须是合法 CogLang 表达式
- `Create["Edge", attrs]` 表示边创建模式；其余情况进入节点创建模式
- 基于求值结果的类型约束、字段约束与权限约束不属于 validator 阶段

**返回契约**：

- `nodeType` 求值后不是字符串：`TypeError["Create", "type", ...]`
- `attrs` 求值后不是字典：`TypeError["Create", "attrs", ...]`
- 节点模式下，`nodeType` 不是 `Entity / Concept / Rule / Meta`：`TypeError["Create", "type", "Entity|Concept|Rule|Meta|Edge", ...]`
- 节点模式下，`attrs` 显式提供保留键 `type`：`TypeError["Create", "attrs", "reserved key type", ...]`
- 节点模式下，`attrs` 显式提供的 `id` 已存在：`TypeError["Create", "id", "node id already exists", ...]`
- 节点或边模式下，若显式提供 `confidence` 但不是 `(0, 1]` 内数值：`TypeError["Create", "confidence", ...]`
- 边模式下，`attrs` 缺少 `from`、`to`、`relation_type` 任一必填字段：`TypeError["Create", "Edge", "missing required field", ...]`
- 边模式下，`from`、`to`、`relation_type` 任一字段求值后不是字符串：`TypeError["Create", "Edge", "invalid field type", ...]`
- 边模式下，`from` 或 `to` 指向的节点不存在或不可见：`NotFound[]`
- 当前 profile 禁止图写入：`PermissionError["Create", "graph_write"]`
- 节点模式成功：返回节点最终采用的 ID 字符串；若 `attrs.id` 缺失，则这是执行环境为该次创建分配的唯一 ID
- 边模式成功：返回 `List[from, relation_type, to]`

**语义**：

`Create` 在节点模式下创建公开知识图谱节点，在边模式下创建公开边对象。

节点模式的第一参数 `nodeType` 是公开主类型的唯一权威来源；`attrs` 只负责补充业务属性与可选 `id / confidence`。因此：

- 公开节点 `type` 只允许 `Entity / Concept / Rule / Meta`
- 旧式 `attrs["type"] = "Person"` 之类业务分类写法在 `v1.1.x` 中不再合法
- 业务分类应通过非保留业务字段或图结构表达，但本版不冻结统一字段名

`Create["Rule", attrs]` 创建的是公开 `Rule` 节点，而不是可执行 operator 定义；图内动态 operator 仍由 `Compose` 负责。

边模式中的调用面键名 `from / to / relation_type` 是 call-surface alias；实现内部若采用 `source_id / target_id / relation`，必须做无歧义映射，但不得把这种内部命名差异暴露成语义差异。

节点模式下，若 `attrs.id` 显式给出且未冲突，则执行环境必须使用该值作为本次创建采用的节点 ID；若 `attrs.id` 缺失，则执行环境必须在形成内部写入请求、`WriteBundleCandidate` 或等价宿主提交对象之前分配唯一 ID，并以该 ID 作为语言层返回值与后续内部引用的共同标识。ID 的具体格式与生成策略由执行环境定义；一种常见做法是预分配 UUID。

若内部实现采用 `source_id / target_id / relation`，则 `from / to / relation_type` 到内部字段的映射必须在构造内部写入请求、bundle 校验输入或等价宿主提交对象时完成；不得把这一步推迟到提交后，从而让内部引用校验面对未映射的 call-surface 字段。

`Create` 失败时不得产生部分写入。

本条冻结的是语言级写意图与成功/失败语义，不规定宿主的持久化提交路径。若上层架构采用 `WriteBundle`、owning-module 或其他代理提交流程，执行器可以先形成中间写入候选，再由宿主在提交成功后映射回本条的语言级返回契约。相同分层适用于 `Update / Delete`。

**Baseline Availability**：正常执行
**效果类别**：`graph-write`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录 `create_mode = node | edge`
- 必须记录目标主类型或 `relation_type`
- 必须记录 `creation_outcome`

**兼容性承诺**：

- `Create[nodeType, attrs]` 与 `Create["Edge", attrs]` 这两种调用外形在 `v1.1.x` 内冻结
- 节点成功返回字符串 ID、边成功返回三元组的行为在 `v1.1.x` 内冻结
- `Create["Edge", ...]` 中的 `"Edge"` 是调用模式标记，而不是公开主节点类型
- 公开节点 `type` 由第一参数决定，`attrs` 不得覆写该字段，这一点在 `v1.1.x` 内冻结

#### `Update`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Update[target, changes]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `target` 与 `changes` 都必须是合法 CogLang 表达式
- `Update` 在 `v1.1.x` 主规范中只覆盖节点更新，不包含边更新模式

**返回契约**：

- `target` 求值后不是字符串：`TypeError["Update", "target", ...]`
- `changes` 求值后不是字典：`TypeError["Update", "changes", ...]`
- 目标不存在：`NotFound[]`
- 目标已软删除：`PermissionError["Update", ...]`
- 当前 profile 禁止写入，或目标属于不可修改对象：`PermissionError["Update", ...]`
- `changes` 试图改写受保护系统字段，如 `id / type / provenance / created_at / updated_at`：`TypeError["Update", "changes", "writable field set", ...]`
- `changes["confidence"] = 0`：`TypeError["Update", "changes", "use Delete for soft-delete", ...]`
- `changes["confidence"]` 若存在但不是 `(0, 1]` 内数值：`TypeError["Update", "confidence", ...]`
- 成功：`True[]`

**语义**：

`Update` 是单节点、部分字段覆盖式更新；未出现在 `changes` 中的字段必须保持不变。

`Update` 不得承担 soft-delete 或 restore 语义；软删除只能走 `Delete`，恢复不属于当前 `Core` 条目。

运行时管理字段如 `updated_at` 由实现刷新；普通 `Update` 不得伪造覆盖系统管理字段。

`Update["some_rule", ...]` 修改的是公开 `Rule` 节点内容，不得隐式改写 `Compose` 注册的图内动态 operator 定义。

`Update` 失败时不得部分应用变更。

**Baseline Availability**：正常执行
**效果类别**：`graph-write`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录目标节点 ID
- 必须记录变更字段集合
- 必须记录 `update_outcome`

**兼容性承诺**：

- `Update[target, changes]` 的二参数签名在 `v1.1.x` 内冻结
- “目标不存在返回 `NotFound[]`” 与 “目标已软删除返回 `PermissionError[...]`” 在 `v1.1.x` 内冻结
- `Update` 不提供边更新模式这一边界在 `v1.1.x` 内冻结
- `Update` 不允许把 `confidence` 写成 `0` 以模拟删除，这一点在 `v1.1.x` 内冻结

#### `Delete`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Delete[target]
Delete["Edge", attrs]
```

**Validator Constraints**：

- 只允许 1 参数或 2 参数两种形式
- `Delete[target]` 表示节点删除模式
- `Delete["Edge", attrs]` 表示边删除模式；两参数形式下第一参数必须是字面字符串 `"Edge"`
- 所有参数位置都必须是合法 CogLang 表达式

**返回契约**：

- 节点模式下，`target` 求值后不是字符串：`TypeError["Delete", "target", ...]`
- 边模式下，`attrs` 求值后不是字典：`TypeError["Delete", "attrs", ...]`
- 边模式下，缺少 `from`、`to`、`relation_type` 或字段值不是字符串：`TypeError["Delete", "Edge", ...]`
- 节点模式成功：返回被软删除的节点 ID 字符串
- 边模式成功：返回被软删除边的三元组 `List[from, relation_type, to]`
- 节点或边不存在：`NotFound[]`
- 节点或边已软删除：`NotFound[]`
- 当前 profile 禁止删除，或目标属于受保护对象：`PermissionError["Delete", ...]`

**语义**：

`Delete` 只做 soft-delete，不做物理清除；其规范效果是把目标对象的 `confidence` 置为 `0`，并保留历史。

节点与边在被软删除后，默认不再参与 `AllNodes`、`Traverse`、`Query` 等普通可见性路径。

`Delete` 必须是幂等的；对已删除对象再次删除，返回 `NotFound[]`。

`Delete["Edge", attrs]` 删除的是公开边对象，不要求暴露内部 edge handle。其调用面键名 `from / to / relation_type` 仍是 call-surface alias，而不是内部存储 schema 的唯一命名。

`Delete["some_rule"]` 删除的是公开 `Rule` 节点；它不自动等价于注销某个 `Compose` 定义，也不自动清理所有引用该规则的证据边。

**Baseline Availability**：正常执行
**效果类别**：`graph-write`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录 `delete_mode = node | edge`
- 必须记录目标对象引用
- 必须记录 `delete_outcome`

**兼容性承诺**：

- 节点一参数形式与边二参数形式在 `v1.1.x` 内冻结
- soft-delete 而非 hard-delete 的语义在 `v1.1.x` 内冻结
- “已不存在或已删除返回 `NotFound[]`” 的幂等语义在 `v1.1.x` 内冻结

#### `Trace`

**状态**：`Core`
**所属层**：`observability`
**语法与签名**：

```text
Trace[expr]
```

**Validator Constraints**：

- `expr` 必须是合法 CogLang 表达式

**返回契约**：

- 返回值必须与直接执行 `expr` 的结果完全一致
- `expr` 返回错误值时，`Trace` 必须原样返回该错误值

trace sink 不可用不得覆盖业务返回值。

**语义**：

`Trace` 是透明包装器。它执行 `expr`，并将本次执行写入可观测性系统，但不改变 `expr` 的语义、返回值或错误传播行为。

`Trace` 只负责表达式级执行记录，不负责任务级 ROI、规则级回滚、或成本级汇总事件。

**Baseline Availability**：正常执行
**效果类别**：`diagnostic`
**确定性类别**：继承 `expr`；trace 事件编码为 `implementation-defined`
**可观测性要求**：

- 必须至少记录 `expr_id`
- 必须至少记录 `parent_id`
- 必须至少记录 `canonical_expr`
- 必须至少记录 `result_summary`
- 必须至少记录 `duration_ms`
- 必须至少记录 `effect_class`

**兼容性承诺**：

- `Trace[expr]` 的透明包装语义在 `v1.1.x` 内冻结

#### `Assert`

**状态**：`Core`
**所属层**：`observability`
**语法与签名**：

```text
Assert[condition, message]
```

**Validator Constraints**：

- `condition` 必须是合法 CogLang 表达式
- `message` 必须是合法 CogLang 表达式

**返回契约**：

- 返回 `condition` 的求值结果
- 若 `condition` 自身求值出错，原样传播该错误
- 断言失败本身不是 CogLang 运行时错误

**语义**：

`Assert` 执行非致命断言。它先求值 `condition`；若结果为假，则产出断言失败事件，但不终止当前推理链。

`message` 仅在需要记录断言失败时求值。

`Assert` 适用于在组合操作、规则触发、或调试路径中暴露异常状态，而不是替代错误传播机制。

**Baseline Availability**：正常执行
**效果类别**：`diagnostic`
**确定性类别**：继承 `condition`；断言事件编码为 `implementation-defined`
**可观测性要求**：

- 断言失败时必须记录结构化 assertion / anomaly 事件
- 事件必须能被上层纳入错误分类与回滚审计

**兼容性承诺**：

- `Assert` 的非致命语义在 `v1.1.x` 内冻结

#### Core 条目范围说明

本节只冻结本轮优先收口的 `Core` operator 条目。其余仍保留在 catalog 中的旧条目，后续将分别判断是迁入 `Core`、转入 `Reserved`，还是继续维持 `Carry-forward`；不再默认假设它们都会进入本模板。

### 7.3 Reserved Operators

#### `Explain`

**状态**：`Reserved`
**所属层**：`observability`
**语法与签名**：

```text
Explain[expr]
```

**Validator Constraints**：

- `expr` 必须是合法 CogLang 表达式

**返回契约**：

- 在支持该能力的 profile 中，返回执行计划描述对象
- 在默认基线 profile 中，允许返回 `StubError["Explain", ...]`

**语义**：

`Explain` 的语义是“非执行式计划预览”。它用于在不真正执行 `expr` 的前提下，返回对执行步骤、代价或计划结构的说明。

`Explain` 一旦实现：

- 不得产生 graph write
- 不得产生外部副作用
- 不得替代 `Trace`

**Baseline Availability**：`StubError[...]`
**效果类别**：`meta`
**确定性类别**：`implementation-defined`
**可观测性要求**：

- 调用 `Explain` 必须至少留下 `meta` 或 `stub` 事件

**兼容性承诺**：

- `Explain[expr]` 的签名在 `v1.1.x` 内冻结
- 返回对象的完整 schema 暂未冻结

#### `Inspect`

**状态**：`Reserved`
**所属层**：`meta`
**语法与签名**：

```text
Inspect[target]
```

**Validator Constraints**：

- `target` 必须是合法 CogLang 表达式

**返回契约**：

- 在支持该能力的 profile 中，返回对象结构描述数据
- 在默认基线 profile 中，允许返回 `StubError["Inspect", ...]`

**语义**：

`Inspect` 的语义是“把对象结构作为数据返回”，用于检视值、结构化项、或实现公开暴露的对象描述。它不执行计划预览，也不提供时序 trace。

`Inspect` 一旦实现：

- 不得替代 `Trace`
- 不得替代 `Explain`
- 不得因为检视成功就自动暴露宿主私有内部结构

**Baseline Availability**：`Profile Baseline: StubError["Inspect", ...]`; `Profile Enhanced: 正常执行`
**效果类别**：`meta`
**确定性类别**：`implementation-defined`
**可观测性要求**：

- 调用 `Inspect` 必须至少留下 `meta` 或 `stub` 事件

**兼容性承诺**：

- `Inspect[target]` 的一参数签名在 `v1.1.x` 内冻结
- 默认基线 profile 的 `StubError[...]` 留桩路径在 `v1.1.x` 内冻结
- 返回对象的完整 schema 暂未冻结

#### Reserved 范围说明

以下能力在本轮只作为保留位，不在本节写成 `Core`：

- 显式限定名称的具体表面语法
- 非默认 `Query.mode`
- 查询成本 / 信息增益估计
- 规则候选 envelope
- 规则发布与回滚链的完整 schema

### 7.4 Experimental Operators

本节记录**已进入讨论但尚未具备稳定语义承诺**的 operator 方向。

进入 `Experimental` 的条目至少必须满足：

- 名称、层级、效果类别、权限边界有初步描述
- 尚未满足 `Reserved` 所要求的“签名 + 默认失败行为 + trace 要求”冻结强度
- 实现者不得把它们作为稳定依赖对外承诺

当前典型实验方向包括：

- 通用 `Recover[...]`
- 更强的 `InspectSelf[...]`
- 规则自修改相关 operator
- adapter 专用高耦合 operator

这些条目可以出现在附录、设计记录、或实验 profile 中，但在进入 `Reserved` 之前，不应写入 `Core` operator 目录。

---

## 8. 错误与诊断契约

### 8.1 错误表达式

CogLang 的错误对象首先是**合法的 CogLang 表达式**，其次才是诊断事件。实现不得把用户输入、模型输出或执行期错误只表示为宿主语言异常而绕过 CogLang 层。

`v1.1.0` 冻结以下错误 Head 与最小 canonical 结构：

| 错误表达式 | 最小 canonical 结构 | 含义 |
|-----------|--------------------|------|
| `NotFound[]` | `NotFound[]` | 查询无结果、目标不存在、或不可合一 |
| `TypeError[...]` | `TypeError[op, param, expected, actual]` | 动态类型不匹配或参数值不满足运行时约束 |
| `PermissionError[...]` | `PermissionError[op, target]` | 权限不足、profile 禁止、或 capability 不满足 |
| `ParseError[...]` | `ParseError[reason, position]` | 解析失败 |
| `StubError[...]` | `StubError[op, message]` | 调用了已注册但当前未实现或未开放的能力 |
| `RecursionError[...]` | `RecursionError[op, depth, message]` | 递归或展开深度超限 |

上述最小结构是 canonical surface 的兼容性承诺；实现可以在 transport envelope 或诊断记录中附加更多字段，但不得改变这些 Head 的基本含义。

所有错误表达式都必须满足以下要求：

- 可以作为普通 CogLang 值进入后续表达式
- 可以出现在 `Trace` 与推理轨迹中
- 可以被 `Inspect`、`If`、`IfFound` 或等价机制消费
- 不得依赖宿主异常栈作为唯一可见信息源

### 8.2 诊断字段

当 parser、validator、executor 或 render 层生成诊断信息时，宿主侧诊断对象或 transport envelope **必须**支持以下字段名：

- `diagnostic_code`
- `phase`
- `source_span`
- `blame_object`
- `recoverability`
- `trace_policy`

字段约束如下：

- `diagnostic_code`：稳定的字符串代码。相同 profile 中不得把同一代码复用于不相容错误。
- `phase`：至少区分 `parse / validate / execute / render`。
- `source_span`：若诊断可定位到 canonical text，必须给出 1-based 起止位置；若无文本来源，可留空。
- `blame_object`：指向最相关的 `Head`、参数位、graph object ID、或外部 capability 名称。
- `recoverability`：描述调用方是否可通过分支、重试、降级、或能力切换继续推进；允许 profile 扩展具体取值集合。
- `trace_policy`：指示该诊断是否必须进入推理轨迹、仅在 trace 启用时记录、或仅写入宿主日志。

这些字段属于诊断契约，不要求全部编码进 canonical error expression 的参数位置。规范鼓励把“错误表达式”与“宿主诊断元数据”分层表示，而不是把所有上下文都塞进一个 Head 的位置参数里。

### 8.3 ParseError 与部分结构

Parser 遇到语法错误时，**不得**把宿主解析异常直接暴露为唯一结果；它必须返回 `ParseError[...]`，并在可恢复时附带部分结构信息。

`v1.1.0` 对 `ParseError` 的最小要求如下：

- canonical error expression 至少为 `ParseError[reason, position]`
- 若 parser 成功恢复了部分 AST，必须通过 transport envelope、诊断对象、或等价宿主接口暴露 `partial_ast` 或 `partial_ast_ref`
- 若无法恢复部分结构，可以省略 `partial_ast*` 字段，但不得伪造空 AST

保留部分结构的目的有二：

- 为训练期提供“部分正确”的结构反馈
- 为 UI / 调试器提供更精确的错误定位与修复建议

Readable Render 在展示 `ParseError` 时应同时体现：

- 失败原因
- 失败位置
- 已成功恢复的部分结构（若存在）

---

## 9. 可观测性与可读渲染

### 9.1 内置调试能力

`Trace`、`Assert`、`Explain` 是 CogLang 的内置调试与元观察能力，不是宿主系统后加的调试开关。

其边界如下：

- `Trace`：记录实际执行过的表达式轨迹，不改变返回值
- `Assert`：记录非致命异常状态，不替代错误传播
- `Explain`：返回计划预览，不执行目标表达式；在默认 profile 中可为 `StubError[...]`
- `Inspect`：保留的对象结构检视能力；若某实现提供该能力，它把对象结构作为数据返回，属于元认知/结构检视，但不替代 `Trace` 的时序记录，也不替代 `Explain` 的计划预览

因此，宿主实现可以在日志层面整合这些能力，但不得在语言语义上把它们折叠成同一个 operator。

CogLang 执行环境必须把这些调试事件接出到外部可观测性系统；`Observer` 只是推荐命名，等价 hook 亦可，但不得缺失这条桥接能力。

### 9.2 Trace Schema

`ReasoningTrace` 中的单条 CogLang 执行记录，最小字段如下：

| 字段 | 要求 |
|------|------|
| `expr_id` | 当前表达式在本次 trace 中的局部唯一标识 |
| `parent_id` | 父表达式 ID；顶层可为空 |
| `canonical_expr` | 被执行表达式的 canonical 形式 |
| `effect_class` | 对应 operator 的效果类别 |
| `result_summary` | 对返回值的稳定摘要；大对象可只记录摘要与引用 |
| `duration_ms` | 执行耗时，单位毫秒 |

以下字段为 `v1.1.0` 的推荐扩展字段：

- `source_span`
- `status`
- `trace_id`
- `parent_spans`
- `source_instance_id`

扩展字段约束：

- `source_span`：若表达式来自可定位文本，则应与 §8.2 的 `source_span` 协同
- `status`：推荐至少区分 `ok / error / stub / assertion_failed`
- `trace_id`：按需启用即可，不得默认作为所有消息或结果的常驻字段
- `parent_spans`：用于跨表达式或跨组件的溯源链拼接；若实现不支持 span 级追踪，可为空
- `source_instance_id`：为 P2 跨实例 trace 预留；P1 可为空

Trace 记录必须服务于两类消费方：

- 人类调试与审计
- 上层异常检测与统计汇总

因此，trace schema 可以裁剪大对象，但不得裁剪到无法判断“执行了什么、返回了什么、耗时多少”。

### 9.3 Readable Render 契约

每个合法的 CogLang 表达式都必须存在稳定的 Readable Render。Readable Render 是**人类展示层**，不是语义权威源，但它必须足够稳定，能支撑 trace、日志、UI 检查与人工审稿。

`v1.1.0` 对 Readable Render 的最低要求：

- 保留原始 `Head`
- 保留参数顺序
- 对嵌套表达式使用稳定缩进
- 对错误表达式展示错误 Head 与关键参数
- 对列表、字典、结构化结果对象使用稳定字段顺序
- 参考实现应提供 `to_readable()` 或等价接口

Readable Render **不得**：

- 隐式改写 canonical 结构
- 吞掉关键参数或错误字段
- 把不同 canonical 表达式渲染成不可区分的同一文本

Readable Render 的换行、缩进与 token 顺序只服务于显示和传输；它们不得被反向解释为图语义上的邻接顺序或层级顺序。

UI、日志和 trace 可以在 Readable Render 之外增加颜色、高亮、折叠、行号、或跳转锚点，但这些增强不得改变其可回溯到 canonical 表达式的能力。

---

## 10. 扩展与名称解析

### 10.1 名称解析模型

CogLang 的名称解析先冻结**抽象分发模型**，后冻结具体表面语法。

`v1.1.0` 中，名称解析涉及三类定义来源和一类执行提供方：

1. **静态内置 operator 定义**
2. **图内动态 operator 定义**
3. **运行时注册表条目**
4. **外部 adapter 提供者**

#### 1. 静态内置 operator 定义

指静态词表中注册、并由执行器原生提供语义的 operator 定义；其语法入口由对应 `operator head` 指向。

#### 2. 图内动态 operator 定义

指由 `Compose` 或等价图内机制注册到当前图谱作用域的 operator 定义；其语法入口由对应 `operator head` 指向。

#### 3. 运行时注册表条目

指不写入图谱、但由运行时注册表暴露给解析与执行层的 operator 定义条目。其目标是为：

- 插件化 operator
- 阶段性保留 operator
- 与 runtime bridge / adapter 绑定的 runtime capability

提供统一入口。

#### 4. 外部 adapter 提供者

指其最终行为由外部 adapter 提供的执行提供方。它们不单独参与名称优先级竞争；它们附着在某个已解析的 operator 定义或注册表条目之后提供实际执行能力。其执行可能需要：

- capability 检查
- 权限校验
- 外部系统联通性
- 运行时降级

### 10.2 解析顺序与冲突处理

在给定 validation context 中，每个**处于可执行位置的 `operator head`** **MUST** 解析到且仅解析到一个 operator 定义。

`term head` 与 `atom` 默认不参与本节的 operator 解析流程；它们是否被允许出现，以及是否被某个 operator 作为结构化项消费，由对应条目决定。

#### 未显式限定名称时的默认解析顺序

1. 静态内置 operator 定义
2. 图内动态 operator 定义
3. 运行时注册表条目

默认情况下，静态内置 Head **不可**被后续层覆盖。

#### 显式限定名称

`v1.1.0` 冻结“支持显式限定名称”这一抽象能力，但**不在本版本冻结具体分隔符写法**。

也就是说：

- 规范允许未来存在“限定名”
- 但不预先承诺其表面拼写一定是某个具体符号形式
- 因而这项能力当前是面向实现者和架构文档的保留位，而不是面向普通使用者的可教学语法

#### 冲突处理

- 同一解析层内的重复注册必须在注册阶段报错
- 图内动态 operator 定义与运行时注册表条目同名时，未限定名称默认解析到图内动态定义
- 显式限定名称一旦被采用，必须跳过无关层的 shadowing 规则

#### 未解析与不可用的错误语义

- 语法合法但名称未解析：**验证失败**，不得进入执行阶段
- 名称已解析但实现未安装：`StubError[head, "operator_unavailable"]`
- 名称已解析但 capability 不足：`PermissionError[head, capability]`

名称解析失败与语法解析失败属于不同问题。除非某个实现将二者封装在同一宿主诊断对象中，否则名称未解析不应被表述为 `ParseError[...]`。

此类失败不是 CogLang 运行时值；宿主 validator **MUST** 至少报告：

- `head`
- `attempted_resolution_scopes`
- `source_span`
- `diagnostic_code`

### 10.3 扩展能力边界

每个注册表 operator 或外部 adapter 绑定条目至少必须声明：

- canonical name
- status
- layer
- arity / signature
- effect class
- determinism
- required capabilities
- default unavailable behavior
- readable render hint

#### capability 声明

若某个 operator 需要外部能力，规范当前仅冻结“存在 capability 标识符”这一机制；具体 capability 名称在 `v1.1.0` 中为 `implementation-defined`，但 profile manifest **MUST** 公布精确字符串。

实现建议至少区分：

- `graph_write`
- `trace_write`
- `external_io`
- `cross_instance`
- `self_modify`

能力检查失败时，必须返回 `PermissionError[...]`，而不是静默降级。

#### 外部副作用

凡效果类别含 `external` 的 operator：

- 必须显式声明其外部副作用
- 必须声明是否允许在默认 profile 下调用
- 必须进入 trace

凡未声明外部副作用的 operator，不得在执行时隐式访问外部系统。

---

## 11. 当前特性清单与状态记录

### 11.1 Core

当前草案中已按 `Core` 收口的能力包括：

- 四层表示模型：`AST / canonical text / readable render / transport envelope`
- 图优先语言身份与显式写图边界
- 错误是值的基本模型，以及 `NotFound / TypeError / PermissionError / ParseError / StubError / RecursionError`
- 核心值类型：`String / Number / Bool / List / Dict / ErrorExpr`
- 公开知识图谱主节点类型：`Entity / Concept / Rule / Meta`
- `Abstract` 的“原型提取 + 触发”语义，以及其 provenance 约束
- `Equal`
- `Compare`
- `Unify`
- `Match`
- `Get`
- `Query` 的三参数接口、`k` / `mode` 分离、默认 `mode`
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
- Readable Render 最低契约
- 名称解析的抽象分发模型与默认优先级

### 11.2 Reserved

当前草案中作为 `Reserved` 保留、但未要求默认实现的能力包括：

- `Explain`
- `Inspect`
- 非默认 `Query.mode`
- 查询 `cost / gain` 相关元推理接口
- 规则候选 envelope
- 规则发布、验证、回滚链的完整 schema
- 显式限定名称的具体表面语法
- 更完整的跨实例 trace 字段集与跨组件溯源拼接细节

### 11.3 Experimental

当前仅作为 `Experimental` 议题记录、尚未进入稳定规范的方向包括：

- 通用 `Recover[...]` 风格恢复语法
- 更强的自检 / 自修改 operator
- 更强的类型标注与泛型系统
- 语法糖（如局部绑定、管道等）
- 高风险、强宿主耦合的 adapter 专用能力

### 11.4 `Baseline / Enhanced` Profiles

`v1.1.0` 建议至少区分以下两类 profile：

- `Baseline`：默认基线 profile，用于承载图优先主链、最小组合能力、基础诊断与可观测性、以及当前 `Core` 的最低一致性要求
- `Enhanced`：增强 profile，用于承载扩展 operator、非默认查询模式、受控外部能力、以及仍不适合进入 `Core` 主干的增强执行能力

这两类 profile 的关系约束如下：

- `Enhanced` **MUST** 保持对 `Baseline` 兼容性表面的兼容，不得破坏既有 `Core`
- 某能力若只在 `Enhanced` 中可用，其条目 **MUST** 在 `Baseline Availability` 中明确写出 profile 条件
- `Baseline` 不应承载高风险、强宿主耦合、或架构级协议能力
- `Enhanced` 可以承载更强的扩展执行能力，但这些能力默认仍不等于“可自动入图”、“程序执行域”、或“已成为公开知识层对象”

当前建议的收口方式是：

- `Baseline`：`Abstract / Equal / Compare / Unify / Match / Get / Query / AllNodes / Traverse / If / IfFound / Do / ForEach / Compose / Create / Update / Delete / Trace / Assert` 及其相关基础模型
- `Enhanced`：更强的 `Query.mode`、`Explain`、`Inspect`、`cost / gain` 元推理接口、扩展注册表 operator、受控外部能力、以及其他仍不适合进入 `Core` 的增强执行能力

Profile 是执行可用性与能力打包边界，不是新的语言层级；其作用是承接复杂度压力，而不是改写 `Core` 语义主干。

### 11.5 与 §1.4 的关系

本章不重复定义晋升 / 降级规则；权威规则见 `§1.4`。

本章只负责记录当前版本中哪些能力处于：

- `Core`
- `Reserved`
- `Experimental`

以及它们的当前状态说明、备注和引用位置。

---

## 12. 一致性测试与参考实现边界

### 12.1 Conformance Suite

`Conformance Suite` 的目标不是覆盖所有实现细节，而是验证实现是否遵守规范冻结的兼容性表面。

`v1.1.0` 至少应包含以下测试组：

- parser / validator 测试：语法、变量位置、名称解析、诊断字段
- canonical round-trip 测试：`AST <-> canonical text`
- execution 测试：核心 operator 的正常值、错误值、边界值
- graph-write boundary 测试：显式写图与禁止隐式图化
- error propagation 测试：默认传播与显式阻断点
- trace 测试：`Trace` / `Assert` 的最小字段与值透明语义
- rendering 测试：readable render 的稳定输出
- extension 测试：注册表条目、未安装实现、capability 失败

测试通过的判据应优先依赖规范声明的字段和语义，而不是依赖某个具体实现的内部数据结构。

### 12.2 Golden Examples

每个进入 `Core` 的 operator 至少应配套以下 example 类型：

- 正例：典型成功路径
- 边界例：空列表、空图、最小参数、`k=0` 等边界输入
- 错误例：类型不匹配、权限不足、名称未解析、留桩能力
- trace 例：至少一条可验证 `Trace` / `Assert` 字段的样例

以下主题必须有单独的 golden example：

- `Abstract` 不直接生成规则
- `Query` 的 `k` 与 `mode` 解耦
- 显式写图边界与禁止隐式图化
- `ParseError` 与 `partial_ast`
- Readable Render 与 canonical text 的非同一性
- `Operation` 作为 executor 内部载体时的对外标注方式

本规范的展开样例集见伴随文档 `CogLang_Conformance_Suite_v1_1_0.md`。其中以下样例 ID 应被视为本版最小权威样例索引：

- `GE-001`：`operator head` 与 `term head` 的区分
- `GE-002`：canonical text 与多行 readable render 的非同一性
- `GE-003`：`Query` 基本成功路径
- `GE-004`：`Query.k` 的最小语义
- `GE-005`：`Abstract` 只做原型提取与触发
- `GE-006`：`Trace` 的值透明与最小 trace 字段
- `GE-007`：`Assert` 的非致命语义
- `GE-008`：`ParseError` 与 `partial_ast`
- `GE-009`：名称未解析属于 validator 诊断，不等同于 `ParseError`
- `GE-010`：`Operation` 作为 executor 内部载体时的对外标注
- `GE-018`：`Explain` 在 `Baseline` 中的默认留桩
- `GE-019`：extension-backed operator 的 capability denied
- `GE-020`：名称已解析但实现未安装
- `GE-021`：`If` 对自动传播错误值的条件分支处理
- `GE-022`：`IfFound` 对 `NotFound[]`、错误值与 `List[]` 的分流
- `GE-023`：`ForEach` 的稳定映射与结果保留
- `GE-024`：`Do` 的顺序执行与非自动中止
- `GE-025`：`Inspect` 在 `Baseline` 中的默认留桩
- `GE-026`：`IfFound` 的 bind-and-continue 惯用法
- `GE-027`：`AllNodes` 的可见性与稳定顺序
- `GE-028`：`Update` 的成功路径与 `confidence=0` 拒绝
- `GE-029`：`Delete` 的 soft-delete 与幂等性
- `GE-030`：`ForEach` 对 body 错误的结果保留
- `GE-031`：`Get` 的 `Dict / List / node_attr` 三路分派
- `GE-032`：`Create` 缺省 ID 的唯一分配与返回一致性
- `GE-033`：`Create["Edge", ...]` 的 alias 归一化早于内部引用校验

### 12.3 参考实现边界

参考实现应覆盖以下最小能力：

- parser
- validator
- canonical serializer
- readable renderer
- 核心 error model
- `Core` operator 的最小可执行语义

以下内容不要求由参考实现完整覆盖：

- runtime bridge 内部算法
- SoftGraphMemory 内部物理实现
- Observer 后端的具体日志系统
- 外部 adapter 的真实网络或插件执行
- `Reserved / Experimental` 能力的完整行为

规范约束关注的是：输入输出语义、诊断字段、trace 字段、名称解析规则、以及兼容性表面。实现优化可以自由变化，但不得破坏这些外部可观察契约。

---

## 13. 非目标与延后事项

以下内容不属于 `v1.1.0` 的目标：

- 把 CogLang 优化成面向人类手写的通用编程语言
- 为了语法简洁而引入大量等价写法
- 把所有 runtime metadata 都提升为核心语法
- 在语言规范中冻结 runtime bridge、宿主传输层或外部 adapter 的完整协议
- 把原始结构层、规范表示层、输出解释层重新压成一层
- 把 `Reserved` 条目写成看似可稳定依赖的 `Core` 能力

延后事项包括但不限于：

- 更强的元认知 operator
- 更完整的规则候选 / 发布 / 回滚对象模型
- 应用侧生命周期对象模型与持久化提交协议
- 更强类型系统
- 更丰富的语法糖
- `P3/P4` 方向的程序性语法与程序执行域能力
- 跨实例 trace / provenance 的完整对象模型
- capability manifest 与 adapter catalog 的细化

---

## 附录 A：Operator 规格模板

```text
Operator: <name>
Status: Core | Reserved | Experimental
Layer: language | executor | runtime_bridge | observability | adapter
Syntax & Signature: <sig>
Validator Constraints: <validator rules>
Return Contract: <normal return and failure contract>
Effect Class: pure | graph-read | graph-write | meta | diagnostic | external
Determinism: deterministic | graph-state-dependent | model-dependent | implementation-defined
Semantics: <normative behavior>
Baseline Availability: <正常执行 | StubError | PermissionError | profile-specific availability>
Observability: <trace/log requirements>
Compatibility: <name frozen? semantics frozen?>
Notes: <informative notes>
```

## 附录 B：语言规范后续补写优先级

建议优先补写顺序：

1. 查询 operator 的 `k / mode` 设计
2. 扩展与名称解析模型
3. `Explain` / trace schema
4. Reserved / Experimental 清单
5. grammar 与 conformance suite
6. rendering / UI contract 的同步细化
