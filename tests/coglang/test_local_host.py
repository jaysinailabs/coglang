import json

import networkx as nx

from logos.coglang.local_host import (
    LocalCogLangHost,
    LocalHostSnapshot,
    LocalHostSummary,
    LocalHostTrace,
)
from logos.coglang.parser import CogLangExpr
from logos.coglang.write_bundle import (
    ErrorReport,
    LocalWriteHeader,
    LocalWriteQueryResult,
    LocalWriteSubmissionRecord,
    LocalWriteTrace,
    WriteBundleCandidate,
    WriteBundleResponseMessage,
    WriteBundleSubmissionMessage,
    WriteOperation,
)


def test_local_host_executes_string_expression():
    host = LocalCogLangHost(nx.DiGraph())

    result = host.execute('Equal[1, 1]')

    assert result == CogLangExpr("True", ())


def test_local_host_submit_candidate_and_query_result():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    result, candidate = source_host.execute_with_candidate('Create["Entity", {"name": "Tesla"}]')

    assert isinstance(result, str)
    assert candidate is not None

    response = target_host.submit_candidate(candidate, correlation_id="corr-local-host-1")

    assert response is not None
    assert isinstance(response.payload.to_dict(), dict)
    query_result = target_host.query_write("corr-local-host-1")
    assert query_result.status == "committed"
    assert query_result.submission_id == response.submission_id
    assert target_host.query_write_status("corr-local-host-1") == "committed"
    assert target_host.query_write_status("missing-correlation-id") == "not_found"
    assert target_host.query_write_payload_kind("corr-local-host-1") == "WriteResult"
    assert target_host.query_write_payload_kind("missing-correlation-id") is None
    typed_header = target_host.query_write_header("corr-local-host-1")
    assert isinstance(typed_header, LocalWriteHeader)
    assert typed_header.correlation_id == "corr-local-host-1"
    assert typed_header.submission_id == response.submission_id
    assert typed_header.status == "committed"
    assert typed_header.payload_kind == "WriteResult"
    assert LocalWriteHeader.from_json(typed_header.to_json()).to_dict() == typed_header.to_dict()
    header = target_host.query_write_header_dict("corr-local-host-1")
    assert header["correlation_id"] == "corr-local-host-1"
    assert header["submission_id"] == response.submission_id
    assert header["status"] == "committed"
    assert header["payload_kind"] == "WriteResult"
    missing_header = target_host.query_write_header_dict("missing-correlation-id")
    assert missing_header["correlation_id"] == "missing-correlation-id"
    assert missing_header["submission_id"] is None
    assert missing_header["status"] == "not_found"
    assert missing_header["payload_kind"] is None
    by_submission = target_host.query_write_by_submission_id(response.submission_id)
    assert by_submission.status == "committed"
    assert by_submission.correlation_id == "corr-local-host-1"
    assert (
        target_host.query_write_status_by_submission_id(response.submission_id)
        == "committed"
    )
    assert (
        target_host.query_write_payload_kind_by_submission_id(response.submission_id)
        == "WriteResult"
    )
    assert (
        target_host.query_write_payload_kind_by_submission_id("missing-submission-id")
        is None
    )
    typed_header_by_submission = target_host.query_write_header_by_submission_id(
        response.submission_id
    )
    assert typed_header_by_submission.correlation_id == "corr-local-host-1"
    assert typed_header_by_submission.submission_id == response.submission_id
    assert typed_header_by_submission.status == "committed"
    header_by_submission = target_host.query_write_header_dict_by_submission_id(
        response.submission_id
    )
    assert header_by_submission["correlation_id"] == "corr-local-host-1"
    assert header_by_submission["submission_id"] == response.submission_id
    assert header_by_submission["status"] == "committed"
    assert header_by_submission["payload_kind"] == "WriteResult"
    missing_header_by_submission = target_host.query_write_header_dict_by_submission_id(
        "missing-submission-id"
    )
    assert missing_header_by_submission["correlation_id"] == ""
    assert missing_header_by_submission["submission_id"] == "missing-submission-id"
    assert missing_header_by_submission["status"] == "not_found"
    assert missing_header_by_submission["payload_kind"] is None
    typed_missing_header = target_host.query_write_header_by_submission_id(
        "missing-submission-id"
    )
    assert typed_missing_header.correlation_id == ""
    assert typed_missing_header.submission_id == "missing-submission-id"
    assert typed_missing_header.status == "not_found"
    assert typed_missing_header.payload_kind is None
    assert (
        target_host.query_write_status_by_submission_id("missing-submission-id")
        == "not_found"
    )
    missing_by_submission = target_host.query_write_by_submission_id("missing-submission-id")
    assert missing_by_submission.status == "not_found"
    assert missing_by_submission.submission_id == "missing-submission-id"
    assert missing_by_submission.correlation_id == ""
    query_dict = target_host.query_write_dict("corr-local-host-1")
    assert query_dict["status"] == "committed"
    assert LocalWriteQueryResult.from_json(query_result.to_json()).to_dict() == query_result.to_dict()
    query_json = target_host.query_write_json("corr-local-host-1")
    query_from_json = json.loads(query_json)
    assert query_from_json["status"] == "committed"
    header_json = target_host.query_write_header_json("corr-local-host-1")
    header_from_json = json.loads(header_json)
    assert header_from_json["correlation_id"] == "corr-local-host-1"
    assert header_from_json["submission_id"] == response.submission_id
    by_submission_dict = target_host.query_write_dict_by_submission_id(response.submission_id)
    assert by_submission_dict["correlation_id"] == "corr-local-host-1"
    by_submission_json = target_host.query_write_json_by_submission_id(response.submission_id)
    by_submission_from_json = json.loads(by_submission_json)
    assert by_submission_from_json["correlation_id"] == "corr-local-host-1"
    header_json_by_submission = target_host.query_write_header_json_by_submission_id(
        response.submission_id
    )
    header_from_json_by_submission = json.loads(header_json_by_submission)
    assert header_from_json_by_submission["correlation_id"] == "corr-local-host-1"
    assert header_from_json_by_submission["submission_id"] == response.submission_id
    header_history = target_host.export_write_header_history()
    assert len(header_history) == 1
    assert header_history[0]["correlation_id"] == "corr-local-host-1"
    assert header_history[0]["submission_id"] == response.submission_id
    assert header_history[0]["status"] == "committed"
    assert header_history[0]["payload_kind"] == "WriteResult"
    committed_header_history = target_host.export_write_header_history_by_status("committed")
    assert len(committed_header_history) == 1
    assert committed_header_history[0]["correlation_id"] == "corr-local-host-1"
    typed_header_history = target_host.export_write_headers()
    assert len(typed_header_history) == 1
    assert typed_header_history[0].correlation_id == "corr-local-host-1"
    assert typed_header_history[0].submission_id == response.submission_id
    committed_typed_header_history = target_host.query_write_headers(status="committed")
    assert len(committed_typed_header_history) == 1
    assert committed_typed_header_history[0].status == "committed"
    typed_header_history_json = target_host.export_write_headers_json()
    typed_header_history_from_json = LocalWriteHeader.from_json_many(
        typed_header_history_json
    )
    assert len(typed_header_history_from_json) == 1
    assert typed_header_history_from_json[0].correlation_id == "corr-local-host-1"
    committed_typed_header_history_json = target_host.query_write_headers_json(
        status="committed"
    )
    committed_typed_header_history_from_json = LocalWriteHeader.from_json_many(
        committed_typed_header_history_json
    )
    assert len(committed_typed_header_history_from_json) == 1
    assert committed_typed_header_history_from_json[0].status == "committed"
    header_history_json = target_host.export_write_header_history_json()
    header_history_from_json = LocalWriteHeader.from_json_many(header_history_json)
    assert len(header_history_from_json) == 1
    assert header_history_from_json[0].payload_kind == "WriteResult"
    committed_header_history_json = target_host.export_write_header_history_json_by_status(
        "committed"
    )
    committed_header_history_from_json = LocalWriteHeader.from_json_many(
        committed_header_history_json
    )
    assert len(committed_header_history_from_json) == 1
    assert committed_header_history_from_json[0].status == "committed"
    missing_by_submission_dict = target_host.query_write_dict_by_submission_id(
        "missing-submission-id"
    )
    assert missing_by_submission_dict["status"] == "not_found"
    assert missing_by_submission_dict["submission_id"] == "missing-submission-id"
    missing_by_submission_json = target_host.query_write_json_by_submission_id(
        "missing-submission-id"
    )
    missing_by_submission_from_json = json.loads(missing_by_submission_json)
    assert missing_by_submission_from_json["status"] == "not_found"
    assert missing_by_submission_from_json["submission_id"] == "missing-submission-id"
    response_message = target_host.peek_write_response_message("corr-local-host-1")
    assert response_message is not None
    assert response_message.correlation_id == "corr-local-host-1"
    assert (
        response_message.to_json()
        == target_host.query_write_response_message_json("corr-local-host-1")
    )
    assert (
        type(response_message).from_json(response_message.to_json()).to_dict()
        == response_message.to_dict()
    )
    response_message_by_id = target_host.peek_write_response_message_by_submission_id(
        response.submission_id
    )
    assert response_message_by_id is not None
    assert response_message_by_id.correlation_id == "corr-local-host-1"
    assert target_host.peek_write_response_message("missing-correlation-id") is None
    assert (
        target_host.peek_write_response_message_by_submission_id("missing-submission-id")
        is None
    )
    response_message_dict = target_host.query_write_response_message_dict(
        "corr-local-host-1"
    )
    assert response_message_dict is not None
    assert response_message_dict["header"]["correlation_id"] == "corr-local-host-1"
    assert (
        target_host.query_write_response_message_dict("missing-correlation-id") is None
    )
    response_message_json = target_host.query_write_response_message_json(
        "corr-local-host-1"
    )
    assert response_message_json is not None
    response_message_from_json = WriteBundleResponseMessage.from_json(
        response_message_json
    )
    assert response_message_from_json.correlation_id == "corr-local-host-1"
    assert (
        target_host.query_write_response_message_json("missing-correlation-id") is None
    )
    response_message_dict_by_id = target_host.query_write_response_message_dict_by_submission_id(
        response.submission_id
    )
    assert response_message_dict_by_id is not None
    assert response_message_dict_by_id["header"]["correlation_id"] == "corr-local-host-1"
    assert (
        target_host.query_write_response_message_dict_by_submission_id(
            "missing-submission-id"
        )
        is None
    )
    response_message_json_by_id = target_host.query_write_response_message_json_by_submission_id(
        response.submission_id
    )
    assert response_message_json_by_id is not None
    response_message_from_json_by_id = WriteBundleResponseMessage.from_json(
        response_message_json_by_id
    )
    assert response_message_from_json_by_id.correlation_id == "corr-local-host-1"
    assert (
        target_host.query_write_response_message_json_by_submission_id(
            "missing-submission-id"
        )
        is None
    )
    submission_message = target_host.peek_write_submission_message("corr-local-host-1")
    assert submission_message is not None
    assert submission_message.correlation_id == "corr-local-host-1"
    assert (
        submission_message.to_json()
        == target_host.query_write_submission_message_json("corr-local-host-1")
    )
    assert (
        type(submission_message).from_json(submission_message.to_json()).to_dict()
        == submission_message.to_dict()
    )
    submission_message_by_id = target_host.peek_write_submission_message_by_submission_id(
        response.submission_id
    )
    assert submission_message_by_id is not None
    assert submission_message_by_id.correlation_id == "corr-local-host-1"
    assert target_host.peek_write_submission_message("missing-correlation-id") is None
    assert (
        target_host.peek_write_submission_message_by_submission_id(
            "missing-submission-id"
        )
        is None
    )
    submission_message_dict = target_host.query_write_submission_message_dict(
        "corr-local-host-1"
    )
    assert submission_message_dict is not None
    assert submission_message_dict["header"]["correlation_id"] == "corr-local-host-1"
    assert (
        target_host.query_write_submission_message_dict("missing-correlation-id")
        is None
    )
    submission_message_json = target_host.query_write_submission_message_json(
        "corr-local-host-1"
    )
    assert submission_message_json is not None
    submission_message_from_json = WriteBundleSubmissionMessage.from_json(
        submission_message_json
    )
    assert submission_message_from_json.correlation_id == "corr-local-host-1"
    assert (
        target_host.query_write_submission_message_json("missing-correlation-id")
        is None
    )
    submission_message_dict_by_id = target_host.query_write_submission_message_dict_by_submission_id(
        response.submission_id
    )
    assert submission_message_dict_by_id is not None
    assert submission_message_dict_by_id["header"]["correlation_id"] == "corr-local-host-1"
    assert (
        target_host.query_write_submission_message_dict_by_submission_id(
            "missing-submission-id"
        )
        is None
    )
    submission_message_json_by_id = (
        target_host.query_write_submission_message_json_by_submission_id(
            response.submission_id
        )
    )
    assert submission_message_json_by_id is not None
    submission_message_from_json_by_id = WriteBundleSubmissionMessage.from_json(
        submission_message_json_by_id
    )
    assert submission_message_from_json_by_id.correlation_id == "corr-local-host-1"
    assert (
        target_host.query_write_submission_message_json_by_submission_id(
            "missing-submission-id"
        )
        is None
    )
    submission_record = target_host.peek_write_submission_record("corr-local-host-1")
    assert submission_record is not None
    assert submission_record.status == "committed"
    assert (
        submission_record.to_json()
        == target_host.query_write_submission_record_json("corr-local-host-1")
    )
    assert (
        type(submission_record).from_json(submission_record.to_json()).to_dict()
        == submission_record.to_dict()
    )
    submission_record_by_id = target_host.peek_write_submission_record_by_submission_id(
        response.submission_id
    )
    assert submission_record_by_id is not None
    assert submission_record_by_id.correlation_id == "corr-local-host-1"
    assert target_host.peek_write_submission_record("missing-correlation-id") is None
    assert (
        target_host.peek_write_submission_record_by_submission_id(
            "missing-submission-id"
        )
        is None
    )
    submission_record_dict = target_host.query_write_submission_record_dict(
        "corr-local-host-1"
    )
    assert submission_record_dict is not None
    assert submission_record_dict["status"] == "committed"
    assert (
        target_host.query_write_submission_record_dict("missing-correlation-id") is None
    )
    submission_record_json = target_host.query_write_submission_record_json(
        "corr-local-host-1"
    )
    assert submission_record_json is not None
    submission_record_from_json = LocalWriteSubmissionRecord.from_json(
        submission_record_json
    )
    assert submission_record_from_json.status == "committed"
    assert (
        target_host.query_write_submission_record_json("missing-correlation-id") is None
    )
    submission_record_dict_by_id = target_host.query_write_submission_record_dict_by_submission_id(
        response.submission_id
    )
    assert submission_record_dict_by_id is not None
    assert submission_record_dict_by_id["correlation_id"] == "corr-local-host-1"
    assert (
        target_host.query_write_submission_record_dict_by_submission_id(
            "missing-submission-id"
        )
        is None
    )
    submission_record_json_by_id = (
        target_host.query_write_submission_record_json_by_submission_id(
            response.submission_id
        )
    )
    assert submission_record_json_by_id is not None
    submission_record_from_json_by_id = LocalWriteSubmissionRecord.from_json(
        submission_record_json_by_id
    )
    assert submission_record_from_json_by_id.correlation_id == "corr-local-host-1"
    assert (
        target_host.query_write_submission_record_json_by_submission_id(
            "missing-submission-id"
        )
        is None
    )
    response_history = target_host.export_write_response_messages()
    assert len(response_history) == 1
    assert response_history[0].correlation_id == "corr-local-host-1"
    committed_response_history = target_host.query_write_response_messages(
        status="committed"
    )
    assert len(committed_response_history) == 1
    assert committed_response_history[0].correlation_id == "corr-local-host-1"
    assert target_host.query_write_response_messages(status="failed") == []
    response_history_dict = target_host.export_write_response_history()
    assert len(response_history_dict) == 1
    assert response_history_dict[0]["header"]["correlation_id"] == "corr-local-host-1"
    committed_response_history_dict = target_host.export_write_response_history_by_status(
        "committed"
    )
    assert len(committed_response_history_dict) == 1
    assert committed_response_history_dict[0]["header"]["correlation_id"] == "corr-local-host-1"
    submission_messages = target_host.export_write_submission_messages()
    assert len(submission_messages) == 1
    assert submission_messages[0].correlation_id == "corr-local-host-1"
    committed_submission_messages = target_host.query_write_submission_messages(
        status="committed"
    )
    assert len(committed_submission_messages) == 1
    assert committed_submission_messages[0].correlation_id == "corr-local-host-1"
    assert target_host.query_write_submission_messages(status="failed") == []
    submission_message_history = target_host.export_write_submission_message_history()
    assert len(submission_message_history) == 1
    assert submission_message_history[0]["header"]["correlation_id"] == "corr-local-host-1"
    committed_submission_message_history = (
        target_host.export_write_submission_message_history_by_status("committed")
    )
    assert len(committed_submission_message_history) == 1
    assert (
        committed_submission_message_history[0]["header"]["correlation_id"]
        == "corr-local-host-1"
    )
    submission_records = target_host.export_write_submission_records()
    assert len(submission_records) == 1
    assert submission_records[0].status == "committed"
    committed_submission_records = target_host.query_write_submission_records(
        status="committed"
    )
    assert len(committed_submission_records) == 1
    assert committed_submission_records[0].correlation_id == "corr-local-host-1"
    assert target_host.query_write_submission_records(status="failed") == []
    history = target_host.export_write_submission_history()
    assert len(history) == 1
    committed_history = target_host.export_write_submission_history_by_status(
        "committed"
    )
    assert len(committed_history) == 1
    assert committed_history[0]["correlation_id"] == "corr-local-host-1"
    query_history = target_host.export_write_query_results()
    assert len(query_history) == 1
    assert query_history[0]["status"] == "committed"
    trace = target_host.query_write_trace("corr-local-host-1")
    assert isinstance(trace, LocalHostTrace)
    assert trace is not None
    assert trace.query_result.status == "committed"
    runtime_trace = target_host.executor.query_local_write_trace("corr-local-host-1")
    assert runtime_trace is not None
    assert LocalHostTrace.from_runtime(runtime_trace) == trace
    assert LocalWriteTrace.from_json(runtime_trace.to_json()).to_dict() == runtime_trace.to_dict()
    assert LocalHostTrace.from_json(trace.to_json()).to_dict() == trace.to_dict()
    trace_by_id = target_host.query_write_trace_by_submission_id(response.submission_id)
    assert trace_by_id is not None
    assert trace_by_id.correlation_id == "corr-local-host-1"
    assert target_host.query_write_trace("missing-correlation-id") is None
    assert (
        target_host.query_write_trace_by_submission_id("missing-submission-id") is None
    )
    trace_dict = target_host.query_write_trace_dict("corr-local-host-1")
    assert trace_dict is not None
    assert trace_dict["query_result"]["status"] == "committed"
    assert target_host.query_write_trace_dict("missing-correlation-id") is None
    trace_json = target_host.query_write_trace_json("corr-local-host-1")
    assert trace_json is not None
    trace_from_json = json.loads(trace_json)
    assert trace_from_json["query_result"]["status"] == "committed"
    assert target_host.query_write_trace_json("missing-correlation-id") is None
    trace_dict_by_id = target_host.query_write_trace_dict_by_submission_id(
        response.submission_id
    )
    assert trace_dict_by_id is not None
    assert trace_dict_by_id["correlation_id"] == "corr-local-host-1"
    assert (
        target_host.query_write_trace_dict_by_submission_id("missing-submission-id")
        is None
    )
    trace_json_by_id = target_host.query_write_trace_json_by_submission_id(
        response.submission_id
    )
    assert trace_json_by_id is not None
    trace_from_json_by_id = json.loads(trace_json_by_id)
    assert trace_from_json_by_id["correlation_id"] == "corr-local-host-1"
    assert (
        target_host.query_write_trace_json_by_submission_id("missing-submission-id")
        is None
    )
    trace_history = target_host.export_write_traces()
    assert len(trace_history) == 1
    assert trace_history[0].submission_id == response.submission_id
    trace_history_json = target_host.export_write_traces_json()
    assert trace_history_json == target_host.export_write_trace_history_json()
    assert [item.to_dict() for item in LocalHostTrace.from_json_many(trace_history_json)] == [
        item.to_dict() for item in trace_history
    ]
    trace_history_dict = target_host.export_write_trace_history()
    assert len(trace_history_dict) == 1
    assert trace_history_dict[0]["query_result"]["status"] == "committed"
    committed_traces = target_host.query_write_traces(status="committed")
    assert len(committed_traces) == 1
    assert committed_traces[0].correlation_id == "corr-local-host-1"
    committed_traces_json = target_host.query_write_traces_json(status="committed")
    assert committed_traces_json == target_host.export_write_trace_history_json_by_status(
        "committed"
    )
    assert [
        item.to_dict()
        for item in LocalHostTrace.from_json_many(committed_traces_json)
    ] == [item.to_dict() for item in committed_traces]
    failed_traces = target_host.query_write_traces(status="failed")
    assert failed_traces == []
    failed_traces_json = target_host.query_write_traces_json(status="failed")
    assert json.loads(failed_traces_json) == []
    committed_trace_history = target_host.export_write_trace_history_by_status(
        "committed"
    )
    assert len(committed_trace_history) == 1
    assert committed_trace_history[0]["query_result"]["status"] == "committed"

    another_target_host = LocalCogLangHost(nx.DiGraph())
    response2, query_result2 = another_target_host.submit_candidate_and_query(
        candidate,
        correlation_id="corr-local-host-1b",
    )
    assert response2 is not None
    assert query_result2 is not None
    assert query_result2.status == "committed"
    assert query_result2.correlation_id == "corr-local-host-1b"

    query_target_host_2 = LocalCogLangHost(nx.DiGraph())
    response_dict2c, query_result_dict2c = query_target_host_2.submit_candidate_and_query_dict(
        candidate,
        correlation_id="corr-local-host-1bb",
    )
    assert response_dict2c is not None
    assert query_result_dict2c is not None
    assert response_dict2c["header"]["correlation_id"] == "corr-local-host-1bb"
    assert query_result_dict2c["status"] == "committed"
    assert query_result_dict2c["correlation_id"] == "corr-local-host-1bb"

    query_target_host_3 = LocalCogLangHost(nx.DiGraph())
    response_json2d, query_result_json2d = query_target_host_3.submit_candidate_and_query_json(
        candidate,
        correlation_id="corr-local-host-1bc",
    )
    assert response_json2d is not None
    assert query_result_json2d is not None
    response_from_json2d = json.loads(response_json2d)
    query_result_from_json2d = json.loads(query_result_json2d)
    assert response_from_json2d["header"]["correlation_id"] == "corr-local-host-1bc"
    assert query_result_from_json2d["status"] == "committed"
    assert query_result_from_json2d["correlation_id"] == "corr-local-host-1bc"

    trace_target_host = LocalCogLangHost(nx.DiGraph())
    response3, trace3 = trace_target_host.submit_candidate_and_trace(
        candidate,
        correlation_id="corr-local-host-1c",
    )
    assert response3 is not None
    assert trace3 is not None
    assert trace3.correlation_id == "corr-local-host-1c"
    assert trace3.submission_id == response3.submission_id
    assert trace3.query_result.status == "committed"

    trace_target_host_2 = LocalCogLangHost(nx.DiGraph())
    response_dict4, trace_dict4 = trace_target_host_2.submit_candidate_and_trace_dict(
        candidate,
        correlation_id="corr-local-host-1d",
    )
    assert response_dict4 is not None
    assert trace_dict4 is not None
    assert response_dict4["header"]["correlation_id"] == "corr-local-host-1d"
    assert trace_dict4["correlation_id"] == "corr-local-host-1d"
    assert trace_dict4["query_result"]["status"] == "committed"

    trace_target_host_3 = LocalCogLangHost(nx.DiGraph())
    response_json5, trace_json5 = trace_target_host_3.submit_candidate_and_trace_json(
        candidate,
        correlation_id="corr-local-host-1e",
    )
    assert response_json5 is not None
    assert trace_json5 is not None
    response_from_json5 = json.loads(response_json5)
    trace_from_json5 = json.loads(trace_json5)
    assert response_from_json5["header"]["correlation_id"] == "corr-local-host-1e"
    assert trace_from_json5["correlation_id"] == "corr-local-host-1e"
    assert trace_from_json5["query_result"]["status"] == "committed"


