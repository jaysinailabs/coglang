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

## 7. Operator Specification

### 7.1 Entry Template

Each operator entry MUST contain the following **7 core items**:

1. **Status**: `Core / Reserved / Experimental`
2. **Layer**: `language / executor / runtime_bridge / observability / adapter`
3. **Syntax and Signature**
4. **Validator Constraints**
5. **Return Contract**
6. **Semantics**
7. **Baseline Availability**

Each operator entry MUST also contain the following **4 supplemental items**:

- **Effect Category**
- **Determinism Category**
- **Observability Requirements**
- **Compatibility Commitment**

#### Entry Writing Rules

- A `Core` operator's "Semantics" item MUST be a complete normative description, not only a statement of design intent.
- A `Reserved` operator MUST at least freeze its signature, validation constraints, default failure behavior, and trace requirements.
- An `Experimental` operator MAY retain implementation freedom, but it MUST still declare its effect category and permission boundary.
- If an operator depends on an external implementation, its entry MUST explicitly state whether "name frozen" and "behavior not frozen" are both true.
- `Validator Constraints` describe only syntax, arity, variable positions, name resolution, and statically decidable literal constraints. Dynamic type mismatches after expression evaluation MUST be documented under "Return Contract" or "Semantics"; they MUST NOT be mixed into validator failure.
- For transparent wrappers or conditional wrappers, the determinism category MAY be declared as "inherits from the wrapped expression". If diagnostic events or metadata encoding still retain implementation freedom, the entry MUST state that explicitly under "Semantics" or "Observability Requirements".

#### Baseline Availability Determination

This item describes **runtime baseline availability after successful validation**. It does not cover parser-stage or validator-stage rejection.

`Baseline Availability` may use only the following three forms:

- **Normal execution**
- **`StubError[...]`**
- **`PermissionError[...]`**

It MUST NOT be written as "implementation-defined" or "may be unavailable".

If availability depends on a profile, the entry MUST use the form `Profile <name>: ...`, and the profile name MUST be defined in a companion document or manifest.

#### Admission Principles for Future Program-Layer Capabilities

When a future version considers introducing stronger program-layer capabilities, a capability **SHOULD** satisfy at least the following conditions before entering `Core`:

- It directly supports graph query, graph update, rule triggering, pre-validation representation, or observable execution.
- Its core semantics can be stably frozen without depending on host-specific implementation tricks.
- It does not promote temporary intermediate state, local containers, or one-off algorithmic steps into graph objects by default.
- It is not introduced primarily to align CogLang with a traditional general-purpose language surface or to improve human hand-writing comfort.
- It cannot be represented more naturally as a `Reserved` operator, an `Experimental` operator, an `extension-backed operator`, or a profile-specific capability.

If a capability mainly provides:

- complex reduction, aggregation, sorting, or filtering over lists or dictionaries,
- strongly host-coupled local algorithms, external system calls, or toolchain bridges,
- local processing steps that serve only one execution and do not form stable knowledge objects,

then it **SHOULD** first exist as a profile extension, registry entry, or `Reserved / Experimental` entry rather than directly expanding the `Core` trunk.

### 7.2 Core Operators

#### `Abstract`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Abstract[instances]
```

**Validator Constraints**:

- MUST accept exactly one argument.
- `instances` MUST be a valid CogLang expression.

**Return Contract**:

On success, returns a structured result object:

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

On failure:

- If `instances` evaluates to a non-list value: `TypeError["Abstract", "instances", ...]`
- If the name and arguments pass validation but the current profile does not support the operator: `StubError["Abstract", ...]`

An empty-list input MUST return a non-triggering summary object. `triggered = False[]` is a valid normal result, not an error.

**Semantics**:

`Abstract` performs prototype extraction and trigger determination over a set of instances. It:

- receives a batch of instances to abstract,
- first forms an equivalence class or candidate cluster, then forms the corresponding prototype / cluster representation for that batch,
- determines whether the pattern has reached the threshold of "mature enough to trigger downstream induction",
- returns a structured summary of this abstraction result.

The main specification freezes only the field type and semantic boundary of `triggered`. It does not freeze concrete thresholds, concrete clustering algorithms, or concrete trigger heuristics. Implementation starting recommendations for those details belong in a companion / implementation note, not in the normative body of this entry.

`Abstract` MUST preserve two kinds of provenance:

- a traceable reference to the equivalence-class member list,
- a traceable explanation of the representative selection or prototype formation basis.

`Abstract` MUST NOT delete, overwrite, or implicitly merge original instances merely because it forms a representative or prototype. It can only provide a trigger summary for later normalization, induction, or explanation-layer operations.

`Abstract` does **not** directly generate rule candidates, does **not** execute Logic Engine validation, and does **not** directly write to the draft graph or main graph. Rule generation and validation belong to the downstream pipeline:

`Abstract -> Encoder -> Logic Engine -> draft/promote`

**Baseline Availability**: Normal execution
**Effect Category**: `meta`
**Determinism Category**: `model-dependent`
**Observability Requirements**:

- MUST record `cluster_id`.
- MUST record `instance_count`.
- MUST record `prototype_ref`.
- MUST record `equivalence_class_ref`.
- MUST record `selection_basis`.
- MUST record `triggered`.

**Compatibility Commitment**:

- The `Abstract[instances]` signature is frozen within `v1.1.x`.
- The six minimal return fields are frozen within `v1.1.x`.
- The internal encoding of prototypes and the concrete training backend may still evolve.

#### `Equal`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Equal[a, b]
```

**Validator Constraints**:

- MUST accept exactly 2 arguments.
- `a` and `b` MUST both be valid CogLang expressions.
- `Equal` does not introduce a new binding-variable position and does not provide name-resolution extension semantics.
- Dynamic type differences are not validator failures; they are part of runtime comparison semantics.

**Return Contract**:

- If evaluation of `a` or `b` yields an auto-propagating error value: propagate that error value unchanged.
- If the two values are structurally equal: return `True[]`.
- If the two values are not structurally equal: return `False[]`.
- `Equal` MUST NOT return `TypeError[...]` merely because value types differ; comparison between heterogeneous normal values returns `False[]`.

**Semantics**:

`Equal` is a normal eager operator, not a `special form`.

`Equal` compares structural equality of semantic values, not textual equality of source text, readable render, or transport envelopes. "Structural equality" uses the global definition from `§3.2`: source spans, render hints, and transport-only metadata are ignored.

The concrete rules are:

