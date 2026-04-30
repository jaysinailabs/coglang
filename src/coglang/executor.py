# CogLang executor.
# Implements PythonCogLangExecutor — the evaluation engine for CogLang expressions.
# Design notes in T1_handoff_s2c.md and T1_log.md (sessions 1, 3, 4).
from __future__ import annotations

import hashlib
import json
import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional

import networkx as nx

from .parser import CogLangExpr, CogLangVar, canonicalize
from .vocab import ERROR_HEADS
from .graph_backend import GraphBackend
from .unify_backend import get_unify_backend, UnifyBackend
from .write_bundle import (
    WriteBundleCandidate,
    ErrorReport,
    LocalWriteHeader,
    LocalWriteQueryResult,
    LocalWriteTrace,
    LocalWriteSubmissionRecord,
    local_write_header,
    local_write_query_result,
    local_write_status_from_response,
    WriteBundleResponseMessage,
    WriteBundleSubmissionMessage,
    WriteBundleSubmissionResult,
    WriteResult,
    WriteOperation,
)

MAX_DEPTH = 200


def _var_key(var: CogLangVar) -> str:
    """Canonical env dict key for a CogLangVar: first letter uppercased, no trailing '_'.

    Matches the key format used by the unify backend and ForEach/Query binding,
    so env lookups are consistent across all contexts.
    """
    name = var.name
    return name[0].upper() + name[1:]


def _typed_to_dict(value: Any | None) -> Optional[dict[str, Any]]:
    """Return a typed object's dict envelope while preserving missing lookups."""
    return None if value is None else value.to_dict()


def _typed_to_json(value: Any | None) -> Optional[str]:
    """Return a typed object's JSON envelope while preserving missing lookups."""
    return None if value is None else value.to_json()


def _typed_list_to_dicts(values: list[Any]) -> list[dict[str, Any]]:
    """Return dict envelopes for a homogeneous typed-object list."""
    return [value.to_dict() for value in values]


# ---------------------------------------------------------------------------
# Observer protocol (S2c-1)
# ---------------------------------------------------------------------------

class Observer(ABC):
    """Abstract observer for CogLang execution events (Trace / Assert)."""

    @abstractmethod
    def on_trace(self, expr: CogLangExpr, result: Any, depth: int) -> None:
        """Called after Trace[expr] evaluates; receives original AST, result, depth."""

    @abstractmethod
    def on_assert_fail(self, message: str, depth: int) -> None:
        """Called when Assert[condition, message] evaluates condition as falsy."""


class NullObserver(Observer):
    """No-op observer — discards all events (default for PythonCogLangExecutor)."""
    def on_trace(self, expr, result, depth): pass
    def on_assert_fail(self, message, depth): pass


# ---------------------------------------------------------------------------
# Executor ABC (S2c-1)
# ---------------------------------------------------------------------------

class CogLangExecutor(ABC):
    """Minimal abstract CogLang execution engine interface.

    This ABC intentionally covers only the semantic executor surface that a
    second implementation must provide. Host-local query helpers, dict/JSON
    export variants, and submission-id lookup conveniences belong on concrete
    runtimes such as PythonCogLangExecutor; they are not inheritance
    requirements for every executor implementation.
    """

    @abstractmethod
    def execute(self, expr: Any) -> Any:
        """Evaluate a CogLang expression and return the result."""

    @abstractmethod
    def validate(self, expr: Any) -> bool:
        """Return True if expr is a structurally valid CogLang expression."""

    def execute_with_write_bundle_candidate(
        self, expr: Any, env: Optional[dict] = None
    ) -> tuple[Any, Optional[WriteBundleCandidate]]:
        """Evaluate expr and return (result, write_bundle_candidate).

        Minimal executor implementations are not required to support local
        write-bundle candidates. Runtimes that need env-aware execution or
        write-candidate capture should override this method.
        """
        return self.execute(expr), self.peek_write_bundle_candidate()

    def peek_write_bundle_candidate(self) -> Optional[WriteBundleCandidate]:
        """Return the most recent write bundle candidate without consuming it."""
        return None

    def consume_write_bundle_candidate(self) -> Optional[WriteBundleCandidate]:
        """Return and clear the most recent write bundle candidate."""
        return None

    def validate_write_bundle_candidate(
        self, candidate: Optional[WriteBundleCandidate] = None
    ) -> tuple[bool, list[str]]:
        """Validate a write bundle candidate against the current graph snapshot."""
        if candidate is None:
            return True, []
        return False, ["write bundle candidates are not supported by this executor"]

    def set_observer(self, observer: Observer) -> None:
        """Inject an execution observer when a concrete runtime exposes one."""
        self.observer = observer


# ---------------------------------------------------------------------------
# PythonCogLangExecutor (S2c-2)
# ---------------------------------------------------------------------------

