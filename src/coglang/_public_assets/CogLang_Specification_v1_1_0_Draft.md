# CogLang Language Specification

**Version: v1.1.0**
**Status: stable language release (the filename temporarily retains `Draft` for compatibility with existing references; this document is no longer a free-form draft)**
**Position: authoritative main document for the current CogLang specification set; intended for implementation, conformance, external trials, and cross-host alignment**

---

## 0. Role of This Document

This document is the stable main specification for CogLang `v1.1.0`. It carries forward:

- The frozen core syntax, evaluation semantics, and error semantics from `v1.0.2`
- Requirements for extension mechanisms, meta-reasoning, observability, query interfaces, and rule bridging under the current architecture boundaries
- Reserved capabilities that need language-level declaration ahead of time, while leaving implementation details unfrozen by this version of the main text

This document is no longer used as a "chapter skeleton draft". For the current stage, it should be treated as:

- The stable authoritative source for the v1.1.0 language surface, evaluation semantics, error model, and expression-level observability
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

The freeze of `v1.0.2` applies only during the initial dependency-alignment period and is not a permanent freeze.

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

- During a future unreleased draft stage before a `-pre` or stable release candidate is declared
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

`Abstract` does **not** directly generate rule candidates, does **not** execute downstream validation, and does **not** directly write to any draft or primary graph. Rule generation, validation, and promotion belong to later host or application stages outside the `Abstract` operator contract.

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

## 8. Error and Diagnostic Contract

### 8.1 Error Expressions

CogLang error objects are first **valid CogLang expressions** and only secondarily diagnostic events. Implementations MUST NOT represent user input errors, model output errors, or execution-time errors only as host-language exceptions while bypassing the CogLang layer.

`v1.1.0` freezes the following error Heads and minimum canonical structures:

| Error expression | Minimum canonical structure | Meaning |
|------------------|-----------------------------|---------|
| `NotFound[]` | `NotFound[]` | Query returned no result, the target does not exist, or unification failed |
| `TypeError[...]` | `TypeError[op, param, expected, actual]` | Dynamic type mismatch or parameter value violates runtime constraints |
| `PermissionError[...]` | `PermissionError[op, target]` | Insufficient permission, profile prohibition, or unsatisfied capability |
| `ParseError[...]` | `ParseError[reason, position]` | Parse failure |
| `StubError[...]` | `StubError[op, message]` | A registered capability was called but is currently unimplemented or unavailable |
| `RecursionError[...]` | `RecursionError[op, depth, message]` | Recursion or expansion depth exceeded |

The minimum structures above are a compatibility commitment for the canonical surface. Implementations MAY add more fields in the transport envelope or diagnostic record, but MUST NOT change the basic meaning of these Heads.

All error expressions MUST satisfy the following requirements:

- They can flow into subsequent expressions as ordinary CogLang values
- They can appear in `Trace` and reasoning traces
- They can be consumed by `Inspect`, `If`, `IfFound`, or equivalent mechanisms
- They MUST NOT depend on the host exception stack as the only visible information source

### 8.2 Diagnostic Fields

When the parser, validator, executor, or render layer generates diagnostic information, the host-side diagnostic object or transport envelope **MUST** support the following field names:

- `diagnostic_code`
- `phase`
- `source_span`
- `blame_object`
- `recoverability`
- `trace_policy`

Field constraints are as follows:

- `diagnostic_code`: A stable string code. Within the same profile, the same code MUST NOT be reused for incompatible errors.
- `phase`: MUST distinguish at least `parse / validate / execute / render`.
- `source_span`: If the diagnostic can be located in canonical text, a 1-based start and end position MUST be provided; if there is no text source, it MAY be empty.
- `blame_object`: Points to the most relevant `Head`, parameter position, graph object ID, or external capability name.
- `recoverability`: Describes whether the caller can continue through branching, retry, fallback, or capability switching; profiles MAY extend the concrete value set.
- `trace_policy`: Indicates whether the diagnostic MUST enter the reasoning trace, is recorded only when trace is enabled, or is written only to host logs.

These fields are part of the diagnostic contract and are not required to all be encoded into positional arguments of the canonical error expression. The specification encourages layered representation of "error expression" and "host diagnostic metadata" rather than stuffing all context into positional arguments of a single Head.

### 8.3 ParseError and Partial Structure

When the parser encounters a syntax error, it **MUST NOT** expose the host parsing exception directly as the only result. It MUST return `ParseError[...]`, and when recovery is possible it MUST attach partial structure information.