- Strings are compared by literal value.
- Numbers are compared by numeric value.
- `True[] / False[]` are compared by boolean value.
- `List` values MUST have the same length, and elements are compared recursively by position; list order is semantically significant.
- `Dict` values MUST have the same key set, and each corresponding value is compared recursively; key order is not semantically significant.
- Structured terms / applications MUST have the same `Head`, the same arity, and recursively equal arguments by position.

`Equal` does not consume auto-propagating error values. If a caller needs structured matching over error expressions, it should use `Unify` or an equivalent explicit inspection mechanism.

If a string happens to be a node ID, `Equal` still treats it only as a string value. It MUST NOT implicitly dereference graph nodes.

`Equal` is for boolean judgment and control flow. It does not provide difference explanation; difference explanation belongs to `Compare`.

**Baseline Availability**: Normal execution
**Effect Category**: Inherits the union of the evaluation effects of `a` and `b`
**Determinism Category**: Inherits from `a` and `b`; once both values are fixed, equality judgment itself MUST be `deterministic`
**Observability Requirements**:

- MUST record `comparison_kind = equal`.
- MUST record `result = True[] | False[]`.

**Compatibility Commitment**:

- The two-argument signature `Equal[a, b]` is frozen within `v1.1.x`.
- "Structurally equal returns `True[]`; otherwise returns `False[]`" is frozen within `v1.1.x`.
- `List` order sensitivity and `Dict` key-order insensitivity are frozen within `v1.1.x`.
- `Equal` not automatically piercing transport / UI wrappers and not automatically dereferencing node strings are frozen within `v1.1.x`.

#### `Compare`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Compare[a, b]
```

**Validator Constraints**:

- MUST accept exactly 2 arguments.
- `a` and `b` MUST both be valid CogLang expressions.
- `Compare` does not introduce a binding-variable position and does not provide name-resolution extension semantics.
- Dynamic type differences are not validator failures; they are part of runtime delta-construction semantics.

**Return Contract**:

- If evaluation of `a` or `b` yields an auto-propagating error value: propagate that error value unchanged.
- If the two values are structurally equal: return the empty dictionary `{}`.
- If the two values are not equal: return a `Dict` describing the structural difference.
- `Compare` MUST NOT return `TypeError[...]` merely because value types differ; differences between heterogeneous normal values are still expressed as a delta dictionary.

**Semantics**:

`Compare` is a normal eager operator, not a `special form`.

`Compare` compares semantic value structure, not source text, readable render, or transport envelopes. Its output is a diagnostic delta, not a boolean value; control flow should use `Equal`, not `Compare`.

The minimal delta rules frozen in `v1.1.x` are:

- Fully equal values: return `{}`.
- Unequal atomic values, or different structural types/shapes: return `{"expected": a, "actual": b}`.
- If both sides are applications with the same `Head` and arity: generate child deltas only for unequal argument positions, using keys `arg0`, `arg1`, `arg2`, ...
- If both sides are equal-length `List` values: generate child deltas only for unequal positions, using keys `index0`, `index1`, `index2`, ...
- If both sides are `Dict` values: generate child deltas only for unequal or missing keys; the missing side may use `NotFound[]` as `expected` or `actual`.

`Compare` does not consume auto-propagating error values. If a caller needs structured matching over error expressions, it should use `Unify` or an equivalent explicit inspection mechanism.

Therefore, the stable result of `Compare[f[a, b], f[a, c]]` should be:

```text
{"arg1": {"expected": "b", "actual": "c"}}
```

If a string happens to be a node ID, `Compare` still treats it only as a string value. It MUST NOT implicitly dereference graph nodes and MUST NOT expand into a graph-level diff.

Delta key order is not semantically significant, but canonical serialization MUST be stable.

The recursive expansion depth of `Compare` inherits the execution environment's general recursion limit. If an implementation sets a protection limit for overly deep nested structures, exceeding that limit MUST return `RecursionError["Compare", ...]`, not stack overflow, silent truncation, or a partial delta.

**Baseline Availability**: Normal execution
**Effect Category**: Inherits the union of the evaluation effects of `a` and `b`
**Determinism Category**: Inherits from `a` and `b`; once both values are fixed, delta construction itself MUST be `deterministic`
**Observability Requirements**:

- MUST record `comparison_kind = compare`.
- MUST record `delta_is_empty = True[] | False[]`.

**Compatibility Commitment**:

- The two-argument signature `Compare[a, b]` is frozen within `v1.1.x`.
- "Equal returns `{}`; unequal returns a delta dictionary" is frozen within `v1.1.x`.
- The minimal leaf-delta structure `{"expected": ..., "actual": ...}` is frozen within `v1.1.x`.
- The rules that application argument positions use `argN` and list positions use `indexN` are frozen within `v1.1.x`.
- `Compare` not automatically piercing transport / UI wrappers and not automatically dereferencing node strings are frozen within `v1.1.x`.

#### `Unify`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Unify[pattern, target]
```

**Validator Constraints**:

- MUST accept exactly 2 arguments.
- `pattern` and `target` MUST both be valid CogLang expressions.
- `pattern` and `target` may contain `term head` applications, `atom` values, named variables, the anonymous wildcard `_`, dictionary literals, and canonical value forms such as `List[...]`, `True[]`, `False[]`, `NotFound[]`, and `TypeError[...]`.
- A `term head` in either argument of `Unify` MUST be interpreted as a structured term, not as an executable operator.
- If a host enables free-variable checking, `Unify` MUST be an explicit exception: named variables in the two arguments that are not resolved by an outer binding context MUST be treated as local unification variables for this unification call, not as validation failures.

**Return Contract**:

- If unification succeeds: return a variable-binding dictionary `{"X": value, ...}`.
- If unification succeeds but there are no named variables to output: return `{}`.
- If unification fails: return `NotFound[]`.
- `_` matches only; it does not bind and MUST NOT appear in the returned dictionary.
- Auto-propagating error values such as `TypeError[...]`, `PermissionError[...]`, and `NotFound[]` are normal target terms that can be matched inside `Unify`; they MUST NOT be auto-propagated outward again merely because they are error values.

Returned dictionary keys MUST be the identifier core of named variables after removing the trailing `_`.

**Semantics**:

`Unify` computes the most general unifier, `MGU`, for two canonical value / term trees.

Named variables with the same name represent the same logical variable both across the two sides and within the same side. If their constraints cannot be satisfied simultaneously, the result is `NotFound[]`.

`_` matches any subtree but never enters the binding result.

Forms such as `Unify[f[X_, b], f[a, Y_]]` remain valid in `v1.1.0`. Their validity depends on lowercase `f` being explicitly classified as a `term head`: it is a structured term and does not go through default operator resolution.

