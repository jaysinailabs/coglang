# CogLang Generation Eval Offline Runner Example

This directory contains companion example material for the provider-neutral
`generation-eval` request/response workflow.

It is not a model provider integration, a benchmark, or a prompt optimization
loop. The runner uses only the Python standard library and echoes fixture
`reference_expr` values from request records so the response-file contract can
be tested without spending model tokens or importing provider SDKs.

## Contract Smoke

For the shortest path, score the included three-case fixture and static
response file:

```powershell
python -m coglang generation-eval --fixture examples/generation_eval_offline_runner/fixtures/generation_eval_three_case_v0_1.json --responses-file examples/generation_eval_offline_runner/fixtures/mock_responses.jsonl --summary-only
```

This fixture only checks the response-file contract. It is not a replacement
for the default 50-case L1-L3 generation-eval fixture.

## Dry Run

From the repository root:

```powershell
python -m coglang generation-eval --export-requests --request-format jsonl --include-reference > .tmp_generation_eval_requests.jsonl
python examples/generation_eval_offline_runner/mock_responses.py .tmp_generation_eval_requests.jsonl .tmp_generation_eval_responses.jsonl
python -m coglang generation-eval --responses-file .tmp_generation_eval_responses.jsonl --summary-only
```

The first command exports provider-neutral prompt records. The second command
acts as a tiny external runner and writes JSONL response records with `case_id`
and `output`. The third command scores those responses with CogLang's
deterministic scorer.

For real model usage, replace `mock_responses.py` with your own runner that
preserves the same response-file shape.
