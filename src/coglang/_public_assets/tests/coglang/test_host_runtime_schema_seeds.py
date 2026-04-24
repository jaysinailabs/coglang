import json
from pathlib import Path

from coglang.local_host import LocalHostSummary
from coglang.write_bundle import (
    ErrorReport,
    LocalWriteHeader,
    LocalWriteQueryResult,
    LocalWriteSubmissionRecord,
    LocalWriteTrace,
    WriteBundleCandidate,
    WriteBundleResponseMessage,
    WriteBundleSubmissionMessage,
    WriteOperation,
    WriteResult,
)


def _resolve_schema_dir() -> Path:
    root = Path(__file__).resolve().parents[2]
    candidates = [
        root / "plans" / "coglang" / "internal_schemas" / "host_runtime" / "v0.1",
        root / "internal_schemas" / "host_runtime" / "v0.1",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


SCHEMA_DIR = _resolve_schema_dir()
EXAMPLES_DIR = SCHEMA_DIR / "examples"
FORMAL_EXPORT_CANDIDATES = {
    "ErrorReport",
    "LocalHostSummary",
    "LocalWriteHeader",
    "WriteBundleResponseMessage",
    "WriteResult",
}
SEED_ONLY_OBJECTS = {
    "LocalWriteQueryResult",
    "LocalWriteSubmissionRecord",
    "LocalWriteTrace",
    "WriteBundleCandidate",
    "WriteBundleSubmissionMessage",
    "WriteOperation",
}
PROMOTION_REASON_BY_NAME = {
    "ErrorReport": "minimal_response_surface",
    "LocalHostSummary": "minimal_summary_surface",
    "LocalWriteHeader": "minimal_response_surface",
    "LocalWriteQueryResult": "aggregate_rebuild_surface",
    "LocalWriteSubmissionRecord": "aggregate_rebuild_surface",
    "LocalWriteTrace": "aggregate_rebuild_surface",
    "WriteBundleCandidate": "request_side_surface",
    "WriteBundleResponseMessage": "minimal_response_surface",
    "WriteBundleSubmissionMessage": "request_side_surface",
    "WriteOperation": "request_side_surface",
    "WriteResult": "minimal_response_surface",
}
CANDIDATE_SURFACE_FIELDS_BY_NAME = {
    "ErrorReport": [
        "correlation_id",
        "submission_id",
        "owner",
        "error_kind",
        "retryable",
        "errors",
    ],
    "LocalHostSummary": [
        "node_count",
        "edge_count",
        "request_count",
        "response_count",
        "submission_record_count",
        "query_result_count",
        "trace_count",
        "status_counts",
    ],
    "LocalWriteHeader": [
        "correlation_id",
        "submission_id",
        "status",
        "payload_kind",
    ],
    "WriteBundleResponseMessage": [
        "header.message_type",
        "header.operation",
        "header.correlation_id",
        "header.submission_id",
        "header.payload_kind",
        "payload",
        "metadata.owner",
    ],
    "WriteResult": [
        "correlation_id",
        "submission_id",
        "owner",
        "commit_timestamp",
        "applied_ops",
    ],
}
SEED_DETAIL_FIELDS_BY_NAME = {
    "WriteBundleResponseMessage": [
        "metadata.additionalProperties",
    ],
    "WriteResult": [
        "phase_counts",
        "touched_node_ids",
        "touched_edge_refs",
    ],
}


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def _load_example(name: str) -> dict:
    return json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))


def _assert_required_keys(schema: dict, payload: dict) -> None:
    for key in schema["required"]:
        assert key in payload


def _assert_schema_path_exists(schema: dict, path: str) -> None:
    current = schema
    for segment in path.split("."):
        if segment == "additionalProperties":
            assert segment in current
            current = current[segment]
            continue
        assert "properties" in current
        assert segment in current["properties"]
        current = current["properties"][segment]


def _sample_submission_message() -> WriteBundleSubmissionMessage:
    candidate = WriteBundleCandidate(
        owner="tester",
        base_node_ids=set(),
        operations=[
            WriteOperation(
                op="create_node",
                payload={
                    "node_id": "node-1",
                    "node_type": "Entity",
                    "attrs": {"name": "Tesla"},
                },
            )
        ],
    )
    return WriteBundleSubmissionMessage(
        correlation_id="corr-1",
        submission_id="sub-1",
        candidate=candidate,
    )


def _sample_success_response() -> WriteBundleResponseMessage:
    return WriteBundleResponseMessage(
        correlation_id="corr-1",
        submission_id="sub-1",
        owner="tester",
        payload=WriteResult(
            correlation_id="corr-1",
            submission_id="sub-1",
            owner="tester",
            commit_timestamp="2026-04-18T00:00:00Z",
            applied_ops=1,
        ),
    )