`Unify` is term-level / value-level structural matching, not graph-level search. To find nodes in a graph that satisfy a condition, use `Query` rather than `Unify`.

Under default eager semantics, ordinary executable subexpressions in the arguments may first reduce to their canonical values. Once the unification step begins, matching only observes the structure of the resulting trees and does not re-trigger parsing or execution of inner `Head` values.

**Baseline Availability**: Normal execution
**Effect Category**: Inherits the effects of the reduction phase for `pattern` and `target`; the unification step itself is `pure`
**Determinism Category**: Inherits the reduction determinism of `pattern` and `target`; given two canonical value trees, the unification result MUST be `deterministic`
**Observability Requirements**:

- MUST record `unify_outcome = success | not_found`.
- MUST record the binding-result size.

**Compatibility Commitment**:

- The two-argument signature `Unify[pattern, target]` is frozen within `v1.1.x`.
- The binary return shape of "success returns a binding dictionary; failure returns `NotFound[]`" is frozen within `v1.1.x`.
- The rule that returned dictionary keys remove the trailing `_` from variable names is frozen within `v1.1.x`.
- The fact that `term head` participates in matching as a structured term inside `Unify`, rather than participating in default operator resolution, is frozen within `v1.1.x`.
- The fact that auto-propagating error values can be structurally matched by `Unify`, rather than being auto-propagated again, is frozen within `v1.1.x`.

#### `Match`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Match[pattern, target]
```

**Validator Constraints**:

- Exactly the same as `Unify`.
- `Match` does not introduce an independent pattern grammar. It directly inherits `Unify`'s interpretation rules for `term head`, named variables, `_`, and canonical value forms.

**Return Contract**:

- Exactly the same as `Unify`.
- If unification succeeds, returns a binding dictionary; if unification fails, returns `NotFound[]`; `_` does not enter the returned result.

**Semantics**:

`Match` is an exact alias of `Unify`. Its semantics, return shape, error-matching capability, and interpretation rules for `operator head / term head` MUST remain fully consistent with `Unify`.

`Match` is retained because it is closer to user intuition. `Unify` is retained because it aligns with logic / formal-methods terminology.

`Match / Unify` performs term-level matching, not graph-level pattern search. Graph-level hit retrieval remains the responsibility of `Query`.

**Baseline Availability**: Normal execution
**Effect Category**: Exactly the same as `Unify`
**Determinism Category**: Exactly the same as `Unify`
**Observability Requirements**:

- Exactly the same as `Unify`.
- A trace may additionally record `alias_of = "Unify"`.

**Compatibility Commitment**:

- `Match[pattern, target]` MUST remain an exact alias of `Unify[pattern, target]` within `v1.1.x`.
- `Match` MUST NOT evolve within `v1.1.x` into a broader graph-pattern query, regular-expression matching, or approximate-matching interface.
- The return shape, key-name rule, and error-matching behavior of `Match` and `Unify` MUST NOT drift apart.

#### `Get`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Get[source, key]
```

**Validator Constraints**:

- MUST accept exactly 2 arguments.
- `source` and `key` MUST both be valid CogLang expressions.
- `Get` dispatch belongs to runtime semantics; dynamic type constraints on `source` or `key` are not validator failures.

**Return Contract**:

- If evaluation of `source` or `key` yields an auto-propagating error value: propagate that error value unchanged.
- If `source` evaluates to a `Dict` and `key` evaluates to a string: return the corresponding keyed value; if the key does not exist, return `NotFound[]`.
- If `source` evaluates to `List[...]` and `key` evaluates to an integer: return the element at the `0-based` index; if the index is out of range, return `NotFound[]`.
- If `source` evaluates to a string node ID and `key` evaluates to a string: return that node's corresponding property value; if the node does not exist, the node is not visible, or the property does not exist, return `NotFound[]`.
- If `source` evaluates to any other normal value: return `TypeError["Get", "source", ...]`.
- If dispatch has been determined but the `key` type does not match that dispatch: return `TypeError["Get", "key", ...]`.

**Semantics**:

`Get` is a normal eager operator, not a `special form`.

The runtime dispatch order of `Get` is frozen as:

1. `Dict`
2. `List`
3. string node ID

`Get` unifies three common access operations, "dictionary key lookup / list indexing / node property read", rather than splitting them into multiple core operators.

The normative input object of `Get` is a canonical CogLang value. Outer wrappers such as `transport envelope`, `readable render`, and host diagnostic objects MUST NOT be normatively pierced and read by `Get`; if a host has wrappers, it MUST unwrap them before entering CogLang evaluation.

**Baseline Availability**: Normal execution
**Effect Category**: `graph-read`
**Determinism Category**: `graph-state-dependent`
**Observability Requirements**:

- MUST record `dispatch_branch = dict | list | node_attr`.
- MUST record `result_kind = hit | not_found | type_error`.

**Compatibility Commitment**:

- The two-argument signature `Get[source, key]` is frozen within `v1.1.x`.
- The three-branch dispatch model is frozen within `v1.1.x`.
- "Missing key / out-of-range index / missing property / missing or invisible node returns `NotFound[]`" is frozen within `v1.1.x`.
- The `0-based` list-index rule is frozen within `v1.1.x`.

