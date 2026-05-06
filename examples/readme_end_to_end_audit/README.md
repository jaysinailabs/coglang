# CogLang README End-to-End Audit Demo

This directory contains the small adoption-facing demo referenced from the
README. It shows the shortest useful CogLang path:

1. an external model or runner emits CogLang expression text
2. CogLang parses and canonicalizes it
3. static preflight derives an audit action
4. accepted read-only work executes against an in-memory graph
5. write intent is queued for review instead of being executed

The demo is provider-neutral. It does not import an LLM SDK, make network calls,
submit HRC envelopes, expand HRC v0.2, or define a new protocol.

## Run

From the repository root:

```powershell
python examples/readme_end_to_end_audit/readme_end_to_end_audit.py
```

Expected shape:

- one read-only traced query is allowed and executed
- one write proposal is parsed, hashed, and queued for review
- the JSON output records canonical expression text, expression hash, preflight
  decision, derived audit action, execution result, and trace evidence

This is intentionally a first-contact example, not a host implementation.