def test_local_host_execute_and_submit_to_convenience():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    result, response = source_host.execute_and_submit_to(
        target_host,
        'Create["Entity", {"name": "Tesla"}]',
        correlation_id="corr-local-host-auto-1",
    )

    assert isinstance(result, str)
    assert response is not None
    assert response.correlation_id == "corr-local-host-auto-1"
    query_result = target_host.query_write("corr-local-host-auto-1")
    assert query_result.status == "committed"
    assert query_result.submission_id == response.submission_id


def test_local_host_execute_and_prepare_submission_message():
    host = LocalCogLangHost(nx.DiGraph())

    result, message = host.execute_and_prepare_submission_message(
        'Create["Entity", {"name": "Gauss"}]',
        correlation_id="corr-local-host-msg-auto-1",
        consume=True,
    )

    assert isinstance(result, str)
    assert message is not None
    assert message.correlation_id == "corr-local-host-msg-auto-1"
    assert message.candidate.operations[0].op == "create_node"
    assert host.peek_candidate() is None

    result2, message_dict = host.execute_and_prepare_submission_message_dict(
        'Create["Entity", {"name": "Euler"}]',
        correlation_id="corr-local-host-msg-auto-2",
        consume=True,
    )
    assert isinstance(result2, str)
    assert message_dict is not None
    assert message_dict["header"]["correlation_id"] == "corr-local-host-msg-auto-2"
    assert message_dict["payload"]["candidate"]["operations"][0]["op"] == "create_node"

    host.execute('Create["Entity", {"name": "Riemann"}]')
    candidate_dict = host.peek_candidate_dict()
    assert candidate_dict is not None
    assert candidate_dict["operations"][0]["op"] == "create_node"

    prepared_message_dict = host.prepare_submission_message_dict(
        correlation_id="corr-local-host-msg-auto-3",
        consume=True,
    )
    assert prepared_message_dict is not None
    assert prepared_message_dict["header"]["correlation_id"] == "corr-local-host-msg-auto-3"
    assert host.peek_candidate() is None
    assert host.consume_candidate_dict() is None


