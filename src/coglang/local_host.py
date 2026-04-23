from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any

import networkx as nx

from .executor import PythonCogLangExecutor
from .graph_backend import GraphBackend
from .parser import CogLangExpr, parse
from .write_bundle import (
    LocalWriteHeader,
    LocalWriteQueryResult,
    LocalWriteSubmissionRecord,
    LocalWriteTrace,
    WriteBundleCandidate,
    WriteBundleResponseMessage,
    WriteBundleSubmissionMessage,
    local_write_status_from_response,
)


def _coerce_expr(expr: str | CogLangExpr) -> CogLangExpr:
    if isinstance(expr, str):
        return parse(expr)
    return expr


@dataclass
class LocalHostSnapshot:
    """Typed snapshot of a minimal standalone CogLang host state."""

    graph: dict[str, Any]
    write_submission_messages: list[WriteBundleSubmissionMessage] = field(default_factory=list)
    write_response_messages: list[WriteBundleResponseMessage] = field(default_factory=list)
    write_submission_records: list[LocalWriteSubmissionRecord] = field(default_factory=list)
    write_query_results: list[LocalWriteQueryResult] = field(default_factory=list)
    write_traces: list["LocalHostTrace"] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph": dict(self.graph),
            "write_submission_messages": [
                item.to_dict() for item in self.write_submission_messages
            ],
            "write_response_messages": [
                item.to_dict() for item in self.write_response_messages
            ],
            "write_submission_records": [
                item.to_dict() for item in self.write_submission_records
            ],
            "write_query_results": [
                item.to_dict() for item in self.write_query_results
            ],
            "write_traces": [item.to_dict() for item in self.write_traces],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LocalHostSnapshot":
        return cls(
            graph=dict(data["graph"]),
            write_submission_messages=[
                WriteBundleSubmissionMessage.from_dict(dict(item))
                for item in data.get("write_submission_messages", [])
            ],
            write_response_messages=[
                WriteBundleResponseMessage.from_dict(dict(item))
                for item in data.get("write_response_messages", [])
            ],
            write_submission_records=[
                LocalWriteSubmissionRecord.from_dict(dict(item))
                for item in data.get("write_submission_records", [])
            ],
            write_query_results=[
                LocalWriteQueryResult.from_dict(dict(item))
                for item in data.get("write_query_results", [])
            ],
            write_traces=[
                LocalHostTrace.from_dict(dict(item))
                for item in data.get("write_traces", [])
            ],
        )

    @classmethod
    def from_json(cls, payload: str) -> "LocalHostSnapshot":
        return cls.from_dict(json.loads(payload))

    @classmethod
    def from_host(cls, host: "LocalCogLangHost") -> "LocalHostSnapshot":
        return cls(
            graph=host.executor.graph_backend.to_dict(),
            write_submission_messages=host.export_write_submission_messages(),
            write_response_messages=host.export_write_response_messages(),
            write_submission_records=host.export_write_submission_records(),
            write_query_results=host.query_writes(),
            write_traces=host.export_write_traces(),
        )


@dataclass
class LocalHostSummary:
    """Typed minimal summary of a standalone CogLang host."""

    node_count: int
    edge_count: int
    request_count: int
    response_count: int
    submission_record_count: int
    query_result_count: int
    trace_count: int
    status_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "request_count": self.request_count,
            "response_count": self.response_count,
            "submission_record_count": self.submission_record_count,
            "query_result_count": self.query_result_count,
            "trace_count": self.trace_count,
            "status_counts": dict(self.status_counts),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LocalHostSummary":
        return cls(
            node_count=int(data["node_count"]),
            edge_count=int(data["edge_count"]),
            request_count=int(data["request_count"]),
            response_count=int(data["response_count"]),
            submission_record_count=int(data["submission_record_count"]),
            query_result_count=int(data["query_result_count"]),
            trace_count=int(data["trace_count"]),
            status_counts={str(k): int(v) for k, v in dict(data.get("status_counts", {})).items()},
        )

    @classmethod
    def from_json(cls, payload: str) -> "LocalHostSummary":
        return cls.from_dict(json.loads(payload))

    @classmethod
    def from_snapshot(cls, snapshot: LocalHostSnapshot) -> "LocalHostSummary":
        status_counts: dict[str, int] = {}
        for item in snapshot.write_query_results:
            status_counts[item.status] = status_counts.get(item.status, 0) + 1
        graph = GraphBackend.from_dict(dict(snapshot.graph)).graph
        return cls(
            node_count=graph.number_of_nodes(),
            edge_count=graph.number_of_edges(),
            request_count=len(snapshot.write_submission_messages),
            response_count=len(snapshot.write_response_messages),
            submission_record_count=len(snapshot.write_submission_records),
            query_result_count=len(snapshot.write_query_results),
            trace_count=len(snapshot.write_traces),
            status_counts=status_counts,
        )

    @classmethod
    def from_host(cls, host: "LocalCogLangHost") -> "LocalHostSummary":
        return cls.from_snapshot(host.export_snapshot())


