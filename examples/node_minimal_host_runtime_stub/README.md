# Node Minimal Host Runtime Stub

This is an experimental in-repository Node.js standard-library example.

It is not HRC v0.3, not a conformance runtime, not a third-party host, and not a
complete CogLang implementation. It exists to show that non-Python code can do a
little more than read HRC samples: it can validate and execute a tiny expression
subset, consume the existing typed write-envelope shape, and return success and
failure response envelopes without importing the Python runtime.

Run it from the repository root:

```powershell
node examples/node_minimal_host_runtime_stub/run_demo.mjs
```

The demo intentionally stays small:

- `runtime_stub.mjs` supports only `True`, `False`, and simple literal
  `Equal[...]` expressions.
- `host_stub.mjs` supports only a minimal in-memory `create_node` write path and
  explicit failure envelopes for unsupported or invalid submissions.
- `run_demo.mjs` reads the existing
  `internal_schemas/host_runtime/v0.1/examples/write-bundle-submission-message.sample.json`
  sample, submits it, then submits one invalid message.

This example does not change the HRC v0.2 frozen scope. The frozen scope remains
the narrow typed write-envelope surface documented by
`CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md`.
