# CogLang Contribution Guide v0.1

**Status**: pre-release contribution guide
**Audience**: contributors preparing issues, PRs, documentation updates, examples, or tooling improvements for `CogLang`
**Purpose**: explain why `experimental / pre-release` is stated explicitly, which contributions are most welcome now, which changes are not priorities, and which boundaries contributors should understand first

---

## 0. Why `experimental / pre-release` Is Explicit

`CogLang` currently has:

- a main specification
- a Quickstart
- conformance and golden examples
- a reference runtime
- a minimal CLI, REPL, self-check path, and release-check path

It still does not yet have:

- stable multi-host validation
- a mature extension ecosystem
- complete platformization and release automation

The public framing therefore needs both statements to remain true:

1. **It is already worth trying, reading, implementing, and minimally integrating.**
2. **It should not be mistaken for a mature standalone platform.**

The `experimental / pre-release` label is not meant to discourage contribution. It exists to prevent incorrect expectations from turning normal evolution into claims of arbitrary compatibility breakage or unclear draft status.

---

## 1. Most Welcome Contributions Right Now

The following contribution types are the highest-value areas at this stage.

### 1.1 Documentation Clarification

Prioritize issues such as:

- specification boundaries that are not clear enough
- companion documents whose relationship to the main specification is hard to read
- Quickstart steps that are not friendly enough for first-time users
- README reading paths, command explanations, or document discoverability that are unclear

### 1.2 Conformance and Golden Examples

Prioritize issues such as:

- frozen semantics without corresponding golden examples
- important boundaries that different implementers could interpret differently
- minimal regression sets that do not cover common paths

This is one of the most valuable contribution areas because it directly affects:

- whether the language boundary is executable
- whether documentation and implementation keep drifting
- whether external hosts can reproduce behavior at low cost

### 1.3 CLI and Tooling Surface

Prioritize issues such as:

- CLI discoverability
- readability and stability of `info / manifest / bundle / doctor / smoke / demo`
- smoothness of the minimal post-install trial path
- stable output that is friendlier to scripts, CI, and `release-check`

### 1.4 Host Bridge and Runtime Contract

Prioritize issues such as:

- clearer Host Runtime Contract boundaries
- alignment of local bridge, provenance, and request-response behavior
- stable minimal interfaces for write intent, commit, receipt, and query surfaces

### 1.5 Non-Reference Host Examples and Minimal Host Demos

Prioritize issues such as:

- examples that are weakly coupled to the reference host
- a minimal in-memory host
- a minimal graph-workflow host
- independent examples showing that `CogLang` is not only a private in-project DSL

### 1.6 Minimal Executor Implementations

Prioritize issues such as:

- independent executor implementations that start from `execute(expr)` and `validate(expr)`
- tests showing that host-local query helpers are not required for a valid executor
- documentation that keeps the language executor boundary separate from host bridge convenience APIs

The `CogLangExecutor` ABC is intentionally small. The inheritance requirement is
the semantic minimum: `execute` and `validate`. Optional write-candidate hooks
have safe default behavior, and Python-specific helpers such as
`query_local_write_result`, dict/JSON view helpers, and submission-id lookup
helpers are concrete runtime conveniences, not obligations for every second
implementation.

### 1.7 Specification-Alignment Bug Fixes

These fixes are welcome:

- the implementation differs from the main specification
- the implementation differs from conformance expectations
- the CLI, documentation, and release surface have drifted apart

---

## 2. Contributions That Are Not Current Priorities

The following change types are not priorities at this stage.

### 2.1 Large Expansion of the Language Surface

Examples include:

- adding many new operators at once
- moving long-term program-layer ideas directly into `Core`
- adding syntax sugar quickly to make the language look more general-purpose

The reason is not that these directions are permanently out of scope. The current stage needs more work on:

- stabilizing specification and conformance
- stabilizing the reference implementation and host bridge
- stabilizing the independent trial path and minimal release surface

### 2.2 Moving Roadmap Ideas Directly Into the Main Specification

Roadmap items, boundary notes, and open directions are not automatically language-core commitments.

If a contribution would move the following directly into the main `CogLang` specification body, it is usually not a current priority:

- roadmap ideas
- host-specific protocols
- experimental practices