def test_local_host_execute_and_submit_to_query_convenience():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    result, response, query_result = source_host.execute_and_submit_to_query(
        target_host,
        'Create["Entity", {"name": "Ada"}]',
        correlation_id="corr-local-host-auto-2",
    )

    assert isinstance(result, str)
    assert response is not None
    assert query_result is not None
    assert response.correlation_id == "corr-local-host-auto-2"
    assert query_result.status == "committed"
    assert query_result.submission_id == response.submission_id

    result2, response_dict, query_result_dict = source_host.execute_and_submit_to_query_dict(
        target_host,
        'Create["Entity", {"name": "Babbage"}]',
        correlation_id="corr-local-host-auto-3",
    )
    assert isinstance(result2, str)
    assert response_dict is not None
    assert query_result_dict is not None
    assert response_dict["header"]["correlation_id"] == "corr-local-host-auto-3"
    assert query_result_dict["status"] == "committed"

    result3, response_json3, query_result_json3 = source_host.execute_and_submit_to_query_json(
        target_host,
        'Create["Entity", {"name": "Lovelace"}]',
        correlation_id="corr-local-host-auto-4",
    )
    assert isinstance(result3, str)
    assert response_json3 is not None
    assert query_result_json3 is not None
    response_from_json3 = json.loads(response_json3)
    query_result_from_json3 = json.loads(query_result_json3)
    assert response_from_json3["header"]["correlation_id"] == "corr-local-host-auto-4"
    assert query_result_from_json3["status"] == "committed"

    result4, response4, trace4 = source_host.execute_and_submit_to_trace(
        target_host,
        'Create["Entity", {"name": "Hopper"}]',
        correlation_id="corr-local-host-auto-5",
    )
    assert isinstance(result4, str)
    assert response4 is not None
    assert trace4 is not None
    assert response4.correlation_id == "corr-local-host-auto-5"
    assert trace4.correlation_id == "corr-local-host-auto-5"
    assert trace4.submission_id == response4.submission_id
    assert trace4.query_result.status == "committed"

    result5, response_dict5, trace_dict5 = source_host.execute_and_submit_to_trace_dict(
        target_host,
        'Create["Entity", {"name": "Knuth"}]',
        correlation_id="corr-local-host-auto-6",
    )
    assert isinstance(result5, str)
    assert response_dict5 is not None
    assert trace_dict5 is not None
    assert response_dict5["header"]["correlation_id"] == "corr-local-host-auto-6"
    assert trace_dict5["correlation_id"] == "corr-local-host-auto-6"
    assert trace_dict5["query_result"]["status"] == "committed"

    result6, response_json6, trace_json6 = source_host.execute_and_submit_to_trace_json(
        target_host,
        'Create["Entity", {"name": "Minsky"}]',
        correlation_id="corr-local-host-auto-7",
    )
    assert isinstance(result6, str)
    assert response_json6 is not None
    assert trace_json6 is not None
    response_from_json6 = json.loads(response_json6)
    trace_from_json6 = json.loads(trace_json6)
    assert response_from_json6["header"]["correlation_id"] == "corr-local-host-auto-7"
    assert trace_from_json6["correlation_id"] == "corr-local-host-auto-7"
    assert trace_from_json6["query_result"]["status"] == "committed"


