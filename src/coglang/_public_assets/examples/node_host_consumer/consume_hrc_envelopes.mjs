import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function valueAt(payload, dottedPath) {
  return dottedPath.split(".").reduce((current, segment) => {
    if (current === undefined || current === null) {
      return undefined;
    }
    return current[segment];
  }, payload);
}

function assertEqual(actual, expected, label) {
  assert(actual === expected, `${label}: expected ${expected}, got ${actual}`);
}

function resolveSchemaDir() {
  const input = process.argv[2]
    ? path.resolve(process.argv[2])
    : path.resolve(scriptDir, "..", "..");
  if (fs.existsSync(path.join(input, "schema-pack.json"))) {
    return input;
  }
  return path.join(input, "internal_schemas", "host_runtime", "v0.1");
}

function loadSamples(schemaDir, pack) {
  const samples = new Map();
  for (const entry of pack.samples) {
    const samplePath = path.join(schemaDir, entry.file);
    assert(fs.existsSync(samplePath), `missing sample: ${entry.file}`);
    samples.set(entry.name, readJson(samplePath));
  }
  return samples;
}

function checkSchemaPack(schemaDir, pack, checks) {
  assert(pack.pack_id === "urn:coglang:host-runtime-schema-pack:v0.1", "unexpected pack_id");
  assert(pack.schema_version === "v0.1", "unexpected schema_version");
  assert(pack.scope === "stable-host-runtime-objects", "unexpected scope");
  assert(pack.reference_rules.schema_ids_match_embedded_ids === true, "schema id rule is disabled");
  assert(pack.schemas.length === 11, "expected 11 schema entries");
  assert(pack.samples.length === 8, "expected 8 sample entries");
  checks.push("schema-pack-header");

  for (const entry of pack.schemas) {
    const schemaPath = path.join(schemaDir, entry.file);
    assert(fs.existsSync(schemaPath), `missing schema: ${entry.file}`);
    const schema = readJson(schemaPath);
    assertEqual(schema.$id, entry.schema_id, `${entry.name} schema_id`);
    assert(schema.type === "object", `${entry.name} must be an object schema`);
  }
  checks.push("schema-files-and-ids");

  for (const entry of pack.samples) {
    const samplePath = path.join(schemaDir, entry.file);
    assert(fs.existsSync(samplePath), `missing sample: ${entry.file}`);
    assert(entry.file.startsWith("examples/"), `sample must be under examples/: ${entry.file}`);
  }
  checks.push("sample-files");
}

function checkSubmissionAndResponses(samples, checks) {
  const submission = samples.get("write-bundle-submission-message");
  const success = samples.get("write-bundle-response-message.success");
  const failure = samples.get("write-bundle-response-message.error");

  assertEqual(submission.header.message_type, "KnowledgeMessage", "submission message_type");
  assertEqual(submission.header.operation, "submit_write_bundle", "submission operation");
  assertEqual(success.header.message_type, "KnowledgeMessage", "success message_type");
  assertEqual(success.header.operation, "write_bundle_response", "success operation");
  assertEqual(success.header.payload_kind, "WriteResult", "success payload kind");
  assertEqual(failure.header.payload_kind, "ErrorReport", "error payload kind");

  for (const field of ["correlation_id", "submission_id"]) {
    assertEqual(success.header[field], submission.header[field], `success/header ${field}`);
    assertEqual(success.payload[field], success.header[field], `success/payload ${field}`);
    assertEqual(failure.payload[field], failure.header[field], `error/payload ${field}`);
  }
  assert(failure.payload.retryable === false, "error report retryable must stay explicit");
  checks.push("submission-response-envelopes");
}

function checkLocalViews(samples, checks) {
  const success = samples.get("write-bundle-response-message.success");
  const header = samples.get("local-write-header");
  const record = samples.get("local-write-submission-record");
  const query = samples.get("local-write-query-result");
  const trace = samples.get("local-write-trace");
  const summary = samples.get("local-host-summary");

  for (const field of ["correlation_id", "submission_id"]) {
    assertEqual(header[field], success.header[field], `header ${field}`);
    assertEqual(record[field], success.header[field], `record ${field}`);
    assertEqual(trace[field], success.header[field], `trace ${field}`);
  }
  assertEqual(header.status, "committed", "header status");
  assertEqual(record.status, "committed", "record status");
  assertEqual(query.status, "committed", "query status");

  for (const fieldPath of [
    "request.header.correlation_id",
    "request.header.submission_id",
    "response.header.correlation_id",
    "response.header.submission_id",
    "response.payload.correlation_id",
    "response.payload.submission_id",
  ]) {
    assertEqual(valueAt(record, fieldPath), valueAt(trace.record, fieldPath), `trace.record ${fieldPath}`);
  }
  assertEqual(query.record.submission_id, record.submission_id, "query record submission_id");
  assertEqual(trace.query_result.record.submission_id, record.submission_id, "trace query record submission_id");
  assertEqual(summary.response_count, 1, "summary response_count");
  assertEqual(summary.trace_count, 1, "summary trace_count");
  checks.push("local-view-consistency");
}

function main() {
  const schemaDir = resolveSchemaDir();
  const packPath = path.join(schemaDir, "schema-pack.json");
  assert(fs.existsSync(packPath), `schema-pack.json not found under ${schemaDir}`);
  const pack = readJson(packPath);
  const checks = [];

  checkSchemaPack(schemaDir, pack, checks);
  const samples = loadSamples(schemaDir, pack);
  checkSubmissionAndResponses(samples, checks);
  checkLocalViews(samples, checks);

  return {
    schema_version: "coglang-node-host-consumer-demo/v0.1",
    ok: true,
    runtime: "node",
    schema_pack: pack.pack_id,
    schema_dir: schemaDir,
    schema_count: pack.schemas.length,
    sample_count: pack.samples.length,
    checks,
  };
}

try {
  console.log(JSON.stringify(main(), null, 2));
} catch (error) {
  console.error(JSON.stringify({
    schema_version: "coglang-node-host-consumer-demo/v0.1",
    ok: false,
    runtime: "node",
    error: error instanceof Error ? error.message : String(error),
  }, null, 2));
  process.exitCode = 1;
}