#### `Query`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Query[bindVar_, condition]
Query[bindVar_, condition, options]
```

The two-argument form is equivalent to:

```text
Query[bindVar_, condition, {"k": 1, "mode": "default"}]
```

**Validator Constraints**:

- Only 2 or 3 arguments are allowed.
- `bindVar_` MUST be a variable.
- `condition` MUST be a valid CogLang expression.
- If the third argument is provided, that position MUST be a valid CogLang expression.
- Unresolved names, illegal variable positions, and similar issues are validation failures and do not enter the execution stage.

**Return Contract**:

- Successful hits: `List[node_id, ...]`
- No hits: `List[]`
- If the third argument evaluates to a non-dictionary value: `TypeError["Query", "options", ...]`
- If `options["k"]` evaluates to neither a non-negative integer nor the string `"inf"`: `TypeError["Query", "k", ...]`
- If `options["mode"]` evaluates to a non-string value: `TypeError["Query", "mode", ...]`
- If condition evaluation fails: propagate the underlying error value.

The returned node list MUST use a stable order. Unless an entry says otherwise, the default is canonical ascending order of node IDs.

**Semantics**:

`Query` searches all visible nodes for nodes that satisfy `condition`. Its core semantics inherit the `v1.0.2` "bound variable + condition expression" model, while `v1.1.0` adds independent `k` and `mode` fields to the query interface.

- `k` is the upper bound on graph expansion depth allowed during `condition` evaluation; the default is `1`.
- `mode` is the execution strategy; the default is `"default"`.
- `k` and `mode` are two independent dimensions and MUST NOT be coupled by an implementation into a single implicit parameter.

The minimal semantic constraints for `k` are:

- `k = 0`: only node-local property checks are allowed; graph adjacency expansion is not allowed.
- `k = 1`: direct-neighbor access is allowed.
- `k = N`: graph expansion up to `N` hops is allowed.
- `k = "inf"`: removes the fixed hop-count bound, but profile budgets and permissions still apply.

If `condition` references only node-local properties, different `k` values MUST NOT change the result set.

In `Core` semantics, `mode = "default"` is the only default mode required to be implemented. Regardless of whether the current implementation declares `Baseline` or `Enhanced`, omitting the third argument or explicitly providing `{"mode": "default"}` MUST land on that default mode. Non-default modes are reserved extension points that may be supplied by profiles or runtime registries.

An empty result `List[]` means "execution succeeded but produced no hits" and MUST NOT be conflated with an execution error.

The result of `Query` is part of the canonical internal representation. Any human-readable render for a `delta+` default path is an outer interface contract, not part of `Query` core syntax.

**Baseline Availability**: Normal execution
**Effect Category**: `graph-read`
**Determinism Category**: `graph-state-dependent`
**Observability Requirements**:

- MUST record the canonical form of `condition`.
- MUST record `k`.
- MUST record `mode`.
- MUST record result count and elapsed time.

**Compatibility Commitment**:

- The two-argument form remains valid within `v1.1.x`.
- The `k` / `mode` keys in `options` are frozen within `v1.1.x`.
- The concrete set of non-default `mode` values is not frozen by this entry.

#### `AllNodes`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
AllNodes[]
```

**Validator Constraints**:

- Accepts no arguments.

**Return Contract**:

- Success: `List[node_id, ...]`
- Empty graph: `List[]`

The return order MUST be stable. Unless an entry says otherwise, the default is canonical ascending order of node IDs.

**Semantics**:

`AllNodes` returns the ID list of all visible nodes. "Visible" here means:

- the node has `confidence > 0`,
- the node is not hidden by the current profile.

`AllNodes` is a basic building block of the query family. It does not provide additional filtering, sorting-strategy selection, or execution-mode switching.

**Baseline Availability**: Normal execution
**Effect Category**: `graph-read`
**Determinism Category**: `graph-state-dependent`
**Observability Requirements**:

- MUST record result count and elapsed time.

**Compatibility Commitment**:

- The zero-argument signature `AllNodes[]` is frozen within `v1.1.x`.

#### `Traverse`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Traverse[node, relation]
```

**Validator Constraints**:

- MUST accept exactly 2 arguments.
- `node` and `relation` MUST both be valid CogLang expressions.

**Return Contract**:

- Successful hits: `List[node_id, ...]`
- No hits, missing start node, or invisible start node: `List[]`
- If `node` evaluates to a non-string value: `TypeError["Traverse", "node", ...]`
- If `relation` evaluates to a non-string value: `TypeError["Traverse", "relation", ...]`
- If evaluation of an underlying argument yields an auto-propagating error value: propagate that error value unchanged.

The returned node list MUST use a stable order. Unless an entry says otherwise, the default is canonical ascending order of target node IDs.

**Semantics**:

`Traverse` starts from the start node, traverses one step along all **visible outgoing edges** whose relation type equals `relation`, and returns the ID list of all visible target nodes.

"Visible" requires at least:

- the edge has `confidence > 0`,
- the target node has `confidence > 0`,
- the edge and target node are not hidden by the current profile.

`Traverse` does not provide reverse traversal. To express "which nodes point to the current node through some relation", use `Query` or equivalent graph search at the outer layer.

`Traverse` treats "missing start node" as "no visible neighbors", not as a permission error or resolution error.

**Baseline Availability**: Normal execution
**Effect Category**: `graph-read`
**Determinism Category**: `graph-state-dependent`
**Observability Requirements**:

- MUST record the start node ID or its summary.
- MUST record `relation`.
- MUST record result count and elapsed time.

**Compatibility Commitment**:

- The two-argument signature `Traverse[node, relation]` is frozen within `v1.1.x`.
- "Missing start node returns `List[]`" is frozen within `v1.1.x`.
- "Only visible outgoing edges are traversed; reverse traversal is not included" is frozen within `v1.1.x`.

#### `ForEach`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
ForEach[collection, bindVar_, body]
```

**Validator Constraints**:

- MUST accept exactly 3 arguments.
- `collection` and `body` MUST be valid CogLang expressions.
- `bindVar_` MUST be a valid variable slot.
- `bindVar_` is valid only within the evaluation scope of `body`; any out-of-scope reference is a validation failure.
- Reusing the same `bindVar_` name in nested binding scopes is a validation failure.

**Return Contract**:

- If `collection` evaluates to `List[v1, ..., vn]`: returns `List[r1, ..., rn]`.
- If `collection` evaluates to an auto-propagating error value: returns `List[]`.
- If `collection` evaluates to a normal non-list value: `TypeError["ForEach", "collection", ...]`.

Each `ri` is the result of evaluating `body` after binding the `i`-th element to `bindVar_`. If an iteration produces an error value, that error value is retained at the corresponding result position and does not terminate the whole iteration early.

**Semantics**:

`ForEach` is a frozen `special form`. It evaluates `collection` once to obtain a snapshot, then evaluates `body` one element at a time in snapshot order.

The core constraints are:

- `collection` is evaluated only once before iteration starts.
- `body` is evaluated during each iteration with the binding environment for the current element.
- The scope of `bindVar_` is strictly limited to `body`.
- Side effects in `body` MUST NOT write back to change snapshot members that have not yet been consumed in the current iteration.

If the execution environment makes an explicit graph-write action take effect during some iteration of `body`, graph queries in later iterations may observe those effective changes. However, this visibility MUST NOT retroactively change the `collection` snapshot members or iteration order that were already frozen before this `ForEach` run began.

`ForEach` is an explicit propagation blocking point: when `collection` itself is an error value, it returns `List[]` instead of continuing to auto-propagate that error value.

**Baseline Availability**: Normal execution
**Effect Category**: inherits the union of the effects of `collection` and `body`
**Determinism Category**: inherits `collection` and `body`; the iteration order itself MUST be stable
**Observability Requirements**:

- MUST record the snapshot size.
- MUST record the iteration order.
- MUST record result count and elapsed time.

**Compatibility Commitment**:

- The three-argument signature `ForEach[collection, bindVar_, body]` is frozen within `v1.1.x`.
- Snapshot semantics are frozen within `v1.1.x`.
- The behavior of returning `List[]` when `collection` is an error value is frozen within `v1.1.x`.

#### `Do`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Do[expr1, expr2, expr3, ...]
```

**Validator Constraints**:

- MUST accept at least 1 argument.
- Every argument MUST be a valid CogLang expression.
- `Do` itself does not introduce new binding variable slots; binding and scope are handled by the internal operators themselves.

**Return Contract**:

- On success, returns the evaluation result of the last subexpression.
- Return values from preceding subexpressions are discarded, but their side effects are retained.
- When some step returns an auto-propagating error value, `Do` does not automatically abort; subsequent steps continue to execute.
- If the last subexpression returns an error value, `Do` returns that error value.
- `Do` does not return an "aggregate list of all step results" unless the last subexpression itself returns `List[...]` or another aggregate value.

**Semantics**:

`Do` is a frozen `special form`. It evaluates subexpressions one by one from left to right; it does not perform an eager expansion that first evaluates all arguments and then calls the operator.

`Do` expresses a sequential execution container, not a dependency-chain recovery mechanism. To decide later control flow based on the result of an earlier step, callers MUST explicitly use structures such as `If`, `IfFound`, or `ForEach` instead of relying on implicit short-circuiting by `Do`.

If a host accepts multi-line top-level input and lowers it to `Do[...]`, its normative semantics are the same as this entry's left-to-right sequential execution; this does not introduce additional block semantics.

**Baseline Availability**: Normal execution
**Effect Category**: inherits the union of its subexpression effects
**Determinism Category**: inherits its subexpression sequence; the evaluation order itself MUST be fixed as left-to-right
**Observability Requirements**:

- MUST record the step count.
- MUST record the step order.
- MUST record the final return value summary.

**Compatibility Commitment**:

- Left-to-right sequential evaluation of `Do[e1, e2, ...]` is frozen within `v1.1.x`.
- "`Do` returns the result of the last evaluated subexpression, not all intermediate results" is frozen within `v1.1.x`.
- "An error in a preceding step does not automatically abort subsequent steps" is frozen within `v1.1.x`.
- "Multi-line top-level input may be lowered to `Do[...]`, but does not constitute additional block semantics" is frozen within `v1.1.x`.

#### `If`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
If[condition, thenExpr, elseExpr]
```

**Validator Constraints**:

- MUST accept exactly 3 arguments.
- `condition`, `thenExpr`, and `elseExpr` MUST all be valid CogLang expressions.
- `If` itself does not introduce new binding variable slots; binding and scope are handled only by other operators inside its subexpressions.

**Return Contract**:

- Evaluates `condition` first.
- If the result of `condition` is truthy: returns the evaluation result of `thenExpr`.
- If the result of `condition` is falsy: returns the evaluation result of `elseExpr`.
- If the result of `condition` belongs to the set of auto-propagating error values: it is not auto-propagated outward further, but is treated as falsy and enters `elseExpr`.
- If the executed branch returns an error value: returns that error value as-is.
- The non-executed branch MUST NOT be evaluated, and its potential side effects and errors MUST NOT occur.

**Semantics**:

`If` is a frozen `special form`. It first eagerly evaluates `condition`, then evaluates only one branch.

The falsy set frozen in `v1.1.x` is:

- `False[]`
- `NotFound[]`
- `List[]`
- `0`
- `0.0`
- `""`
- Auto-propagating error values defined by `§8`

Except for the falsy values above, all other valid CogLang values are treated as truthy.

`If` distinguishes "truthy/falsy", not "has result/no result". Therefore `List[]` is falsy in `If`, but it is not an error value; this MUST remain layered separately from the semantics of `IfFound`.

`If` is an explicit propagation blocking point, but not a general error recovery mechanism. When control needs to branch on "missing/error", `IfFound` SHOULD be used instead of repurposing `If`.

**Baseline Availability**: Normal execution
**Effect Category**: inherits the union of the effects of `condition` and the executed branch
**Determinism Category**: inherits `condition` and the executed branch; branch selection itself MUST be deterministic
**Observability Requirements**:

- MUST record `condition_result_kind`.
- MUST record `branch_taken = then | else`.

**Compatibility Commitment**:

- The three-argument signature `If[condition, thenExpr, elseExpr]` is frozen within `v1.1.x`.
- The `special form` semantics of "execute only one branch" are frozen within `v1.1.x`.
- The falsy classification table defined by this entry is frozen within `v1.1.x`.
- "Auto-propagating error values are treated as falsy in `If`" is frozen within `v1.1.x`.

#### `IfFound`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
IfFound[expr, bindVar_, thenExpr, elseExpr]
```

**Validator Constraints**:

- MUST accept exactly 4 arguments.
- `expr`, `thenExpr`, and `elseExpr` MUST be valid CogLang expressions.
- `bindVar_` MUST be a valid variable slot and is valid only within the evaluation scope of `thenExpr`.
- Any out-of-scope reference to `bindVar_` in `elseExpr` or an outer scope is a validation failure.
- Reusing the same `bindVar_` name in nested binding scopes is a validation failure.

**Return Contract**:

- If the evaluation result of `expr` is neither `NotFound[]` nor an auto-propagating error value, binds the result to `bindVar_` and returns the evaluation result of `thenExpr`.
- If the evaluation result of `expr` is `NotFound[]` or an auto-propagating error value, returns the evaluation result of `elseExpr`.
- `List[]` is not an error value; when `expr -> List[]`, execution MUST enter the `thenExpr` branch.
- If `thenExpr` or `elseExpr` itself fails during evaluation, the corresponding underlying error value is propagated.

**Semantics**:

`IfFound` is a frozen `special form`. It first eagerly evaluates `expr`, then evaluates only one branch.

`IfFound` distinguishes "result available" from "missing/error", not "truthy/falsy". Therefore:

- `NotFound[]` enters `elseExpr`.
- Auto-propagating error values enter `elseExpr`.
- `List[]` enters `thenExpr`.

`IfFound` is an explicit recovery boundary: it does not allow missing values or error values from `expr` to continue auto-propagating outward, but instead transfers control to `elseExpr`.

`IfFound` is also the bind-and-continue idiom formally frozen in the current `v1.1.0`: when `expr` produces a value that a later step needs to consume, callers may use `IfFound[expr, v_, thenExpr, elseExpr]` to explicitly bind that value into `thenExpr` without changing the semantics of `Do` as "responsible only for sequential execution, not responsible for binding between steps". This idiom does not redefine `IfFound` as a general sequential construct, but it is the official spelling in the current release for expressing a "produce first, consume later" chain.

**Baseline Availability**: Normal execution
**Effect Category**: inherits the union of the effects of `expr` and the executed branch
**Determinism Category**: inherits `expr` and the executed branch
**Observability Requirements**:

- MUST record `branch_taken = then | else`.
- MUST record `source_expr_result_kind = normal | not_found | error`.

**Compatibility Commitment**:

- The four-argument signature `IfFound[expr, bindVar_, thenExpr, elseExpr]` is frozen within `v1.1.x`.
- The behavior of `List[]` entering the `thenExpr` branch is frozen within `v1.1.x`.
- The set of auto-propagating error values is defined uniformly by `§8`; this entry only consumes that set and does not extend it separately.

#### `Compose`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Compose[name, params, body]
```