`v1.1.0` defines the following minimum requirements for `ParseError`:

- The canonical error expression is at least `ParseError[reason, position]`
- If the parser successfully recovers a partial AST, it MUST expose `partial_ast` or `partial_ast_ref` through the transport envelope, diagnostic object, or an equivalent host interface
- If no partial structure can be recovered, the `partial_ast*` fields MAY be omitted, but an empty AST MUST NOT be fabricated

Partial structure is preserved for two purposes:

- To provide "partially correct" structural feedback for authoring, debugging, tests, or training workflows
- To provide more precise error location and repair suggestions for UIs and debuggers

When Readable Render displays a `ParseError`, it should also show:

- The failure reason
- The failure position
- The successfully recovered partial structure, if present

---

## 9. Observability and Readable Render

### 9.1 Built-in Debug Capabilities

`Trace`, `Assert`, and `Explain` are built-in debugging and meta-observation capabilities of CogLang. They are not debugging switches bolted on by the host system.

Their boundaries are as follows:

- `Trace`: Records the trace of expressions actually executed and does not change the return value
- `Assert`: Records a non-fatal abnormal state and does not replace error propagation
- `Explain`: Returns a plan preview and does not execute the target expression; in the default profile, it MAY be `StubError[...]`
- `Inspect`: A reserved object-structure inspection capability; if an implementation provides it, it returns object structure as data and belongs to metacognitive / structural inspection, but it does not replace the temporal record of `Trace` or the plan preview of `Explain`

Therefore, a host implementation MAY integrate these capabilities at the logging layer, but MUST NOT collapse them into the same operator at the language-semantics layer.

The CogLang execution environment MUST bridge these debugging events out to an external observability system. `Observer` is only a recommended name; an equivalent hook is acceptable, but this bridging capability MUST NOT be absent.

### 9.2 Trace Schema

A single CogLang execution record in `ReasoningTrace` has the following minimum fields:

| Field | Requirement |
|-------|-------------|
| `expr_id` | Locally unique identifier of the current expression within this trace |
| `parent_id` | Parent expression ID; MAY be empty at the top level |
| `canonical_expr` | Canonical form of the executed expression |
| `effect_class` | Effect class of the corresponding operator |
| `result_summary` | Stable summary of the return value; large objects MAY record only a summary and reference |
| `duration_ms` | Execution duration in milliseconds |

The following fields are recommended extension fields for `v1.1.0`:

- `source_span`
- `status`
- `trace_id`
- `parent_spans`
- `source_instance_id`

Extension field constraints:

- `source_span`: If the expression comes from locatable text, it should coordinate with `source_span` in §8.2
- `status`: Recommended to distinguish at least `ok / error / stub / assertion_failed`
- `trace_id`: MAY be enabled as needed; it MUST NOT be a resident field on all messages or results by default
- `parent_spans`: Used to stitch provenance chains across expressions or components; MAY be empty if the implementation does not support span-level tracing
- `source_instance_id`: Reserved for a future cross-instance trace phase; MAY be empty in the current phase

Trace records MUST serve two classes of consumers:

- Human debugging and audit
- Upper-layer anomaly detection and statistical aggregation

Therefore, the trace schema MAY trim large objects, but MUST NOT trim to the point where it is impossible to determine "what executed, what returned, and how long it took."

### 9.3 Readable Render Contract

Every valid CogLang expression MUST have a stable Readable Render. Readable Render is the **human display layer**, not the authoritative semantic source, but it MUST be stable enough to support trace, logs, UI inspection, and human review.

`v1.1.0` defines the following minimum requirements for Readable Render:

- Preserve the original `Head`
- Preserve argument order
- Use stable indentation for nested expressions
- Display the error Head and key arguments for error expressions
- Use stable field order for lists, dictionaries, and structured result objects
- The reference implementation should provide `to_readable()` or an equivalent interface

Readable Render **MUST NOT**:

- Implicitly rewrite the canonical structure
- Drop key arguments or error fields
- Render distinct canonical expressions into indistinguishable text

Line breaks, indentation, and token order in Readable Render serve only display and transport. They MUST NOT be interpreted backward as graph-semantic adjacency order or hierarchy order.

UIs, logs, and traces MAY add color, highlighting, folding, line numbers, or jump anchors beyond Readable Render, but those enhancements MUST NOT impair the ability to trace back to the canonical expression.

---

## 10. Extensions and Name Resolution

### 10.1 Name Resolution Model

CogLang freezes the **abstract dispatch model** of name resolution before freezing concrete surface syntax.