def test_local_host_submit_message_and_query():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, candidate = source_host.execute_with_candidate('Create["Entity", {"name": "Curie"}]')
    assert candidate is not None
    message = target_host.prepare_submission_message(
        correlation_id="corr-local-host-msg-1",
    )
    assert message is None

    message = source_host.prepare_submission_message(
        correlation_id="corr-local-host-msg-1",
        consume=True,
    )
    assert message is not None

    response, query_result = target_host.submit_message_and_query(message)
    assert response.correlation_id == "corr-local-host-msg-1"
    assert query_result.status == "committed"
    assert query_result.submission_id == response.submission_id

    result_query_dict, message_query_dict = source_host.execute_and_prepare_submission_message(
        'Create["Entity", {"name": "Planck"}]',
        correlation_id="corr-local-host-msg-1c",
        consume=True,
    )
    assert isinstance(result_query_dict, str)
    assert message_query_dict is not None
    response_dict_query, query_result_dict_query = target_host.submit_message_and_query_dict(
        message_query_dict
    )
    assert response_dict_query["header"]["correlation_id"] == "corr-local-host-msg-1c"
    assert query_result_dict_query["status"] == "committed"
    assert query_result_dict_query["correlation_id"] == "corr-local-host-msg-1c"

    result_query_json, message_query_json = source_host.execute_and_prepare_submission_message(
        'Create["Entity", {"name": "Dirac"}]',
        correlation_id="corr-local-host-msg-1d",
        consume=True,
    )
    assert isinstance(result_query_json, str)
    assert message_query_json is not None
    response_json_query, query_result_json_query = target_host.submit_message_and_query_json(
        message_query_json
    )
    response_from_json_query = json.loads(response_json_query)
    query_result_from_json_query = json.loads(query_result_json_query)
    assert response_from_json_query["header"]["correlation_id"] == "corr-local-host-msg-1d"
    assert query_result_from_json_query["status"] == "committed"
    assert query_result_from_json_query["correlation_id"] == "corr-local-host-msg-1d"

    result_trace, message_trace = source_host.execute_and_prepare_submission_message(
        'Create["Entity", {"name": "Emmy"}]',
        correlation_id="corr-local-host-msg-1b",
        consume=True,
    )
    assert isinstance(result_trace, str)
    assert message_trace is not None
    response_trace, trace = target_host.submit_message_and_trace(message_trace)
    assert response_trace.correlation_id == "corr-local-host-msg-1b"
    assert trace is not None
    assert trace.correlation_id == "corr-local-host-msg-1b"
    assert trace.submission_id == response_trace.submission_id
    assert trace.query_result.status == "committed"

    result_trace_dict, message_trace_dict = source_host.execute_and_prepare_submission_message(
        'Create["Entity", {"name": "Hilbert"}]',
        correlation_id="corr-local-host-msg-1e",
        consume=True,
    )
    assert isinstance(result_trace_dict, str)
    assert message_trace_dict is not None
    response_dict_trace, trace_dict = target_host.submit_message_and_trace_dict(
        message_trace_dict
    )
    assert response_dict_trace["header"]["correlation_id"] == "corr-local-host-msg-1e"
    assert trace_dict is not None
    assert trace_dict["correlation_id"] == "corr-local-host-msg-1e"
    assert trace_dict["query_result"]["status"] == "committed"

    result_trace_json, message_trace_json = source_host.execute_and_prepare_submission_message(
        'Create["Entity", {"name": "Godel"}]',
        correlation_id="corr-local-host-msg-1f",
        consume=True,
    )
    assert isinstance(result_trace_json, str)
    assert message_trace_json is not None
    response_json_trace, trace_json = target_host.submit_message_and_trace_json(
        message_trace_json
    )
    response_from_json_trace = json.loads(response_json_trace)
    assert response_from_json_trace["header"]["correlation_id"] == "corr-local-host-msg-1f"
    assert trace_json is not None
    trace_from_json = json.loads(trace_json)
    assert trace_from_json["correlation_id"] == "corr-local-host-msg-1f"
    assert trace_from_json["query_result"]["status"] == "committed"

    result2, message_dict = source_host.execute_and_prepare_submission_message_dict(
        'Create["Entity", {"name": "Noether"}]',
        correlation_id="corr-local-host-msg-2",
        consume=True,
    )
    assert isinstance(result2, str)
    assert message_dict is not None

    response2 = target_host.submit_message_dict(message_dict)
    assert response2.correlation_id == "corr-local-host-msg-2"

    result3, message_dict2 = source_host.execute_and_prepare_submission_message_dict(
        'Create["Entity", {"name": "Turing"}]',
        correlation_id="corr-local-host-msg-3",
        consume=True,
    )
    assert isinstance(result3, str)
    assert message_dict2 is not None

    response3, query_result3 = target_host.submit_message_dict_and_query(
        message_dict2
    )
    assert response3.correlation_id == "corr-local-host-msg-3"
    assert query_result3.status == "committed"
    assert query_result3.submission_id == response3.submission_id

    result3b, message_dict3b = source_host.execute_and_prepare_submission_message_dict(
        'Create["Entity", {"name": "Shannon"}]',
        correlation_id="corr-local-host-msg-3b",
        consume=True,
    )
    assert isinstance(result3b, str)
    assert message_dict3b is not None
    response_json3b, query_result_json3b = target_host.submit_message_dict_and_query_json(
        message_dict3b
    )
    response_from_json3b = json.loads(response_json3b)
    query_result_from_json3b = json.loads(query_result_json3b)
    assert response_from_json3b["header"]["correlation_id"] == "corr-local-host-msg-3b"
    assert query_result_from_json3b["status"] == "committed"
    assert query_result_from_json3b["correlation_id"] == "corr-local-host-msg-3b"

    result4, message_dict4 = source_host.execute_and_prepare_submission_message_dict(
        'Create["Entity", {"name": "Shannon"}]',
        correlation_id="corr-local-host-msg-4",
        consume=True,
    )
    assert isinstance(result4, str)
    assert message_dict4 is not None
    response4, trace4 = target_host.submit_message_dict_and_trace(message_dict4)
    assert response4.correlation_id == "corr-local-host-msg-4"
    assert trace4 is not None
    assert trace4.correlation_id == "corr-local-host-msg-4"
    assert trace4.submission_id == response4.submission_id
    assert trace4.query_result.status == "committed"

    result5, message_dict5 = source_host.execute_and_prepare_submission_message_dict(
        'Create["Entity", {"name": "McCarthy"}]',
        correlation_id="corr-local-host-msg-5",
        consume=True,
    )
    assert isinstance(result5, str)
    assert message_dict5 is not None
    response_json5, trace_json5 = target_host.submit_message_dict_and_trace_json(
        message_dict5
    )
    response_from_json5 = json.loads(response_json5)
    assert response_from_json5["header"]["correlation_id"] == "corr-local-host-msg-5"
    assert trace_json5 is not None
    trace_from_json5 = json.loads(trace_json5)
    assert trace_from_json5["correlation_id"] == "corr-local-host-msg-5"
    assert trace_from_json5["query_result"]["status"] == "committed"


def test_local_host_state_roundtrip():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, candidate = source_host.execute_with_candidate('Create["Entity", {"name": "Tesla"}]')
    assert candidate is not None
    response = target_host.submit_candidate(candidate, correlation_id="corr-local-host-2")
    assert response is not None

    exported = target_host.export_state()
    rebuilt = LocalCogLangHost.from_state(exported)

    query_result = rebuilt.query_write("corr-local-host-2")
    assert query_result.status == "committed"
    assert query_result.submission_id == response.submission_id
    assert "graph" in exported
    assert "write_submission_history" in exported


def test_local_host_typed_snapshot_roundtrip():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, response = source_host.execute_and_submit_to(
        target_host,
        'Create["Entity", {"name": "Tesla"}]',
        correlation_id="corr-local-host-typed-1",
    )
    assert response is not None

    snapshot = target_host.export_snapshot()
    assert isinstance(snapshot, LocalHostSnapshot)
    assert len(snapshot.write_submission_messages) == 1
    assert len(snapshot.write_response_messages) == 1
    assert len(snapshot.write_submission_records) == 1
    assert len(snapshot.write_query_results) == 1
    assert len(snapshot.write_traces) == 1

    rebuilt_snapshot = LocalHostSnapshot.from_host(target_host)
    assert rebuilt_snapshot == snapshot
    assert LocalHostSnapshot.from_json(snapshot.to_json()).to_dict() == snapshot.to_dict()

    snapshot_dict = target_host.export_snapshot_dict()
    rebuilt = LocalCogLangHost.from_snapshot(snapshot_dict)
    query_result = rebuilt.query_write("corr-local-host-typed-1")
    assert query_result.status == "committed"
    assert query_result.submission_id == response.submission_id

    trace_only_snapshot = LocalHostSnapshot(
        graph=snapshot.graph,
        write_traces=snapshot.write_traces,
    )
    rebuilt_from_trace_only = LocalCogLangHost.from_snapshot(trace_only_snapshot)
    trace_only_result = rebuilt_from_trace_only.query_write("corr-local-host-typed-1")
    assert trace_only_result.status == "committed"
    assert trace_only_result.submission_id == response.submission_id
    assert len(rebuilt_from_trace_only.export_write_submission_messages()) == 1
    assert len(rebuilt_from_trace_only.export_write_response_messages()) == 1
    assert len(rebuilt_from_trace_only.export_write_submission_records()) == 1
    assert len(rebuilt_from_trace_only.export_write_traces()) == 1

    request_response_only_snapshot = LocalHostSnapshot(
        graph=snapshot.graph,
        write_submission_messages=snapshot.write_submission_messages,
        write_response_messages=snapshot.write_response_messages,
    )
    rebuilt_from_request_response = LocalCogLangHost.from_snapshot(
        request_response_only_snapshot
    )
    request_response_result = rebuilt_from_request_response.query_write(
        "corr-local-host-typed-1"
    )
    assert request_response_result.status == "committed"
    assert request_response_result.submission_id == response.submission_id
    assert len(rebuilt_from_request_response.export_write_submission_records()) == 1
    assert len(rebuilt_from_request_response.export_write_response_messages()) == 1
    assert len(rebuilt_from_request_response.export_write_traces()) == 1


def test_local_host_failed_partial_snapshot_roundtrip_preserves_error_report():
    target_host = LocalCogLangHost(nx.DiGraph())

    failed_candidate = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_edge",
                {
                    "source_id": "missing-source",
                    "target_id": "missing-target",
                    "relation": "knows",
                },
            ),
        ],
    )
    failed_response = target_host.submit_candidate(
        failed_candidate,
        correlation_id="corr-local-host-failed-partial-1",
    )
    assert failed_response is not None
    assert isinstance(failed_response.payload, ErrorReport)

    snapshot = target_host.export_snapshot()

    trace_only_snapshot = LocalHostSnapshot(
        graph=snapshot.graph,
        write_traces=snapshot.write_traces,
    )
    rebuilt_from_trace_only = LocalCogLangHost.from_snapshot(trace_only_snapshot)
    trace_only_result = rebuilt_from_trace_only.query_write(
        "corr-local-host-failed-partial-1"
    )
    assert trace_only_result.status == "failed"
    assert trace_only_result.response is not None
    assert isinstance(trace_only_result.response.payload, ErrorReport)
    trace_only_header = rebuilt_from_trace_only.query_write_header(
        "corr-local-host-failed-partial-1"
    )
    assert trace_only_header.status == "failed"
    assert trace_only_header.payload_kind == "ErrorReport"
    trace_only_trace = rebuilt_from_trace_only.query_write_trace(
        "corr-local-host-failed-partial-1"
    )
    assert trace_only_trace is not None
    assert isinstance(trace_only_trace.response.payload, ErrorReport)
    assert trace_only_trace.record.status == "failed"
    assert trace_only_trace.query_result.status == "failed"
    assert rebuilt_from_trace_only.export_summary().status_counts == {"failed": 1}
    assert len(rebuilt_from_trace_only.export_write_submission_records()) == 1
    assert len(rebuilt_from_trace_only.export_write_response_messages()) == 1
    assert len(rebuilt_from_trace_only.export_write_traces()) == 1

    request_response_only_snapshot = LocalHostSnapshot(
        graph=snapshot.graph,
        write_submission_messages=snapshot.write_submission_messages,
        write_response_messages=snapshot.write_response_messages,
    )
    rebuilt_from_request_response = LocalCogLangHost.from_snapshot(
        request_response_only_snapshot
    )
    request_response_result = rebuilt_from_request_response.query_write(
        "corr-local-host-failed-partial-1"
    )
    assert request_response_result.status == "failed"
    assert request_response_result.response is not None
    assert isinstance(request_response_result.response.payload, ErrorReport)
    request_response_header = rebuilt_from_request_response.query_write_header(
        "corr-local-host-failed-partial-1"
    )
    assert request_response_header.status == "failed"
    assert request_response_header.payload_kind == "ErrorReport"
    request_response_trace = rebuilt_from_request_response.query_write_trace(
        "corr-local-host-failed-partial-1"
    )
    assert request_response_trace is not None
    assert isinstance(request_response_trace.response.payload, ErrorReport)
    assert request_response_trace.record.status == "failed"
    assert request_response_trace.query_result.status == "failed"
    assert rebuilt_from_request_response.export_summary().status_counts == {"failed": 1}
    assert len(rebuilt_from_request_response.export_write_submission_records()) == 1
    assert len(rebuilt_from_request_response.export_write_response_messages()) == 1
    assert len(rebuilt_from_request_response.export_write_traces()) == 1