**Validator Constraints**:

- MUST accept exactly 3 arguments.
- `name` MUST be a string literal compatible with an `operator head`.
- `params` MUST be a literal-form `List[var1_, var2_, ...]`.
- Variable names inside `params` MUST be mutually distinct and MUST NOT use the anonymous `_`.
- `body` MUST be a valid CogLang expression.
- The validation context for `body` MUST explicitly include the variables declared in `params`, as well as the operator name currently being registered, to support recursive definitions.

**Return Contract**:

- Success: returns a minimal registration receipt that externally contains at least:

```text
{
  "operator_name": <string>,
  "scope": "graph-local"
}
```

- If `name` is not a string literal compatible with an `operator head`: validation failure.
- If `params` is not a literal list composed of mutually distinct named variables: validation failure.
- If `name` conflicts with a static built-in operator or an existing definition in the same graph-dynamic scope: `TypeError["Compose", "name", "operator already exists or reserved", ...]`.
- If the current profile does not allow graph-dynamic definitions: `PermissionError["Compose", "capability denied", ...]`.

Implementations may include an internal definition handle in transport, diagnostics, or management APIs, but that handle is not part of the public semantic return value.

**Semantics**:

`Compose` is a frozen `special form`. It reads literal `name` and `params`, but **does not** execute `body` at definition time; `body` is stored as an AST as a graph-dynamic operator definition.

After success, the definition enters the "in-graph dynamic operator definition" layer of `§10`. `Compose` is responsible only for registering in-graph dynamic definitions; name resolution order, registry extension, external adapters, and capability constraints are governed uniformly by `§10`.

`Compose` is not equivalent to a general plugin registration interface, and it is not responsible for freezing runtime registry or external adapter behavior.

The normative semantics of `Compose` are "register a graph-dynamic operator definition", not "create a public knowledge node". Implementations may use executor-internal `Operation` carriers to hold the definition, but such carriers SHOULD NOT be mistaken for public knowledge graph primary types.

The defined operator may recursively call itself. The default baseline profile MUST support at least recursion depth 100; when the limit is exceeded, it returns `RecursionError[...]`.

**Baseline Availability**: Normal execution
**Effect Category**: `meta`
**Determinism Category**: `graph-state-dependent`
**Observability Requirements**:

- MUST record `registered_name`.
- MUST record `param_count`.
- MUST record the target scope as `graph-local`.
- MUST record `registration_outcome`.

**Compatibility Commitment**:

- The three-argument signature `Compose[name, params, body]` is frozen within `v1.1.x`.
- The constraints that `name` is a string literal and `params` is a literal list of named variables are frozen within `v1.1.x`.
- "`body` is not executed at definition time" is frozen within `v1.1.x`.
- "Static built-in definitions cannot be overridden by `Compose`" is frozen within `v1.1.x`.
- "The recursion-depth floor for the default baseline profile is 100" is frozen within `v1.1.x`.

#### `Create`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Create[nodeType, attrs]
Create["Edge", attrs]
```

**Validator Constraints**:

- MUST accept exactly 2 arguments.
- `nodeType` and `attrs` MUST both be valid CogLang expressions.
- `Create["Edge", attrs]` indicates edge creation mode; all other cases enter node creation mode.
- Type constraints, field constraints, and permission constraints based on evaluation results are not part of the validator phase.

**Return Contract**:

- If `nodeType` does not evaluate to a string: `TypeError["Create", "type", ...]`.
- If `attrs` does not evaluate to a dictionary: `TypeError["Create", "attrs", ...]`.
- In node mode, if `nodeType` is not `Entity / Concept / Rule / Meta`: `TypeError["Create", "type", "Entity|Concept|Rule|Meta|Edge", ...]`.
- In node mode, if `attrs` explicitly provides the reserved key `type`: `TypeError["Create", "attrs", "reserved key type", ...]`.
- In node mode, if the `id` explicitly provided by `attrs` already exists: `TypeError["Create", "id", "node id already exists", ...]`.
- In node or edge mode, if `confidence` is explicitly provided but is not a numeric value in `(0, 1]`: `TypeError["Create", "confidence", ...]`.
- In edge mode, if `attrs` is missing any required field among `from`, `to`, and `relation_type`: `TypeError["Create", "Edge", "missing required field", ...]`.
- In edge mode, if any field among `from`, `to`, and `relation_type` does not evaluate to a string: `TypeError["Create", "Edge", "invalid field type", ...]`.
- In edge mode, if the node pointed to by `from` or `to` does not exist or is not visible: `NotFound[]`.
- If the current profile forbids graph writes: `PermissionError["Create", "graph_write"]`.
- Node mode success: returns the ID string finally used by the node; if `attrs.id` is missing, this is the unique ID assigned by the execution environment for this creation.
- Edge mode success: returns `List[from, relation_type, to]`.

**Semantics**:

`Create` creates a public knowledge graph node in node mode, and creates a public edge object in edge mode.

In node mode, the first argument `nodeType` is the only authoritative source of the public primary type; `attrs` is responsible only for supplemental business attributes and optional `id / confidence`. Therefore:

- Public node `type` only allows `Entity / Concept / Rule / Meta`.
- Legacy business-classification spellings such as `attrs["type"] = "Person"` are no longer legal in `v1.1.x`.
- Business classification SHOULD be expressed through non-reserved business fields or graph structure, but this version does not freeze a unified field name.

`Create["Rule", attrs]` creates a public `Rule` node, not an executable operator definition; in-graph dynamic operators remain the responsibility of `Compose`.

The call-surface key names `from / to / relation_type` in edge mode are call-surface aliases. If an implementation internally uses `source_id / target_id / relation`, it MUST perform an unambiguous mapping, but MUST NOT expose this internal naming difference as a semantic difference.

In node mode, if `attrs.id` is explicitly provided and does not conflict, the execution environment MUST use that value as the node ID adopted for this creation. If `attrs.id` is missing, the execution environment MUST allocate a unique ID before forming the internal write request, `WriteBundleCandidate`, or equivalent host submission object, and MUST use that ID as the common identifier for the language-level return value and subsequent internal references. The concrete ID format and generation strategy are defined by the execution environment; one common approach is to preallocate a UUID.

If an internal implementation uses `source_id / target_id / relation`, then the mapping from `from / to / relation_type` to internal fields MUST be completed when constructing the internal write request, bundle validation input, or equivalent host submission object. This step MUST NOT be delayed until after submission in a way that causes internal reference validation to see unmapped call-surface fields.

`Create` MUST NOT produce partial writes when it fails.

This entry freezes language-level write intent and success/failure semantics; it does not prescribe the host's persistence submission path. If an upper-layer architecture uses `WriteBundle`, an owning module, or another delegated submission flow, the executor may first form an intermediate write candidate and then have the host map back to this entry's language-level return contract after submission succeeds. The same layering applies to `Update / Delete`.

**Baseline Availability**: Normal execution
**Effect Category**: `graph-write`
**Determinism Category**: `graph-state-dependent`
**Observability Requirements**:

- MUST record `create_mode = node | edge`.
- MUST record the target primary type or `relation_type`.
- MUST record `creation_outcome`.

**Compatibility Commitment**:

- The two call shapes `Create[nodeType, attrs]` and `Create["Edge", attrs]` are frozen within `v1.1.x`.
- The behavior where node success returns a string ID and edge success returns a triple is frozen within `v1.1.x`.
- `"Edge"` in `Create["Edge", ...]` is a call-mode marker, not a public primary node type.
- The public node `type` is determined by the first argument, and `attrs` MUST NOT overwrite this field; this is frozen within `v1.1.x`.

#### `Update`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Update[target, changes]
```