def _sample_error_response() -> WriteBundleResponseMessage:
    return WriteBundleResponseMessage(
        correlation_id="corr-2",
        submission_id="sub-2",
        owner="tester",
        payload=ErrorReport(
            correlation_id="corr-2",
            submission_id="sub-2",
            owner="tester",
            error_kind="ValidationError",
            retryable=False,
            errors=["bad payload"],
        ),
    )


def _sample_record() -> LocalWriteSubmissionRecord:
    return LocalWriteSubmissionRecord(
        correlation_id="corr-1",
        submission_id="sub-1",
        request=_sample_submission_message(),
        response=_sample_success_response(),
        status="committed",
    )


def _sample_query_result() -> LocalWriteQueryResult:
    return LocalWriteQueryResult(
        correlation_id="corr-1",
        status="committed",
        response=_sample_success_response(),
        record=_sample_record(),
    )


def _sample_trace() -> LocalWriteTrace:
    return LocalWriteTrace(
        correlation_id="corr-1",
        submission_id="sub-1",
        request=_sample_submission_message(),
        response=_sample_success_response(),
        record=_sample_record(),
        query_result=_sample_query_result(),
    )


def test_host_runtime_schema_seed_files_are_valid_json():
    schema_files = sorted(SCHEMA_DIR.glob("*.schema.json"))

    assert [path.name for path in schema_files] == [
        "error-report.schema.json",
        "local-host-summary.schema.json",
        "local-write-header.schema.json",
        "local-write-query-result.schema.json",
        "local-write-submission-record.schema.json",
        "local-write-trace.schema.json",
        "write-bundle-candidate.schema.json",
        "write-bundle-response-message.schema.json",
        "write-bundle-submission-message.schema.json",
        "write-operation.schema.json",
        "write-result.schema.json",
    ]

    schema_ids: set[str] = set()
    for path in schema_files:
        schema = json.loads(path.read_text(encoding="utf-8"))
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["$id"].startswith("urn:coglang:host-runtime:v0.1:")
        assert schema["$id"] not in schema_ids
        assert schema["title"]
        assert schema["type"] == "object"
        schema_ids.add(schema["$id"])


def test_host_runtime_schema_pack_index_matches_files():
    pack = json.loads((SCHEMA_DIR / "schema-pack.json").read_text(encoding="utf-8"))

    assert pack["pack_id"] == "urn:coglang:host-runtime-schema-pack:v0.1"
    assert pack["status"] == "internal-seed"
    assert pack["schema_version"] == "v0.1"
    assert pack["scope"] == "stable-host-runtime-objects"
    assert pack["v0_2_position"] == {
        "recommended_companion": True,
        "freeze_blocker": False,
        "formal_export_required": False,
    }
    assert pack["reference_rules"] == {
        "sample_files_relative_to_pack_root": True,
        "sample_files_under_examples_dir": True,
        "schema_files_relative_to_pack_root": True,
        "schema_ids_match_embedded_ids": True,
    }
    assert pack["versioning_rules"] == {
        "breaking_changes_require_new_pack_version": True,
        "existing_schema_files_stable_within_pack": True,
        "existing_schema_ids_stable_within_pack": True,
        "sample_files_are_illustrative_not_normative": True,
    }
    assert pack["promotion_rules"] == {
        "candidate_track_does_not_imply_public_export": True,
        "candidate_track_targets_minimal_response_or_summary_objects": True,
        "request_side_and_rebuild_objects_remain_seed_only_in_v0_1": True,
    }
    assert pack["candidate_field_rules"] == {
        "fields_describe_minimal_future_surface_only": True,
        "unlisted_fields_remain_seed_detail_in_v0_1": True,
        "envelope_fields_may_reference_other_candidate_objects": True,
    }
    assert pack["candidate_detail_rules"] == {
        "write_result_audit_fields_remain_seed_detail_in_v0_1": True,
        "response_metadata_extensions_remain_seed_detail_in_v0_1": True,
    }

    schema_files = {path.name for path in SCHEMA_DIR.glob("*.schema.json")}
    sample_files = {
        str(path.relative_to(SCHEMA_DIR)).replace("\\", "/")
        for path in EXAMPLES_DIR.glob("*.json")
    }
    assert {entry["file"] for entry in pack["schemas"]} == schema_files
    assert {entry["file"] for entry in pack["samples"]} == sample_files

    schema_names = [entry["name"] for entry in pack["schemas"]]
    sample_names = [entry["name"] for entry in pack["samples"]]
    assert len(schema_names) == len(set(schema_names))
    assert len(sample_names) == len(set(sample_names))

    candidate_names = {
        entry["name"]
        for entry in pack["schemas"]
        if entry["promotion_track"] == "candidate"
    }
    seed_only_names = {
        entry["name"]
        for entry in pack["schemas"]
        if entry["promotion_track"] == "seed_only"
    }
    assert candidate_names == FORMAL_EXPORT_CANDIDATES
    assert seed_only_names == SEED_ONLY_OBJECTS
    assert candidate_names | seed_only_names == set(schema_names)

    schema_id_by_name = {entry["name"]: entry["schema_id"] for entry in pack["schemas"]}
    for entry in pack["schemas"]:
        schema = _load_schema(entry["file"])
        assert entry["file"].endswith(".schema.json")
        assert entry["schema_id"] == schema["$id"]
        assert entry["stability"] == "seed"
        assert entry["promotion_track"] in {"candidate", "seed_only"}
        assert entry["promotion_reason"] == PROMOTION_REASON_BY_NAME[entry["name"]]
        if entry["promotion_track"] == "candidate":
            assert entry["candidate_surface_fields"] == CANDIDATE_SURFACE_FIELDS_BY_NAME[entry["name"]]
            for path in entry["candidate_surface_fields"]:
                _assert_schema_path_exists(schema, path)
            assert entry.get("seed_detail_fields", []) == SEED_DETAIL_FIELDS_BY_NAME.get(entry["name"], [])
            for path in entry.get("seed_detail_fields", []):
                _assert_schema_path_exists(schema, path)
        else:
            assert "candidate_surface_fields" not in entry
            assert "seed_detail_fields" not in entry

    for entry in pack["samples"]:
        assert entry["file"].startswith("examples/")
        assert entry["file"].endswith(".json")
        for match in entry["matches"]:
            assert match in schema_id_by_name