class PythonCogLangExecutor(CogLangExecutor):
    """Pure-Python CogLang evaluation engine backed by NetworkX + Robinson unification.

    Architecture (DL-013 method B):
      self.graph_backend — sole owner of nx.DiGraph; no self.graph attribute.
      self.unify_backend — cached once at __init__ (subprocess probe; TD-003 safety).
      self._user_ops     — dict of Compose-registered operations.
      self._dispatch     — built-in operation handlers (eager-eval'd args supplied).
      self._special_forms — handlers that control their own eval order.

    Error semantics (CogLang Principle 3):
      All errors are CogLangExpr values; no Python exceptions escape.
      Error propagation: if any eager-eval'd arg is an error value, short-circuit.
    """

    def __init__(
        self,
        graph: Optional[nx.DiGraph] = None,
        observer: Optional[Observer] = None,
        write_bundle_owner: str = "coglang_executor",
        abstract_trigger_min_instances: int = 5,
    ) -> None:
        # DL-013: GraphBackend is sole owner; executor never holds self.graph.
        self.graph_backend = GraphBackend(graph)
        # TD-003: cache backend to avoid repeated subprocess probe (~0.5s each).
        self.unify_backend: UnifyBackend = get_unify_backend()
        self.observer: Observer = observer if observer is not None else NullObserver()
        self.write_bundle_owner = write_bundle_owner
        self.abstract_trigger_min_instances = max(0, int(abstract_trigger_min_instances))
        # User-defined operations registered via Compose.
        self._user_ops: dict[str, dict] = {}
        self.last_write_bundle_candidate: Optional[WriteBundleCandidate] = None
        self.write_bundle_history: list[WriteBundleCandidate] = []
        self.write_response_history: list[WriteBundleResponseMessage] = []
        self.write_submission_history: list[LocalWriteSubmissionRecord] = []
        self._write_response_index: dict[str, WriteBundleResponseMessage] = {}
        self._write_submission_index: dict[str, LocalWriteSubmissionRecord] = {}
        self._write_submission_by_submission_id: dict[str, LocalWriteSubmissionRecord] = {}
        self._active_write_bundle_candidate: Optional[WriteBundleCandidate] = None
        self._query_budget_stack: list[int | str] = []
        self._query_depth_map_stack: list[dict[str, int]] = []

        # ------------------------------------------------------------------
        # Built-in dispatch: handlers called as fn(*evaled_args).
        # All args have already been eager-eval'd before reaching dispatch.
        # ------------------------------------------------------------------
        self._dispatch: dict[str, Any] = {
            # Transparent constructors for error heads (SCC-E5, TD-001).
            # execute(NotFound[]) must return NotFound[], not ParseError["unknown_head"].
            "NotFound":        lambda:       CogLangExpr("NotFound", ()),
            "TypeError":       lambda *a:    CogLangExpr("TypeError", tuple(a)),
            "PermissionError": lambda *a:    CogLangExpr("PermissionError", tuple(a)),
            "ParseError":      lambda *a:    CogLangExpr("ParseError", tuple(a)),
            "StubError":       lambda *a:    CogLangExpr("StubError", tuple(a)),
            "RecursionError":  lambda *a:    CogLangExpr("RecursionError", tuple(a)),
            # Boolean / state constructors
            "True":            lambda:       CogLangExpr("True", ()),
            "False":           lambda:       CogLangExpr("False", ()),
            "Deferred":        lambda *a:    CogLangExpr("Deferred", tuple(a)),
            "Draft":           lambda *a:    CogLangExpr("Draft", tuple(a)),
            "Published":       lambda *a:    CogLangExpr("Published", tuple(a)),
            # List constructor
            "List":            lambda *a:    CogLangExpr("List", tuple(a)),
            # Graph operations
            "Traverse":        self._do_traverse,
            "Create":          self._do_create,
            "Update":          self._do_update,
            "Delete":          self._do_delete,
            "AllNodes":        self._do_all_nodes,
            # Value operations
            "Get":             self._do_get,
            "Equal":           self._do_equal,
            "Compare":         self._do_compare,
            # Stub operations return StubError[op_name, ...args] for reserved operators.
            "Abstract":        self._do_abstract,
            "Instantiate": lambda *a: CogLangExpr("StubError", ("Instantiate",) + a),
            "Probe":       lambda *a: CogLangExpr("StubError", ("Probe",)       + a),
            "Explore":     lambda *a: CogLangExpr("StubError", ("Explore",)     + a),
            "Estimate":    lambda *a: CogLangExpr("StubError", ("Estimate",)    + a),
            "Decompose":   lambda *a: CogLangExpr("StubError", ("Decompose",)   + a),
            "Defer":       lambda *a: CogLangExpr("StubError", ("Defer",)       + a),
            "Resume":      lambda *a: CogLangExpr("StubError", ("Resume",)      + a),
            "Merge":       lambda *a: CogLangExpr("StubError", ("Merge",)       + a),
            "Explain":     lambda *a: CogLangExpr("StubError", ("Explain",)     + a),
            "Send":        lambda *a: CogLangExpr("StubError", ("Send",)        + a),
            "Inspect":     lambda *a: CogLangExpr("StubError", ("Inspect",)     + a),
        }

        # ------------------------------------------------------------------
        # Special Forms: each handler controls its own argument eval order.
        # Not in _dispatch; checked before eager eval.
        # ------------------------------------------------------------------
        self._special_forms: dict[str, Any] = {
            "If":      self._handle_if,
            "IfFound": self._handle_iffound,
            "ForEach": self._handle_foreach,
            "Do":      self._handle_do,
            "Compose": self._handle_compose,
            "Assert":  self._handle_assert,
            "Query":   self._handle_query,
            "Trace":   self._handle_trace,
            # Unify/Match: raw AST → unify_backend (vars must NOT be CogLang-eval'd)
            "Unify":   self._handle_unify,
            "Match":   self._handle_unify,  # alias
        }

    # ------------------------------------------------------------------
    # Core evaluate
    # ------------------------------------------------------------------

    def execute(self, expr: Any, env: Optional[dict] = None, _depth: int = 0) -> Any:
        """Evaluate a CogLang expression under variable environment env.

        Args:
            expr:    CogLangExpr | CogLangVar | str | int | float | bool | dict
            env:     variable bindings {canonical_key: value}; None → empty dict.
            _depth:  recursion depth counter (used for MAX_DEPTH guard).

        Returns:
            Evaluated CogLang value; never raises Python exceptions.
        """
        if env is None:
            env = {}

        top_level_call = _depth == 0 and self._active_write_bundle_candidate is None
        if top_level_call:
            self.last_write_bundle_candidate = None
            self._active_write_bundle_candidate = WriteBundleCandidate(
                owner=self.write_bundle_owner,
                base_node_ids=set(self.graph_backend.graph.nodes),
            )

        try:
            # Depth guard — returns CogLang error value, not Python exception.
            if _depth > MAX_DEPTH:
                return CogLangExpr("RecursionError", ("max_depth_exceeded",))

            # ① CogLangVar — look up in env.
            #    SCC-E1: MUST precede isinstance(expr, CogLangExpr) check.
            if isinstance(expr, CogLangVar):
                if expr.is_anonymous:
                    return expr               # anonymous var evaluates to itself
                key = _var_key(expr)
                if key in env:
                    return env[key]
                # Unbound variable → CogLang error value (not Python exception)
                return CogLangExpr("TypeError", ("unbound_variable", expr.name))

            # ② Literals: str / int / float / bool / dict → evaluate to themselves.
            if not isinstance(expr, CogLangExpr):
                return expr

            # ③ Special Forms — handler controls eval order.
            handler = self._special_forms.get(expr.head)
            if handler is not None:
                return handler(expr, env, _depth)

            # ④ Eager eval: evaluate all args before dispatch.
            # Dict args: evaluate values (allows computed attrs like {"name": Get[var_,"k"]}).
            # Dict keys are always literal strings and are not evaluated.
            evaled = tuple(
                {k: self.execute(v, env, _depth + 1) for k, v in a.items()}
                if isinstance(a, dict)
                else self.execute(a, env, _depth + 1)
                for a in expr.args
            )

            # ⑤ Error propagation (SCC-E2 + TD-001: isinstance guard required).
            #    Prevents node IDs that happen to equal ERROR_HEADS strings from
            #    triggering false short-circuit (e.g. a node named "NotFound").
            for arg in evaled:
                if isinstance(arg, CogLangExpr) and arg.head in ERROR_HEADS:
                    return arg

            # ⑥ User-defined operations (registered via Compose).
            if expr.head in self._user_ops:
                return self._call_user_op(expr.head, evaled, env, _depth)

            # ⑦ Built-in dispatch.
            fn = self._dispatch.get(expr.head)
            if fn is None:
                return CogLangExpr("ParseError", ("unknown_head", expr.head))
            return fn(*evaled)
        finally:
            if top_level_call:
                bundle = self._active_write_bundle_candidate
                if bundle is not None and bundle.operations:
                    self.last_write_bundle_candidate = bundle
                    self.write_bundle_history.append(bundle)
                self._active_write_bundle_candidate = None

    def execute_with_write_bundle_candidate(
        self, expr: Any, env: Optional[dict] = None
    ) -> tuple[Any, Optional[WriteBundleCandidate]]:
        result = self.execute(expr, env=env)
        return result, self.peek_write_bundle_candidate()

    def peek_write_bundle_candidate(self) -> Optional[WriteBundleCandidate]:
        return self.last_write_bundle_candidate

    def consume_write_bundle_candidate(self) -> Optional[WriteBundleCandidate]:
        bundle = self.last_write_bundle_candidate
        self.last_write_bundle_candidate = None
        return bundle

    def validate_write_bundle_candidate(
        self, candidate: Optional[WriteBundleCandidate] = None
    ) -> tuple[bool, list[str]]:
        bundle = candidate if candidate is not None else self.last_write_bundle_candidate
        if bundle is None:
            return True, []
        existing_ids = set(bundle.base_node_ids) if bundle.base_node_ids else set(self.graph_backend.graph.nodes)
        return bundle.validate_against_existing_ids(existing_ids)

    def prepare_write_bundle_submission_payload(
        self,
        correlation_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        consume: bool = False,
    ) -> Optional[dict[str, Any]]:
        message = self.prepare_write_bundle_submission_message(
            correlation_id=correlation_id,
            metadata=metadata,
            consume=consume,
        )
        return None if message is None else message.to_dict()

    def prepare_write_bundle_submission_message(
        self,
        correlation_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        consume: bool = False,
    ) -> Optional[WriteBundleSubmissionMessage]:
        bundle = self.consume_write_bundle_candidate() if consume else self.peek_write_bundle_candidate()
        if bundle is None:
            return None
        return bundle.submission_message(correlation_id=correlation_id, metadata=metadata)

    def apply_write_bundle_candidate(
        self,
        candidate: Optional[WriteBundleCandidate] = None,
        consume: bool = False,
    ) -> Optional[WriteBundleSubmissionResult]:
        bundle = candidate
        if bundle is None:
            bundle = self.consume_write_bundle_candidate() if consume else self.peek_write_bundle_candidate()
        if bundle is None:
            return None
        result = bundle.apply_to_backend(self.graph_backend)
        if consume and candidate is not None and self.last_write_bundle_candidate is bundle:
            self.last_write_bundle_candidate = None
        return result

    def submit_write_bundle_candidate_local(
        self,
        candidate: Optional[WriteBundleCandidate] = None,
        correlation_id: Optional[str] = None,
        consume: bool = False,
    ) -> Optional[WriteResult | ErrorReport]:
        response = self.submit_write_bundle_candidate_local_message(
            candidate=candidate,
            correlation_id=correlation_id,
            consume=consume,
        )
        return None if response is None else response.payload

    def submit_write_bundle_submission_message_local(
        self,
        message: WriteBundleSubmissionMessage,
    ) -> WriteResult | ErrorReport:
        return self.submit_write_bundle_submission_message_local_message(message).payload

    def submit_write_bundle_candidate_local_message(
        self,
        candidate: Optional[WriteBundleCandidate] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        consume: bool = False,
    ) -> Optional[WriteBundleResponseMessage]:
        bundle = candidate
        if bundle is None:
            bundle = self.consume_write_bundle_candidate() if consume else self.peek_write_bundle_candidate()
        if bundle is None:
            return None
        if consume and candidate is not None and self.last_write_bundle_candidate is bundle:
            self.last_write_bundle_candidate = None
        message = bundle.submission_message(
            correlation_id=correlation_id,
            metadata=metadata,
        )
        response = message.submit_to_backend_response_message(
            self.graph_backend,
            metadata=metadata,
        )
        self._record_local_write_submission(message, response)
        return response

    def submit_write_bundle_submission_message_local_message(
        self,
        message: WriteBundleSubmissionMessage,
        metadata: Optional[dict[str, Any]] = None,
    ) -> WriteBundleResponseMessage:
        response = message.submit_to_backend_response_message(
            self.graph_backend,
            metadata=metadata,
        )
        self._record_local_write_submission(message, response)
        return response

    def query_local_write_status(self, correlation_id: str) -> str:
        return local_write_status_from_response(
            self._write_response_index.get(correlation_id)
        )

    def query_local_write_status_by_submission_id(self, submission_id: str) -> str:
        record = self._write_submission_by_submission_id.get(submission_id)
        if record is None:
            return "not_found"
        return record.status

    def clear_local_write_state(self) -> None:
        self.write_response_history.clear()
        self.write_submission_history.clear()
        self._write_response_index.clear()
        self._write_submission_index.clear()
        self._write_submission_by_submission_id.clear()

    def query_local_write_result(self, correlation_id: str) -> LocalWriteQueryResult:
        response = self._write_response_index.get(correlation_id)
        record = self._write_submission_index.get(correlation_id)
        return local_write_query_result(
            correlation_id=correlation_id,
            response=response,
            record=record,
        )

    def query_local_write_result_by_submission_id(
        self, submission_id: str
    ) -> LocalWriteQueryResult:
        record = self._write_submission_by_submission_id.get(submission_id)
        if record is None:
            return local_write_query_result(
                correlation_id="",
                response=None,
                record=None,
                requested_submission_id=submission_id,
            )
        return local_write_query_result(
            correlation_id=record.correlation_id,
            response=record.response,
            record=record,
        )

    def query_local_write_result_dict(self, correlation_id: str) -> dict[str, Any]:
        return self.query_local_write_result(correlation_id).to_dict()

    def query_local_write_result_dict_by_submission_id(
        self, submission_id: str
    ) -> dict[str, Any]:
        return self.query_local_write_result_by_submission_id(submission_id).to_dict()

    def query_local_write_result_json(self, correlation_id: str) -> str:
        return self.query_local_write_result(correlation_id).to_json()

    def query_local_write_result_json_by_submission_id(
        self, submission_id: str
    ) -> str:
        return self.query_local_write_result_by_submission_id(submission_id).to_json()

    def query_local_write_header(self, correlation_id: str) -> LocalWriteHeader:
        return local_write_header(self.query_local_write_result(correlation_id))

    def query_local_write_header_by_submission_id(
        self, submission_id: str
    ) -> LocalWriteHeader:
        return local_write_header(
            self.query_local_write_result_by_submission_id(submission_id)
        )

    def query_local_write_payload_kind(self, correlation_id: str) -> Optional[str]:
        return self.query_local_write_header(correlation_id).payload_kind

    def query_local_write_payload_kind_by_submission_id(
        self, submission_id: str
    ) -> Optional[str]:
        return self.query_local_write_header_by_submission_id(submission_id).payload_kind

    def query_local_write_header_dict(self, correlation_id: str) -> dict[str, Any]:
        return self.query_local_write_header(correlation_id).to_dict()

    def query_local_write_header_dict_by_submission_id(
        self, submission_id: str
    ) -> dict[str, Any]:
        return self.query_local_write_header_by_submission_id(submission_id).to_dict()

    def query_local_write_header_json(self, correlation_id: str) -> str:
        return self.query_local_write_header(correlation_id).to_json()

    def query_local_write_header_json_by_submission_id(
        self, submission_id: str
    ) -> str:
        return self.query_local_write_header_by_submission_id(submission_id).to_json()

    def export_local_write_headers(self) -> list[LocalWriteHeader]:
        return [local_write_header(result) for result in self.query_local_write_results()]

    def query_local_write_headers(
        self, status: Optional[str] = None
    ) -> list[LocalWriteHeader]:
        return [local_write_header(result) for result in self.query_local_write_results(status=status)]

    def export_local_write_headers_json(self) -> str:
        return LocalWriteHeader.to_json_many(self.export_local_write_headers())

    def query_local_write_headers_json(self, status: Optional[str] = None) -> str:
        return LocalWriteHeader.to_json_many(
            self.query_local_write_headers(status=status)
        )

    def export_local_write_header_history(self) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(self.export_local_write_headers())

    def export_local_write_header_history_by_status(
        self, status: str
    ) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(self.query_local_write_headers(status=status))

    def export_local_write_header_history_json(self) -> str:
        return self.export_local_write_headers_json()

    def export_local_write_header_history_json_by_status(
        self, status: str
    ) -> str:
        return self.query_local_write_headers_json(status=status)

    def query_local_write_trace(
        self, correlation_id: str
    ) -> Optional[LocalWriteTrace]:
        record = self.peek_local_write_submission_record(correlation_id)
        if record is None:
            return None
        query_result = self.query_local_write_result(correlation_id)
        return LocalWriteTrace(
            correlation_id=record.correlation_id,
            submission_id=record.submission_id,
            request=record.request,
            response=record.response,
            record=record,
            query_result=query_result,
        )

    def query_local_write_trace_by_submission_id(
        self, submission_id: str
    ) -> Optional[LocalWriteTrace]:
        record = self.peek_local_write_submission_record_by_submission_id(submission_id)
        if record is None:
            return None
        return self.query_local_write_trace(record.correlation_id)

    def query_local_write_trace_dict(
        self, correlation_id: str
    ) -> Optional[dict[str, Any]]:
        return _typed_to_dict(self.query_local_write_trace(correlation_id))

    def query_local_write_trace_dict_by_submission_id(
        self, submission_id: str
    ) -> Optional[dict[str, Any]]:
        return _typed_to_dict(self.query_local_write_trace_by_submission_id(submission_id))

    def query_local_write_trace_json(
        self, correlation_id: str
    ) -> Optional[str]:
        return _typed_to_json(self.query_local_write_trace(correlation_id))

    def query_local_write_trace_json_by_submission_id(
        self, submission_id: str
    ) -> Optional[str]:
        return _typed_to_json(self.query_local_write_trace_by_submission_id(submission_id))

    def peek_local_write_response_message(
        self, correlation_id: str
    ) -> Optional[WriteBundleResponseMessage]:
        return self._write_response_index.get(correlation_id)

    def peek_local_write_response_message_by_submission_id(
        self, submission_id: str
    ) -> Optional[WriteBundleResponseMessage]:
        record = self.peek_local_write_submission_record_by_submission_id(submission_id)
        return None if record is None else record.response

    def query_local_write_response_message_dict(
        self, correlation_id: str
    ) -> Optional[dict[str, Any]]:
        return _typed_to_dict(self.peek_local_write_response_message(correlation_id))

    def query_local_write_response_message_dict_by_submission_id(
        self, submission_id: str
    ) -> Optional[dict[str, Any]]:
        return _typed_to_dict(
            self.peek_local_write_response_message_by_submission_id(submission_id)
        )

    def query_local_write_response_message_json(
        self, correlation_id: str
    ) -> Optional[str]:
        return _typed_to_json(self.peek_local_write_response_message(correlation_id))

    def query_local_write_response_message_json_by_submission_id(
        self, submission_id: str
    ) -> Optional[str]:
        return _typed_to_json(
            self.peek_local_write_response_message_by_submission_id(submission_id)
        )

    def peek_local_write_submission_message(
        self, correlation_id: str
    ) -> Optional[WriteBundleSubmissionMessage]:
        record = self.peek_local_write_submission_record(correlation_id)
        return None if record is None else record.request

    def peek_local_write_submission_message_by_submission_id(
        self, submission_id: str
    ) -> Optional[WriteBundleSubmissionMessage]:
        record = self.peek_local_write_submission_record_by_submission_id(submission_id)
        return None if record is None else record.request

    def query_local_write_submission_message_dict(
        self, correlation_id: str
    ) -> Optional[dict[str, Any]]:
        return _typed_to_dict(self.peek_local_write_submission_message(correlation_id))

    def query_local_write_submission_message_dict_by_submission_id(
        self, submission_id: str
    ) -> Optional[dict[str, Any]]:
        return _typed_to_dict(
            self.peek_local_write_submission_message_by_submission_id(submission_id)
        )

    def query_local_write_submission_message_json(
        self, correlation_id: str
    ) -> Optional[str]:
        return _typed_to_json(self.peek_local_write_submission_message(correlation_id))

    def query_local_write_submission_message_json_by_submission_id(
        self, submission_id: str
    ) -> Optional[str]:
        return _typed_to_json(
            self.peek_local_write_submission_message_by_submission_id(submission_id)
        )

    def peek_local_write_submission_record(
        self, correlation_id: str
    ) -> Optional[LocalWriteSubmissionRecord]:
        return self._write_submission_index.get(correlation_id)

    def peek_local_write_submission_record_by_submission_id(
        self, submission_id: str
    ) -> Optional[LocalWriteSubmissionRecord]:
        return self._write_submission_by_submission_id.get(submission_id)

    def query_local_write_submission_record_dict(
        self, correlation_id: str
    ) -> Optional[dict[str, Any]]:
        return _typed_to_dict(self.peek_local_write_submission_record(correlation_id))

    def query_local_write_submission_record_dict_by_submission_id(
        self, submission_id: str
    ) -> Optional[dict[str, Any]]:
        return _typed_to_dict(
            self.peek_local_write_submission_record_by_submission_id(submission_id)
        )

    def query_local_write_submission_record_json(
        self, correlation_id: str
    ) -> Optional[str]:
        return _typed_to_json(self.peek_local_write_submission_record(correlation_id))

    def query_local_write_submission_record_json_by_submission_id(
        self, submission_id: str
    ) -> Optional[str]:
        return _typed_to_json(
            self.peek_local_write_submission_record_by_submission_id(submission_id)
        )

    def export_local_write_submission_history(self) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(self.write_submission_history)

    def export_local_write_submission_history_json(self) -> str:
        return LocalWriteSubmissionRecord.to_json_many(
            self.export_local_write_submission_records()
        )

    def export_local_write_submission_records(self) -> list[LocalWriteSubmissionRecord]:
        return list(self.write_submission_history)

    def query_local_write_submission_records(
        self, status: Optional[str] = None
    ) -> list[LocalWriteSubmissionRecord]:
        if status is None:
            return list(self.write_submission_history)
        return [record for record in self.write_submission_history if record.status == status]

    def export_local_write_submission_history_by_status(
        self, status: str
    ) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(
            self.query_local_write_submission_records(status=status)
        )

    def export_local_write_submission_history_json_by_status(
        self, status: str
    ) -> str:
        return LocalWriteSubmissionRecord.to_json_many(
            self.query_local_write_submission_records(status=status)
        )

    def export_local_write_response_history(self) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(self.write_response_history)

    def export_local_write_response_history_json(self) -> str:
        return WriteBundleResponseMessage.to_json_many(
            self.export_local_write_response_messages()
        )

    def export_local_write_response_messages(self) -> list[WriteBundleResponseMessage]:
        return list(self.write_response_history)

    def query_local_write_response_messages(
        self, status: Optional[str] = None
    ) -> list[WriteBundleResponseMessage]:
        if status is None:
            return list(self.write_response_history)
        return [
            response
            for response in self.write_response_history
            if local_write_status_from_response(response) == status
        ]

    def export_local_write_response_history_by_status(
        self, status: str
    ) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(
            self.query_local_write_response_messages(status=status)
        )

    def export_local_write_response_history_json_by_status(
        self, status: str
    ) -> str:
        return WriteBundleResponseMessage.to_json_many(
            self.query_local_write_response_messages(status=status)
        )

    def export_local_write_submission_messages(self) -> list[WriteBundleSubmissionMessage]:
        return [record.request for record in self.write_submission_history]

    def query_local_write_submission_messages(
        self, status: Optional[str] = None
    ) -> list[WriteBundleSubmissionMessage]:
        if status is None:
            return self.export_local_write_submission_messages()
        return [
            record.request for record in self.write_submission_history if record.status == status
        ]

    def export_local_write_submission_message_history(self) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(self.export_local_write_submission_messages())

    def export_local_write_submission_message_history_json(self) -> str:
        return WriteBundleSubmissionMessage.to_json_many(
            self.export_local_write_submission_messages()
        )

    def export_local_write_submission_message_history_by_status(
        self, status: str
    ) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(
            self.query_local_write_submission_messages(status=status)
        )

    def export_local_write_submission_message_history_json_by_status(
        self, status: str
    ) -> str:
        return WriteBundleSubmissionMessage.to_json_many(
            self.query_local_write_submission_messages(status=status)
        )

    def export_local_write_query_results(self) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(self.query_local_write_results())

    def export_local_write_query_results_json(self) -> str:
        return LocalWriteQueryResult.to_json_many(self.query_local_write_results())

    def query_local_write_results(
        self, status: Optional[str] = None
    ) -> list[LocalWriteQueryResult]:
        results = [
            local_write_query_result(
                correlation_id=record.correlation_id,
                response=record.response,
                record=record,
            )
            for record in self.write_submission_history
        ]
        if status is None:
            return results
        return [result for result in results if result.status == status]

    def export_local_write_query_results_by_status(
        self, status: str
    ) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(self.query_local_write_results(status=status))

    def export_local_write_query_results_json_by_status(
        self, status: str
    ) -> str:
        return LocalWriteQueryResult.to_json_many(
            self.query_local_write_results(status=status)
        )

    def export_local_write_traces(self) -> list[LocalWriteTrace]:
        return [
            trace
            for trace in (
                self.query_local_write_trace(record.correlation_id)
                for record in self.write_submission_history
            )
            if trace is not None
        ]

    def query_local_write_traces(
        self, status: Optional[str] = None
    ) -> list[LocalWriteTrace]:
        traces = self.export_local_write_traces()
        if status is None:
            return traces
        return [trace for trace in traces if trace.query_result.status == status]

    def export_local_write_trace_history(self) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(self.export_local_write_traces())

    def export_local_write_trace_history_json(self) -> str:
        return LocalWriteTrace.to_json_many(self.export_local_write_traces())

    def export_local_write_trace_history_by_status(
        self, status: str
    ) -> list[dict[str, Any]]:
        return _typed_list_to_dicts(self.query_local_write_traces(status=status))

    def export_local_write_trace_history_json_by_status(self, status: str) -> str:
        return LocalWriteTrace.to_json_many(
            self.query_local_write_traces(status=status)
        )

    def _record_local_write_submission(
        self,
        message: WriteBundleSubmissionMessage,
        response: WriteBundleResponseMessage,
    ) -> None:
        self._write_response_index[response.correlation_id] = response
        self.write_response_history.append(response)
        record = LocalWriteSubmissionRecord(
            correlation_id=message.correlation_id,
            submission_id=message.submission_id,
            request=message,
            response=response,
            status=local_write_status_from_response(response),
        )
        self._write_submission_index[record.correlation_id] = record
        self._write_submission_by_submission_id[record.submission_id] = record
        self.write_submission_history.append(record)

    # ------------------------------------------------------------------
    # Truthiness (used by If, IfFound, Assert, Query)
    # ------------------------------------------------------------------

    def _is_truthy(self, val: Any) -> bool:
        """CogLang truthiness: False[], empty List[], errors, and None are falsy."""
        if val is None:
            return False
        if isinstance(val, CogLangExpr):
            if val.head == "False":
                return False
            if val.head == "List" and len(val.args) == 0:
                return False
            if val.head in ERROR_HEADS:
                return False
        return True

    # ------------------------------------------------------------------
    # Special Form handlers
    # ------------------------------------------------------------------

    def _handle_if(self, expr: CogLangExpr, env: dict, _depth: int) -> Any:
        """If[condition, then, else] — evaluate condition, branch on truthiness."""
        if len(expr.args) != 3:
            return CogLangExpr("TypeError", ("If", "arity", "expected 3 args"))
        condition_expr, then_expr, else_expr = expr.args
        cond = self.execute(condition_expr, env, _depth + 1)
        if self._is_truthy(cond):
            return self.execute(then_expr, env, _depth + 1)
        return self.execute(else_expr, env, _depth + 1)

    def _handle_iffound(self, expr: CogLangExpr, env: dict, _depth: int) -> Any:
        """IfFound[result_expr, bind_var, then, else] — null/error guard.

        If result_expr evaluates to an error value → else.
        Otherwise → bind bind_var = result, execute then.
        Trigger condition (R-4): isinstance check, NOT string comparison.
        """
        if len(expr.args) != 4:
            return CogLangExpr("TypeError", ("IfFound", "arity", "expected 4 args"))
        result_expr, bind_var, then_expr, else_expr = expr.args
        result = self.execute(result_expr, env, _depth + 1)
        if isinstance(result, CogLangExpr) and result.head in ERROR_HEADS:
            return self.execute(else_expr, env, _depth + 1)
        key = _var_key(bind_var) if isinstance(bind_var, CogLangVar) else str(bind_var)
        new_env = {**env, key: result}
        return self.execute(then_expr, new_env, _depth + 1)

    def _handle_foreach(self, expr: CogLangExpr, env: dict, _depth: int) -> Any:
        """ForEach[collection, bind_var, body] — iterate over collection snapshot.

        collection is evaluated to a snapshot BEFORE iteration (SCC-E8).
        Each iteration creates an isolated env (SCC-E6 analogue — no shared state).
        """
        if len(expr.args) != 3:
            return CogLangExpr("TypeError", ("ForEach", "arity", "expected 3 args"))
        collection_expr, bind_var, body = expr.args
        snap = self.execute(collection_expr, env, _depth + 1)
        if not (isinstance(snap, CogLangExpr) and snap.head == "List"):
            return CogLangExpr(
                "TypeError", ("ForEach", "collection", "expected List", repr(snap))
            )
        snapshot = list(snap.args)          # snapshot before iteration (SCC-E8)
        key = _var_key(bind_var) if isinstance(bind_var, CogLangVar) else str(bind_var)
        results = []
        for item in snapshot:
            item_env = {**env, key: item}   # fresh env per iteration (SCC-E6)
            results.append(self.execute(body, item_env, _depth + 1))
        return CogLangExpr("List", tuple(results))

    def _handle_do(self, expr: CogLangExpr, env: dict, _depth: int) -> Any:
        """Do[step...] — sequential execution; does NOT abort on error; returns last."""
        if len(expr.args) < 1:
            return CogLangExpr("TypeError", ("Do", "arity", "expected at least 1 arg"))
        last: Any = CogLangExpr("List", ())
        for step in expr.args:
            last = self.execute(step, env, _depth + 1)
        return last

    def _record_write_op(self, op: str, payload: dict[str, Any]) -> None:
        if self._active_write_bundle_candidate is None:
            return
        self._active_write_bundle_candidate.operations.append(
            WriteOperation(op=op, payload=dict(payload))
        )

    def _allocate_node_id(self) -> str:
        """Allocate a unique language-level node ID before backend submission."""
        while True:
            candidate = str(uuid.uuid4())
            if candidate not in self.graph_backend.graph:
                return candidate

    def _handle_compose(self, expr: CogLangExpr, env: dict, _depth: int) -> Any:
        """Compose[name, List[params...], body] — register a user-defined operation.

        Body is stored as AST and executed only when the operation is called (SCC-E4).
        Registering an existing built-in name returns TypeError[].
        """
        if len(expr.args) != 3:
            return CogLangExpr("TypeError", ("Compose", "arity", "expected 3 args"))
        name_str = expr.args[0]
        params_expr = expr.args[1]      # CogLangExpr("List", (CogLangVar,...))
        body = expr.args[2]             # raw AST — NOT evaluated here (SCC-E4)

        # Guard: do not allow overriding built-in operations or special forms (§2.5).
        if name_str in self._dispatch or name_str in self._special_forms:
            return CogLangExpr("TypeError", ("Compose", "override_builtin", name_str))

        # Guard: do not allow re-registering an already-defined user operation (§2.5).
        if name_str in self._user_ops:
            return CogLangExpr("TypeError", ("Compose", "already_registered", name_str))

        param_vars = list(params_expr.args)
        self._user_ops[name_str] = {"params": param_vars, "body": body}

        # Register Operation node in graph (best-effort; ignore duplicate-id error).
        self.graph_backend.create_node("Operation", {"id": name_str, "name": name_str})
        return {"operator_name": name_str, "scope": "graph-local"}

    def _call_user_op(
        self, name: str, evaled_args: tuple, env: dict, _depth: int
    ) -> Any:
        """Execute a Compose-registered operation with already-evaluated args."""
        op = self._user_ops[name]
        param_vars: list = op["params"]   # list of CogLangVar
        body: CogLangExpr = op["body"]   # raw AST
        # Bind args to canonical keys; inner bindings take priority over outer env.
        new_env = {_var_key(p): a for p, a in zip(param_vars, evaled_args)}
        merged_env = {**env, **new_env}
        return self.execute(body, merged_env, _depth + 1)

    def _handle_assert(self, expr: CogLangExpr, env: dict, _depth: int) -> Any:
        """Assert[condition [, message]] — evaluate condition; log on failure."""
        if len(expr.args) not in {1, 2}:
            return CogLangExpr("TypeError", ("Assert", "arity", "expected 1 or 2 args"))
        condition_expr = expr.args[0]
        message_expr = expr.args[1] if len(expr.args) > 1 else None
        cond = self.execute(condition_expr, env, _depth + 1)
        if not self._is_truthy(cond):
            if message_expr is not None:
                msg = self.execute(message_expr, env, _depth + 1)
            else:
                msg = "assertion failed"
            self.observer.on_assert_fail(str(msg), _depth)
        return cond

    def _handle_query(self, expr: CogLangExpr, env: dict, _depth: int) -> Any:
        """Query[bind_var, predicate [, options]] — collect nodes where predicate is truthy.

        Iterates all graph nodes with confidence > 0 (SCC-E6: isolated env per node).
        """
        if len(expr.args) not in {2, 3}:
            return CogLangExpr("TypeError", ("Query", "arity", "expected 2 or 3 args"))

        bind_var, predicate = expr.args[0], expr.args[1]
        options_expr = expr.args[2] if len(expr.args) == 3 else {"k": 1, "mode": "default"}
        options = self.execute(options_expr, env, _depth + 1) if len(expr.args) == 3 else options_expr
        if isinstance(options, CogLangExpr) and options.head in ERROR_HEADS:
            return options
        if not isinstance(options, dict):
            return CogLangExpr("TypeError", ("Query", "options", "expected Dict"))

        k = options.get("k", 1)
        if isinstance(k, bool) or not ((isinstance(k, int) and k >= 0) or k == "inf"):
            return CogLangExpr("TypeError", ("Query", "k", "expected non-negative int or \"inf\""))

        mode = options.get("mode", "default")
        if not isinstance(mode, str):
            return CogLangExpr("TypeError", ("Query", "mode", "expected string"))
        if mode != "default":
            return CogLangExpr("StubError", ("Query", "mode", mode))

        key = _var_key(bind_var) if isinstance(bind_var, CogLangVar) else str(bind_var)
        results = []
        for node_id, node_data in sorted(self.graph_backend.graph.nodes(data=True), key=lambda item: item[0]):
            if node_data.get("confidence", 1.0) <= 0:
                continue
            item_env = {**env, key: node_id}    # fresh env per iteration (SCC-E6)
            self._query_budget_stack.append(k)
            self._query_depth_map_stack.append({node_id: 0})
            try:
                cond = self.execute(predicate, item_env, _depth + 1)
            finally:
                self._query_budget_stack.pop()
                self._query_depth_map_stack.pop()
            if self._is_truthy(cond):
                results.append(node_id)
        return CogLangExpr("List", tuple(results))

    def _handle_trace(self, expr: CogLangExpr, env: dict, _depth: int) -> Any:
        """Trace[expr] — evaluate expr, notify observer with original AST."""
        inner = expr.args[0]
        result = self.execute(inner, env, _depth + 1)
        self.observer.on_trace(inner, result, _depth)
        return result

    def _handle_unify(self, expr: CogLangExpr, env: dict, _depth: int) -> Any:
        """Unify/Match[pattern, target] — pass raw AST to unify backend.

        MUST be a Special Form: pattern/target contain CogLangVar objects used as
        Prolog-style free variables.  If eagerly evaluated, unbound vars would
        resolve to TypeError["unbound_variable"] before unification.
        """
        pattern, target = expr.args[0], expr.args[1]
        return self.unify_backend.unify(pattern, target)

    # ------------------------------------------------------------------
    # Built-in operation handlers (called by _dispatch with evaled args)
    # ------------------------------------------------------------------

    def _do_traverse(self, source: Any, edge_type: Any) -> CogLangExpr:
        if not isinstance(source, str):
            return CogLangExpr(
                "TypeError", ("Traverse", "source", "expected string", repr(source))
            )
        next_depth: Optional[int] = None
        if self._query_budget_stack:
            budget = self._query_budget_stack[-1]
            depth_map = self._query_depth_map_stack[-1]
            source_depth = depth_map.get(source, 0)
            next_depth = source_depth + 1
            if budget != "inf" and next_depth > budget:
                return CogLangExpr("NotFound", ())

        result = self.graph_backend.traverse(source, str(edge_type))
        if (
            next_depth is not None
            and isinstance(result, CogLangExpr)
            and result.head == "List"
        ):
            depth_map = self._query_depth_map_stack[-1]
            for target in result.args:
                if isinstance(target, str):
                    depth_map[target] = min(depth_map.get(target, next_depth), next_depth)
        return result

    def _do_abstract(self, instances: Any) -> Any:
        if not (isinstance(instances, CogLangExpr) and instances.head == "List"):
            return CogLangExpr("TypeError", ("Abstract", "instances", "expected List"))

        member_refs = tuple(
            item if isinstance(item, str) else canonicalize(item)
            for item in instances.args
        )
        seed = "\u241f".join(member_refs) if member_refs else "empty"
        digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
        cluster_id = f"cluster:{digest}"
        triggered = (
            CogLangExpr("True", ())
            if len(member_refs) >= self.abstract_trigger_min_instances
            else CogLangExpr("False", ())
        )
        prototype_ref = member_refs[0] if member_refs else f"{cluster_id}:prototype"
        return {
            "cluster_id": cluster_id,
            "instance_count": len(member_refs),
            "prototype_ref": prototype_ref,
            "equivalence_class_ref": f"{cluster_id}:equivalence_class",
            "selection_basis": "baseline:first_member_canonical_ref",
            "triggered": triggered,
            # Extra provenance field beyond the frozen minimum six fields.
            "member_refs": CogLangExpr("List", member_refs),
        }

    def _do_create(self, *args: Any) -> Any:
        """Create["NodeType", attrs_dict] or Create["Edge", edge_attrs_dict]."""
        type_or_edge = args[0] if args else None
        attrs = args[1] if len(args) > 1 else {}
        if not isinstance(attrs, dict):
            return CogLangExpr("TypeError", ("Create", "attrs", "expected Dict"))
        confidence = attrs.get("confidence")
        if confidence is not None:
            if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
                return CogLangExpr("TypeError", ("Create", "confidence", "expected 0 < confidence <= 1"))
            confidence = float(confidence)
            if not (0.0 < confidence <= 1.0):
                return CogLangExpr("TypeError", ("Create", "confidence", "expected 0 < confidence <= 1"))
        if type_or_edge == "Edge":
            missing = [k for k in ("from", "to", "relation_type") if k not in attrs]
            if missing:
                return CogLangExpr("TypeError", ("Create", "Edge", "missing required field", missing[0]))
            for field in ("from", "to", "relation_type"):
                if not isinstance(attrs.get(field), str):
                    return CogLangExpr("TypeError", ("Create", "Edge", "invalid field type", field))
            result = self.graph_backend.create_edge(
                attrs["from"],
                attrs["to"],
                attrs["relation_type"],
                confidence if confidence is not None else 1.0,
            )
            if isinstance(result, CogLangExpr) and result.head in ERROR_HEADS:
                return result
            self._record_write_op(
                "create_edge",
                {
                    "source_id": attrs["from"],
                    "target_id": attrs["to"],
                    "relation": attrs["relation_type"],
                    "confidence": confidence if confidence is not None else 1.0,
                },
            )
            return result
        if not isinstance(type_or_edge, str):
            return CogLangExpr("TypeError", ("Create", "type", "expected string"))
        if type_or_edge not in {"Entity", "Concept", "Rule", "Meta"}:
            return CogLangExpr("TypeError", ("Create", "type", "Entity|Concept|Rule|Meta|Edge", type_or_edge))
        if "type" in attrs:
            return CogLangExpr("TypeError", ("Create", "attrs", "reserved key type"))
        allocated_id = attrs.get("id") if isinstance(attrs.get("id"), str) else self._allocate_node_id()
        attrs_with_id = dict(attrs)
        attrs_with_id["id"] = allocated_id
        result = self.graph_backend.create_node(type_or_edge, attrs_with_id)
        if isinstance(result, CogLangExpr) and result.head in ERROR_HEADS:
            return result
        self._record_write_op(
            "create_node",
            {
                "id": result if isinstance(result, str) else allocated_id,
                "node_type": type_or_edge,
                "attrs": {k: v for k, v in attrs_with_id.items() if k != "type"},
            },
        )
        return result

    def _do_update(self, target: Any, changes: Any) -> CogLangExpr:
        if not isinstance(target, str):
            return CogLangExpr("TypeError", ("Update", "target", "expected string"))
        if not isinstance(changes, dict):
            return CogLangExpr("TypeError", ("Update", "changes", "expected Dict"))

        protected_fields = {"id", "type", "provenance", "created_at", "updated_at"}
        protected_hit = next((field for field in protected_fields if field in changes), None)
        if protected_hit is not None:
            return CogLangExpr(
                "TypeError",
                ("Update", "changes", "writable field set", protected_hit),
            )

        confidence = changes.get("confidence")
        if confidence is not None:
            if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
                return CogLangExpr("TypeError", ("Update", "confidence", "expected 0 < confidence <= 1"))
            confidence = float(confidence)
            if confidence == 0.0:
                return CogLangExpr(
                    "TypeError",
                    ("Update", "changes", "use Delete for soft-delete", "confidence"),
                )
            if not (0.0 < confidence <= 1.0):
                return CogLangExpr("TypeError", ("Update", "confidence", "expected 0 < confidence <= 1"))

        result = self.graph_backend.update(target, changes)
        if isinstance(result, CogLangExpr) and result.head == "True":
            self._record_write_op(
                "update_node",
                {"target_id": target, "changes": dict(changes)},
            )
        return result

    def _do_delete(self, *args: Any) -> Any:
        """Delete[target] or Delete["Edge", attrs]."""
        if len(args) == 1:
            result = self.graph_backend.delete_node(args[0])
            if isinstance(result, str):
                self._record_write_op("delete_node", {"target_id": result})
            return result
        if len(args) == 2 and args[0] == "Edge":
            attrs = args[1]
            if not isinstance(attrs, dict):
                return CogLangExpr("TypeError", ("Delete", "attrs", "expected Dict"))
            missing = [k for k in ("from", "to", "relation_type") if k not in attrs]
            if missing:
                return CogLangExpr("TypeError", ("Delete", "Edge", "missing required field", missing[0]))
            for field in ("from", "to", "relation_type"):
                if not isinstance(attrs.get(field), str):
                    return CogLangExpr("TypeError", ("Delete", "Edge", "invalid field type", field))
            result = self.graph_backend.delete_edge(attrs["from"], attrs["to"], attrs["relation_type"])
            if isinstance(result, CogLangExpr) and result.head == "List" and len(result.args) == 3:
                self._record_write_op(
                    "delete_edge",
                    {
                        "source_id": result.args[0],
                        "relation": result.args[1],
                        "target_id": result.args[2],
                    },
                )
            return result
        return CogLangExpr("TypeError", ("Delete", "arity", "expected 1 or 2 args"))

    def _do_all_nodes(self) -> CogLangExpr:
        """AllNodes[] — return List of all node IDs with confidence > 0."""
        nodes = [
            n for n, d in self.graph_backend.graph.nodes(data=True)
            if d.get("confidence", 1.0) > 0
        ]
        return CogLangExpr("List", tuple(nodes))

    def _do_get(self, target: Any, key: Any) -> Any:
        """Get[target, key] — three dispatch cases (SCC-E7 order: dict → List → node).

        dict:    Get[{"k": v}, "k"] → v
        List:    Get[List["a","b"], 0] → "a"
        node:    Get["Einstein", "type"] → "Person"
        """
        # ① Dict lookup — check first (SCC-E7)
        if isinstance(target, dict):
            val = target.get(key)
            return val if val is not None else CogLangExpr("NotFound", ())

        # ② List index
        if isinstance(target, CogLangExpr) and target.head == "List":
            if isinstance(key, int) and 0 <= key < len(target.args):
                return target.args[key]
            return CogLangExpr("NotFound", ())

        # ③ Graph node attribute (string node_id)
        if isinstance(target, str):
            g = self.graph_backend.graph
            if target not in g:
                return CogLangExpr("NotFound", ())
            val = g.nodes[target].get(key)
            return val if val is not None else CogLangExpr("NotFound", ())

        return CogLangExpr(
            "TypeError", ("Get", "source", "expected dict/List/string", repr(target))
        )

    def _do_equal(self, a: Any, b: Any) -> CogLangExpr:
        """Equal[a, b] → True[] if a == b else False[]."""
        return CogLangExpr("True", ()) if a == b else CogLangExpr("False", ())

    def _do_compare(self, a: Any, b: Any) -> Any:
        """Compare[a, b] → {} if equal, else {"a": a, "b": b} diff dict."""
        if a == b:
            return {}
        return {"a": a, "b": b}

    # ------------------------------------------------------------------
    # CogLangExecutor ABC
    # ------------------------------------------------------------------

    def validate(self, expr: Any) -> bool:
        """Return True if expr is a valid CogLang expression (per vocabulary)."""
        from .validator import valid_coglang
        return valid_coglang(expr, graph=self.graph_backend.graph)