def test_local_host_typed_summary():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, response = source_host.execute_and_submit_to(
        target_host,
        'Create["Entity", {"name": "Tesla"}]',
        correlation_id="corr-local-host-summary-1",
    )
    assert response is not None

    summary = target_host.export_summary()
    assert isinstance(summary, LocalHostSummary)
    assert summary.node_count == 1
    assert summary.edge_count == 0
    assert summary.request_count == 1
    assert summary.response_count == 1
    assert summary.submission_record_count == 1
    assert summary.query_result_count == 1
    assert summary.trace_count == 1
    assert summary.status_counts["committed"] == 1
    rebuilt_from_snapshot = LocalHostSummary.from_snapshot(target_host.export_snapshot())
    assert rebuilt_from_snapshot == summary
    rebuilt_from_host = LocalHostSummary.from_host(target_host)
    assert rebuilt_from_host == summary

    summary_dict = target_host.export_summary_dict()
    rebuilt = LocalHostSummary.from_dict(summary_dict)
    assert rebuilt.node_count == 1
    assert rebuilt.request_count == 1
    assert rebuilt.trace_count == 1
    assert rebuilt.status_counts["committed"] == 1

    summary_json = target_host.export_summary_json()
    assert summary.to_json() == summary_json
    rebuilt_from_json = LocalHostSummary.from_json(summary_json)
    assert rebuilt_from_json.node_count == 1
    assert rebuilt_from_json.request_count == 1
    assert rebuilt_from_json.trace_count == 1
    assert rebuilt_from_json.status_counts["committed"] == 1


def test_local_host_reset_clears_graph_and_write_state():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, response = source_host.execute_and_submit_to(
        target_host,
        'Create["Entity", {"name": "Tesla"}]',
        correlation_id="corr-local-host-reset-1",
    )
    assert response is not None
    failed_candidate = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_edge",
                {
                    "source_id": "missing-source",
                    "target_id": "missing-target",
                    "relation": "knows",
                },
            ),
        ],
    )
    failed_response = target_host.submit_candidate(
        failed_candidate,
        correlation_id="corr-local-host-reset-2",
    )
    assert failed_response is not None
    assert isinstance(failed_response.payload, ErrorReport)
    assert target_host.query_write_status("corr-local-host-reset-1") == "committed"
    assert target_host.query_write_status("corr-local-host-reset-2") == "failed"
    assert target_host.export_summary().node_count == 1
    assert target_host.export_summary().request_count == 2
    assert target_host.export_summary().status_counts == {"committed": 1, "failed": 1}

    target_host.reset()

    cleared_summary = target_host.export_summary()
    assert cleared_summary.node_count == 0
    assert cleared_summary.edge_count == 0
    assert cleared_summary.request_count == 0
    assert cleared_summary.response_count == 0
    assert cleared_summary.submission_record_count == 0
    assert cleared_summary.query_result_count == 0
    assert cleared_summary.trace_count == 0
    assert cleared_summary.status_counts == {}
    assert target_host.query_write_status("corr-local-host-reset-1") == "not_found"
    assert target_host.query_write_status("corr-local-host-reset-2") == "not_found"
    assert (
        target_host.query_write_status_by_submission_id(response.submission_id) == "not_found"
    )
    assert (
        target_host.query_write_status_by_submission_id(failed_response.submission_id)
        == "not_found"
    )

    snapshot = target_host.export_snapshot()
    assert snapshot.graph["nodes"] == []
    assert snapshot.graph["edges"] == []
    assert snapshot.write_submission_messages == []
    assert snapshot.write_response_messages == []
    assert snapshot.write_submission_records == []
    assert snapshot.write_query_results == []
    assert snapshot.write_traces == []


def test_local_host_clone_creates_independent_copy():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, response = source_host.execute_and_submit_to(
        target_host,
        'Create["Entity", {"name": "Tesla"}]',
        correlation_id="corr-local-host-clone-1",
    )
    assert response is not None

    cloned = target_host.clone()

    assert cloned is not target_host
    assert cloned.query_write_status("corr-local-host-clone-1") == "committed"
    assert cloned.export_summary().node_count == 1
    assert cloned.export_summary().request_count == 1

    cloned.reset()

    assert cloned.export_summary().node_count == 0
    assert cloned.query_write_status("corr-local-host-clone-1") == "not_found"
    assert target_host.export_summary().node_count == 1
    assert target_host.query_write_status("corr-local-host-clone-1") == "committed"


def test_local_host_clone_preserves_mixed_statuses_independently():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, committed_candidate = source_host.execute_with_candidate(
        'Create["Entity", {"id": "dog_clone_1", "name": "Dog"}]'
    )
    assert committed_candidate is not None
    committed_response = target_host.submit_candidate(
        committed_candidate,
        correlation_id="corr-local-host-clone-mixed-1",
    )
    assert committed_response is not None

    failed_candidate = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_edge",
                {
                    "source_id": "missing-source",
                    "target_id": "missing-target",
                    "relation": "knows",
                },
            ),
        ],
    )
    failed_response = target_host.submit_candidate(
        failed_candidate,
        correlation_id="corr-local-host-clone-mixed-2",
    )
    assert failed_response is not None
    assert isinstance(failed_response.payload, ErrorReport)

    cloned = target_host.clone()

    assert cloned is not target_host
    assert cloned.query_write_status("corr-local-host-clone-mixed-1") == "committed"
    assert cloned.query_write_status("corr-local-host-clone-mixed-2") == "failed"
    assert [item.correlation_id for item in cloned.query_writes(status="committed")] == [
        "corr-local-host-clone-mixed-1"
    ]
    assert [item.correlation_id for item in cloned.query_writes(status="failed")] == [
        "corr-local-host-clone-mixed-2"
    ]
    assert (
        cloned.query_write_status_by_submission_id(committed_response.submission_id)
        == "committed"
    )
    assert (
        cloned.query_write_status_by_submission_id(failed_response.submission_id)
        == "failed"
    )
    assert (
        cloned.query_write_payload_kind_by_submission_id(failed_response.submission_id)
        == "ErrorReport"
    )
    failed_trace = cloned.query_write_trace_by_submission_id(failed_response.submission_id)
    assert failed_trace is not None
    assert failed_trace.query_result.status == "failed"
    assert isinstance(failed_trace.response.payload, ErrorReport)
    cloned_committed_query_results = LocalWriteQueryResult.from_json_many(
        cloned.export_write_query_results_json_by_status("committed")
    )
    assert [item.correlation_id for item in cloned_committed_query_results] == [
        "corr-local-host-clone-mixed-1"
    ]
    cloned_failed_query_results = LocalWriteQueryResult.from_json_many(
        cloned.export_write_query_results_json_by_status("failed")
    )
    assert [item.correlation_id for item in cloned_failed_query_results] == [
        "corr-local-host-clone-mixed-2"
    ]
    cloned_committed_headers = LocalWriteHeader.from_json_many(
        cloned.query_write_headers_json(status="committed")
    )
    assert [item.correlation_id for item in cloned_committed_headers] == [
        "corr-local-host-clone-mixed-1"
    ]
    cloned_failed_headers = LocalWriteHeader.from_json_many(
        cloned.query_write_headers_json(status="failed")
    )
    assert [item.correlation_id for item in cloned_failed_headers] == [
        "corr-local-host-clone-mixed-2"
    ]
    assert [item.payload_kind for item in cloned_failed_headers] == ["ErrorReport"]
    cloned_failed_header_history = LocalWriteHeader.from_json_many(
        cloned.export_write_header_history_json_by_status("failed")
    )
    assert [item.correlation_id for item in cloned_failed_header_history] == [
        "corr-local-host-clone-mixed-2"
    ]
    cloned_committed_traces = LocalHostTrace.from_json_many(
        cloned.query_write_traces_json(status="committed")
    )
    assert [item.correlation_id for item in cloned_committed_traces] == [
        "corr-local-host-clone-mixed-1"
    ]
    cloned_failed_traces = LocalHostTrace.from_json_many(
        cloned.query_write_traces_json(status="failed")
    )
    assert [item.correlation_id for item in cloned_failed_traces] == [
        "corr-local-host-clone-mixed-2"
    ]
    assert [item.query_result.status for item in cloned_failed_traces] == ["failed"]
    cloned_failed_trace_history = LocalHostTrace.from_json_many(
        cloned.export_write_trace_history_json_by_status("failed")
    )
    assert [item.correlation_id for item in cloned_failed_trace_history] == [
        "corr-local-host-clone-mixed-2"
    ]
    assert cloned.export_summary().status_counts == {"committed": 1, "failed": 1}

    cloned.reset()

    assert cloned.export_summary().status_counts == {}
    assert cloned.query_write_status("corr-local-host-clone-mixed-1") == "not_found"
    assert cloned.query_write_status("corr-local-host-clone-mixed-2") == "not_found"
    assert target_host.query_write_status("corr-local-host-clone-mixed-1") == "committed"
    assert target_host.query_write_status("corr-local-host-clone-mixed-2") == "failed"
    assert target_host.export_summary().status_counts == {"committed": 1, "failed": 1}


