# Node Host Envelope Consumer

This example is a minimal non-Python consumer for CogLang host-runtime envelope
fixtures. It does not execute CogLang expressions. It shows that a host-side
tool written outside Python can read the HRC schema pack, load the sample
envelopes, and verify the cross-view identity fields that matter for replay and
audit.

Run from the repository root:

```powershell
node examples/node_host_consumer/consume_hrc_envelopes.mjs
```

You can also pass the schema-pack directory directly:

```powershell
node examples/node_host_consumer/consume_hrc_envelopes.mjs internal_schemas/host_runtime/v0.1
```

The script uses only Node standard-library modules. A successful run prints a
JSON summary with `ok: true`, the schema pack id, schema/sample counts, and the
checks that were applied.

## Local npm Scaffold

This directory also includes a private package scaffold for local Node tooling
checks:

```powershell
npm --prefix examples/node_host_consumer test
npm --prefix examples/node_host_consumer run pack:dry
```

The package is intentionally `private: true` and versioned `0.0.0`. It is an
example packaging shell for local validation, not a published npm package, not a
stable JavaScript SDK, and not a second CogLang runtime API.

This is intentionally a consumer demo, not a second runtime implementation. Its
purpose is to keep the HRC envelope surface consumable from a non-Python host
tool while the full multi-host conformance story remains on the roadmap.
