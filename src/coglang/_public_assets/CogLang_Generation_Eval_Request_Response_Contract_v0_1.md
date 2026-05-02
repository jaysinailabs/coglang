# CogLang Generation Eval Request/Response Contract v0.1

**Status**: versioned companion contract
**Schema versions**:

- `coglang-generation-eval-request-batch/v0.1`
- `coglang-generation-eval-request/v0.1`
- `coglang-generation-eval-response-batch/v0.1`
- `coglang-generation-eval-response/v0.1`

**Audience**: generation-eval runner authors, evaluation maintainers, and
reviewers
**Purpose**: define the provider-neutral file boundary between CogLang's
deterministic generation scorer and external model runners

---

## 0. Positioning

This contract is a file boundary. CogLang exports prompt records, an external
runner produces response records, and CogLang scores those responses with the
deterministic `generation-eval` scorer.

This contract does not:

- call a model provider
- require OpenAI, Anthropic, Ollama, LangChain, DSPy, Outlines, or any other SDK
- define a benchmark claim
- replace the packaged generation-eval fixture format
- change CogLang language syntax or validation semantics

## 1. Request Batch

When `coglang generation-eval --export-requests --request-format json` is used,
the top-level object has schema version
`coglang-generation-eval-request-batch/v0.1`.

Required top-level fields:

- `schema_version`: must be `coglang-generation-eval-request-batch/v0.1`
- `tool`: `coglang`
- `fixture_schema_version`: schema version of the source fixture
- `fixture_path`: path or package-relative fixture source used by CogLang
- `case_count`: number of request records
- `include_reference`: whether `reference_expr` was included in request records
- `request_record_schema_version`: `coglang-generation-eval-request/v0.1`
- `response_schema_version`: `coglang-generation-eval-response-batch/v0.1`
- `response_record_schema_version`: `coglang-generation-eval-response/v0.1`
- `response_contract`: machine-readable summary of accepted response shape
- `requests`: array of request records

JSONL export omits the batch wrapper and writes one request record per line.

## 2. Request Record

Each request record has schema version
`coglang-generation-eval-request/v0.1`.

Required fields:

- `schema_version`: must be `coglang-generation-eval-request/v0.1`
- `case_id`: stable case identifier from the source fixture
- `level`: maturity level label such as `L1`, `L2`, or `L3`
- `prompt`: natural-language instruction for an external model runner
- `instructions`: output discipline; the runner should return exactly one
  CogLang M-expression
- `expected_top_level_heads`: expected top-level CogLang heads used by the
  deterministic scorer

Optional fields:

- `reference_expr`: included only when `--include-reference` is passed; useful
  for offline contract smoke tests, not for benchmark claims

Example JSONL request record:

```json
{"schema_version":"coglang-generation-eval-request/v0.1","case_id":"L1-001","level":"L1","prompt":"Return a CogLang expression that tests whether 1 equals 1.","instructions":"Return exactly one CogLang M-expression as the output for this case. Do not include Markdown fences, prose, or multiple alternatives.","expected_top_level_heads":["Equal"]}
```

## 3. Response Batch

CogLang accepts response files in three forms:

- JSONL: one response record per line
- JSON list: an array of response records
- JSON object: a batch object with `responses` or `answers`

The preferred JSON object form has schema version
`coglang-generation-eval-response-batch/v0.1`.

Required top-level fields for the preferred batch object:

- `schema_version`: `coglang-generation-eval-response-batch/v0.1`
- `tool`: runner name or integration name
- `responses`: array of response records

Optional top-level fields:

- `provider`
- `model`
- `created_at`
- `metadata`

## 4. Response Record

Each new response record should use schema version
`coglang-generation-eval-response/v0.1`. The loader accepts omitted
`schema_version` for transition compatibility, but rejects any non-matching
explicit value.

Required fields for new runners:

- `schema_version`: `coglang-generation-eval-response/v0.1`
- `case_id`: request `case_id` copied exactly
- one output field: prefer `output`; `text` and `completion` are accepted
  aliases

Optional fields:

- `provider`
- `model`
- `latency_ms`
- `raw_response_id`
- `input_token_count`
- `output_token_count`
- `metadata`

Extra fields are allowed. The deterministic scorer consumes only `case_id` and
the first available output field in this order: `output`, `text`, `completion`.

Example JSONL response record:

```json
{"schema_version":"coglang-generation-eval-response/v0.1","case_id":"L1-001","output":"Equal[1, 1]","provider":"example-runner","model":"local-demo"}
```

## 5. Runner Responsibilities

External runners should:

- preserve each `case_id` exactly
- return exactly one CogLang M-expression in the output field
- avoid Markdown fences, prose, or multiple alternatives
- keep provider credentials, network calls, retry policy, and billing outside
  CogLang
- store any provider-specific metadata in optional or extra fields

CogLang's scorer remains a pure local consumer of response files. It reports
parse, canonicalization, validation, expected-head, hallucinated-operator,
preflight, and maturity summaries without calling the model runner.

## 6. Minimal Flow

```powershell
python -m coglang generation-eval --export-requests --request-format jsonl > .tmp_generation_eval_requests.jsonl
python examples/generation_eval_offline_runner/mock_responses.py .tmp_generation_eval_requests.jsonl .tmp_generation_eval_responses.jsonl
python -m coglang generation-eval --responses-file .tmp_generation_eval_responses.jsonl --summary-only
```

The middle command is only a no-provider smoke runner. Replace it with any
runner that writes records matching this contract.