@dataclass
class LocalHostTrace:
    """Typed correlated local write view for one submission."""

    correlation_id: str
    submission_id: str
    request: WriteBundleSubmissionMessage
    response: WriteBundleResponseMessage
    record: LocalWriteSubmissionRecord
    query_result: LocalWriteQueryResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "submission_id": self.submission_id,
            "request": self.request.to_dict(),
            "response": self.response.to_dict(),
            "record": self.record.to_dict(),
            "query_result": self.query_result.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def to_json_many(cls, items: list["LocalHostTrace"]) -> str:
        return json.dumps(
            [item.to_dict() for item in items],
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LocalHostTrace":
        return cls(
            correlation_id=str(data["correlation_id"]),
            submission_id=str(data["submission_id"]),
            request=WriteBundleSubmissionMessage.from_dict(dict(data["request"])),
            response=WriteBundleResponseMessage.from_dict(dict(data["response"])),
            record=LocalWriteSubmissionRecord.from_dict(dict(data["record"])),
            query_result=LocalWriteQueryResult.from_dict(dict(data["query_result"])),
        )

    @classmethod
    def from_json(cls, payload: str) -> "LocalHostTrace":
        return cls.from_dict(json.loads(payload))

    @classmethod
    def from_json_many(cls, payload: str) -> list["LocalHostTrace"]:
        return [cls.from_dict(dict(item)) for item in json.loads(payload)]

    @classmethod
    def from_runtime(cls, trace: LocalWriteTrace) -> "LocalHostTrace":
        return cls(
            correlation_id=trace.correlation_id,
            submission_id=trace.submission_id,
            request=trace.request,
            response=trace.response,
            record=trace.record,
            query_result=trace.query_result,
        )

class LocalCogLangHost:
    """Minimal host-facing facade for standalone CogLang evaluation and local write flow.

    This intentionally stays small:
    - parse / execute
    - capture latest write candidate
    - turn it into a typed submission message
    - submit it against the local backend
    - query local write results

    It is not a full bus adapter or provenance store.
    """

    def __init__(
        self,
        graph: nx.DiGraph | None = None,
        executor: PythonCogLangExecutor | None = None,
    ) -> None:
        self.executor = executor if executor is not None else PythonCogLangExecutor(graph)

    def parse(self, expr: str | CogLangExpr) -> CogLangExpr:
        return _coerce_expr(expr)

    def execute(self, expr: str | CogLangExpr, env: dict[str, Any] | None = None) -> Any:
        return self.executor.execute(_coerce_expr(expr), env=env)

    @staticmethod
    def _to_dict(value: Any) -> dict[str, Any]:
        return value.to_dict()

    @staticmethod
    def _to_json(value: Any) -> str:
        return value.to_json()

    @classmethod
    def _to_dict_or_none(cls, value: Any | None) -> dict[str, Any] | None:
        return None if value is None else cls._to_dict(value)

    @classmethod
    def _to_json_or_none(cls, value: Any | None) -> str | None:
        return None if value is None else cls._to_json(value)

    def execute_with_candidate(
        self,
        expr: str | CogLangExpr,
        env: dict[str, Any] | None = None,
    ) -> tuple[Any, WriteBundleCandidate | None]:
        return self.executor.execute_with_write_bundle_candidate(_coerce_expr(expr), env=env)

    def execute_and_prepare_submission_message(
        self,
        expr: str | CogLangExpr,
        env: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        consume: bool = False,
    ) -> tuple[Any, WriteBundleSubmissionMessage | None]:
        result, candidate = self.execute_with_candidate(expr, env=env)
        if candidate is None:
            return result, None
        message = self.prepare_submission_message(
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )
        return result, message

    def execute_and_prepare_submission_message_dict(
        self,
        expr: str | CogLangExpr,
        env: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        consume: bool = False,
    ) -> tuple[Any, dict[str, Any] | None]:
        result, message = self.execute_and_prepare_submission_message(
            expr=expr,
            env=env,
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )
        if message is None:
            return result, None
        return result, self._to_dict(message)

    def execute_and_submit_to(
        self,
        target_host: "LocalCogLangHost",
        expr: str | CogLangExpr,
        env: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Any, WriteBundleResponseMessage | None]:
        result, candidate = self.execute_with_candidate(expr, env=env)
        if candidate is None:
            return result, None
        response = target_host.submit_candidate(
            candidate,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        return result, response

    def execute_and_submit_to_query(
        self,
        target_host: "LocalCogLangHost",
        expr: str | CogLangExpr,
        env: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Any, WriteBundleResponseMessage | None, LocalWriteQueryResult | None]:
        result, response = self.execute_and_submit_to(
            target_host=target_host,
            expr=expr,
            env=env,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        if response is None:
            return result, None, None
        return result, response, target_host.query_write(response.correlation_id)

    def execute_and_submit_to_trace(
        self,
        target_host: "LocalCogLangHost",
        expr: str | CogLangExpr,
        env: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Any, WriteBundleResponseMessage | None, LocalHostTrace | None]:
        result, response = self.execute_and_submit_to(
            target_host=target_host,
            expr=expr,
            env=env,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        if response is None:
            return result, None, None
        return result, response, target_host.query_write_trace(response.correlation_id)

    def execute_and_submit_to_trace_dict(
        self,
        target_host: "LocalCogLangHost",
        expr: str | CogLangExpr,
        env: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Any, dict[str, Any] | None, dict[str, Any] | None]:
        result, response, trace = self.execute_and_submit_to_trace(
            target_host=target_host,
            expr=expr,
            env=env,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        return (
            result,
            self._to_dict_or_none(response),
            self._to_dict_or_none(trace),
        )

    def execute_and_submit_to_trace_json(
        self,
        target_host: "LocalCogLangHost",
        expr: str | CogLangExpr,
        env: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Any, str | None, str | None]:
        result, response, trace = self.execute_and_submit_to_trace(
            target_host=target_host,
            expr=expr,
            env=env,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        return (
            result,
            self._to_json_or_none(response),
            self._to_json_or_none(trace),
        )

    def execute_and_submit_to_query_dict(
        self,
        target_host: "LocalCogLangHost",
        expr: str | CogLangExpr,
        env: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Any, dict[str, Any] | None, dict[str, Any] | None]:
        result, response, query_result = self.execute_and_submit_to_query(
            target_host=target_host,
            expr=expr,
            env=env,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        return (
            result,
            self._to_dict_or_none(response),
            self._to_dict_or_none(query_result),
        )

    def execute_and_submit_to_query_json(
        self,
        target_host: "LocalCogLangHost",
        expr: str | CogLangExpr,
        env: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Any, str | None, str | None]:
        result, response, query_result = self.execute_and_submit_to_query(
            target_host=target_host,
            expr=expr,
            env=env,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        return (
            result,
            self._to_json_or_none(response),
            self._to_json_or_none(query_result),
        )

    def peek_candidate(self) -> WriteBundleCandidate | None:
        return self.executor.peek_write_bundle_candidate()

    def peek_candidate_dict(self) -> dict[str, Any] | None:
        candidate = self.peek_candidate()
        return self._to_dict_or_none(candidate)

    def consume_candidate(self) -> WriteBundleCandidate | None:
        return self.executor.consume_write_bundle_candidate()

    def consume_candidate_dict(self) -> dict[str, Any] | None:
        candidate = self.consume_candidate()
        return self._to_dict_or_none(candidate)

    def prepare_submission_message(
        self,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        consume: bool = False,
    ) -> WriteBundleSubmissionMessage | None:
        return self.executor.prepare_write_bundle_submission_message(
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )

    def prepare_submission_message_dict(
        self,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        consume: bool = False,
    ) -> dict[str, Any] | None:
        message = self.prepare_submission_message(
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )
        return self._to_dict_or_none(message)

    def submit_candidate(
        self,
        candidate: WriteBundleCandidate | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        consume: bool = False,
        ) -> WriteBundleResponseMessage | None:
        return self.executor.submit_write_bundle_candidate_local_message(
            candidate=candidate,
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )

    def submit_candidate_and_query(
        self,
        candidate: WriteBundleCandidate | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        consume: bool = False,
    ) -> tuple[WriteBundleResponseMessage | None, LocalWriteQueryResult | None]:
        response = self.submit_candidate(
            candidate=candidate,
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )
        if response is None:
            return None, None
        return response, self.query_write(response.correlation_id)

    def submit_candidate_and_trace(
        self,
        candidate: WriteBundleCandidate | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        consume: bool = False,
    ) -> tuple[WriteBundleResponseMessage | None, LocalHostTrace | None]:
        response = self.submit_candidate(
            candidate=candidate,
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )
        if response is None:
            return None, None
        return response, self.query_write_trace(response.correlation_id)

    def submit_candidate_and_trace_dict(
        self,
        candidate: WriteBundleCandidate | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        consume: bool = False,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        response, trace = self.submit_candidate_and_trace(
            candidate=candidate,
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )
        return (
            self._to_dict_or_none(response),
            self._to_dict_or_none(trace),
        )

    def submit_candidate_and_trace_json(
        self,
        candidate: WriteBundleCandidate | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        consume: bool = False,
    ) -> tuple[str | None, str | None]:
        response, trace = self.submit_candidate_and_trace(
            candidate=candidate,
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )
        return (
            self._to_json_or_none(response),
            self._to_json_or_none(trace),
        )

    def submit_candidate_and_query_dict(
        self,
        candidate: WriteBundleCandidate | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        consume: bool = False,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        response, query_result = self.submit_candidate_and_query(
            candidate=candidate,
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )
        return (
            self._to_dict_or_none(response),
            self._to_dict_or_none(query_result),
        )

    def submit_candidate_and_query_json(
        self,
        candidate: WriteBundleCandidate | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        consume: bool = False,
    ) -> tuple[str | None, str | None]:
        response, query_result = self.submit_candidate_and_query(
            candidate=candidate,
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )
        return (
            self._to_json_or_none(response),
            self._to_json_or_none(query_result),
        )

    def submit_message(
        self,
        message: WriteBundleSubmissionMessage,
        metadata: dict[str, Any] | None = None,
    ) -> WriteBundleResponseMessage:
        return self.executor.submit_write_bundle_submission_message_local_message(
            message,
            metadata=metadata,
        )

    def submit_message_dict(
        self,
        message: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> WriteBundleResponseMessage:
        return self.submit_message(
            WriteBundleSubmissionMessage.from_dict(dict(message)),
            metadata=metadata,
        )

    def submit_message_and_query(
        self,
        message: WriteBundleSubmissionMessage,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[WriteBundleResponseMessage, LocalWriteQueryResult]:
        response = self.submit_message(message, metadata=metadata)
        return response, self.query_write(response.correlation_id)

    def submit_message_and_query_dict(
        self,
        message: WriteBundleSubmissionMessage,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        response, query_result = self.submit_message_and_query(message, metadata=metadata)
        return self._to_dict(response), self._to_dict(query_result)

    def submit_message_and_query_json(
        self,
        message: WriteBundleSubmissionMessage,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[str, str]:
        response, query_result = self.submit_message_and_query(message, metadata=metadata)
        return self._to_json(response), self._to_json(query_result)

    def submit_message_and_trace(
        self,
        message: WriteBundleSubmissionMessage,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[WriteBundleResponseMessage, LocalHostTrace | None]:
        response = self.submit_message(message, metadata=metadata)
        return response, self.query_write_trace(response.correlation_id)

    def submit_message_and_trace_dict(
        self,
        message: WriteBundleSubmissionMessage,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        response, trace = self.submit_message_and_trace(message, metadata=metadata)
        return self._to_dict(response), self._to_dict_or_none(trace)

    def submit_message_and_trace_json(
        self,
        message: WriteBundleSubmissionMessage,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[str, str | None]:
        response, trace = self.submit_message_and_trace(message, metadata=metadata)
        return self._to_json(response), self._to_json_or_none(trace)

    def submit_message_dict_and_query(
        self,
        message: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> tuple[WriteBundleResponseMessage, LocalWriteQueryResult]:
        response = self.submit_message_dict(message, metadata=metadata)
        return response, self.query_write(response.correlation_id)

    def submit_message_dict_and_trace(
        self,
        message: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> tuple[WriteBundleResponseMessage, LocalHostTrace | None]:
        response = self.submit_message_dict(message, metadata=metadata)
        return response, self.query_write_trace(response.correlation_id)

    def submit_message_dict_and_trace_json(
        self,
        message: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> tuple[str, str | None]:
        response, trace = self.submit_message_dict_and_trace(message, metadata=metadata)
        return self._to_json(response), self._to_json_or_none(trace)

    def submit_message_dict_and_query_json(
        self,
        message: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> tuple[str, str]:
        response, query_result = self.submit_message_dict_and_query(
            message,
            metadata=metadata,
        )
        return self._to_json(response), self._to_json(query_result)

    def query_write(self, correlation_id: str) -> LocalWriteQueryResult:
        return self.executor.query_local_write_result(correlation_id)

    def query_write_status(self, correlation_id: str) -> str:
        return self.executor.query_local_write_status(correlation_id)

    def clear_write_state(self) -> None:
        self.executor.clear_local_write_state()

    def reset(self) -> None:
        """Clear graph state and local write state for host reuse."""
        self.executor.graph_backend.graph.clear()
        self.clear_write_state()

    def query_write_by_submission_id(self, submission_id: str) -> LocalWriteQueryResult:
        return self.executor.query_local_write_result_by_submission_id(submission_id)

    def query_write_status_by_submission_id(self, submission_id: str) -> str:
        return self.executor.query_local_write_status_by_submission_id(submission_id)

    def query_write_payload_kind(self, correlation_id: str) -> str | None:
        return self.executor.query_local_write_payload_kind(correlation_id)

    def query_write_payload_kind_by_submission_id(
        self,
        submission_id: str,
    ) -> str | None:
        return self.executor.query_local_write_payload_kind_by_submission_id(submission_id)

    def query_write_header(self, correlation_id: str) -> LocalWriteHeader:
        return self.executor.query_local_write_header(correlation_id)

    def query_write_header_by_submission_id(
        self,
        submission_id: str,
    ) -> LocalWriteHeader:
        return self.executor.query_local_write_header_by_submission_id(submission_id)

    def export_write_headers(self) -> list[LocalWriteHeader]:
        return self.executor.export_local_write_headers()

    def query_write_headers(self, status: str | None = None) -> list[LocalWriteHeader]:
        return self.executor.query_local_write_headers(status=status)

    def export_write_headers_json(self) -> str:
        return self.executor.export_local_write_headers_json()

    def query_write_headers_json(self, status: str | None = None) -> str:
        return self.executor.query_local_write_headers_json(status=status)

    def query_write_header_dict(self, correlation_id: str) -> dict[str, Any]:
        return self.executor.query_local_write_header_dict(correlation_id)

    def query_write_header_dict_by_submission_id(
        self,
        submission_id: str,
    ) -> dict[str, Any]:
        return self.executor.query_local_write_header_dict_by_submission_id(submission_id)

    def query_write_header_json(self, correlation_id: str) -> str:
        return self.executor.query_local_write_header_json(correlation_id)

    def query_write_header_json_by_submission_id(self, submission_id: str) -> str:
        return self.executor.query_local_write_header_json_by_submission_id(submission_id)

    def export_write_header_history(self) -> list[dict[str, Any]]:
        return self.executor.export_local_write_header_history()

    def export_write_header_history_json(self) -> str:
        return self.executor.export_local_write_header_history_json()

    def export_write_header_history_by_status(self, status: str) -> list[dict[str, Any]]:
        return self.executor.export_local_write_header_history_by_status(status)

    def export_write_header_history_json_by_status(self, status: str) -> str:
        return self.executor.export_local_write_header_history_json_by_status(status)

    def query_write_dict(self, correlation_id: str) -> dict[str, Any]:
        return self.executor.query_local_write_result_dict(correlation_id)

    def query_write_dict_by_submission_id(self, submission_id: str) -> dict[str, Any]:
        return self.executor.query_local_write_result_dict_by_submission_id(submission_id)

    def query_write_json(self, correlation_id: str) -> str:
        return self.executor.query_local_write_result_json(correlation_id)

    def query_write_json_by_submission_id(self, submission_id: str) -> str:
        return self.executor.query_local_write_result_json_by_submission_id(
            submission_id
        )

    def query_write_trace(self, correlation_id: str) -> LocalHostTrace | None:
        trace = self.executor.query_local_write_trace(correlation_id)
        if trace is None:
            return None
        return LocalHostTrace.from_runtime(trace)

    def query_write_trace_by_submission_id(
        self,
        submission_id: str,
    ) -> LocalHostTrace | None:
        trace = self.executor.query_local_write_trace_by_submission_id(submission_id)
        if trace is None:
            return None
        return LocalHostTrace.from_runtime(trace)

    def query_write_trace_dict(self, correlation_id: str) -> dict[str, Any] | None:
        trace = self.query_write_trace(correlation_id)
        return self._to_dict_or_none(trace)

    def query_write_trace_dict_by_submission_id(
        self,
        submission_id: str,
    ) -> dict[str, Any] | None:
        trace = self.query_write_trace_by_submission_id(submission_id)
        return self._to_dict_or_none(trace)

    def query_write_trace_json(self, correlation_id: str) -> str | None:
        return self.executor.query_local_write_trace_json(correlation_id)

    def query_write_trace_json_by_submission_id(
        self,
        submission_id: str,
    ) -> str | None:
        return self.executor.query_local_write_trace_json_by_submission_id(
            submission_id
        )

    def peek_write_response_message(
        self,
        correlation_id: str,
    ) -> WriteBundleResponseMessage | None:
        return self.executor.peek_local_write_response_message(correlation_id)

    def peek_write_response_message_by_submission_id(
        self,
        submission_id: str,
    ) -> WriteBundleResponseMessage | None:
        return self.executor.peek_local_write_response_message_by_submission_id(
            submission_id
        )

    def query_write_response_message_dict(
        self,
        correlation_id: str,
    ) -> dict[str, Any] | None:
        return self.executor.query_local_write_response_message_dict(correlation_id)

    def query_write_response_message_json(
        self,
        correlation_id: str,
    ) -> str | None:
        return self.executor.query_local_write_response_message_json(correlation_id)

    def query_write_response_message_dict_by_submission_id(
        self,
        submission_id: str,
    ) -> dict[str, Any] | None:
        return self.executor.query_local_write_response_message_dict_by_submission_id(
            submission_id
        )

    def query_write_response_message_json_by_submission_id(
        self,
        submission_id: str,
    ) -> str | None:
        return self.executor.query_local_write_response_message_json_by_submission_id(
            submission_id
        )

    def peek_write_submission_message(
        self,
        correlation_id: str,
    ) -> WriteBundleSubmissionMessage | None:
        return self.executor.peek_local_write_submission_message(correlation_id)

    def peek_write_submission_message_by_submission_id(
        self,
        submission_id: str,
    ) -> WriteBundleSubmissionMessage | None:
        return self.executor.peek_local_write_submission_message_by_submission_id(
            submission_id
        )

    def query_write_submission_message_dict(
        self,
        correlation_id: str,
    ) -> dict[str, Any] | None:
        return self.executor.query_local_write_submission_message_dict(correlation_id)

    def query_write_submission_message_json(
        self,
        correlation_id: str,
    ) -> str | None:
        return self.executor.query_local_write_submission_message_json(correlation_id)

    def query_write_submission_message_dict_by_submission_id(
        self,
        submission_id: str,
    ) -> dict[str, Any] | None:
        return self.executor.query_local_write_submission_message_dict_by_submission_id(
            submission_id
        )

    def query_write_submission_message_json_by_submission_id(
        self,
        submission_id: str,
    ) -> str | None:
        return self.executor.query_local_write_submission_message_json_by_submission_id(
            submission_id
        )

    def peek_write_submission_record(
        self,
        correlation_id: str,
    ) -> LocalWriteSubmissionRecord | None:
        return self.executor.peek_local_write_submission_record(correlation_id)

    def peek_write_submission_record_by_submission_id(
        self,
        submission_id: str,
    ) -> LocalWriteSubmissionRecord | None:
        return self.executor.peek_local_write_submission_record_by_submission_id(
            submission_id
        )

    def query_write_submission_record_dict(
        self,
        correlation_id: str,
    ) -> dict[str, Any] | None:
        return self.executor.query_local_write_submission_record_dict(correlation_id)

    def query_write_submission_record_json(
        self,
        correlation_id: str,
    ) -> str | None:
        return self.executor.query_local_write_submission_record_json(correlation_id)

    def query_write_submission_record_dict_by_submission_id(
        self,
        submission_id: str,
    ) -> dict[str, Any] | None:
        return self.executor.query_local_write_submission_record_dict_by_submission_id(
            submission_id
        )

    def query_write_submission_record_json_by_submission_id(
        self,
        submission_id: str,
    ) -> str | None:
        return self.executor.query_local_write_submission_record_json_by_submission_id(
            submission_id
        )

    def export_write_response_messages(self) -> list[WriteBundleResponseMessage]:
        return self.executor.export_local_write_response_messages()

    def export_write_response_messages_json(self) -> str:
        return WriteBundleResponseMessage.to_json_many(
            self.export_write_response_messages()
        )

    def query_write_response_messages(
        self, status: str | None = None
    ) -> list[WriteBundleResponseMessage]:
        return self.executor.query_local_write_response_messages(status=status)

    def query_write_response_messages_json(self, status: str | None = None) -> str:
        return WriteBundleResponseMessage.to_json_many(
            self.query_write_response_messages(status=status)
        )

    def export_write_response_history(self) -> list[dict[str, Any]]:
        return self.executor.export_local_write_response_history()

    def export_write_response_history_json(self) -> str:
        return self.executor.export_local_write_response_history_json()

    def export_write_response_history_by_status(
        self,
        status: str,
    ) -> list[dict[str, Any]]:
        return self.executor.export_local_write_response_history_by_status(status)

    def export_write_response_history_json_by_status(self, status: str) -> str:
        return self.executor.export_local_write_response_history_json_by_status(status)

    def export_write_submission_messages(self) -> list[WriteBundleSubmissionMessage]:
        return self.executor.export_local_write_submission_messages()

    def export_write_submission_messages_json(self) -> str:
        return WriteBundleSubmissionMessage.to_json_many(
            self.export_write_submission_messages()
        )

    def query_write_submission_messages(
        self, status: str | None = None
    ) -> list[WriteBundleSubmissionMessage]:
        return self.executor.query_local_write_submission_messages(status=status)

    def query_write_submission_messages_json(self, status: str | None = None) -> str:
        return WriteBundleSubmissionMessage.to_json_many(
            self.query_write_submission_messages(status=status)
        )

    def export_write_submission_records(self) -> list[LocalWriteSubmissionRecord]:
        return self.executor.export_local_write_submission_records()

    def export_write_submission_records_json(self) -> str:
        return LocalWriteSubmissionRecord.to_json_many(
            self.export_write_submission_records()
        )

    def query_write_submission_records(
        self, status: str | None = None
    ) -> list[LocalWriteSubmissionRecord]:
        return self.executor.query_local_write_submission_records(status=status)

    def query_write_submission_records_json(self, status: str | None = None) -> str:
        return LocalWriteSubmissionRecord.to_json_many(
            self.query_write_submission_records(status=status)
        )

    def export_write_submission_history(self) -> list[dict[str, Any]]:
        return self.executor.export_local_write_submission_history()

    def export_write_submission_history_json(self) -> str:
        return self.executor.export_local_write_submission_history_json()

    def export_write_submission_history_by_status(
        self,
        status: str,
    ) -> list[dict[str, Any]]:
        return self.executor.export_local_write_submission_history_by_status(status)

    def export_write_submission_history_json_by_status(self, status: str) -> str:
        return self.executor.export_local_write_submission_history_json_by_status(
            status
        )

    def export_write_submission_message_history(self) -> list[dict[str, Any]]:
        return self.executor.export_local_write_submission_message_history()

    def export_write_submission_message_history_json(self) -> str:
        return self.executor.export_local_write_submission_message_history_json()

    def export_write_submission_message_history_by_status(
        self,
        status: str,
    ) -> list[dict[str, Any]]:
        return self.executor.export_local_write_submission_message_history_by_status(status)

    def export_write_submission_message_history_json_by_status(self, status: str) -> str:
        return self.executor.export_local_write_submission_message_history_json_by_status(
            status
        )

    def export_write_traces(self) -> list[LocalHostTrace]:
        return [
            LocalHostTrace.from_runtime(trace)
            for trace in self.executor.export_local_write_traces()
        ]

    def query_write_traces(self, status: str | None = None) -> list[LocalHostTrace]:
        return [
            LocalHostTrace.from_runtime(trace)
            for trace in self.executor.query_local_write_traces(status=status)
        ]

    def export_write_traces_json(self) -> str:
        return LocalHostTrace.to_json_many(self.export_write_traces())

    def query_write_traces_json(self, status: str | None = None) -> str:
        return LocalHostTrace.to_json_many(
            self.query_write_traces(status=status)
        )

    def export_write_trace_history(self) -> list[dict[str, Any]]:
        return self.executor.export_local_write_trace_history()

    def export_write_trace_history_json(self) -> str:
        return self.executor.export_local_write_trace_history_json()

    def export_write_trace_history_by_status(
        self,
        status: str,
    ) -> list[dict[str, Any]]:
        return self.executor.export_local_write_trace_history_by_status(status)

    def export_write_trace_history_json_by_status(self, status: str) -> str:
        return self.executor.export_local_write_trace_history_json_by_status(status)

    def query_writes(self, status: str | None = None) -> list[LocalWriteQueryResult]:
        return self.executor.query_local_write_results(status=status)

    def export_write_query_results(self) -> list[dict[str, Any]]:
        return self.executor.export_local_write_query_results()

    def export_write_query_results_json(self) -> str:
        return self.executor.export_local_write_query_results_json()

    def export_write_query_results_by_status(
        self,
        status: str,
    ) -> list[dict[str, Any]]:
        return self.executor.export_local_write_query_results_by_status(status)

    def export_write_query_results_json_by_status(self, status: str) -> str:
        return self.executor.export_local_write_query_results_json_by_status(status)

    def export_snapshot(self) -> LocalHostSnapshot:
        return LocalHostSnapshot.from_host(self)

    def export_snapshot_dict(self) -> dict[str, Any]:
        return self.export_snapshot().to_dict()

    def export_snapshot_json(self) -> str:
        return self.export_snapshot().to_json()

    def clone(self) -> "LocalCogLangHost":
        """Return an independent host rebuilt from the current typed snapshot."""
        return self.from_snapshot(self.export_snapshot())

    def restore(self, snapshot: LocalHostSnapshot | dict[str, Any]) -> None:
        """Replace the current host state from a typed or dict-form snapshot."""
        rebuilt = self.from_snapshot(snapshot)
        self.executor = rebuilt.executor

    def restore_snapshot_json(self, payload: str) -> None:
        self.restore(LocalHostSnapshot.from_json(payload))

    def export_summary(self) -> LocalHostSummary:
        return LocalHostSummary.from_host(self)

    def export_summary_dict(self) -> dict[str, Any]:
        return self.export_summary().to_dict()

    def export_summary_json(self) -> str:
        return self.export_summary().to_json()

    def export_state(self) -> dict[str, Any]:
        """Return a transport-safe snapshot of the minimal local host state."""
        return {
            "graph": self.executor.graph_backend.to_dict(),
            "write_submission_history": self.executor.export_local_write_submission_history(),
        }

    def export_state_json(self) -> str:
        return json.dumps(self.export_state(), ensure_ascii=False, sort_keys=True)

    def restore_state(self, data: dict[str, Any]) -> None:
        """Replace the current host state from export_state() output."""
        rebuilt = self.from_state(data)
        self.executor = rebuilt.executor

    def restore_state_json(self, payload: str) -> None:
        self.restore_state(json.loads(payload))

    @classmethod
    def from_state(cls, data: dict[str, Any]) -> "LocalCogLangHost":
        """Rebuild a LocalCogLangHost from export_state() output."""
        backend = GraphBackend.from_dict(dict(data["graph"]))
        host = cls(backend.graph)
        records = [
            LocalWriteSubmissionRecord.from_dict(dict(item))
            for item in data.get("write_submission_history", [])
        ]
        host.executor.write_submission_history = list(records)
        host.executor.write_response_history = [record.response for record in records]
        host.executor._write_submission_index = {
            record.correlation_id: record for record in records
        }
        host.executor._write_submission_by_submission_id = {
            record.submission_id: record for record in records
        }
        host.executor._write_response_index = {
            record.correlation_id: record.response for record in records
        }
        return host

    @classmethod
    def from_snapshot(
        cls,
        snapshot: LocalHostSnapshot | dict[str, Any],
    ) -> "LocalCogLangHost":
        """Rebuild a LocalCogLangHost from a typed or dict-form snapshot."""
        if isinstance(snapshot, LocalHostSnapshot):
            typed_snapshot = snapshot
        else:
            typed_snapshot = LocalHostSnapshot.from_dict(snapshot)

        backend = GraphBackend.from_dict(dict(typed_snapshot.graph))
        host = cls(backend.graph)
        requests_by_correlation: dict[str, WriteBundleSubmissionMessage] = {
            request.correlation_id: request
            for request in typed_snapshot.write_submission_messages
        }
        responses_by_correlation: dict[str, WriteBundleResponseMessage] = {
            response.correlation_id: response
            for response in typed_snapshot.write_response_messages
        }
        records_by_correlation: dict[str, LocalWriteSubmissionRecord] = {
            record.correlation_id: record
            for record in typed_snapshot.write_submission_records
        }
        for trace in typed_snapshot.write_traces:
            requests_by_correlation.setdefault(trace.correlation_id, trace.request)
            responses_by_correlation.setdefault(trace.correlation_id, trace.response)
            records_by_correlation.setdefault(trace.correlation_id, trace.record)
        for record in records_by_correlation.values():
            requests_by_correlation.setdefault(record.correlation_id, record.request)
            responses_by_correlation.setdefault(record.correlation_id, record.response)

        for correlation_id, request in requests_by_correlation.items():
            if correlation_id in records_by_correlation:
                continue
            response = responses_by_correlation.get(correlation_id)
            if response is None:
                continue
            records_by_correlation[correlation_id] = LocalWriteSubmissionRecord(
                correlation_id=request.correlation_id,
                submission_id=request.submission_id,
                request=request,
                response=response,
                status=local_write_status_from_response(response),
            )

        records = list(records_by_correlation.values())
        responses = list(responses_by_correlation.values())

        host.executor.write_submission_history = list(records)
        host.executor.write_response_history = list(responses)
        host.executor._write_submission_index = {
            record.correlation_id: record for record in records
        }
        host.executor._write_submission_by_submission_id = {
            record.submission_id: record for record in records
        }
        host.executor._write_response_index = {
            response.correlation_id: response for response in responses
        }
        return host
