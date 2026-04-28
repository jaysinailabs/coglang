"""Reference transport host for CogLang write-message envelopes.

This host intentionally avoids the richer LocalCogLangHost API. It exists to
show that the public typed write envelope can be consumed by a separate host
implementation using only the graph backend and write-bundle contracts.
"""

from __future__ import annotations

from typing import Any

import networkx as nx

from .graph_backend import GraphBackend
from .write_bundle import (
    LocalWriteHeader,
    LocalWriteQueryResult,
    LocalWriteSubmissionRecord,
    WriteBundleResponseMessage,
    WriteBundleSubmissionMessage,
    local_write_header,
    local_write_query_result,
    local_write_status_from_response,
)


class ReferenceTransportHost:
    """Minimal host that accepts typed CogLang write-submission messages."""

    def __init__(self, graph: GraphBackend | nx.DiGraph | None = None):
        self.graph_backend = graph if isinstance(graph, GraphBackend) else GraphBackend(graph)
        self._submission_messages: list[WriteBundleSubmissionMessage] = []
        self._response_messages: list[WriteBundleResponseMessage] = []
        self._records: list[LocalWriteSubmissionRecord] = []
        self._responses_by_correlation_id: dict[str, WriteBundleResponseMessage] = {}
        self._records_by_correlation_id: dict[str, LocalWriteSubmissionRecord] = {}
        self._responses_by_submission_id: dict[str, WriteBundleResponseMessage] = {}
        self._records_by_submission_id: dict[str, LocalWriteSubmissionRecord] = {}

    @staticmethod
    def _coerce_submission_message(
        message: WriteBundleSubmissionMessage | dict[str, Any] | str,
    ) -> WriteBundleSubmissionMessage:
        if isinstance(message, WriteBundleSubmissionMessage):
            return message
        if isinstance(message, str):
            return WriteBundleSubmissionMessage.from_json(message)
        return WriteBundleSubmissionMessage.from_dict(message)

    def submit_message(
        self,
        message: WriteBundleSubmissionMessage | dict[str, Any] | str,
    ) -> WriteBundleResponseMessage:
        submission_message = self._coerce_submission_message(message)
        response_message = submission_message.submit_to_backend_response_message(
            self.graph_backend,
            metadata=submission_message.metadata,
        )
        record = LocalWriteSubmissionRecord(
            correlation_id=submission_message.correlation_id,
            submission_id=submission_message.submission_id,
            request=submission_message,
            response=response_message,
            status=local_write_status_from_response(response_message),
        )
        self._submission_messages.append(submission_message)
        self._response_messages.append(response_message)
        self._records.append(record)
        self._responses_by_correlation_id[submission_message.correlation_id] = response_message
        self._records_by_correlation_id[submission_message.correlation_id] = record
        self._responses_by_submission_id[submission_message.submission_id] = response_message
        self._records_by_submission_id[submission_message.submission_id] = record
        return response_message

    def submit_dict(self, message: dict[str, Any]) -> dict[str, Any]:
        return self.submit_message(message).to_dict()

    def submit_json(self, message: str) -> str:
        return self.submit_message(message).to_json()

    def response(self, correlation_id: str) -> WriteBundleResponseMessage:
        return self._responses_by_correlation_id[correlation_id]

    def record(self, correlation_id: str) -> LocalWriteSubmissionRecord:
        return self._records_by_correlation_id[correlation_id]

    def query_result(self, correlation_id: str) -> LocalWriteQueryResult:
        return local_write_query_result(
            correlation_id=correlation_id,
            response=self.response(correlation_id),
            record=self.record(correlation_id),
        )

    def query_header(self, correlation_id: str) -> LocalWriteHeader:
        return local_write_header(self.query_result(correlation_id))

    def export_state(self) -> dict[str, Any]:
        return {
            "graph": self.graph_backend.to_dict(),
            "submissions": [message.to_dict() for message in self._submission_messages],
            "responses": [message.to_dict() for message in self._response_messages],
            "records": [record.to_dict() for record in self._records],
        }