In `v1.1.0`, name resolution involves three definition sources and one execution provider:

1. **Static built-in operator definitions**
2. **In-graph dynamic operator definitions**
3. **Runtime registry entries**
4. **External adapter providers**

#### 1. Static Built-in Operator Definitions

These are operator definitions registered in the static vocabulary and natively given semantics by the executor. Their syntactic entry point is addressed by the corresponding `operator head`.

#### 2. In-graph Dynamic Operator Definitions

These are operator definitions registered into the current graph scope by `Compose` or an equivalent in-graph mechanism. Their syntactic entry point is addressed by the corresponding `operator head`.

#### 3. Runtime Registry Entries

These are operator definition entries that are not written into the graph but are exposed to the parsing and execution layers by the runtime registry. Their purpose is to provide a uniform entry point for:

- Pluginized operators
- Temporarily reserved operators
- Runtime capabilities bound to the runtime bridge / adapter

#### 4. External Adapter Providers

These are execution providers whose final behavior is provided by an external adapter. They do not independently participate in name-priority competition; they attach after a resolved operator definition or registry entry and provide the actual execution capability. Their execution may require:

- Capability checks
- Permission checks
- External system connectivity
- Runtime fallback

### 10.2 Resolution Order and Conflict Handling

In a given validation context, each **`operator head` in executable position** **MUST** resolve to exactly one operator definition.

By default, `term head` and `atom` do not participate in the operator resolution process in this section. Whether they are permitted to appear, and whether they are consumed by an operator as structured items, is determined by the corresponding entry.

#### Default Resolution Order When the Name Is Not Explicitly Qualified

1. Static built-in operator definitions
2. In-graph dynamic operator definitions
3. Runtime registry entries

By default, a static built-in Head **MUST NOT** be overridden by later layers.

#### Explicitly Qualified Names

`v1.1.0` freezes the abstract capability of "supporting explicitly qualified names", but **does not freeze the concrete separator spelling in this version**.

That is:

- The specification allows "qualified names" to exist in the future
- It does not pre-commit that their surface spelling must be any particular symbolic form
- Therefore, this capability is currently a reserved slot for implementers and architecture documents, not teachable syntax for ordinary users

#### Conflict Handling

- Duplicate registrations within the same resolution layer MUST error at registration time
- When an in-graph dynamic operator definition and a runtime registry entry have the same name, the unqualified name resolves to the in-graph dynamic definition by default
- Once explicitly qualified names are adopted, they MUST skip shadowing rules from unrelated layers

#### Error Semantics for Unresolved and Unavailable Names

- Syntax is valid but the name is unresolved: **validation failure**; execution MUST NOT begin
- Name is resolved but implementation is not installed: `StubError[head, "operator_unavailable"]`
- Name is resolved but capability is insufficient: `PermissionError[head, capability]`

Name resolution failure and syntax parsing failure are distinct problems. Unless an implementation wraps both in the same host diagnostic object, an unresolved name should not be represented as `ParseError[...]`.

This kind of failure is not a CogLang runtime value. The host validator **MUST** report at least:

- `head`
- `attempted_resolution_scopes`
- `source_span`
- `diagnostic_code`

### 10.3 Extension Capability Boundaries

Each registry operator or external-adapter binding entry MUST declare at least:

- canonical name
- status
- layer
- arity / signature
- effect class
- determinism
- required capabilities
- default unavailable behavior
- readable render hint

#### Capability Declaration

When an operator requires an external capability, the specification currently freezes only the mechanism that a capability identifier exists. Concrete capability names are `implementation-defined` in `v1.1.0`, but the profile manifest **MUST** publish the exact strings.

Implementations are advised to distinguish at least:

- `graph_write`
- `trace_write`
- `external_io`
- `cross_instance`
- `self_modify`

When capability checks fail, the implementation MUST return `PermissionError[...]` rather than silently falling back.

#### External Side Effects

For any operator whose effect class contains `external`:

- It MUST explicitly declare its external side effects
- It MUST declare whether it may be called under the default profile
- It MUST enter trace

Any operator that does not declare external side effects MUST NOT implicitly access external systems during execution.

---

## 11. Current Feature Inventory and Status Record

### 11.1 Core

Capabilities already converged as `Core` in the current draft include:

