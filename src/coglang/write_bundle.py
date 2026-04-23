from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any

from .graph_backend import GraphBackend
from .parser import CogLangExpr
from .vocab import ERROR_HEADS


@dataclass(frozen=True)
class WriteOperation:
    """A single write intent captured during CogLang evaluation."""

    op: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"op": self.op, "payload": dict(self.payload)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WriteOperation":
        return cls(op=str(data["op"]), payload=dict(data["payload"]))


@dataclass
class WriteBundleSubmissionResult:
    """Structured result for local host-side bundle validation and replay."""

    accepted: bool
    owner: str
    applied_ops: int = 0
    errors: list[str] = field(default_factory=list)
    phase_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "owner": self.owner,
            "applied_ops": self.applied_ops,
            "errors": list(self.errors),
            "phase_counts": dict(self.phase_counts),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WriteBundleSubmissionResult":
        return cls(
            accepted=bool(data["accepted"]),
            owner=str(data["owner"]),
            applied_ops=int(data.get("applied_ops", 0)),
            errors=[str(item) for item in data.get("errors", [])],
            phase_counts={str(k): int(v) for k, v in dict(data.get("phase_counts", {})).items()},
        )


@dataclass
class WriteBundleSubmissionMessage:
    """Typed host-facing message object for KnowledgeMessage write submission."""

    correlation_id: str
    submission_id: str
    candidate: "WriteBundleCandidate"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        envelope_metadata = {"owner": self.candidate.owner}
        envelope_metadata.update(dict(self.metadata))
        return {
            "header": {
                "message_type": "KnowledgeMessage",
                "operation": "submit_write_bundle",
                "correlation_id": self.correlation_id,
                "submission_id": self.submission_id,
            },
            "payload": {
                "candidate": self.candidate.to_dict(),
                "commit_plan": self.candidate.commit_plan(),
            },
            "metadata": envelope_metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def to_json_many(cls, items: list["WriteBundleSubmissionMessage"]) -> str:
        return json.dumps(
            [item.to_dict() for item in items],
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WriteBundleSubmissionMessage":
        header = dict(data.get("header", {}))
        payload = dict(data.get("payload", {}))
        metadata = dict(data.get("metadata", {}))
        return cls(
            correlation_id=str(header["correlation_id"]),
            submission_id=str(header.get("submission_id", uuid.uuid4())),
            candidate=WriteBundleCandidate.from_dict(payload["candidate"]),
            metadata=metadata,
        )

    @classmethod
    def from_json(cls, payload: str) -> "WriteBundleSubmissionMessage":
        return cls.from_dict(json.loads(payload))

    @classmethod
    def from_json_many(cls, payload: str) -> list["WriteBundleSubmissionMessage"]:
        return [cls.from_dict(dict(item)) for item in json.loads(payload)]

    def submit_to_backend(self, graph_backend: GraphBackend) -> "WriteResult | ErrorReport":
        """Submit this typed message locally and return a typed response object."""
        return self.candidate.submit_to_backend(
            graph_backend,
            correlation_id=self.correlation_id,
            submission_id=self.submission_id,
        )

    def submit_to_backend_response_message(
        self,
        graph_backend: GraphBackend,
        metadata: dict[str, Any] | None = None,
    ) -> "WriteBundleResponseMessage":
        """Submit this typed message locally and return a typed response envelope."""
        response = self.submit_to_backend(graph_backend)
        return response.response_message(metadata=metadata)


@dataclass
class WriteResult:
    """Local success receipt aligned with the architecture's write-response shape."""

    correlation_id: str
    submission_id: str
    owner: str
    commit_timestamp: str
    applied_ops: int = 0
    phase_counts: dict[str, int] = field(default_factory=dict)
    touched_node_ids: list[str] = field(default_factory=list)
    touched_edge_refs: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "submission_id": self.submission_id,
            "owner": self.owner,
            "commit_timestamp": self.commit_timestamp,
            "applied_ops": self.applied_ops,
            "phase_counts": dict(self.phase_counts),
            "touched_node_ids": list(self.touched_node_ids),
            "touched_edge_refs": [dict(item) for item in self.touched_edge_refs],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WriteResult":
        return cls(
            correlation_id=str(data["correlation_id"]),
            submission_id=str(data.get("submission_id", uuid.uuid4())),
            owner=str(data["owner"]),
            commit_timestamp=str(data["commit_timestamp"]),
            applied_ops=int(data.get("applied_ops", 0)),
            phase_counts={str(k): int(v) for k, v in dict(data.get("phase_counts", {})).items()},
            touched_node_ids=[str(item) for item in data.get("touched_node_ids", [])],
            touched_edge_refs=[dict(item) for item in data.get("touched_edge_refs", [])],
        )

    def response_message(
        self,
        metadata: dict[str, Any] | None = None,
    ) -> "WriteBundleResponseMessage":
        return WriteBundleResponseMessage(
            correlation_id=self.correlation_id,
            submission_id=self.submission_id,
            owner=self.owner,
            payload=self,
            metadata=dict(metadata or {}),
        )


@dataclass
class ErrorReport:
    """Local failure receipt aligned with the architecture's error-report shape."""

    correlation_id: str
    submission_id: str
    owner: str
    error_kind: str
    retryable: bool
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "submission_id": self.submission_id,
            "owner": self.owner,
            "error_kind": self.error_kind,
            "retryable": self.retryable,
            "errors": list(self.errors),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ErrorReport":
        return cls(
            correlation_id=str(data["correlation_id"]),
            submission_id=str(data.get("submission_id", uuid.uuid4())),
            owner=str(data["owner"]),
            error_kind=str(data["error_kind"]),
            retryable=bool(data["retryable"]),
            errors=[str(item) for item in data.get("errors", [])],
        )

    def response_message(
        self,
        metadata: dict[str, Any] | None = None,
    ) -> "WriteBundleResponseMessage":
        return WriteBundleResponseMessage(
            correlation_id=self.correlation_id,
            submission_id=self.submission_id,
            owner=self.owner,
            payload=self,
            metadata=dict(metadata or {}),
        )


@dataclass
class WriteBundleResponseMessage:
    """Typed host-facing response envelope for local write submission results."""

    correlation_id: str
    submission_id: str
    owner: str
    payload: WriteResult | ErrorReport
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload_kind = "WriteResult" if isinstance(self.payload, WriteResult) else "ErrorReport"
        envelope_metadata = {"owner": self.owner}
        envelope_metadata.update(dict(self.metadata))
        return {
            "header": {
                "message_type": "KnowledgeMessage",
                "operation": "write_bundle_response",
                "correlation_id": self.correlation_id,
                "submission_id": self.submission_id,
                "payload_kind": payload_kind,
            },
            "payload": self.payload.to_dict(),
            "metadata": envelope_metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def to_json_many(cls, items: list["WriteBundleResponseMessage"]) -> str:
        return json.dumps(
            [item.to_dict() for item in items],
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WriteBundleResponseMessage":
        header = dict(data.get("header", {}))
        metadata = dict(data.get("metadata", {}))
        payload_kind = str(header.get("payload_kind", "ErrorReport"))
        payload_data = dict(data.get("payload", {}))
        if payload_kind == "WriteResult":
            payload: WriteResult | ErrorReport = WriteResult.from_dict(payload_data)
        else:
            payload = ErrorReport.from_dict(payload_data)
        return cls(
            correlation_id=str(header["correlation_id"]),
            submission_id=str(header.get("submission_id", getattr(payload, "submission_id", uuid.uuid4()))),
            owner=str(metadata.get("owner", payload.owner)),
            payload=payload,
            metadata=metadata,
        )

    @classmethod
    def from_json(cls, payload: str) -> "WriteBundleResponseMessage":
        return cls.from_dict(json.loads(payload))

    @classmethod
    def from_json_many(cls, payload: str) -> list["WriteBundleResponseMessage"]:
        return [cls.from_dict(dict(item)) for item in json.loads(payload)]


def local_write_status_from_response(
    response: WriteBundleResponseMessage | None,
) -> str:
    """Map a local typed response envelope to the minimal provenance-style status."""
    if response is None:
        return "not_found"
    if isinstance(response.payload, WriteResult):
        return "committed"
    return "failed"


@dataclass
class LocalWriteSubmissionRecord:
    """Minimal local provenance-style record for one write submission attempt."""

    correlation_id: str
    submission_id: str
    request: WriteBundleSubmissionMessage
    response: WriteBundleResponseMessage
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "submission_id": self.submission_id,
            "status": self.status,
            "request": self.request.to_dict(),
            "response": self.response.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def to_json_many(cls, items: list["LocalWriteSubmissionRecord"]) -> str:
        return json.dumps(
            [item.to_dict() for item in items],
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LocalWriteSubmissionRecord":
        request = WriteBundleSubmissionMessage.from_dict(dict(data["request"]))
        response = WriteBundleResponseMessage.from_dict(dict(data["response"]))
        return cls(
            correlation_id=str(data["correlation_id"]),
            submission_id=str(data["submission_id"]),
            request=request,
            response=response,
            status=str(data["status"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> "LocalWriteSubmissionRecord":
        return cls.from_dict(json.loads(payload))

    @classmethod
    def from_json_many(cls, payload: str) -> list["LocalWriteSubmissionRecord"]:
        return [cls.from_dict(dict(item)) for item in json.loads(payload)]


@dataclass
class LocalWriteQueryResult:
    """Typed local provenance-style query result for one correlation_id lookup."""

    correlation_id: str
    status: str
    response: WriteBundleResponseMessage | None = None
    record: LocalWriteSubmissionRecord | None = None
    requested_submission_id: str | None = None

    @property
    def submission_id(self) -> str | None:
        if self.record is not None:
            return self.record.submission_id
        if self.response is not None:
            return self.response.submission_id
        return self.requested_submission_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "status": self.status,
            "submission_id": self.submission_id,
            "response": None if self.response is None else self.response.to_dict(),
            "record": None if self.record is None else self.record.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def to_json_many(cls, items: list["LocalWriteQueryResult"]) -> str:
        return json.dumps(
            [item.to_dict() for item in items],
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LocalWriteQueryResult":
        response_data = data.get("response")
        record_data = data.get("record")
        return cls(
            correlation_id=str(data["correlation_id"]),
            status=str(data["status"]),
            response=(
                None
                if response_data is None
                else WriteBundleResponseMessage.from_dict(dict(response_data))
            ),
            record=(
                None
                if record_data is None
                else LocalWriteSubmissionRecord.from_dict(dict(record_data))
            ),
            requested_submission_id=(
                None
                if data.get("submission_id") in {None, ""}
                else str(data["submission_id"])
            ),
        )

    @classmethod
    def from_json(cls, payload: str) -> "LocalWriteQueryResult":
        return cls.from_dict(json.loads(payload))

    @classmethod
    def from_json_many(cls, payload: str) -> list["LocalWriteQueryResult"]:
        return [cls.from_dict(dict(item)) for item in json.loads(payload)]


@dataclass
class LocalWriteHeader:
    """Typed minimal host-facing header for one local write lookup."""

    correlation_id: str
    submission_id: str | None
    status: str
    payload_kind: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "submission_id": self.submission_id,
            "status": self.status,
            "payload_kind": self.payload_kind,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def to_json_many(cls, items: list["LocalWriteHeader"]) -> str:
        return json.dumps(
            [item.to_dict() for item in items],
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LocalWriteHeader":
        return cls(
            correlation_id=str(data["correlation_id"]),
            submission_id=(
                None if data.get("submission_id") is None else str(data["submission_id"])
            ),
            status=str(data["status"]),
            payload_kind=(
                None if data.get("payload_kind") is None else str(data["payload_kind"])
            ),
        )

    @classmethod
    def from_json(cls, payload: str) -> "LocalWriteHeader":
        return cls.from_dict(json.loads(payload))

    @classmethod
    def from_json_many(cls, payload: str) -> list["LocalWriteHeader"]:
        return [cls.from_dict(dict(item)) for item in json.loads(payload)]


def local_write_query_result(
    correlation_id: str,
    response: WriteBundleResponseMessage | None = None,
    record: LocalWriteSubmissionRecord | None = None,
    requested_submission_id: str | None = None,
) -> LocalWriteQueryResult:
    """Build a typed local provenance-style query result for one correlation_id."""
    return LocalWriteQueryResult(
        correlation_id=correlation_id,
        status=local_write_status_from_response(response),
        response=response,
        record=record,
        requested_submission_id=requested_submission_id,
    )


def local_write_header(
    query_result: LocalWriteQueryResult,
) -> LocalWriteHeader:
    payload_kind: str | None = None
    if query_result.response is not None:
        payload_kind = (
            "WriteResult"
            if isinstance(query_result.response.payload, WriteResult)
            else "ErrorReport"
        )
    return LocalWriteHeader(
        correlation_id=query_result.correlation_id,
        submission_id=query_result.submission_id,
        status=query_result.status,
        payload_kind=payload_kind,
    )


@dataclass
class LocalWriteTrace:
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
    def to_json_many(cls, items: list["LocalWriteTrace"]) -> str:
        return json.dumps(
            [item.to_dict() for item in items],
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LocalWriteTrace":
        return cls(
            correlation_id=str(data["correlation_id"]),
            submission_id=str(data["submission_id"]),
            request=WriteBundleSubmissionMessage.from_dict(dict(data["request"])),
            response=WriteBundleResponseMessage.from_dict(dict(data["response"])),
            record=LocalWriteSubmissionRecord.from_dict(dict(data["record"])),
            query_result=LocalWriteQueryResult.from_dict(dict(data["query_result"])),
        )

    @classmethod
    def from_json(cls, payload: str) -> "LocalWriteTrace":
        return cls.from_dict(json.loads(payload))

    @classmethod
    def from_json_many(cls, payload: str) -> list["LocalWriteTrace"]:
        return [cls.from_dict(dict(item)) for item in json.loads(payload)]


@dataclass
class WriteBundleCandidate:
    """Ordered write intents emitted by one top-level CogLang evaluation."""

    owner: str
    base_node_ids: set[str] = field(default_factory=set)
    operations: list[WriteOperation] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "owner": self.owner,
            "base_node_ids": sorted(self.base_node_ids),
            "operations": [operation.to_dict() for operation in self.operations],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WriteBundleCandidate":
        return cls(
            owner=str(data["owner"]),
            base_node_ids=set(data.get("base_node_ids", [])),
            operations=[
                WriteOperation.from_dict(item)
                for item in data.get("operations", [])
            ],
        )

    def validate_against_existing_ids(self, existing_ids: set[str]) -> tuple[bool, list[str]]:
        """Validate bundle-local references against persisted and earlier-local IDs."""
        errors: list[str] = []
        seen_local_ids: set[str] = set()
        allowed_ops = {
            "create_node",
            "create_edge",
            "update_node",
            "delete_node",
            "delete_edge",
        }

        for index, operation in enumerate(self.operations):
            if operation.op not in allowed_ops:
                errors.append(f"op[{index}] unknown op '{operation.op}'")
                continue
            payload = operation.payload

            if operation.op == "create_node":
                node_id = payload.get("id")
                if not isinstance(node_id, str):
                    errors.append(f"op[{index}] create_node missing string id")
                    continue
                if node_id in existing_ids:
                    errors.append(f"op[{index}] create_node duplicates persisted id '{node_id}'")
                if node_id in seen_local_ids:
                    errors.append(f"op[{index}] create_node duplicates local id '{node_id}'")
                seen_local_ids.add(node_id)
                continue

            refs: list[tuple[str, Any]] = []
            if operation.op == "create_edge":
                refs = [
                    ("source_id", payload.get("source_id")),
                    ("target_id", payload.get("target_id")),
                ]
            elif operation.op in {"update_node", "delete_node"}:
                refs = [("target_id", payload.get("target_id"))]
            elif operation.op == "delete_edge":
                refs = [
                    ("source_id", payload.get("source_id")),
                    ("target_id", payload.get("target_id")),
                ]

            for field, ref in refs:
                if not isinstance(ref, str):
                    errors.append(f"op[{index}] {operation.op} missing string {field}")
                    continue
                if ref in existing_ids:
                    continue
                if ref in seen_local_ids:
                    continue
                errors.append(f"op[{index}] {operation.op} has unresolved {field} '{ref}'")

        return len(errors) == 0, errors

    def commit_ordered_operations(self) -> list[WriteOperation]:
        """Return operations reordered for commit: nodes, then edges, then update/delete."""
        phase_order = {
            "create_node": 0,
            "create_edge": 1,
            "update_node": 2,
            "delete_node": 2,
            "delete_edge": 2,
        }
        indexed = list(enumerate(self.operations))
        indexed.sort(key=lambda item: (phase_order.get(item[1].op, 99), item[0]))
        return [operation for _, operation in indexed]

    def commit_plan(self) -> dict[str, list[dict[str, Any]]]:
        """Return a serializable commit plan grouped by REV-33 phases."""
        phases = {
            "phase_1a_create_nodes": [],
            "phase_1b_create_edges": [],
            "phase_1c_update_delete": [],
        }
        for operation in self.commit_ordered_operations():
            if operation.op == "create_node":
                phases["phase_1a_create_nodes"].append(operation.to_dict())
            elif operation.op == "create_edge":
                phases["phase_1b_create_edges"].append(operation.to_dict())
            else:
                phases["phase_1c_update_delete"].append(operation.to_dict())
        return phases

    def submission_payload(
        self,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return a transport-safe submission envelope for host-side WriteBundle flow."""
        return self.submission_message(correlation_id=correlation_id, metadata=metadata).to_dict()

    def submission_message(
        self,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WriteBundleSubmissionMessage:
        """Return a typed host-facing message object for write submission."""
        return WriteBundleSubmissionMessage(
            correlation_id=correlation_id or str(uuid.uuid4()),
            submission_id=str(uuid.uuid4()),
            candidate=self,
            metadata=dict(metadata or {}),
        )

    def apply_to_backend(self, graph_backend: GraphBackend) -> WriteBundleSubmissionResult:
        """Validate and atomically replay this bundle against a target backend."""
        phase_counts = {
            "phase_1a_create_nodes": 0,
            "phase_1b_create_edges": 0,
            "phase_1c_update_delete": 0,
        }
        is_valid, errors = self.validate_against_existing_ids(set(graph_backend.graph.nodes))
        if not is_valid:
            return WriteBundleSubmissionResult(
                accepted=False,
                owner=self.owner,
                applied_ops=0,
                errors=errors,
                phase_counts=phase_counts,
            )

        trial_backend = GraphBackend.from_dict(graph_backend.to_dict())
        ordered = self.commit_ordered_operations()

        for index, operation in enumerate(ordered):
            payload = operation.payload
            if operation.op == "create_node":
                result = trial_backend.create_node(payload["node_type"], payload["attrs"])
                phase_counts["phase_1a_create_nodes"] += 1
            elif operation.op == "create_edge":
                result = trial_backend.create_edge(
                    payload["source_id"],
                    payload["target_id"],
                    payload.get("relation", payload.get("relation_type")),
                    payload.get("confidence", 1.0),
                )
                phase_counts["phase_1b_create_edges"] += 1
            elif operation.op == "update_node":
                result = trial_backend.update(payload["target_id"], payload["changes"])
                phase_counts["phase_1c_update_delete"] += 1
            elif operation.op == "delete_node":
                result = trial_backend.delete_node(payload["target_id"])
                phase_counts["phase_1c_update_delete"] += 1
            elif operation.op == "delete_edge":
                result = trial_backend.delete_edge(
                    payload["source_id"],
                    payload["target_id"],
                    payload.get("relation", payload.get("relation_type")),
                )
                phase_counts["phase_1c_update_delete"] += 1
            else:
                return WriteBundleSubmissionResult(
                    accepted=False,
                    owner=self.owner,
                    applied_ops=0,
                    errors=[f"op[{index}] unknown op '{operation.op}'"],
                    phase_counts={
                        "phase_1a_create_nodes": 0,
                        "phase_1b_create_edges": 0,
                        "phase_1c_update_delete": 0,
                    },
                )

            if isinstance(result, CogLangExpr) and result.head in ERROR_HEADS:
                return WriteBundleSubmissionResult(
                    accepted=False,
                    owner=self.owner,
                    applied_ops=0,
                    errors=[f"op[{index}] {operation.op} failed with {result.head}"],
                    phase_counts={
                        "phase_1a_create_nodes": 0,
                        "phase_1b_create_edges": 0,
                        "phase_1c_update_delete": 0,
                    },
                )

        graph_backend.graph = trial_backend.graph
        graph_backend._next_id = trial_backend._next_id
        return WriteBundleSubmissionResult(
            accepted=True,
            owner=self.owner,
            applied_ops=len(ordered),
            errors=[],
            phase_counts=phase_counts,
        )

    def submit_to_backend(
        self,
        graph_backend: GraphBackend,
        correlation_id: str | None = None,
        submission_id: str | None = None,
    ) -> WriteResult | ErrorReport:
        """Return architecture-shaped success/failure receipts for local host submission."""
        cid = correlation_id or str(uuid.uuid4())
        sid = submission_id or str(uuid.uuid4())
        result = self.apply_to_backend(graph_backend)
        if not result.accepted:
            return ErrorReport(
                correlation_id=cid,
                submission_id=sid,
                owner=self.owner,
                error_kind="ValidationError",
                retryable=True,
                errors=list(result.errors),
            )

        touched_node_ids: list[str] = []
        touched_edge_refs: list[dict[str, str]] = []
        for operation in self.commit_ordered_operations():
            payload = operation.payload
            if operation.op == "create_node":
                touched_node_ids.append(str(payload["id"]))
            elif operation.op in {"update_node", "delete_node"}:
                touched_node_ids.append(str(payload["target_id"]))
            elif operation.op in {"create_edge", "delete_edge"}:
                touched_edge_refs.append(
                    {
                        "source_id": str(payload["source_id"]),
                        "relation": str(payload.get("relation", payload.get("relation_type"))),
                        "target_id": str(payload["target_id"]),
                    }
                )

        return WriteResult(
            correlation_id=cid,
            submission_id=sid,
            owner=self.owner,
            commit_timestamp=datetime.now(timezone.utc).isoformat(),
            applied_ops=result.applied_ops,
            phase_counts=dict(result.phase_counts),
            touched_node_ids=touched_node_ids,
            touched_edge_refs=touched_edge_refs,
        )

    def submit_to_backend_response_message(
        self,
        graph_backend: GraphBackend,
        correlation_id: str | None = None,
        submission_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WriteBundleResponseMessage:
        """Return a typed response envelope for local host submission."""
        response = self.submit_to_backend(
            graph_backend,
            correlation_id=correlation_id,
            submission_id=submission_id,
        )
        return response.response_message(metadata=metadata)