**Validator Constraints**:

- MUST accept exactly 2 arguments.
- `target` and `changes` MUST both be valid CogLang expressions.
- In the main `v1.1.x` specification, `Update` covers only node updates and does not include an edge update mode.

**Return Contract**:

- If `target` does not evaluate to a string: `TypeError["Update", "target", ...]`.
- If `changes` does not evaluate to a dictionary: `TypeError["Update", "changes", ...]`.
- If the target does not exist: `NotFound[]`.
- If the target has been soft-deleted: `PermissionError["Update", ...]`.
- If the current profile forbids writes, or the target is a non-modifiable object: `PermissionError["Update", ...]`.
- If `changes` attempts to rewrite protected system fields, such as `id / type / provenance / created_at / updated_at`: `TypeError["Update", "changes", "writable field set", ...]`.
- If `changes["confidence"] = 0`: `TypeError["Update", "changes", "use Delete for soft-delete", ...]`.
- If `changes["confidence"]` exists but is not a numeric value in `(0, 1]`: `TypeError["Update", "confidence", ...]`.
- Success: `True[]`.

**Semantics**:

`Update` is a single-node, partial-field overwrite update; fields that do not appear in `changes` MUST remain unchanged.

`Update` MUST NOT assume soft-delete or restore semantics. Soft delete can only go through `Delete`, and restore is not part of the current `Core` entry.

Runtime-managed fields such as `updated_at` are refreshed by the implementation; ordinary `Update` MUST NOT forge overwrites of system-managed fields.

`Update["some_rule", ...]` modifies the content of a public `Rule` node; it MUST NOT implicitly rewrite an in-graph dynamic operator definition registered by `Compose`.

`Update` MUST NOT partially apply changes when it fails.

**Baseline Availability**: Normal execution
**Effect Category**: `graph-write`
**Determinism Category**: `graph-state-dependent`
**Observability Requirements**:

- MUST record the target node ID.
- MUST record the set of changed fields.
- MUST record `update_outcome`.

**Compatibility Commitment**:

- The two-argument signature `Update[target, changes]` is frozen within `v1.1.x`.
- "A missing target returns `NotFound[]`" and "a soft-deleted target returns `PermissionError[...]`" are frozen within `v1.1.x`.
- The boundary that `Update` does not provide an edge update mode is frozen within `v1.1.x`.
- The rule that `Update` does not allow writing `confidence` to `0` to simulate deletion is frozen within `v1.1.x`.

#### `Delete`

**Status**: `Core`
**Layer**: `language`
**Syntax and Signature**:

```text
Delete[target]
Delete["Edge", attrs]
```

**Validator Constraints**:

- Allows only the 1-argument and 2-argument forms.
- `Delete[target]` indicates node deletion mode.
- `Delete["Edge", attrs]` indicates edge deletion mode; in the 2-argument form, the first argument MUST be the literal string `"Edge"`.
- All argument positions MUST be valid CogLang expressions.

**Return Contract**:

- In node mode, if `target` does not evaluate to a string: `TypeError["Delete", "target", ...]`.
- In edge mode, if `attrs` does not evaluate to a dictionary: `TypeError["Delete", "attrs", ...]`.
- In edge mode, if `from`, `to`, or `relation_type` is missing, or if a field value is not a string: `TypeError["Delete", "Edge", ...]`.
- Node mode success: returns the ID string of the soft-deleted node.
- Edge mode success: returns the triple of the soft-deleted edge, `List[from, relation_type, to]`.
- If the node or edge does not exist: `NotFound[]`.
- If the node or edge has already been soft-deleted: `NotFound[]`.
- If the current profile forbids deletion, or the target is a protected object: `PermissionError["Delete", ...]`.

**Semantics**:

`Delete` only performs soft-delete and does not perform physical removal; its normative effect is to set the target object's `confidence` to `0` while retaining history.

After nodes and edges are soft-deleted, by default they no longer participate in ordinary visibility paths such as `AllNodes`, `Traverse`, and `Query`.

`Delete` MUST be idempotent; deleting an already deleted object again returns `NotFound[]`.

`Delete["Edge", attrs]` deletes a public edge object and does not require exposing an internal edge handle. Its call-surface key names `from / to / relation_type` remain call-surface aliases, not the only naming of the internal storage schema.

`Delete["some_rule"]` deletes a public `Rule` node; it is not automatically equivalent to unregistering some `Compose` definition, and it does not automatically clean up all evidence edges that reference that rule.

**Baseline Availability**: Normal execution
**Effect Category**: `graph-write`
**Determinism Category**: `graph-state-dependent`
**Observability Requirements**:

- MUST record `delete_mode = node | edge`.
- MUST record the target object reference.
- MUST record `delete_outcome`.