- Four-layer representation model: `AST / canonical text / readable render / transport envelope`
- Graph-first language identity and explicit graph-write boundary
- The basic model that errors are values, including `NotFound / TypeError / PermissionError / ParseError / StubError / RecursionError`
- Core value types: `String / Number / Bool / List / Dict / ErrorExpr`
- Public knowledge graph primary node types: `Entity / Concept / Rule / Meta`
- `Abstract` semantics of "prototype extraction + triggering", and its provenance constraints
- `Equal`
- `Compare`
- `Unify`
- `Match`
- `Get`
- The three-argument interface of `Query`, separation of `k` / `mode`, and default `mode`
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
- Minimum Readable Render contract
- Abstract dispatch model and default priority for name resolution

### 11.2 Reserved

Capabilities reserved as `Reserved` in the current draft, but not required to be implemented by default, include:

- `Explain`
- `Inspect`
- Non-default `Query.mode`
- Query-related `cost / gain` metareasoning interfaces
- Rule candidate envelope
- Complete schema for rule publication, validation, and rollback chains
- Concrete surface syntax for explicitly qualified names
- More complete cross-instance trace field set and cross-component provenance stitching details

### 11.3 Experimental

Directions currently recorded only as `Experimental` topics and not yet part of the stable specification include:

- General `Recover[...]`-style recovery syntax
- Stronger self-inspection / self-modifying operators
- Stronger type annotations and generic type system
- Syntax sugar, such as local bindings and pipelines
- High-risk, strongly host-coupled adapter-specific capabilities

### 11.4 `Baseline / Enhanced` Profiles

`v1.1.0` recommends distinguishing at least the following two profile classes:

- `Baseline`: The default baseline profile, used to carry the graph-first main chain, minimum composition capability, basic diagnostics and observability, and the current minimum consistency requirements for `Core`
- `Enhanced`: An enhanced profile, used to carry extension operators, non-default query modes, controlled external capabilities, and enhanced execution capabilities that are still not suitable for the `Core` trunk

The relationship constraints for these two profile classes are as follows:

- `Enhanced` **MUST** remain compatible with the compatibility surface of `Baseline` and MUST NOT break existing `Core`
- If a capability is available only in `Enhanced`, its entry **MUST** state the profile condition explicitly in `Baseline Availability`
- `Baseline` should not carry high-risk, strongly host-coupled, or architecture-level protocol capabilities
- `Enhanced` may carry stronger extension execution capabilities, but those capabilities still do not by default mean "may be automatically written into the graph", "program execution domain", or "has become a public knowledge-layer object"

The currently recommended convergence is:

- `Baseline`: `Abstract / Equal / Compare / Unify / Match / Get / Query / AllNodes / Traverse / If / IfFound / Do / ForEach / Compose / Create / Update / Delete / Trace / Assert` and their related basic models
- `Enhanced`: Stronger `Query.mode`, `Explain`, `Inspect`, `cost / gain` metareasoning interfaces, extension registry operators, controlled external capabilities, and other enhanced execution capabilities that are still not suitable for `Core`

Profile is a boundary for execution availability and capability packaging, not a new language layer. Its role is to absorb complexity pressure, not to rewrite the semantic trunk of `Core`.

### 11.5 Relationship to §1.4

This chapter does not redefine promotion / demotion rules; the authoritative rules are in `§1.4`.

This chapter is responsible only for recording which capabilities in the current version are in:

- `Core`
- `Reserved`
- `Experimental`

and their current status descriptions, notes, and reference locations.

---

## 12. Conformance Tests and Reference Implementation Boundary

### 12.1 Conformance Suite

The goal of the `Conformance Suite` is not to cover every implementation detail, but to verify whether implementations comply with the compatibility surface frozen by the specification.

`v1.1.0` should include at least the following test groups:

- parser / validator tests: syntax, variable positions, name resolution, diagnostic fields
- canonical round-trip tests: `AST <-> canonical text`
- execution tests: normal values, error values, and boundary values for core operators
- graph-write boundary tests: explicit graph writes and prohibition of implicit graphization
- error propagation tests: default propagation and explicit blocking points
- trace tests: minimum fields and value-transparent semantics of `Trace` / `Assert`
- rendering tests: stable output from readable render
- extension tests: registry entries, uninstalled implementations, capability failures

Pass criteria for tests should primarily depend on fields and semantics declared by the specification rather than on internal data structures of a particular implementation.

### 12.2 Golden Examples

Each operator entering `Core` should be accompanied by at least the following example types:

- Positive example: typical success path
- Boundary example: boundary inputs such as empty list, empty graph, minimum arguments, and `k=0`
- Error example: type mismatch, insufficient permission, unresolved name, and stubbed capability
- Trace example: at least one sample that verifies `Trace` / `Assert` fields