def test_local_write_header_schema_seed_matches_sample_payload():
    schema = _load_schema("local-write-header.schema.json")
    payload = LocalWriteHeader(
        correlation_id="corr-1",
        submission_id="sub-1",
        status="committed",
        payload_kind="WriteResult",
    ).to_dict()

    _assert_required_keys(schema, payload)
    assert payload["status"] in schema["properties"]["status"]["enum"]
    assert payload["payload_kind"] in schema["properties"]["payload_kind"]["enum"]


def test_write_result_and_error_report_schema_seeds_match_sample_payloads():
    write_result_schema = _load_schema("write-result.schema.json")
    error_report_schema = _load_schema("error-report.schema.json")

    write_result = WriteResult(
        correlation_id="corr-1",
        submission_id="sub-1",
        owner="tester",
        commit_timestamp="2026-04-18T00:00:00Z",
        applied_ops=1,
        phase_counts={"phase_1a_create_nodes": 1},
        touched_node_ids=["node-1"],
        touched_edge_refs=[{"edge_id": "edge-1"}],
    ).to_dict()
    error_report = ErrorReport(
        correlation_id="corr-2",
        submission_id="sub-2",
        owner="tester",
        error_kind="ValidationError",
        retryable=False,
        errors=["bad payload"],
    ).to_dict()

    _assert_required_keys(write_result_schema, write_result)
    _assert_required_keys(error_report_schema, error_report)
    assert write_result["applied_ops"] >= write_result_schema["properties"]["applied_ops"]["minimum"]
    assert isinstance(error_report["retryable"], bool)


def test_write_bundle_response_message_schema_seed_matches_sample_payloads():
    schema = _load_schema("write-bundle-response-message.schema.json")
    write_result_response = _sample_success_response().to_dict()
    error_report_response = _sample_error_response().to_dict()

    for payload in [write_result_response, error_report_response]:
        _assert_required_keys(schema, payload)
        _assert_required_keys(schema["properties"]["header"], payload["header"])
        _assert_required_keys(schema["properties"]["metadata"], payload["metadata"])
        assert (
            payload["header"]["message_type"]
            == schema["properties"]["header"]["properties"]["message_type"]["const"]
        )
        assert (
            payload["header"]["operation"]
            == schema["properties"]["header"]["properties"]["operation"]["const"]
        )
        assert (
            payload["header"]["payload_kind"]
            in schema["properties"]["header"]["properties"]["payload_kind"]["enum"]
        )