def test_local_host_restore_replaces_state_in_place():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, response = source_host.execute_and_submit_to(
        target_host,
        'Create["Entity", {"name": "Tesla"}]',
        correlation_id="corr-local-host-restore-1",
    )
    assert response is not None

    snapshot = target_host.export_snapshot()

    disposable = LocalCogLangHost(nx.DiGraph())
    _, response2 = source_host.execute_and_submit_to(
        disposable,
        'Create["Entity", {"name": "Ada"}]',
        correlation_id="corr-local-host-restore-2",
    )
    assert response2 is not None
    assert disposable.export_summary().node_count == 1
    assert disposable.query_write_status("corr-local-host-restore-2") == "committed"

    disposable.restore(snapshot)

    restored_summary = disposable.export_summary()
    assert restored_summary.node_count == 1
    assert restored_summary.request_count == 1
    assert disposable.query_write_status("corr-local-host-restore-1") == "committed"
    assert disposable.query_write_status("corr-local-host-restore-2") == "not_found"

    snapshot_json = target_host.export_snapshot_json()
    disposable.reset()
    disposable.restore_snapshot_json(snapshot_json)
    assert disposable.query_write_status("corr-local-host-restore-1") == "committed"
    assert disposable.export_summary().request_count == 1


def test_local_host_restore_state_replaces_legacy_state_in_place():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, response = source_host.execute_and_submit_to(
        target_host,
        'Create["Entity", {"name": "Tesla"}]',
        correlation_id="corr-local-host-restore-state-1",
    )
    assert response is not None

    exported_state = target_host.export_state()

    disposable = LocalCogLangHost(nx.DiGraph())
    _, response2 = source_host.execute_and_submit_to(
        disposable,
        'Create["Entity", {"name": "Ada"}]',
        correlation_id="corr-local-host-restore-state-2",
    )
    assert response2 is not None
    assert disposable.query_write_status("corr-local-host-restore-state-2") == "committed"

    disposable.restore_state(exported_state)

    restored_summary = disposable.export_summary()
    assert restored_summary.node_count == 1
    assert restored_summary.request_count == 1
    assert disposable.query_write_status("corr-local-host-restore-state-1") == "committed"
    assert disposable.query_write_status("corr-local-host-restore-state-2") == "not_found"

    state_json = target_host.export_state_json()
    disposable.reset()
    disposable.restore_state_json(state_json)
    assert disposable.query_write_status("corr-local-host-restore-state-1") == "committed"
    assert disposable.export_summary().request_count == 1


def test_local_host_mixed_status_legacy_state_restore_preserves_queries():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, committed_candidate = source_host.execute_with_candidate(
        'Create["Entity", {"id": "dog_state_1", "name": "Dog"}]'
    )
    assert committed_candidate is not None
    committed_response = target_host.submit_candidate(
        committed_candidate,
        correlation_id="corr-local-host-state-mixed-1",
    )
    assert committed_response is not None

    failed_candidate = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_edge",
                {
                    "source_id": "missing-source",
                    "target_id": "missing-target",
                    "relation": "knows",
                },
            ),
        ],
    )
    failed_response = target_host.submit_candidate(
        failed_candidate,
        correlation_id="corr-local-host-state-mixed-2",
    )
    assert failed_response is not None
    assert isinstance(failed_response.payload, ErrorReport)

    rebuilt = LocalCogLangHost.from_state(target_host.export_state())

    assert rebuilt.query_write_status("corr-local-host-state-mixed-1") == "committed"
    assert rebuilt.query_write_status("corr-local-host-state-mixed-2") == "failed"
    assert [item.correlation_id for item in rebuilt.query_writes(status="committed")] == [
        "corr-local-host-state-mixed-1"
    ]
    assert [item.correlation_id for item in rebuilt.query_writes(status="failed")] == [
        "corr-local-host-state-mixed-2"
    ]
    assert (
        rebuilt.query_write_status_by_submission_id(committed_response.submission_id)
        == "committed"
    )
    assert (
        rebuilt.query_write_status_by_submission_id(failed_response.submission_id)
        == "failed"
    )
    assert (
        rebuilt.query_write_payload_kind_by_submission_id(committed_response.submission_id)
        == "WriteResult"
    )
    assert (
        rebuilt.query_write_payload_kind_by_submission_id(failed_response.submission_id)
        == "ErrorReport"
    )

    committed_by_submission = rebuilt.query_write_by_submission_id(
        committed_response.submission_id
    )
    failed_by_submission = rebuilt.query_write_by_submission_id(
        failed_response.submission_id
    )
    assert committed_by_submission.correlation_id == "corr-local-host-state-mixed-1"
    assert committed_by_submission.status == "committed"
    assert failed_by_submission.correlation_id == "corr-local-host-state-mixed-2"
    assert failed_by_submission.status == "failed"
    assert failed_by_submission.response is not None
    assert isinstance(failed_by_submission.response.payload, ErrorReport)

    failed_header = rebuilt.query_write_header_by_submission_id(
        failed_response.submission_id
    )
    assert failed_header.status == "failed"
    assert failed_header.payload_kind == "ErrorReport"
    failed_trace = rebuilt.query_write_trace_by_submission_id(
        failed_response.submission_id
    )
    assert failed_trace is not None
    assert failed_trace.query_result.status == "failed"
    assert isinstance(failed_trace.response.payload, ErrorReport)
    committed_response_dict = rebuilt.query_write_response_message_dict_by_submission_id(
        committed_response.submission_id
    )
    assert committed_response_dict is not None
    assert committed_response_dict["header"]["correlation_id"] == "corr-local-host-state-mixed-1"
    failed_response_dict = rebuilt.query_write_response_message_dict_by_submission_id(
        failed_response.submission_id
    )
    assert failed_response_dict is not None
    assert failed_response_dict["header"]["correlation_id"] == "corr-local-host-state-mixed-2"
    assert failed_response_dict["payload"]["error_kind"] == "ValidationError"
    failed_response_json = rebuilt.query_write_response_message_json_by_submission_id(
        failed_response.submission_id
    )
    assert failed_response_json is not None
    failed_response_from_json = WriteBundleResponseMessage.from_json(failed_response_json)
    assert failed_response_from_json.correlation_id == "corr-local-host-state-mixed-2"
    assert isinstance(failed_response_from_json.payload, ErrorReport)
    committed_submission_message_dict = (
        rebuilt.query_write_submission_message_dict_by_submission_id(
            committed_response.submission_id
        )
    )
    assert committed_submission_message_dict is not None
    assert (
        committed_submission_message_dict["header"]["correlation_id"]
        == "corr-local-host-state-mixed-1"
    )
    failed_submission_message_dict = (
        rebuilt.query_write_submission_message_dict_by_submission_id(
            failed_response.submission_id
        )
    )
    assert failed_submission_message_dict is not None
    assert (
        failed_submission_message_dict["header"]["correlation_id"]
        == "corr-local-host-state-mixed-2"
    )
    failed_submission_message_json = (
        rebuilt.query_write_submission_message_json_by_submission_id(
            failed_response.submission_id
        )
    )
    assert failed_submission_message_json is not None
    failed_submission_message_from_json = WriteBundleSubmissionMessage.from_json(
        failed_submission_message_json
    )
    assert (
        failed_submission_message_from_json.correlation_id
        == "corr-local-host-state-mixed-2"
    )
    failed_record_dict = rebuilt.query_write_submission_record_dict_by_submission_id(
        failed_response.submission_id
    )
    assert failed_record_dict is not None
    assert failed_record_dict["correlation_id"] == "corr-local-host-state-mixed-2"
    assert failed_record_dict["status"] == "failed"
    failed_record_json = rebuilt.query_write_submission_record_json_by_submission_id(
        failed_response.submission_id
    )
    assert failed_record_json is not None
    failed_record_from_json = LocalWriteSubmissionRecord.from_json(failed_record_json)
    assert failed_record_from_json.correlation_id == "corr-local-host-state-mixed-2"
    assert failed_record_from_json.status == "failed"
    rebuilt_committed_query_results = LocalWriteQueryResult.from_json_many(
        rebuilt.export_write_query_results_json_by_status("committed")
    )
    assert [item.correlation_id for item in rebuilt_committed_query_results] == [
        "corr-local-host-state-mixed-1"
    ]
    rebuilt_failed_query_results = LocalWriteQueryResult.from_json_many(
        rebuilt.export_write_query_results_json_by_status("failed")
    )
    assert [item.correlation_id for item in rebuilt_failed_query_results] == [
        "corr-local-host-state-mixed-2"
    ]
    rebuilt_committed_headers = LocalWriteHeader.from_json_many(
        rebuilt.query_write_headers_json(status="committed")
    )
    assert [item.correlation_id for item in rebuilt_committed_headers] == [
        "corr-local-host-state-mixed-1"
    ]
    rebuilt_failed_headers = LocalWriteHeader.from_json_many(
        rebuilt.query_write_headers_json(status="failed")
    )
    assert [item.correlation_id for item in rebuilt_failed_headers] == [
        "corr-local-host-state-mixed-2"
    ]
    assert [item.payload_kind for item in rebuilt_failed_headers] == ["ErrorReport"]
    rebuilt_failed_header_history = LocalWriteHeader.from_json_many(
        rebuilt.export_write_header_history_json_by_status("failed")
    )
    assert [item.correlation_id for item in rebuilt_failed_header_history] == [
        "corr-local-host-state-mixed-2"
    ]
    rebuilt_committed_traces = LocalHostTrace.from_json_many(
        rebuilt.query_write_traces_json(status="committed")
    )
    assert [item.correlation_id for item in rebuilt_committed_traces] == [
        "corr-local-host-state-mixed-1"
    ]
    rebuilt_failed_traces = LocalHostTrace.from_json_many(
        rebuilt.query_write_traces_json(status="failed")
    )
    assert [item.correlation_id for item in rebuilt_failed_traces] == [
        "corr-local-host-state-mixed-2"
    ]
    assert [item.query_result.status for item in rebuilt_failed_traces] == ["failed"]
    rebuilt_failed_trace_history = LocalHostTrace.from_json_many(
        rebuilt.export_write_trace_history_json_by_status("failed")
    )
    assert [item.correlation_id for item in rebuilt_failed_trace_history] == [
        "corr-local-host-state-mixed-2"
    ]

    assert [
        item["correlation_id"] for item in rebuilt.export_write_header_history()
    ] == [
        "corr-local-host-state-mixed-1",
        "corr-local-host-state-mixed-2",
    ]
    assert [
        item["correlation_id"] for item in rebuilt.export_write_trace_history()
    ] == [
        "corr-local-host-state-mixed-1",
        "corr-local-host-state-mixed-2",
    ]
    assert rebuilt.export_summary().status_counts == {"committed": 1, "failed": 1}

    disposable = LocalCogLangHost(nx.DiGraph())
    disposable.restore_state_json(target_host.export_state_json())
    assert (
        disposable.query_write_status_by_submission_id(committed_response.submission_id)
        == "committed"
    )
    assert (
        disposable.query_write_payload_kind_by_submission_id(failed_response.submission_id)
        == "ErrorReport"
    )
    disposable_failed_headers = LocalWriteHeader.from_json_many(
        disposable.query_write_headers_json(status="failed")
    )
    assert [item.correlation_id for item in disposable_failed_headers] == [
        "corr-local-host-state-mixed-2"
    ]
    disposable_failed_traces = LocalHostTrace.from_json_many(
        disposable.query_write_traces_json(status="failed")
    )
    assert [item.correlation_id for item in disposable_failed_traces] == [
        "corr-local-host-state-mixed-2"
    ]
    assert disposable.export_summary().status_counts == {"committed": 1, "failed": 1}