### 2.3 Writing Reference-Host-Specific Protocols Back Into the Language Core

Avoid turning the following into strong language-core commitments:

- physical details of an application-side persistence backend
- application-side message or task-dispatch protocols
- the full host protocol around `WriteBundle`
- lifecycle objects specific to a reference host

The current goal is to layer the language itself and host protocols separately, not to bind them back together.

### 2.4 Freezing an Extension Call Surface for Ordinary Users

Extension capabilities currently serve implementers and host integrators first.

Without enough cross-host validation, it is risky to present any particular extension-call spelling as stable syntax for ordinary users.

### 2.5 Turning Public Positioning Into Competitive Comparison or Unsupported Marketing

The following changes are not priorities and usually will not be accepted:

- public documents framed as comparison tables claiming that `CogLang` is stronger, simpler, or more suitable than another system
- benchmark-style conclusions without public reproducible evidence
- public value narratives based on internal numbers, internal assumptions, or internal terminology

Public documentation should focus on:

- what this is for
- why these design choices were made
- when it should not be used

In other words: design intent, not competitive claims.

---

## 3. Design Invariants Contributors Should Preserve

The following invariants are useful review shortcuts. They do not replace the
specification, but they describe what maintainers will protect when reviewing
language, documentation, host-boundary, and extension proposals.

### 3.1 Canonical Text Is the Stability Anchor

Canonical M-expression text is the stable language form used for storage,
diffing, replay, conformance, and generated examples.

Contributions should not change canonical serialization, frozen head names, or
Core operator spelling unless the change is explicitly treated as a breaking
language-version change.

Readable rendering can improve, but it must not weaken canonical text as the
authoritative representation.

### 3.2 Errors Remain Values

CogLang errors are expression-level values, not hidden host exceptions.

Contributions should preserve explicit `ErrorExpr` behavior, documented failure
modes, and ordinary propagation rules. Host integrations may wrap or transport
errors, but they should not erase the structured error value that the language
and conformance surface depend on.

### 3.3 Feature Tiers Must Stay Meaningful

`Core`, `Reserved`, and `Experimental` are compatibility tiers, not labels for
marketing convenience.

Contributions should not present an experimental capability as generally
available, move roadmap material straight into `Core`, or bypass the promotion
discipline that connects specification text, implementation behavior,
conformance examples, operator catalog entries, and migration notes.

### 3.4 Core Stays Graph-First

The Core language should remain centered on graph queries, graph updates, rule
objects, observable execution, and auditable host boundaries.

Contributions that mainly serve host-specific workflow, application policy, or
general-purpose programming convenience should usually live in profiles,
examples, adapters, or roadmap notes before they are considered for the Core
specification.

### 3.5 Expression Values Should Stay Inspectable and Serializable

Every ordinary expression value should remain suitable for canonical text,
readable rendering, hashing, diffing, and replay.

Large opaque payloads such as raw binary blobs, tensors, model artifacts, or
media bytes should normally be represented by host-owned references plus
metadata, not embedded directly as expression payloads. This is an extension
design boundary, not a new frozen Core type rule; proposals in this area should
come with clear host-contract, conformance, and security implications.

### 3.6 Executor Interface Stays Minimal

The minimal executor contract should remain small enough for another
implementation to start without copying Python runtime internals.

Contributors should preserve this split:

- `CogLangExecutor`: semantic execution minimum, currently `execute` and `validate`
- optional write-candidate hooks: default no-op or unsupported behavior is acceptable
- `PythonCogLangExecutor`: reference runtime plus local host/write-view convenience helpers
- host-runtime contract: typed envelopes, local views, and cross-view evidence for hosts

Do not move host-local query helpers, dict/JSON variants, or correlation-id
lookup conveniences back into the abstract executor unless there is strong
cross-implementation evidence that they belong in the semantic minimum.
`coglang release-check` includes an `executor_interface` gate to make this
boundary visible before release.

---

## 4. What To Do Before Contributing

Before opening a PR, follow this minimal path:

