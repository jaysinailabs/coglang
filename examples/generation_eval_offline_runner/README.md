# CogLang Generation Eval Offline Runner Example

This directory contains companion example material for the provider-neutral
`generation-eval` request/response workflow.

It is not a model provider integration, a benchmark, or a prompt optimization
loop. The runner uses only the Python standard library and echoes fixture
`reference_expr` values from request records so the response-file contract can
be tested without spending model tokens or importing provider SDKs.

The file contract is defined in
[CogLang_Generation_Eval_Request_Response_Contract_v0_1.md](../../CogLang_Generation_Eval_Request_Response_Contract_v0_1.md).

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
acts as a tiny external runner and writes JSONL response records with
`schema_version`, `case_id`, and `output`. The third command scores those
responses with CogLang's deterministic scorer.

For real model usage, replace `mock_responses.py` with your own runner that
preserves the same response-file shape.

## Constrained Generation Link

The companion grammars in [../grammar](../grammar) can be used by an external
runner before it writes response JSONL:

1. export request records with `coglang generation-eval --export-requests`
2. use a Lark, GBNF, Outlines, llama.cpp, or other grammar-aware runner to
   produce one CogLang M-expression per `case_id`
3. write response records with schema version
   `coglang-generation-eval-response/v0.1`
4. score the response file with `coglang generation-eval --responses-file`

CogLang intentionally keeps that runner outside the core package. The grammar
files reduce malformed output; `parse`, `canonicalize`, `valid_coglang`, and
the deterministic scorer remain the authority.
