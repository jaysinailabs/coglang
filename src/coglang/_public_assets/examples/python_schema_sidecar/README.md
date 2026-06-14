# CogLang Python Schema Sidecar Companion Example

This directory contains companion example material for validating generated
CogLang-expression events and audit records through a Python schema sidecar.

It is not a Pydantic integration package, fastjsonschema integration package,
hosted runner, provider SDK, stable audit-envelope protocol, benchmark, HRC
transport envelope, or CogLang Core dependency change.

## What It Shows

CogLang Core validates language/runtime semantics:

- parse generated expression text
- canonicalize expression text
- compute a stable expression hash
- validate known operator heads and arity
- estimate effects and required capabilities
- produce a preflight decision

Python schema tools such as Pydantic or fastjsonschema belong around that core
path as host-chosen sidecar validators. This example demonstrates the boundary
without requiring either package:

1. a fixture records generated-expression event envelopes
2. `python_schema_sidecar.py` validates each event envelope with a small
   standard-library demo validator
3. valid envelopes continue into CogLang parse, validation, canonicalization,
   hash, and preflight
4. invalid envelopes are rejected before CogLang parsing
5. the script writes JSONL audit records with validator identity, schema
   version, generated expression, canonical expression, expression hash,
   preflight decision, and derived audit action

The optional `--validator pydantic` and `--validator fastjsonschema` modes show
where host-selected validators would attach when those packages are installed.
They are deliberately not CogLang runtime dependencies.

## Run

From the repository root:

```powershell
python examples/python_schema_sidecar/python_schema_sidecar.py examples/python_schema_sidecar/fixtures/generated_expression_events.jsonl .tmp_python_schema_sidecar_audit.jsonl
```

The summary is printed to stdout. The audit records are written to the output
JSONL path.

Expected fixture behavior:

- a valid read expression is allowed
- a valid write expression is queued for review
- an unknown operator expression passes the event-envelope sidecar but fails
  CogLang validation
- a malformed expression passes the event-envelope sidecar but fails parsing
- a malformed event envelope is rejected before CogLang parsing

## Boundary

This example deliberately stays outside the stable public surface:

- it does not add Pydantic or fastjsonschema to `pyproject.toml`
- it does not replace CogLang validation
- it does not define a stable audit-envelope schema
- it does not add a `coglang` CLI command
- it does not execute expressions against a host
- it does not submit HRC write envelopes
- it does not expand HRC v0.2 frozen scope
- it does not claim production compliance readiness

For production use, keep the same separation: let CogLang produce expression
semantics and preflight evidence, then let the host-selected sidecar validate
application envelopes, audit records, and compliance metadata.