1. Read [CogLang_Quickstart_v1_1_0.md](./CogLang_Quickstart_v1_1_0.md).
2. Read the relevant section of [CogLang_Specification_v1_1_0_Draft.md](./CogLang_Specification_v1_1_0_Draft.md).
3. Read [CogLang_Conformance_Suite_v1_1_0.md](./CogLang_Conformance_Suite_v1_1_0.md).
4. Read [CogLang_Release_Notes_v1_1_0.md](./CogLang_Release_Notes_v1_1_0.md).
5. Run:

```powershell
coglang bundle
coglang smoke
```

If your change touches the host bridge or runtime contract, also read:

- [CogLang_Host_Runtime_Contract_v0_1.md](./CogLang_Host_Runtime_Contract_v0_1.md)
- [CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md](./CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md)
- [CogLang_HRC_Companion_Asset_Classification_v0_1.md](./CogLang_HRC_Companion_Asset_Classification_v0_1.md)

### 4.1 First External Host or Consumer PR Checklist

For a first host or consumer maintained outside the core runtime, keep the PR
narrow and evidence-first. A good first PR usually adds one minimal adapter,
consumer, or host stub plus deterministic tests. It should not expand the
language, freeze a new host protocol, or present companion schema material as a
normative JSON Schema contract.

Before review, include:

- a short statement of whether the PR is a consumer example, a host stub, or an
  executor implementation
- the language/runtime used and whether the example imports the Python runtime
- the exact HRC asset class being consumed, using the companion asset
  classification document's terms
- the supported envelope or expression subset, plus explicit non-goals
- deterministic fixture or sample data small enough to review in one screen
- tests or commands that fail if correlation IDs, submission IDs, phase counts,
  or error envelopes drift
- no claim that the example extends the frozen HRC v0.2 surface unless a
  separate promotion proposal supplies the required evidence

Run the relevant existing evidence commands before opening the PR:

```powershell
coglang host-demo
coglang reference-host-demo
coglang release-check
```

If the PR is a non-Python consumer, also show the language-native command, such
as the existing Node.js examples:

```powershell
node examples/node_host_consumer/consume_hrc_envelopes.mjs
node examples/node_minimal_host_runtime_stub/run_demo.mjs
```

---

## 5. What Maintainers Will Prioritize

Maintainers currently evaluate contributions with the following questions first.

### 5.1 Does It Make Boundaries Clearer?

A change is usually more valuable when it clarifies the boundaries among:

- language core
- companion documents
- host contract
- roadmap

### 5.2 Does It Strengthen Conformance?

A change usually has high priority if it:

- adds a missing key golden example
- turns drift-prone semantics into a regression surface
- makes it harder for implementation and specification to diverge again

### 5.3 Does It Reduce Hidden Host Coupling?

Welcome changes:

- make host coupling explicit
- stabilize the minimal bridge interface
- help external readers and other host implementers understand the boundary

Unwelcome changes:

- push new host-specific details back into the language core

### 5.4 Does It Avoid Over-Commitment?

`CogLang` is ready for public trial, but it is not a mature standalone platform.

Contributions usually will not be prioritized if they:

- make the documentation sound more mature than the implementation and release surface are
- make roadmap material sound like frozen commitments
- make `Reserved / Experimental` capabilities look available by default

### 5.5 Does It Preserve the Public Design-Intent Narrative?

Maintainers will prioritize public-narrative changes that:

- make the language positioning clearer
- explain design choices and their reasons more clearly
- clarify non-goals and unsuitable scenarios

Maintainers will not prioritize public-narrative changes that:

- make unsupported superiority claims
- invite unnecessary comparison disputes
- move internal benchmarks, internal terminology, or internal hypotheses into public value statements

---

## 6. Best Starting Points for Contributors

If you want a high-value, low-risk place to start, consider:

- adding a missing golden example
- fixing a mismatch between implementation and conformance
- improving the first-run path in README or Quickstart
- improving CLI command discoverability or stable output
- adding a minimal non-reference-host usage example
- tightening ambiguous boundaries in the Host Runtime Contract

---

## 7. One-Sentence Conclusion

`CogLang` welcomes contributions, especially contributions that:

**help it move more reliably from "usable for trial" toward "publicly reusable."**

The highest-value changes are usually not about making the language much larger at once. They are about:

- clarifying boundaries
- pinning behavior down
- completing the tooling surface
- reducing host coupling
- smoothing the external trial path