The following topics MUST have standalone golden examples:

- `Abstract` does not directly generate rules
- `Query` decouples `k` and `mode`
- Explicit graph-write boundary and prohibition of implicit graphization
- `ParseError` and `partial_ast`
- Non-identity of Readable Render and canonical text
- External annotation style for `Operation` when used as the executor's internal carrier

The expanded example set for this specification is in the companion document `CogLang_Conformance_Suite_v1_1_0.md`. The following example IDs should be treated as the minimum authoritative example index for this version:

- `GE-001`: Distinction between `operator head` and `term head`
- `GE-002`: Non-identity of canonical text and multiline readable render
- `GE-003`: Basic success path for `Query`
- `GE-004`: Minimum semantics of `Query.k`
- `GE-005`: `Abstract` only performs prototype extraction and triggering
- `GE-006`: Value transparency and minimum trace fields of `Trace`
- `GE-007`: Non-fatal semantics of `Assert`
- `GE-008`: `ParseError` and `partial_ast`
- `GE-009`: Unresolved name is a validator diagnostic and is not equivalent to `ParseError`
- `GE-010`: External annotation of `Operation` when used as the executor's internal carrier
- `GE-018`: Default stub behavior of `Explain` in `Baseline`
- `GE-019`: Capability denied for an extension-backed operator
- `GE-020`: Name resolved but implementation not installed
- `GE-021`: Branch handling by `If` for automatically propagated error values
- `GE-022`: Dispatch by `IfFound` for `NotFound[]`, error values, and `List[]`
- `GE-023`: Stable mapping and result preservation by `ForEach`
- `GE-024`: Sequential execution and non-automatic abort by `Do`
- `GE-025`: Default stub behavior of `Inspect` in `Baseline`
- `GE-026`: Bind-and-continue idiom of `IfFound`
- `GE-027`: Visibility and stable order of `AllNodes`
- `GE-028`: Success path of `Update` and rejection at `confidence=0`
- `GE-029`: Soft-delete and idempotence of `Delete`
- `GE-030`: Result preservation for body errors in `ForEach`
- `GE-031`: Three-way dispatch of `Get` across `Dict / List / node_attr`
- `GE-032`: Unique allocation and return consistency for default IDs in `Create`
- `GE-033`: Alias normalization in `Create["Edge", ...]` occurs before internal reference validation

### 12.3 Reference Implementation Boundary

The reference implementation should cover the following minimum capabilities:

- parser
- validator
- canonical serializer
- readable renderer
- core error model
- Minimum executable semantics of `Core` operators

The reference implementation is not required to fully cover:

- Internal algorithms of the runtime bridge
- Internal physical implementation of a graph-memory backend
- Concrete logging system behind Observer
- Real network or plugin execution by external adapters
- Complete behavior of `Reserved / Experimental` capabilities

Specification constraints focus on input/output semantics, diagnostic fields, trace fields, name resolution rules, and the compatibility surface. Implementation optimizations may vary freely, but MUST NOT break these externally observable contracts.

---

## 13. Non-goals and Deferred Items

The following are not goals of `v1.1.0`:

- Optimizing CogLang into a general-purpose programming language for handwritten human code
- Introducing many equivalent spellings for syntactic concision
- Promoting all runtime metadata into core syntax
- Freezing the complete protocol of the runtime bridge, host transport layer, or external adapters in the language specification
- Collapsing the raw structure layer, canonical representation layer, and output interpretation layer back into one layer
- Writing `Reserved` entries as if they were stably dependable `Core` capabilities

Deferred items include but are not limited to:

- Stronger metacognitive operators
- More complete rule candidate / publication / rollback object model
- Application-side lifecycle object model and persistent commit protocol
- Stronger type system
- Richer syntax sugar
- Programmatic syntax and program execution-domain capabilities in later roadmap phases
- Complete object model for cross-instance trace / provenance
- Refinement of capability manifest and adapter catalog

---

## Appendix A: Operator Specification Template

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
Baseline Availability: <normal execution | StubError | PermissionError | profile-specific availability>
Observability: <trace/log requirements>
Compatibility: <name frozen? semantics frozen?>
Notes: <informative notes>
```

## Appendix B: Follow-up Priority for Completing the Language Specification

Recommended order for follow-up writing:

1. Design of `k / mode` for the query operator
2. Extensions and name resolution model
3. `Explain` / trace schema
4. Reserved / Experimental inventory
5. grammar and conformance suite
6. Synchronized refinement of rendering / UI contract
