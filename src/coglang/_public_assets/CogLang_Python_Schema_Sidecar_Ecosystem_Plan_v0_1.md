# CogLang Python Schema Sidecar Ecosystem Plan v0.1

Status: public ecosystem participation plan
Audience: CogLang maintainers, Python adapter authors, compliance-sidecar builders, and reviewers
Authority: planning and routing only; stable language semantics, tests, release-check, and release notes remain authoritative
Scope: describes how CogLang can work with Pydantic, fastjsonschema, and adjacent Python schema-validation tools without adding those dependencies to CogLang Core

CogLang can participate in the Python schema-validation ecosystem without
turning the core language/runtime into a Python schema framework.

The intended separation is:

- CogLang Core owns expression parsing, canonical expression text, expression
  hashing, operator inventory, arity, special forms, effects, host capability
  boundaries, and preflight decisions.
- A Python sidecar owns generated-event envelopes, audit-record envelopes, host
  policy configuration, compliance metadata, validator-specific performance
  choices, and application-specific schema guarantees.

This keeps CogLang portable while still making it easy to adopt in Python
compliance and audit pipelines.

## Boundary

Do not add Pydantic, fastjsonschema, jsonschema, OpenAPI, Avro, protobuf, or
policy-engine dependencies to CogLang Core merely to satisfy a sidecar
integration need.

These tools are appropriate at the adapter layer when a host wants Python-native
typed models, compiled JSON Schema validation, or application-specific schema
contracts.

Core participation should expose stable facts that sidecars can validate around:

- generated expression text
- canonical expression text
- stable expression hash
- parse, validation, and preflight status
- effects and required capabilities
- audit action such as allow, reject, or queue for review
- replay and correlation metadata

## Participation Modes

1. Documentation guidance
   - Name Pydantic and fastjsonschema as sidecar-layer options.
   - Keep the core dependency boundary explicit.
   - Explain which checks belong to CogLang and which belong to a host adapter.

2. Companion examples
   - Provide small no-provider examples that show CogLang audit records wrapped
     by Python schema validation.
   - Keep optional validator dependencies outside the main package dependency
     set.
   - Use fixtures rather than production data.

3. Schema packs
   - If examples receive external feedback, promote repeated envelope shapes
     into companion JSON Schema files.
   - Treat those schemas as adapter contracts unless a later release explicitly
     promotes them.

4. Optional adapter packages
   - Consider separate packages such as `coglang-pydantic`,
     `coglang-fastjsonschema`, or `coglang-sidecar-schemas` only after repeated
     external demand.
   - These packages may carry ecosystem dependencies and independent release
     rhythms.

5. Replay and benchmark fixtures
   - Compare sidecar validation strategies with deterministic replay inputs.
   - Report throughput and error-category quality separately.
   - Do not use benchmark results to claim production adoption.

## Short-Term Plan

Deliver a companion example named `examples/python_schema_sidecar`.

The example should:

- demonstrate an adapter envelope around CogLang-generated audit evidence
- keep Pydantic and fastjsonschema optional and outside Core dependencies
- show where a host-chosen validator would validate incoming events and audit
  records
- emit JSONL records with validator identity, schema version, parse/validation
  state, preflight result, audit action, and replay hash
- include one malformed envelope case to show schema-sidecar rejection before
  CogLang parsing
- include one unknown-operator case to show CogLang validation rejection after
  envelope validation
- be covered by focused tests
- be included in public-assets/package-data machinery if it is public

Completion criteria:

- The example runs with the standard CogLang test environment.
- `pyproject.toml` runtime dependencies remain unchanged.
- Tests verify the Core dependency boundary and the sidecar output shape.
- `coglang release-check --format text` can see the example as public companion
  evidence.

## Medium-Term Plan

If the short-term example receives useful external feedback:

- add a larger replay fixture with dozens or hundreds of generated-expression
  events
- add explicit error-category summaries for envelope failures, parse failures,
  validator failures, preflight rejections, and human-review queues
- define a companion audit-envelope JSON Schema only for repeated fields that
  prove stable across examples
- document Pydantic and fastjsonschema adapter recipes in the example README or
  a companion adapter note
- request sanitized adapter patterns from external reviewers and convert them
  into fixtures only after permission

Exit criteria for medium-term promotion:

- at least two independent adapter-style use cases exercise the same envelope
  fields
- release-check and public-assets stay green
- the language specification and HRC freeze scope remain unchanged

## Long-Term Plan

Only after repeated external demand, consider one of these options:

- an optional `coglang-pydantic` package for Python-native typed models
- an optional `coglang-fastjsonschema` package for compiled JSON Schema
  validation around audit envelopes
- a `coglang-sidecar-schemas` package containing companion schemas without
  validator dependencies
- a replay benchmark suite that compares validators without tying CogLang Core
  to any one implementation

Long-term promotion requires:

- a clear owner for adapter package maintenance
- independent versioning from the stable language line
- explicit non-Core status
- documented compatibility and deprecation rules
- evidence that the adapter reduces adoption friction without expanding
  CogLang's language semantics

## Non-Goals

- Do not replace CogLang's validator with Pydantic or JSON Schema.
- Do not make Pydantic or fastjsonschema required CogLang runtime dependencies.
- Do not claim compliance readiness from a companion example.
- Do not present optional Python adapters as cross-language host contracts.
- Do not expand HRC v0.2 or stable `v1.1.0` semantics through this work.
- Do not add provider SDKs or production data to the examples.