**Compatibility Commitment**:

- The one-argument node form and the two-argument edge form are frozen within `v1.1.x`.
- The semantics of soft-delete rather than hard-delete are frozen within `v1.1.x`.
- The idempotent semantics that "already missing or already deleted returns `NotFound[]`" are frozen within `v1.1.x`.

#### `Trace`

**Status**: `Core`
**Layer**: `observability`
**Syntax and Signature**:

```text
Trace[expr]
```

**Validator Constraints**:

- `expr` MUST be a valid CogLang expression.

**Return Contract**:

- The return value MUST be exactly identical to the result of directly executing `expr`.
- When `expr` returns an error value, `Trace` MUST return that error value as-is.

An unavailable trace sink MUST NOT override the business return value.

**Semantics**:

`Trace` is a transparent wrapper. It executes `expr` and writes this execution to the observability system, but does not change the semantics, return value, or error propagation behavior of `expr`.

`Trace` is responsible only for expression-level execution records, not task-level ROI, rule-level rollback, or cost-level aggregate events.

**Baseline Availability**: Normal execution
**Effect Category**: `diagnostic`
**Determinism Category**: inherits `expr`; trace event encoding is `implementation-defined`
**Observability Requirements**:

- MUST record at least `expr_id`.
- MUST record at least `parent_id`.
- MUST record at least `canonical_expr`.
- MUST record at least `result_summary`.
- MUST record at least `duration_ms`.
- MUST record at least `effect_class`.

**Compatibility Commitment**:

- The transparent wrapper semantics of `Trace[expr]` are frozen within `v1.1.x`.

#### `Assert`

**Status**: `Core`
**Layer**: `observability`
**Syntax and Signature**:

```text
Assert[condition, message]
```

**Validator Constraints**:

- `condition` MUST be a valid CogLang expression.
- `message` MUST be a valid CogLang expression.

**Return Contract**:

- Returns the evaluation result of `condition`.
- If `condition` itself errors during evaluation, propagates that error as-is.
- Assertion failure itself is not a CogLang runtime error.

**Semantics**:

`Assert` performs a non-fatal assertion. It first evaluates `condition`; if the result is falsy, it emits an assertion-failure event but does not terminate the current reasoning chain.

`message` is evaluated only when an assertion failure needs to be recorded.

`Assert` is suitable for exposing anomalous states in composed operations, rule triggering, or debugging paths; it is not a replacement for error propagation mechanisms.

**Baseline Availability**: Normal execution
**Effect Category**: `diagnostic`
**Determinism Category**: inherits `condition`; assertion event encoding is `implementation-defined`
**Observability Requirements**:

- When an assertion fails, MUST record a structured assertion / anomaly event.
- The event MUST be able to be incorporated by upper layers into error classification and rollback audit.

**Compatibility Commitment**:

- The non-fatal semantics of `Assert` are frozen within `v1.1.x`.

#### Core Entry Scope Note

This section freezes only the `Core` operator entries prioritized for closure in this pass. Other legacy entries still retained in the catalog will later be evaluated individually for migration into `Core`, transition to `Reserved`, or continued `Carry-forward` status; they are no longer assumed by default to all enter this template.

### 7.3 Reserved Operators

#### `Explain`

**Status**: `Reserved`
**Layer**: `observability`
**Syntax and Signature**:

```text
Explain[expr]
```

**Validator Constraints**:

- `expr` MUST be a valid CogLang expression.

**Return Contract**:

- In a profile that supports this capability, returns an execution-plan description object.
- In the default baseline profile, MAY return `StubError["Explain", ...]`.

**Semantics**:

The semantics of `Explain` are "non-executing plan preview". It is used to return a description of execution steps, cost, or plan structure. It MUST NOT execute `expr`.

Once `Explain` is implemented:

- It MUST NOT produce graph writes.
- It MUST NOT produce external side effects.
- It MUST NOT replace `Trace`.

**Baseline Availability**: `StubError[...]`
**Effect Category**: `meta`
**Determinism Category**: `implementation-defined`
**Observability Requirements**:

- Calling `Explain` MUST leave at least a `meta` or `stub` event.

**Compatibility Commitment**:

- The signature `Explain[expr]` is frozen within `v1.1.x`.
- The complete schema of the returned object is not yet frozen.

#### `Inspect`

**Status**: `Reserved`
**Layer**: `meta`
**Syntax and Signature**:

```text
Inspect[target]
```

**Validator Constraints**:

- `target` MUST be a valid CogLang expression.

**Return Contract**:

- In a profile that supports this capability, returns object-structure description data.
- In the default baseline profile, MAY return `StubError["Inspect", ...]`.

**Semantics**:

The semantics of `Inspect` are "return object structure as data". It is used to inspect values, structured items, or object descriptions exposed publicly by an implementation. It does not perform plan preview and does not provide temporal trace.

Once `Inspect` is implemented:

- It MUST NOT replace `Trace`.
- It MUST NOT replace `Explain`.
- It MUST NOT automatically expose host-private internal structures just because inspection succeeds.

**Baseline Availability**: `Profile Baseline: StubError["Inspect", ...]`; `Profile Enhanced: Normal execution`
**Effect Category**: `meta`
**Determinism Category**: `implementation-defined`
**Observability Requirements**:

- Calling `Inspect` MUST leave at least a `meta` or `stub` event.

**Compatibility Commitment**:

- The one-argument signature `Inspect[target]` is frozen within `v1.1.x`.
- The default baseline profile's `StubError[...]` stub path is frozen within `v1.1.x`.
- The complete schema of the returned object is not yet frozen.

#### Reserved Scope Note

The following capabilities are only placeholders in this pass and are not written as `Core` in this section:

- Concrete surface syntax for explicitly qualified names
- Non-default `Query.mode`
- Query cost / information-gain estimation
- Rule-candidate envelope
- Complete schema for rule publication and rollback chains

### 7.4 Experimental Operators

This section records operator directions that **have entered discussion but do not yet have stable semantic commitments**.

Entries entering `Experimental` MUST satisfy at least:

- Name, layer, effect category, and permission boundary have preliminary descriptions.
- They have not yet met the freeze strength required by `Reserved`: "signature + default failure behavior + trace requirements".
- Implementers MUST NOT externally promise them as stable dependencies.

Current typical experimental directions include:

- General `Recover[...]`
- Stronger `InspectSelf[...]`
- Operators related to rule self-modification
- Adapter-specific highly coupled operators

These entries may appear in appendices, design records, or experimental profiles, but SHOULD NOT be written into the `Core` operator catalog before entering `Reserved`.

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