def test_local_host_status_filtered_query_exports():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, candidate = source_host.execute_with_candidate('Create["Entity", {"name": "Tesla"}]')
    assert candidate is not None
    response = target_host.submit_candidate(candidate, correlation_id="corr-local-host-3")
    assert response is not None

    committed = target_host.query_writes(status="committed")
    assert len(committed) == 1
    assert committed[0].correlation_id == "corr-local-host-3"

    failed = target_host.query_writes(status="failed")
    assert failed == []

    committed_dicts = target_host.export_write_query_results_by_status("committed")
    assert len(committed_dicts) == 1
    assert committed_dicts[0]["status"] == "committed"

    trace_history_json = target_host.export_write_trace_history_json()
    trace_history_from_json = LocalWriteTrace.from_json_many(trace_history_json)
    assert len(trace_history_from_json) == 1
    assert trace_history_from_json[0].query_result.status == "committed"
    committed_trace_history_json = target_host.export_write_trace_history_json_by_status(
        "committed"
    )
    committed_trace_history_from_json = LocalWriteTrace.from_json_many(
        committed_trace_history_json
    )
    assert len(committed_trace_history_from_json) == 1
    assert committed_trace_history_from_json[0].query_result.status == "committed"

    query_results_json = target_host.export_write_query_results_json()
    query_results_from_json = LocalWriteQueryResult.from_json_many(query_results_json)
    assert len(query_results_from_json) == 1
    assert query_results_from_json[0].status == "committed"
    committed_query_results_json = target_host.export_write_query_results_json_by_status(
        "committed"
    )
    committed_query_results_from_json = LocalWriteQueryResult.from_json_many(
        committed_query_results_json
    )
    assert len(committed_query_results_from_json) == 1
    assert committed_query_results_from_json[0].status == "committed"

    response_history_json = target_host.export_write_response_history_json()
    response_history_from_json = WriteBundleResponseMessage.from_json_many(
        response_history_json
    )
    assert len(response_history_from_json) == 1
    assert response_history_from_json[0].correlation_id == "corr-local-host-3"
    committed_response_history_json = target_host.export_write_response_history_json_by_status(
        "committed"
    )
    committed_response_history_from_json = WriteBundleResponseMessage.from_json_many(
        committed_response_history_json
    )
    assert len(committed_response_history_from_json) == 1
    assert committed_response_history_from_json[0].correlation_id == "corr-local-host-3"

    submission_history_json = target_host.export_write_submission_history_json()
    submission_history_from_json = LocalWriteSubmissionRecord.from_json_many(
        submission_history_json
    )
    assert len(submission_history_from_json) == 1
    assert submission_history_from_json[0].correlation_id == "corr-local-host-3"
    committed_submission_history_json = target_host.export_write_submission_history_json_by_status(
        "committed"
    )
    committed_submission_history_from_json = LocalWriteSubmissionRecord.from_json_many(
        committed_submission_history_json
    )
    assert len(committed_submission_history_from_json) == 1
    assert committed_submission_history_from_json[0].correlation_id == "corr-local-host-3"

    submission_message_history_json = target_host.export_write_submission_message_history_json()
    submission_message_history_from_json = WriteBundleSubmissionMessage.from_json_many(
        submission_message_history_json
    )
    assert len(submission_message_history_from_json) == 1
    assert submission_message_history_from_json[0].correlation_id == "corr-local-host-3"
    committed_submission_message_history_json = (
        target_host.export_write_submission_message_history_json_by_status("committed")
    )
    committed_submission_message_history_from_json = WriteBundleSubmissionMessage.from_json_many(
        committed_submission_message_history_json
    )
    assert len(committed_submission_message_history_from_json) == 1
    assert committed_submission_message_history_from_json[0].correlation_id == "corr-local-host-3"


def test_local_host_mixed_status_histories_and_summary():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, committed_candidate = source_host.execute_with_candidate(
        'Create["Entity", {"id": "dog_1", "name": "Dog"}]'
    )
    assert committed_candidate is not None
    committed_response = target_host.submit_candidate(
        committed_candidate,
        correlation_id="corr-local-host-mixed-1",
    )
    assert committed_response is not None

    failed_candidate = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_edge",
                {
                    "source_id": "missing-source",
                    "target_id": "missing-target",
                    "relation": "knows",
                },
            ),
        ],
    )
    failed_response = target_host.submit_candidate(
        failed_candidate,
        correlation_id="corr-local-host-mixed-2",
    )
    assert failed_response is not None
    assert isinstance(failed_response.payload, ErrorReport)
    assert failed_response.payload.error_kind == "ValidationError"

    assert target_host.query_write_status("corr-local-host-mixed-1") == "committed"
    assert target_host.query_write_status("corr-local-host-mixed-2") == "failed"

    committed_results = target_host.query_writes(status="committed")
    failed_results = target_host.query_writes(status="failed")
    assert [item.correlation_id for item in committed_results] == ["corr-local-host-mixed-1"]
    assert [item.correlation_id for item in failed_results] == ["corr-local-host-mixed-2"]

    committed_headers = target_host.query_write_headers(status="committed")
    failed_headers = target_host.query_write_headers(status="failed")
    assert [item.payload_kind for item in committed_headers] == ["WriteResult"]
    assert [item.payload_kind for item in failed_headers] == ["ErrorReport"]

    committed_responses = target_host.query_write_response_messages(status="committed")
    failed_responses = target_host.query_write_response_messages(status="failed")
    assert [item.correlation_id for item in committed_responses] == ["corr-local-host-mixed-1"]
    assert [item.correlation_id for item in failed_responses] == ["corr-local-host-mixed-2"]
    assert isinstance(failed_responses[0].payload, ErrorReport)
    all_responses_from_json = WriteBundleResponseMessage.from_json_many(
        target_host.export_write_response_messages_json()
    )
    assert [item.correlation_id for item in all_responses_from_json] == [
        "corr-local-host-mixed-1",
        "corr-local-host-mixed-2",
    ]
    committed_responses_from_json = WriteBundleResponseMessage.from_json_many(
        target_host.query_write_response_messages_json(status="committed")
    )
    failed_responses_from_json = WriteBundleResponseMessage.from_json_many(
        target_host.query_write_response_messages_json(status="failed")
    )
    assert [item.correlation_id for item in committed_responses_from_json] == [
        "corr-local-host-mixed-1"
    ]
    assert [item.correlation_id for item in failed_responses_from_json] == [
        "corr-local-host-mixed-2"
    ]
    assert isinstance(failed_responses_from_json[0].payload, ErrorReport)

    committed_messages = target_host.query_write_submission_messages(status="committed")
    failed_messages = target_host.query_write_submission_messages(status="failed")
    assert [item.correlation_id for item in committed_messages] == ["corr-local-host-mixed-1"]
    assert [item.correlation_id for item in failed_messages] == ["corr-local-host-mixed-2"]
    all_messages_from_json = WriteBundleSubmissionMessage.from_json_many(
        target_host.export_write_submission_messages_json()
    )
    assert [item.correlation_id for item in all_messages_from_json] == [
        "corr-local-host-mixed-1",
        "corr-local-host-mixed-2",
    ]
    committed_messages_from_json = WriteBundleSubmissionMessage.from_json_many(
        target_host.query_write_submission_messages_json(status="committed")
    )
    failed_messages_from_json = WriteBundleSubmissionMessage.from_json_many(
        target_host.query_write_submission_messages_json(status="failed")
    )
    assert [item.correlation_id for item in committed_messages_from_json] == [
        "corr-local-host-mixed-1"
    ]
    assert [item.correlation_id for item in failed_messages_from_json] == [
        "corr-local-host-mixed-2"
    ]

    committed_records = target_host.query_write_submission_records(status="committed")
    failed_records = target_host.query_write_submission_records(status="failed")
    assert [item.status for item in committed_records] == ["committed"]
    assert [item.status for item in failed_records] == ["failed"]
    all_records_from_json = LocalWriteSubmissionRecord.from_json_many(
        target_host.export_write_submission_records_json()
    )
    assert [item.correlation_id for item in all_records_from_json] == [
        "corr-local-host-mixed-1",
        "corr-local-host-mixed-2",
    ]
    committed_records_from_json = LocalWriteSubmissionRecord.from_json_many(
        target_host.query_write_submission_records_json(status="committed")
    )
    failed_records_from_json = LocalWriteSubmissionRecord.from_json_many(
        target_host.query_write_submission_records_json(status="failed")
    )
    assert [item.correlation_id for item in committed_records_from_json] == [
        "corr-local-host-mixed-1"
    ]
    assert [item.correlation_id for item in failed_records_from_json] == [
        "corr-local-host-mixed-2"
    ]
    assert [item.status for item in committed_records_from_json] == ["committed"]
    assert [item.status for item in failed_records_from_json] == ["failed"]

    committed_traces = target_host.query_write_traces(status="committed")
    failed_traces = target_host.query_write_traces(status="failed")
    assert [item.correlation_id for item in committed_traces] == ["corr-local-host-mixed-1"]
    assert [item.correlation_id for item in failed_traces] == ["corr-local-host-mixed-2"]
    assert [item.query_result.status for item in failed_traces] == ["failed"]

    assert [
        item["correlation_id"]
        for item in target_host.export_write_query_results_by_status("committed")
    ] == ["corr-local-host-mixed-1"]
    assert [
        item["correlation_id"]
        for item in target_host.export_write_query_results_by_status("failed")
    ] == ["corr-local-host-mixed-2"]
    assert [
        item["correlation_id"]
        for item in target_host.export_write_header_history_by_status("committed")
    ] == ["corr-local-host-mixed-1"]
    assert [
        item["correlation_id"]
        for item in target_host.export_write_header_history_by_status("failed")
    ] == ["corr-local-host-mixed-2"]
    assert [
        item["correlation_id"]
        for item in target_host.export_write_trace_history_by_status("committed")
    ] == ["corr-local-host-mixed-1"]
    assert [
        item["correlation_id"]
        for item in target_host.export_write_trace_history_by_status("failed")
    ] == ["corr-local-host-mixed-2"]

    summary = target_host.export_summary()
    assert summary.node_count == 1
    assert summary.request_count == 2
    assert summary.response_count == 2
    assert summary.submission_record_count == 2
    assert summary.query_result_count == 2
    assert summary.trace_count == 2
    assert summary.status_counts == {"committed": 1, "failed": 1}

    rebuilt = LocalCogLangHost.from_snapshot(target_host.export_snapshot())
    assert rebuilt.query_write_status("corr-local-host-mixed-1") == "committed"
    assert rebuilt.query_write_status("corr-local-host-mixed-2") == "failed"
    assert rebuilt.export_summary().status_counts == {"committed": 1, "failed": 1}


