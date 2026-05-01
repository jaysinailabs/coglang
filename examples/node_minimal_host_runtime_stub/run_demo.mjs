import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { createMinimalHost } from "./host_stub.mjs";
import { execute, validate } from "./runtime_stub.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function resolveRepoRoot() {
  return path.resolve(scriptDir, "..", "..");
}

function sampleSubmissionPath(repoRoot) {
  return path.join(
    repoRoot,
    "internal_schemas",
    "host_runtime",
    "v0.1",
    "examples",
    "write-bundle-submission-message.sample.json",
  );
}

function invalidSubmissionFrom(message) {
  return {
    ...message,
    header: {
      ...message.header,
      correlation_id: "corr-node-stub-error",
      submission_id: "sub-node-stub-error",
    },
    payload: {
      candidate: {
        ...message.payload.candidate,
        operations: [
          {
            op: "unsupported_write",
            payload: {
              id: "node-unsupported",
            },
          },
        ],
      },
      commit_plan: {},
    },
  };
}

function runDemo() {
  const repoRoot = resolveRepoRoot();
  const submission = readJson(sampleSubmissionPath(repoRoot));
  const runtimeValidation = validate("Equal[1, 1]");
  const runtimeExecution = execute("Equal[1, 1]");
  const unsupportedExecution = execute("Traverse[\"node-1\", \"knows\"]");
  const host = createMinimalHost();

  assert(runtimeValidation.ok === true, "runtime validation should pass");
  assert(runtimeExecution.ok === true, "runtime execution should pass");
  assert(runtimeExecution.value === true, "runtime Equal[1, 1] should return true");
  assert(unsupportedExecution.ok === false, "unsupported expression should be explicit");

  const successResponse = host.submitMessage(submission);
  const failureResponse = host.submitMessage(invalidSubmissionFrom(submission));
  const successHeader = host.localWriteHeader(submission.header.correlation_id);
  const failureHeader = host.localWriteHeader("corr-node-stub-error");
  const missingHeader = host.localWriteHeader("corr-node-stub-missing");

  assert(successResponse.header.payload_kind === "WriteResult", "success payload kind");
  assert(failureResponse.header.payload_kind === "ErrorReport", "failure payload kind");
  assert(successHeader.status === "committed", "success local status");
  assert(failureHeader.status === "failed", "failure local status");
  assert(missingHeader.status === "not_found", "missing local status");
  assert(
    successResponse.header.correlation_id === submission.header.correlation_id,
    "success preserves correlation_id",
  );
  assert(
    successResponse.header.submission_id === submission.header.submission_id,
    "success preserves submission_id",
  );
  assert(
    successResponse.metadata.owner === submission.metadata.owner,
    "success preserves owner",
  );

  return {
    schema_version: "coglang-node-minimal-host-runtime-stub-demo/v0.1",
    ok: true,
    runtime: "node",
    example_kind: "experimental-in-repository-stub",
    hrc_scope: "post-freeze-example-only",
    hrc_contract_expanded: false,
    checks: [
      "runtime-validate-execute",
      "submission-envelope-read",
      "success-write-result-envelope",
      "failure-error-report-envelope",
      "identity-preservation",
      "local-write-header",
    ],
    runtime_checks: {
      validate_ok: runtimeValidation.ok,
      execute_value: runtimeExecution.value,
      unsupported_error_kind: unsupportedExecution.error_kind,
    },
    success_response: successResponse,
    failure_response: failureResponse,
    local_headers: {
      success: successHeader,
      failure: failureHeader,
      missing: missingHeader,
    },
    graph_state: host.exportState(),
  };
}

try {
  console.log(JSON.stringify(runDemo(), null, 2));
} catch (error) {
  console.error(JSON.stringify({
    schema_version: "coglang-node-minimal-host-runtime-stub-demo/v0.1",
    ok: false,
    runtime: "node",
    error: error instanceof Error ? error.message : String(error),
  }, null, 2));
  process.exitCode = 1;
}