def test_write_bundle_submission_message_schema_seed_matches_sample_payload():
    schema = _load_schema("write-bundle-submission-message.schema.json")
    candidate_schema = _load_schema("write-bundle-candidate.schema.json")
    payload = _sample_submission_message().to_dict()

    _assert_required_keys(schema, payload)
    _assert_required_keys(schema["properties"]["header"], payload["header"])
    _assert_required_keys(schema["properties"]["payload"], payload["payload"])
    _assert_required_keys(candidate_schema, payload["payload"]["candidate"])
    _assert_required_keys(
        schema["properties"]["payload"]["properties"]["commit_plan"],
        payload["payload"]["commit_plan"],
    )
    assert (
        payload["header"]["message_type"]
        == schema["properties"]["header"]["properties"]["message_type"]["const"]
    )
    assert (
        payload["header"]["operation"]
        == schema["properties"]["header"]["properties"]["operation"]["const"]
    )


def test_record_query_result_and_trace_schema_seeds_match_sample_payloads():
    record = _sample_record()
    query_result = _sample_query_result()
    trace = _sample_trace()

    record_schema = _load_schema("local-write-submission-record.schema.json")
    query_result_schema = _load_schema("local-write-query-result.schema.json")
    trace_schema = _load_schema("local-write-trace.schema.json")

    record_payload = record.to_dict()
    query_result_payload = query_result.to_dict()
    trace_payload = trace.to_dict()

    _assert_required_keys(record_schema, record_payload)
    _assert_required_keys(query_result_schema, query_result_payload)
    _assert_required_keys(trace_schema, trace_payload)
    assert record_payload["status"] in record_schema["properties"]["status"]["enum"]
    assert (
        query_result_payload["status"]
        in query_result_schema["properties"]["status"]["enum"]
    )
    assert trace_payload["submission_id"] == query_result_payload["submission_id"]
    assert query_result_payload["record"]["submission_id"] == record_payload["submission_id"]
    assert trace_payload["record"]["correlation_id"] == record_payload["correlation_id"]


def test_local_host_summary_schema_seed_matches_sample_payload():
    schema = _load_schema("local-host-summary.schema.json")
    payload = LocalHostSummary(
        node_count=1,
        edge_count=0,
        request_count=1,
        response_count=1,
        submission_record_count=1,
        query_result_count=1,
        trace_count=1,
        status_counts={"committed": 1},
    ).to_dict()

    _assert_required_keys(schema, payload)
    for key in schema["required"]:
        if key == "status_counts":
            continue
        assert payload[key] >= schema["properties"][key]["minimum"]


def test_host_runtime_schema_examples_match_sample_payloads():
    assert _load_example("local-write-header.sample.json") == LocalWriteHeader(
        correlation_id="corr-1",
        submission_id="sub-1",
        status="committed",
        payload_kind="WriteResult",
    ).to_dict()
    assert _load_example("write-bundle-submission-message.sample.json") == _sample_submission_message().to_dict()
    assert _load_example("write-bundle-response-message.success.sample.json") == _sample_success_response().to_dict()
    assert _load_example("write-bundle-response-message.error.sample.json") == _sample_error_response().to_dict()
    assert _load_example("local-write-submission-record.sample.json") == _sample_record().to_dict()
    assert _load_example("local-write-query-result.sample.json") == _sample_query_result().to_dict()
    assert _load_example("local-write-trace.sample.json") == _sample_trace().to_dict()
    assert _load_example("local-host-summary.sample.json") == LocalHostSummary(
        node_count=1,
        edge_count=0,
        request_count=1,
        response_count=1,
        submission_record_count=1,
        query_result_count=1,
        trace_count=1,
        status_counts={"committed": 1},
    ).to_dict()


def test_host_runtime_schema_examples_roundtrip_through_typed_objects():
    assert LocalWriteHeader.from_dict(_load_example("local-write-header.sample.json")).to_dict() == _load_example("local-write-header.sample.json")
    assert WriteBundleSubmissionMessage.from_dict(_load_example("write-bundle-submission-message.sample.json")).to_dict() == _load_example("write-bundle-submission-message.sample.json")
    assert WriteBundleResponseMessage.from_dict(_load_example("write-bundle-response-message.success.sample.json")).to_dict() == _load_example("write-bundle-response-message.success.sample.json")
    assert WriteBundleResponseMessage.from_dict(_load_example("write-bundle-response-message.error.sample.json")).to_dict() == _load_example("write-bundle-response-message.error.sample.json")
    assert LocalWriteSubmissionRecord.from_dict(_load_example("local-write-submission-record.sample.json")).to_dict() == _load_example("local-write-submission-record.sample.json")
    assert LocalWriteQueryResult.from_dict(_load_example("local-write-query-result.sample.json")).to_dict() == _load_example("local-write-query-result.sample.json")
    assert LocalWriteTrace.from_dict(_load_example("local-write-trace.sample.json")).to_dict() == _load_example("local-write-trace.sample.json")
    assert LocalHostSummary.from_dict(_load_example("local-host-summary.sample.json")).to_dict() == _load_example("local-host-summary.sample.json")