def test_local_host_mixed_status_snapshot_restore_preserves_order_and_filters():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, committed_candidate = source_host.execute_with_candidate(
        'Create["Entity", {"id": "dog_restore_1", "name": "Dog"}]'
    )
    assert committed_candidate is not None
    committed_response = target_host.submit_candidate(
        committed_candidate,
        correlation_id="corr-local-host-restore-mixed-1",
    )
    assert committed_response is not None

    failed_candidate = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_edge",
                {
                    "source_id": "missing-source",
                    "target_id": "missing-target",
                    "relation": "knows",
                },
            ),
        ],
    )
    failed_response = target_host.submit_candidate(
        failed_candidate,
        correlation_id="corr-local-host-restore-mixed-2",
    )
    assert failed_response is not None

    rebuilt = LocalCogLangHost.from_snapshot(target_host.export_snapshot())

    committed_by_submission = rebuilt.query_write_by_submission_id(
        committed_response.submission_id
    )
    failed_by_submission = rebuilt.query_write_by_submission_id(
        failed_response.submission_id
    )
    assert committed_by_submission.correlation_id == "corr-local-host-restore-mixed-1"
    assert committed_by_submission.status == "committed"
    assert failed_by_submission.correlation_id == "corr-local-host-restore-mixed-2"
    assert failed_by_submission.status == "failed"
    assert (
        rebuilt.query_write_status_by_submission_id(committed_response.submission_id)
        == "committed"
    )
    assert (
        rebuilt.query_write_status_by_submission_id(failed_response.submission_id)
        == "failed"
    )
    assert (
        rebuilt.query_write_payload_kind_by_submission_id(committed_response.submission_id)
        == "WriteResult"
    )
    assert (
        rebuilt.query_write_payload_kind_by_submission_id(failed_response.submission_id)
        == "ErrorReport"
    )
    assert (
        rebuilt.query_write_header_by_submission_id(committed_response.submission_id).status
        == "committed"
    )
    assert (
        rebuilt.query_write_header_by_submission_id(failed_response.submission_id).payload_kind
        == "ErrorReport"
    )
    assert (
        rebuilt.query_write_trace_by_submission_id(committed_response.submission_id)
        is not None
    )
    failed_trace_by_submission = rebuilt.query_write_trace_by_submission_id(
        failed_response.submission_id
    )
    assert failed_trace_by_submission is not None
    assert failed_trace_by_submission.query_result.status == "failed"
    assert isinstance(failed_trace_by_submission.response.payload, ErrorReport)
    missing_by_submission = rebuilt.query_write_by_submission_id("missing-submission-id")
    assert missing_by_submission.status == "not_found"
    assert missing_by_submission.submission_id == "missing-submission-id"

    assert [
        item["correlation_id"] for item in rebuilt.export_write_header_history()
    ] == [
        "corr-local-host-restore-mixed-1",
        "corr-local-host-restore-mixed-2",
    ]
    assert [
        item["correlation_id"] for item in rebuilt.export_write_trace_history()
    ] == [
        "corr-local-host-restore-mixed-1",
        "corr-local-host-restore-mixed-2",
    ]
    assert [
        item.correlation_id for item in rebuilt.query_writes(status="committed")
    ] == ["corr-local-host-restore-mixed-1"]
    assert [
        item.correlation_id for item in rebuilt.query_writes(status="failed")
    ] == ["corr-local-host-restore-mixed-2"]
    assert [
        item.correlation_id for item in rebuilt.query_write_headers(status="committed")
    ] == ["corr-local-host-restore-mixed-1"]
    assert [
        item.correlation_id for item in rebuilt.query_write_headers(status="failed")
    ] == ["corr-local-host-restore-mixed-2"]
    assert [
        item.correlation_id for item in rebuilt.query_write_traces(status="committed")
    ] == ["corr-local-host-restore-mixed-1"]
    assert [
        item.correlation_id for item in rebuilt.query_write_traces(status="failed")
    ] == ["corr-local-host-restore-mixed-2"]
    assert [
        item["correlation_id"]
        for item in rebuilt.export_write_header_history_by_status("committed")
    ] == ["corr-local-host-restore-mixed-1"]
    assert [
        item["correlation_id"]
        for item in rebuilt.export_write_header_history_by_status("failed")
    ] == ["corr-local-host-restore-mixed-2"]
    assert [
        item["correlation_id"]
        for item in rebuilt.export_write_trace_history_by_status("committed")
    ] == ["corr-local-host-restore-mixed-1"]
    assert [
        item["correlation_id"]
        for item in rebuilt.export_write_trace_history_by_status("failed")
    ] == ["corr-local-host-restore-mixed-2"]
    assert [
        item.correlation_id for item in rebuilt.query_write_response_messages(status="committed")
    ] == ["corr-local-host-restore-mixed-1"]
    assert [
        item.correlation_id for item in rebuilt.query_write_response_messages(status="failed")
    ] == ["corr-local-host-restore-mixed-2"]
    assert [
        item.correlation_id
        for item in rebuilt.query_write_submission_messages(status="committed")
    ] == ["corr-local-host-restore-mixed-1"]
    assert [
        item.correlation_id
        for item in rebuilt.query_write_submission_messages(status="failed")
    ] == ["corr-local-host-restore-mixed-2"]
    assert [
        item.correlation_id
        for item in rebuilt.query_write_submission_records(status="committed")
    ] == ["corr-local-host-restore-mixed-1"]
    assert [
        item.correlation_id
        for item in rebuilt.query_write_submission_records(status="failed")
    ] == ["corr-local-host-restore-mixed-2"]
    assert [
        item["header"]["correlation_id"]
        for item in rebuilt.export_write_response_history_by_status("committed")
    ] == ["corr-local-host-restore-mixed-1"]
    assert [
        item["header"]["correlation_id"]
        for item in rebuilt.export_write_response_history_by_status("failed")
    ] == ["corr-local-host-restore-mixed-2"]
    assert [
        item["correlation_id"]
        for item in rebuilt.export_write_submission_history_by_status("committed")
    ] == ["corr-local-host-restore-mixed-1"]
    assert [
        item["correlation_id"]
        for item in rebuilt.export_write_submission_history_by_status("failed")
    ] == ["corr-local-host-restore-mixed-2"]
    assert [
        item["header"]["correlation_id"]
        for item in rebuilt.export_write_submission_message_history_by_status("committed")
    ] == ["corr-local-host-restore-mixed-1"]
    assert [
        item["header"]["correlation_id"]
        for item in rebuilt.export_write_submission_message_history_by_status("failed")
    ] == ["corr-local-host-restore-mixed-2"]
    rebuilt_failed_response_history_json = rebuilt.export_write_response_history_json_by_status(
        "failed"
    )
    rebuilt_failed_response_history = WriteBundleResponseMessage.from_json_many(
        rebuilt_failed_response_history_json
    )
    assert [item.correlation_id for item in rebuilt_failed_response_history] == [
        "corr-local-host-restore-mixed-2"
    ]
    assert isinstance(rebuilt_failed_response_history[0].payload, ErrorReport)
    rebuilt_failed_submission_history_json = (
        rebuilt.export_write_submission_history_json_by_status("failed")
    )
    rebuilt_failed_submission_history = LocalWriteSubmissionRecord.from_json_many(
        rebuilt_failed_submission_history_json
    )
    assert [item.correlation_id for item in rebuilt_failed_submission_history] == [
        "corr-local-host-restore-mixed-2"
    ]
    assert rebuilt_failed_submission_history[0].status == "failed"
    rebuilt_failed_submission_message_history_json = (
        rebuilt.export_write_submission_message_history_json_by_status("failed")
    )
    rebuilt_failed_submission_message_history = WriteBundleSubmissionMessage.from_json_many(
        rebuilt_failed_submission_message_history_json
    )
    assert [item.correlation_id for item in rebuilt_failed_submission_message_history] == [
        "corr-local-host-restore-mixed-2"
    ]
    assert rebuilt.export_summary().status_counts == {"committed": 1, "failed": 1}


def test_local_host_clear_write_state():
    source_host = LocalCogLangHost(nx.DiGraph())
    target_host = LocalCogLangHost(nx.DiGraph())

    _, response = source_host.execute_and_submit_to(
        target_host,
        'Create["Entity", {"name": "Tesla"}]',
        correlation_id="corr-local-host-clear-1",
    )
    assert response is not None
    assert target_host.query_write("corr-local-host-clear-1").status == "committed"
    failed_candidate = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_edge",
                {
                    "source_id": "missing-source",
                    "target_id": "missing-target",
                    "relation": "knows",
                },
            ),
        ],
    )
    failed_response = target_host.submit_candidate(
        failed_candidate,
        correlation_id="corr-local-host-clear-2",
    )
    assert failed_response is not None
    assert isinstance(failed_response.payload, ErrorReport)
    assert target_host.query_write("corr-local-host-clear-2").status == "failed"
    assert target_host.export_summary().status_counts == {"committed": 1, "failed": 1}

    target_host.clear_write_state()

    cleared_summary = target_host.export_summary()
    assert cleared_summary.node_count == 1
    assert cleared_summary.request_count == 0
    assert cleared_summary.response_count == 0
    assert cleared_summary.submission_record_count == 0
    assert cleared_summary.query_result_count == 0
    assert cleared_summary.trace_count == 0
    assert cleared_summary.status_counts == {}
    assert target_host.query_write("corr-local-host-clear-1").status == "not_found"
    assert target_host.query_write("corr-local-host-clear-2").status == "not_found"
    assert (
        target_host.query_write_status_by_submission_id(response.submission_id) == "not_found"
    )
    assert (
        target_host.query_write_status_by_submission_id(failed_response.submission_id)
        == "not_found"
    )
    assert target_host.query_writes(status="committed") == []
    assert target_host.query_writes(status="failed") == []
    assert target_host.export_write_submission_messages() == []
    assert target_host.export_write_response_messages() == []
    assert target_host.export_write_submission_records() == []
    assert target_host.export_write_query_results() == []
    assert target_host.export_write_header_history() == []
    assert target_host.export_write_traces() == []
