"""Composite operation and local write-bridge tests for the current runtime.

This file covers:
1. Compose registration and parameter substitution
2. Nested Query / ForEach / Update behavior
3. IfFound bind-and-continue usage with Unify results
4. Variable shadowing across Compose scopes
5. Local write-bundle collection, validation, submission, and typed receipts
"""

import pytest
import networkx as nx
import uuid

from logos.coglang.parser import CogLangExpr, CogLangVar, parse
from logos.coglang.executor import PythonCogLangExecutor
from logos.coglang.write_bundle import (
    WriteBundleCandidate,
    ErrorReport,
    LocalWriteQueryResult,
    LocalWriteSubmissionRecord,
    WriteBundleResponseMessage,
    WriteBundleSubmissionMessage,
    WriteBundleSubmissionResult,
    WriteResult,
    WriteOperation,
)
from tests.coglang.conftest import _build_fixture_graph


@pytest.mark.L2
def test_compose_findbirthplace(executor):
    """Compose["FindBirthplace"] is registered and called with param substitution.

    Verifies that person_ is bound to "Einstein" (not passed as CogLangVar).
    """
    # Register: Compose["FindBirthplace", List[person_], Traverse[person_,"born_in"]]
    reg_result = executor.execute(
        parse('Compose["FindBirthplace", List[person_], Traverse[person_, "born_in"]]')
    )
    assert reg_result == {"operator_name": "FindBirthplace", "scope": "graph-local"}

    # Call: FindBirthplace["Einstein"]
    # Derivation: person_ ← "Einstein" → Traverse["Einstein","born_in"] → List["Ulm"]
    result = executor.execute(parse('FindBirthplace["Einstein"]'))
    assert result == CogLangExpr("List", ("Ulm",))


@pytest.mark.L2
def test_foreach_query_update():
    """ForEach[Query[...], p_, Update[...]] works as a nested read/write flow.

    Query finds all Person nodes (confidence>0) → Einstein only.
    ForEach updates each: Update["Einstein", {"visited": True[]}] → True[].
    ForEach returns List[True[]] (one result per matched node).
    """
    exec_ = PythonCogLangExecutor(_build_fixture_graph())

    result = exec_.execute(
        parse('ForEach['
              'Query[n_, Equal[Get[n_, "type"], "Person"]], '
              'p_, '
              'Update[p_, {"visited": True[]}]'
              ']')
    )
    # Einstein is the only Person node with confidence > 0
    assert result == CogLangExpr("List", (CogLangExpr("True", ()),))

    # Verify the update was applied
    einstein_data = exec_.graph_backend.graph.nodes["Einstein"]
    assert einstein_data.get("visited") == CogLangExpr("True", ())


@pytest.mark.L2
def test_iffound_unify_bind_and_use():
    """IfFound can bind a Unify result and feed it into subsequent expressions.

    Unify succeeds → {"X":"a","Y":"b"}.
    IfFound: result is a dict (not an error) → then branch, bind bindings_={"X":"a","Y":"b"}.
    Get[bindings_,"X"] → "a" (dict lookup with key "X").

    Also verifies computed dict value evaluation: Create with {"name": Get[bindings_,"X"]}
    produces a node with name="a" (Get is evaluated when Create is eager-evaluated).
    """
    exec_ = PythonCogLangExecutor(_build_fixture_graph())

    # Setup: add stale_node for the else branch to operate on
    exec_.execute(parse('Create["Entity", {"id": "stale_node"}]'))

    # Part A: verify IfFound binds Unify result and Get extracts field
    bindings_var = CogLangVar(name="bindings", is_anonymous=False)

    expr_a = CogLangExpr("IfFound", (
        parse('Unify[f[X_,b],f[a,Y_]]'),        # result = {"X":"a","Y":"b"}
        bindings_var,                            # bind bindings_ to result
        parse('Get[bindings_,"X"]'),             # then: extract "X" → "a"
        parse('Delete["stale_node"]'),           # else: not reached
    ))
    result_a = exec_.execute(expr_a)
    assert result_a == "a"

    # Part B: verify computed dict values in Create work (dict value eval fix)
    # Create["Entity", {"id":"bound_entity","name": Get[bindings_,"X"]}]
    # → name is evaluated from env where bindings_ = {"X":"a","Y":"b"}
    expr_b = CogLangExpr("IfFound", (
        parse('Unify[f[X_,b],f[a,Y_]]'),
        bindings_var,
        CogLangExpr("Create", (
            "Entity",
            {"id": "bound_entity",
             "name": CogLangExpr("Get", (bindings_var, "X"))}
        )),
        parse('Delete["stale_node"]'),
    ))
    result_b = exec_.execute(expr_b)
    assert result_b == "bound_entity"
    # Verify the computed name was stored correctly
    assert exec_.graph_backend.graph.nodes["bound_entity"]["name"] == "a"


@pytest.mark.L2
def test_variable_shadowing():
    """Compose inner params shadow outer env bindings of the same logical name.

    outer env: X = "Germany" (valid graph node).
    Compose["ShadowTest", List[x_], Traverse[x_,"born_in"]] registers with param x_.
    Call: ShadowTest["Einstein"] with env={"X": "Germany"}.
    Inside body: x_ binds to "Einstein" (inner), not "Germany" (outer).
    Result: Traverse["Einstein","born_in"] → List["Ulm"], NOT Traverse["Germany","born_in"].
    """
    exec_ = PythonCogLangExecutor(_build_fixture_graph())

    exec_.execute(
        parse('Compose["ShadowTest", List[x_], Traverse[x_, "born_in"]]')
    )

    # Outer env has X="Germany"; call ShadowTest with "Einstein"
    outer_env = {"X": "Germany"}
    result = exec_.execute(parse('ShadowTest["Einstein"]'), env=outer_env)

    # Inner x_="Einstein" must shadow outer X="Germany"
    assert result == CogLangExpr("List", ("Ulm",))
    # Sanity check: if outer had leaked, Germany has no "born_in" edges → List[]
    # (Germany is an Entity node, no outgoing born_in edges in fixture)


@pytest.mark.L2
def test_create_records_write_bundle_candidate():
    """Top-level Create emits a WriteBundleCandidate with the preallocated node ID."""
    exec_ = PythonCogLangExecutor(nx.DiGraph())

    result = exec_.execute(parse('Create["Entity", {"name": "Tesla"}]'))

    assert isinstance(result, str)
    bundle = exec_.last_write_bundle_candidate
    assert bundle is not None
    assert bundle.owner == "coglang_executor"
    assert bundle.base_node_ids == set()
    assert len(bundle.operations) == 1
    op = bundle.operations[0]
    assert op.op == "create_node"
    assert op.payload["id"] == result
    assert op.payload["node_type"] == "Entity"
    assert op.payload["attrs"]["name"] == "Tesla"


@pytest.mark.L2
def test_create_without_explicit_id_uses_preallocated_uuid():
    """Default Create path should allocate a stable UUID before backend submission."""
    exec_ = PythonCogLangExecutor(nx.DiGraph())

    result = exec_.execute(parse('Create["Entity", {"name": "Tesla"}]'))

    assert isinstance(result, str)
    assert str(uuid.UUID(result)) == result
    assert result in exec_.graph_backend.graph
    bundle = exec_.last_write_bundle_candidate
    assert bundle is not None
    assert bundle.operations[0].payload["id"] == result
    assert bundle.operations[0].payload["attrs"]["id"] == result


@pytest.mark.L2
def test_do_collects_ordered_write_bundle_candidate():
    """One top-level Do expression should collect ordered write intents in one bundle."""
    exec_ = PythonCogLangExecutor(_build_fixture_graph())

    result = exec_.execute(
        parse('Do['
              'Create["Entity", {"id": "dog_1", "name": "Dog"}], '
              'Create["Edge", {"from": "Einstein", "to": "dog_1", "relation_type": "knows"}]'
              ']')
    )

    assert result == CogLangExpr("List", ("Einstein", "knows", "dog_1"))
    bundle = exec_.last_write_bundle_candidate
    assert bundle is not None
    assert len(bundle.operations) == 2
    assert "dog_1" not in bundle.base_node_ids
    assert bundle.operations[0].op == "create_node"
    assert bundle.operations[0].payload["id"] == "dog_1"
    assert bundle.operations[1].op == "create_edge"
    assert bundle.operations[1].payload["source_id"] == "Einstein"
    assert bundle.operations[1].payload["target_id"] == "dog_1"
    assert bundle.operations[1].payload["relation"] == "knows"


@pytest.mark.L2
def test_execute_with_write_bundle_candidate_returns_pair():
    """Host-facing helper should return the language result plus the latest candidate."""
    exec_ = PythonCogLangExecutor(nx.DiGraph())

    result, bundle = exec_.execute_with_write_bundle_candidate(
        parse('Create["Entity", {"name": "Tesla"}]')
    )

    assert isinstance(result, str)
    assert bundle is not None
    assert bundle is exec_.peek_write_bundle_candidate()
    assert len(bundle.operations) == 1
    assert bundle.base_node_ids == set()
    assert bundle.operations[0].payload["id"] == result


@pytest.mark.L2
def test_consume_write_bundle_candidate_clears_last_bundle():
    """Host should be able to consume the last candidate once and clear the pointer."""
    exec_ = PythonCogLangExecutor(nx.DiGraph())
    exec_.execute(parse('Create["Entity", {"name": "Tesla"}]'))

    bundle = exec_.consume_write_bundle_candidate()

    assert bundle is not None
    assert len(bundle.operations) == 1
    assert exec_.peek_write_bundle_candidate() is None


@pytest.mark.L2
def test_validate_write_bundle_candidate_accepts_earlier_local_ref():
    """REV-33: references to earlier local IDs in the same bundle are valid."""
    exec_ = PythonCogLangExecutor(_build_fixture_graph())
    exec_.execute(
        parse('Do['
              'Create["Entity", {"id": "dog_1", "name": "Dog"}], '
              'Create["Edge", {"from": "Einstein", "to": "dog_1", "relation_type": "knows"}]'
              ']')
    )

    is_valid, errors = exec_.validate_write_bundle_candidate()

    assert is_valid is True
    assert errors == []


@pytest.mark.L2
def test_write_bundle_candidate_rejects_forward_local_ref():
    """REV-33: references to not-yet-declared local IDs must fail validation."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                op="create_edge",
                payload={"source_id": "Einstein", "target_id": "dog_1", "relation": "knows"},
            ),
            WriteOperation(
                op="create_node",
                payload={"id": "dog_1", "node_type": "Entity", "attrs": {"name": "Dog"}},
            ),
        ],
    )

    is_valid, errors = bundle.validate_against_existing_ids({"Einstein", "Ulm"})

    assert is_valid is False
    assert any("unresolved target_id 'dog_1'" in err for err in errors)


@pytest.mark.L2
def test_write_bundle_candidate_commit_order_groups_by_phase():
    """Commit order should be nodes first, then edges, then update/delete."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation("delete_node", {"target_id": "old_1"}),
            WriteOperation("create_edge", {"source_id": "Einstein", "target_id": "dog_1", "relation": "knows"}),
            WriteOperation("create_node", {"id": "dog_1", "node_type": "Entity", "attrs": {"name": "Dog"}}),
            WriteOperation("update_node", {"target_id": "Einstein", "changes": {"name": "Albert Einstein"}}),
        ],
    )

    ordered = bundle.commit_ordered_operations()

    assert [op.op for op in ordered] == ["create_node", "create_edge", "delete_node", "update_node"]


@pytest.mark.L2
def test_write_bundle_candidate_roundtrip_dict():
    """WriteBundleCandidate should round-trip through a transport-safe dict form."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        base_node_ids={"Einstein", "Ulm"},
        operations=[
            WriteOperation("create_node", {"id": "dog_1", "node_type": "Entity", "attrs": {"name": "Dog"}}),
            WriteOperation("create_edge", {"source_id": "Einstein", "target_id": "dog_1", "relation": "knows"}),
        ],
    )

    encoded = bundle.to_dict()
    decoded = WriteBundleCandidate.from_dict(encoded)

    assert encoded["owner"] == "coglang_executor"
    assert encoded["base_node_ids"] == ["Einstein", "Ulm"]
    assert decoded == bundle


@pytest.mark.L2
def test_write_bundle_candidate_commit_plan_is_serializable():
    """Commit plan should expose explicit REV-33-style phases for host submission."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation("delete_node", {"target_id": "old_1"}),
            WriteOperation("create_edge", {"source_id": "Einstein", "target_id": "dog_1", "relation": "knows"}),
            WriteOperation("create_node", {"id": "dog_1", "node_type": "Entity", "attrs": {"name": "Dog"}}),
            WriteOperation("update_node", {"target_id": "Einstein", "changes": {"name": "Albert Einstein"}}),
        ],
    )

    plan = bundle.commit_plan()

    assert [item["op"] for item in plan["phase_1a_create_nodes"]] == ["create_node"]
    assert [item["op"] for item in plan["phase_1b_create_edges"]] == ["create_edge"]
    assert [item["op"] for item in plan["phase_1c_update_delete"]] == ["delete_node", "update_node"]


@pytest.mark.L2
def test_write_bundle_candidate_rejects_unknown_op():
    """Validation should reject unknown operation kinds before submission."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[WriteOperation("rename_node", {"target_id": "Einstein"})],
    )

    is_valid, errors = bundle.validate_against_existing_ids({"Einstein"})

    assert is_valid is False
    assert any("unknown op 'rename_node'" in err for err in errors)


@pytest.mark.L2
def test_write_bundle_candidate_submission_payload_has_envelope():
    """Candidate should export a host-facing submission envelope with header/payload/metadata."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation("create_node", {"id": "dog_1", "node_type": "Entity", "attrs": {"name": "Dog"}}),
        ],
    )

    payload = bundle.submission_payload(correlation_id="corr-123", metadata={"owning_module": "BeliefRevisor"})

    assert payload["header"]["message_type"] == "KnowledgeMessage"
    assert payload["header"]["operation"] == "submit_write_bundle"
    assert payload["header"]["correlation_id"] == "corr-123"
    assert payload["payload"]["candidate"]["owner"] == "coglang_executor"
    assert payload["payload"]["commit_plan"]["phase_1a_create_nodes"][0]["op"] == "create_node"
    assert payload["metadata"]["owner"] == "coglang_executor"
    assert payload["metadata"]["owning_module"] == "BeliefRevisor"


@pytest.mark.L2
def test_write_bundle_submission_message_roundtrip_dict():
    """Typed submission messages should round-trip through the same envelope form."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation("create_node", {"id": "dog_1", "node_type": "Entity", "attrs": {"id": "dog_1", "name": "Dog"}}),
        ],
    )

    message = bundle.submission_message(
        correlation_id="corr-msg-1",
        metadata={"owning_module": "BeliefRevisor"},
    )
    encoded = message.to_dict()
    decoded = WriteBundleSubmissionMessage.from_dict(encoded)

    assert encoded["header"]["correlation_id"] == "corr-msg-1"
    assert isinstance(encoded["header"]["submission_id"], str)
    assert encoded["payload"]["candidate"]["owner"] == "coglang_executor"
    assert decoded.correlation_id == "corr-msg-1"
    assert decoded.submission_id == message.submission_id
    assert decoded.candidate == bundle
    assert decoded.metadata["owning_module"] == "BeliefRevisor"


@pytest.mark.L2
def test_write_bundle_submission_message_submit_to_backend():
    """A typed submission message should submit locally and return a typed success receipt."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    source_exec.execute(parse('Create["Entity", {"id": "dog_1", "name": "Dog"}]'))
    bundle = source_exec.consume_write_bundle_candidate()
    assert bundle is not None

    message = bundle.submission_message(correlation_id="corr-msg-submit-1")
    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    receipt = message.submit_to_backend(target_exec.graph_backend)

    assert isinstance(receipt, WriteResult)
    assert receipt.correlation_id == "corr-msg-submit-1"
    assert target_exec.graph_backend.graph.nodes["dog_1"]["name"] == "Dog"


@pytest.mark.L2
def test_executor_prepare_write_bundle_submission_payload():
    """Executor should expose a direct host-facing payload helper for the latest candidate."""
    exec_ = PythonCogLangExecutor(nx.DiGraph())
    exec_.execute(parse('Create["Entity", {"name": "Tesla"}]'))

    payload = exec_.prepare_write_bundle_submission_payload(
        correlation_id="corr-456",
        metadata={"owning_module": "LanguageInterpreter"},
    )

    assert payload is not None
    assert payload["header"]["correlation_id"] == "corr-456"
    assert payload["payload"]["candidate"]["operations"][0]["op"] == "create_node"
    assert payload["metadata"]["owning_module"] == "LanguageInterpreter"
    assert exec_.peek_write_bundle_candidate() is not None


@pytest.mark.L2
def test_executor_prepare_write_bundle_submission_message():
    """Executor should expose a typed host-facing submission message helper."""
    exec_ = PythonCogLangExecutor(nx.DiGraph())
    exec_.execute(parse('Create["Entity", {"name": "Tesla"}]'))

    message = exec_.prepare_write_bundle_submission_message(
        correlation_id="corr-msg-2",
        metadata={"owning_module": "LanguageInterpreter"},
    )

    assert message is not None
    assert message.correlation_id == "corr-msg-2"
    assert message.candidate.operations[0].op == "create_node"
    assert message.metadata["owning_module"] == "LanguageInterpreter"
    assert exec_.peek_write_bundle_candidate() is not None


@pytest.mark.L2
def test_executor_prepare_write_bundle_submission_payload_consume():
    """Host helper may consume the latest candidate after preparing submission payload."""
    exec_ = PythonCogLangExecutor(nx.DiGraph())
    exec_.execute(parse('Create["Entity", {"name": "Tesla"}]'))

    payload = exec_.prepare_write_bundle_submission_payload(consume=True)

    assert payload is not None
    assert exec_.peek_write_bundle_candidate() is None


@pytest.mark.L2
def test_executor_prepare_write_bundle_submission_message_consume():
    """Typed message helper may consume the latest candidate after preparing it."""
    exec_ = PythonCogLangExecutor(nx.DiGraph())
    exec_.execute(parse('Create["Entity", {"name": "Tesla"}]'))

    message = exec_.prepare_write_bundle_submission_message(consume=True)

    assert message is not None
    assert exec_.peek_write_bundle_candidate() is None


@pytest.mark.L2
def test_executor_apply_write_bundle_candidate():
    """Executor should expose a direct local host-apply helper for the latest candidate."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    source_exec.execute(parse('Create["Entity", {"id": "dog_1", "name": "Dog"}]'))

    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    result = target_exec.apply_write_bundle_candidate(source_exec.peek_write_bundle_candidate())

    assert result is not None
    assert result.accepted is True
    assert target_exec.graph_backend.graph.nodes["dog_1"]["name"] == "Dog"


@pytest.mark.L2
def test_executor_apply_write_bundle_candidate_consume():
    """Executor host helper may consume the latest local candidate after applying it."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    source_exec.execute(parse('Create["Entity", {"id": "dog_1", "name": "Dog"}]'))
    bundle = source_exec.consume_write_bundle_candidate()

    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    target_exec.last_write_bundle_candidate = bundle

    result = target_exec.apply_write_bundle_candidate(consume=True)

    assert result is not None
    assert result.accepted is True
    assert target_exec.peek_write_bundle_candidate() is None


@pytest.mark.L2
def test_write_bundle_candidate_apply_to_backend_succeeds_atomically():
    """A validated bundle should replay against a fresh backend and report structured success."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    source_exec.execute(
        parse('Do['
              'Create["Entity", {"id": "dog_1", "name": "Dog"}], '
              'Create["Edge", {"from": "Einstein", "to": "dog_1", "relation_type": "knows"}]'
              ']')
    )
    bundle = source_exec.consume_write_bundle_candidate()
    assert bundle is not None

    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    result = bundle.apply_to_backend(target_exec.graph_backend)

    assert result.accepted is True
    assert result.applied_ops == 2
    assert result.errors == []
    assert target_exec.graph_backend.graph.nodes["dog_1"]["name"] == "Dog"
    edge = target_exec.graph_backend.graph.get_edge_data("Einstein", "dog_1")
    assert edge is not None
    assert edge["relation_type"] == "knows"


@pytest.mark.L2
def test_write_bundle_candidate_apply_to_backend_rejects_without_mutation():
    """A bundle failing validation must not mutate the target backend."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_edge",
                {"source_id": "Einstein", "target_id": "dog_1", "relation": "knows"},
            ),
            WriteOperation(
                "create_node",
                {"id": "dog_1", "node_type": "Entity", "attrs": {"id": "dog_1", "name": "Dog"}},
            ),
        ],
    )

    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    before_nodes = set(target_exec.graph_backend.graph.nodes)
    result = bundle.apply_to_backend(target_exec.graph_backend)

    assert result.accepted is False
    assert result.applied_ops == 0
    assert any("unresolved target_id 'dog_1'" in err for err in result.errors)
    assert set(target_exec.graph_backend.graph.nodes) == before_nodes


@pytest.mark.L2
def test_write_bundle_submission_result_roundtrip_dict():
    """Structured submission results should round-trip through dict form."""
    result = WriteBundleSubmissionResult(
        accepted=True,
        owner="coglang_executor",
        applied_ops=2,
        errors=[],
        phase_counts={
            "phase_1a_create_nodes": 1,
            "phase_1b_create_edges": 1,
            "phase_1c_update_delete": 0,
        },
    )

    encoded = result.to_dict()
    decoded = WriteBundleSubmissionResult.from_dict(encoded)

    assert encoded["accepted"] is True
    assert encoded["applied_ops"] == 2
    assert decoded == result


@pytest.mark.L2
def test_write_result_roundtrip_dict():
    """WriteResult should round-trip through dict form."""
    result = WriteResult(
        correlation_id="corr-result-1",
        submission_id="sub-result-1",
        owner="coglang_executor",
        commit_timestamp="2026-04-13T00:00:00+00:00",
        applied_ops=2,
        phase_counts={
            "phase_1a_create_nodes": 1,
            "phase_1b_create_edges": 1,
            "phase_1c_update_delete": 0,
        },
        touched_node_ids=["dog_1"],
        touched_edge_refs=[{"source_id": "Einstein", "relation": "knows", "target_id": "dog_1"}],
    )

    encoded = result.to_dict()
    decoded = WriteResult.from_dict(encoded)

    assert encoded["correlation_id"] == "corr-result-1"
    assert encoded["submission_id"] == "sub-result-1"
    assert decoded == result


@pytest.mark.L2
def test_error_report_roundtrip_dict():
    """ErrorReport should round-trip through dict form."""
    report = ErrorReport(
        correlation_id="corr-error-1",
        submission_id="sub-error-1",
        owner="coglang_executor",
        error_kind="ValidationError",
        retryable=True,
        errors=["op[0] unresolved target_id 'dog_1'"],
    )

    encoded = report.to_dict()
    decoded = ErrorReport.from_dict(encoded)

    assert encoded["error_kind"] == "ValidationError"
    assert decoded == report


@pytest.mark.L2
def test_write_result_response_message_roundtrip_dict():
    """WriteResult should lift into a typed response message and round-trip cleanly."""
    receipt = WriteResult(
        correlation_id="corr-response-1",
        submission_id="sub-response-1",
        owner="coglang_executor",
        commit_timestamp="2026-04-13T00:00:00+00:00",
        applied_ops=1,
        phase_counts={
            "phase_1a_create_nodes": 1,
            "phase_1b_create_edges": 0,
            "phase_1c_update_delete": 0,
        },
        touched_node_ids=["dog_1"],
        touched_edge_refs=[],
    )

    message = receipt.response_message(metadata={"owning_module": "BeliefRevisor"})
    encoded = message.to_dict()
    decoded = WriteBundleResponseMessage.from_dict(encoded)

    assert encoded["header"]["operation"] == "write_bundle_response"
    assert encoded["header"]["submission_id"] == "sub-response-1"
    assert encoded["header"]["payload_kind"] == "WriteResult"
    assert encoded["metadata"]["owning_module"] == "BeliefRevisor"
    assert isinstance(decoded.payload, WriteResult)
    assert decoded.payload == receipt


@pytest.mark.L2
def test_error_report_response_message_roundtrip_dict():
    """ErrorReport should lift into a typed response message and round-trip cleanly."""
    report = ErrorReport(
        correlation_id="corr-response-2",
        submission_id="sub-response-2",
        owner="coglang_executor",
        error_kind="ValidationError",
        retryable=True,
        errors=["op[0] unresolved target_id 'dog_1'"],
    )

    message = report.response_message(metadata={"owning_module": "BeliefRevisor"})
    encoded = message.to_dict()
    decoded = WriteBundleResponseMessage.from_dict(encoded)

    assert encoded["header"]["payload_kind"] == "ErrorReport"
    assert encoded["header"]["submission_id"] == "sub-response-2"
    assert isinstance(decoded.payload, ErrorReport)
    assert decoded.payload == report


@pytest.mark.L2
def test_local_write_submission_record_roundtrip_dict():
    """Local submission records should round-trip through dict form."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_node",
                {"id": "dog_1", "node_type": "Entity", "attrs": {"id": "dog_1", "name": "Dog"}},
            ),
        ],
    )
    request = bundle.submission_message(correlation_id="corr-record-1")
    response = WriteResult(
        correlation_id="corr-record-1",
        submission_id=request.submission_id,
        owner="coglang_executor",
        commit_timestamp="2026-04-13T00:00:00+00:00",
        applied_ops=1,
        phase_counts={
            "phase_1a_create_nodes": 1,
            "phase_1b_create_edges": 0,
            "phase_1c_update_delete": 0,
        },
        touched_node_ids=["dog_1"],
        touched_edge_refs=[],
    ).response_message()
    record = LocalWriteSubmissionRecord(
        correlation_id="corr-record-1",
        submission_id=request.submission_id,
        request=request,
        response=response,
        status="committed",
    )

    encoded = record.to_dict()
    decoded = LocalWriteSubmissionRecord.from_dict(encoded)

    assert encoded["submission_id"] == request.submission_id
    assert decoded.correlation_id == record.correlation_id
    assert decoded.submission_id == record.submission_id
    assert decoded.status == "committed"
    assert decoded.request.correlation_id == request.correlation_id
    assert decoded.request.submission_id == request.submission_id
    assert decoded.response.correlation_id == response.correlation_id
    assert decoded.response.submission_id == response.submission_id


@pytest.mark.L2
def test_local_write_query_result_roundtrip_dict():
    """Typed local query results should round-trip through dict form."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_node",
                {"id": "dog_1", "node_type": "Entity", "attrs": {"id": "dog_1", "name": "Dog"}},
            ),
        ],
    )
    request = bundle.submission_message(correlation_id="corr-query-result-1")
    response = WriteResult(
        correlation_id="corr-query-result-1",
        submission_id=request.submission_id,
        owner="coglang_executor",
        commit_timestamp="2026-04-13T00:00:00+00:00",
        applied_ops=1,
        phase_counts={
            "phase_1a_create_nodes": 1,
            "phase_1b_create_edges": 0,
            "phase_1c_update_delete": 0,
        },
        touched_node_ids=["dog_1"],
        touched_edge_refs=[],
    ).response_message()
    record = LocalWriteSubmissionRecord(
        correlation_id="corr-query-result-1",
        submission_id=request.submission_id,
        request=request,
        response=response,
        status="committed",
    )
    result = LocalWriteQueryResult(
        correlation_id="corr-query-result-1",
        status="committed",
        response=response,
        record=record,
    )

    encoded = result.to_dict()
    decoded = LocalWriteQueryResult.from_dict(encoded)

    assert encoded["submission_id"] == request.submission_id
    assert decoded.correlation_id == result.correlation_id
    assert decoded.status == "committed"
    assert decoded.submission_id == request.submission_id
    assert decoded.response is not None
    assert decoded.response.correlation_id == response.correlation_id
    assert decoded.response.submission_id == response.submission_id
    assert isinstance(decoded.response.payload, WriteResult)
    assert decoded.response.payload == response.payload
    assert decoded.record is not None
    assert decoded.record.correlation_id == record.correlation_id
    assert decoded.record.submission_id == record.submission_id
    assert decoded.record.status == record.status


@pytest.mark.L2
def test_write_bundle_candidate_submit_to_backend_returns_write_result():
    """Local host submission should return a WriteResult on success."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    source_exec.execute(parse('Create["Entity", {"id": "dog_1", "name": "Dog"}]'))
    bundle = source_exec.consume_write_bundle_candidate()
    assert bundle is not None

    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    receipt = bundle.submit_to_backend(target_exec.graph_backend, correlation_id="corr-submit-1")

    assert isinstance(receipt, WriteResult)
    assert receipt.correlation_id == "corr-submit-1"
    assert isinstance(receipt.submission_id, str)
    assert receipt.touched_node_ids == ["dog_1"]


@pytest.mark.L2
def test_write_bundle_candidate_submit_to_backend_returns_error_report():
    """Local host submission should return ErrorReport on validation failure."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_edge",
                {"source_id": "Einstein", "target_id": "dog_1", "relation": "knows"},
            ),
        ],
    )

    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    receipt = bundle.submit_to_backend(target_exec.graph_backend, correlation_id="corr-submit-2")

    assert isinstance(receipt, ErrorReport)
    assert receipt.correlation_id == "corr-submit-2"
    assert isinstance(receipt.submission_id, str)
    assert receipt.error_kind == "ValidationError"


@pytest.mark.L2
def test_write_bundle_candidate_submit_to_backend_response_message():
    """Local host submission may return a typed response envelope instead of a bare receipt."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    source_exec.execute(parse('Create["Entity", {"id": "dog_1", "name": "Dog"}]'))
    bundle = source_exec.consume_write_bundle_candidate()
    assert bundle is not None

    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    response_message = bundle.submit_to_backend_response_message(
        target_exec.graph_backend,
        correlation_id="corr-submit-msg-1",
        metadata={"owning_module": "BeliefRevisor"},
    )

    assert isinstance(response_message, WriteBundleResponseMessage)
    assert response_message.correlation_id == "corr-submit-msg-1"
    assert isinstance(response_message.submission_id, str)
    assert isinstance(response_message.payload, WriteResult)
    assert response_message.payload.submission_id == response_message.submission_id
    assert response_message.metadata["owning_module"] == "BeliefRevisor"
    assert target_exec.graph_backend.graph.nodes["dog_1"]["name"] == "Dog"


@pytest.mark.L2
def test_executor_submit_write_bundle_candidate_local():
    """Executor should expose a local architecture-shaped submission helper."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    source_exec.execute(parse('Create["Entity", {"id": "dog_1", "name": "Dog"}]'))

    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    receipt = target_exec.submit_write_bundle_candidate_local(
        source_exec.peek_write_bundle_candidate(),
        correlation_id="corr-submit-3",
    )

    assert isinstance(receipt, WriteResult)
    assert receipt.correlation_id == "corr-submit-3"
    assert isinstance(receipt.submission_id, str)
    assert target_exec.graph_backend.graph.nodes["dog_1"]["name"] == "Dog"


@pytest.mark.L2
def test_executor_submit_write_bundle_submission_message_local():
    """Executor should accept a typed submission message and return a typed receipt."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    source_exec.execute(parse('Create["Entity", {"id": "dog_1", "name": "Dog"}]'))
    bundle = source_exec.consume_write_bundle_candidate()
    assert bundle is not None

    message = bundle.submission_message(correlation_id="corr-submit-4")
    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    receipt = target_exec.submit_write_bundle_submission_message_local(message)

    assert isinstance(receipt, WriteResult)
    assert receipt.correlation_id == "corr-submit-4"
    assert receipt.submission_id == message.submission_id
    assert target_exec.graph_backend.graph.nodes["dog_1"]["name"] == "Dog"


@pytest.mark.L2
def test_executor_submit_write_bundle_candidate_local_message():
    """Executor should expose a local typed response envelope helper for bundle candidates."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    source_exec.execute(parse('Create["Entity", {"id": "dog_1", "name": "Dog"}]'))

    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    response_message = target_exec.submit_write_bundle_candidate_local_message(
        source_exec.peek_write_bundle_candidate(),
        correlation_id="corr-submit-msg-2",
        metadata={"owning_module": "LanguageInterpreter"},
    )

    assert response_message is not None
    assert isinstance(response_message.payload, WriteResult)
    assert response_message.correlation_id == "corr-submit-msg-2"
    assert isinstance(response_message.submission_id, str)
    assert response_message.metadata["owning_module"] == "LanguageInterpreter"
    assert target_exec.graph_backend.graph.nodes["dog_1"]["name"] == "Dog"


@pytest.mark.L2
def test_executor_submit_write_bundle_submission_message_local_message():
    """Executor should convert a typed submission message into a typed response envelope."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    source_exec.execute(parse('Create["Entity", {"id": "dog_1", "name": "Dog"}]'))
    bundle = source_exec.consume_write_bundle_candidate()
    assert bundle is not None

    message = bundle.submission_message(correlation_id="corr-submit-msg-3")
    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    response_message = target_exec.submit_write_bundle_submission_message_local_message(
        message,
        metadata={"owning_module": "LanguageInterpreter"},
    )

    assert isinstance(response_message, WriteBundleResponseMessage)
    assert isinstance(response_message.payload, WriteResult)
    assert response_message.correlation_id == "corr-submit-msg-3"
    assert response_message.submission_id == message.submission_id
    assert target_exec.graph_backend.graph.nodes["dog_1"]["name"] == "Dog"


@pytest.mark.L2
def test_query_local_write_status_reports_committed():
    """Local write bridge should expose a correlation-based committed status."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    source_exec.execute(parse('Create["Entity", {"id": "dog_1", "name": "Dog"}]'))

    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    response_message = target_exec.submit_write_bundle_candidate_local_message(
        source_exec.peek_write_bundle_candidate(),
        correlation_id="corr-status-1",
    )

    assert response_message is not None
    assert target_exec.query_local_write_status("corr-status-1") == "committed"
    assert target_exec.peek_local_write_response_message("corr-status-1") == response_message
    assert isinstance(response_message.submission_id, str)

    record = target_exec.peek_local_write_submission_record("corr-status-1")
    assert isinstance(record, LocalWriteSubmissionRecord)
    assert record is not None
    assert record.request.correlation_id == "corr-status-1"
    assert record.response == response_message
    assert record.status == "committed"
    assert target_exec.peek_local_write_submission_record_by_submission_id(
        response_message.submission_id
    ) == record
    record_dict = target_exec.query_local_write_submission_record_dict("corr-status-1")
    assert record_dict is not None
    assert record_dict["correlation_id"] == "corr-status-1"
    assert record_dict["submission_id"] == response_message.submission_id
    assert record_dict["status"] == "committed"
    query_result = target_exec.query_local_write_result("corr-status-1")
    assert isinstance(query_result, LocalWriteQueryResult)
    assert query_result.status == "committed"
    assert query_result.submission_id == response_message.submission_id
    assert query_result.response == response_message
    assert query_result.record == record
    assert query_result.to_dict()["status"] == "committed"
    query_by_submission = target_exec.query_local_write_result_by_submission_id(
        response_message.submission_id
    )
    assert query_by_submission.status == "committed"
    assert query_by_submission.correlation_id == "corr-status-1"
    assert query_by_submission.submission_id == response_message.submission_id
    assert query_by_submission.record == record
    query_result_dict = target_exec.query_local_write_result_dict("corr-status-1")
    assert query_result_dict["correlation_id"] == "corr-status-1"
    assert query_result_dict["submission_id"] == response_message.submission_id
    assert query_result_dict["status"] == "committed"
    query_result_dict_by_submission = target_exec.query_local_write_result_dict_by_submission_id(
        response_message.submission_id
    )
    assert query_result_dict_by_submission["correlation_id"] == "corr-status-1"
    assert query_result_dict_by_submission["submission_id"] == response_message.submission_id
    assert query_result_dict_by_submission["status"] == "committed"


@pytest.mark.L2
def test_query_local_write_status_reports_failed():
    """Validation failures should be queryable by correlation_id as failed."""
    bundle = WriteBundleCandidate(
        owner="coglang_executor",
        operations=[
            WriteOperation(
                "create_edge",
                {"source_id": "Einstein", "target_id": "dog_1", "relation": "knows"},
            ),
        ],
    )

    target_exec = PythonCogLangExecutor(_build_fixture_graph())
    response_message = target_exec.submit_write_bundle_candidate_local_message(
        bundle,
        correlation_id="corr-status-2",
    )

    assert response_message is not None
    assert isinstance(response_message.payload, ErrorReport)
    assert target_exec.query_local_write_status("corr-status-2") == "failed"
    assert target_exec.peek_local_write_response_message("corr-status-2") == response_message
    assert isinstance(response_message.submission_id, str)

    record = target_exec.peek_local_write_submission_record("corr-status-2")
    assert isinstance(record, LocalWriteSubmissionRecord)
    assert record is not None
    assert record.status == "failed"
    assert target_exec.peek_local_write_submission_record_by_submission_id(
        response_message.submission_id
    ) == record
    query_result = target_exec.query_local_write_result("corr-status-2")
    assert query_result.status == "failed"
    assert query_result.submission_id == response_message.submission_id
    assert query_result.response == response_message
    assert query_result.record == record
    query_by_submission = target_exec.query_local_write_result_by_submission_id(
        response_message.submission_id
    )
    assert query_by_submission.status == "failed"
    assert query_by_submission.correlation_id == "corr-status-2"
    assert query_by_submission.submission_id == response_message.submission_id
    assert query_by_submission.record == record
    query_result_dict = target_exec.query_local_write_result_dict("corr-status-2")
    assert query_result_dict["correlation_id"] == "corr-status-2"
    assert query_result_dict["submission_id"] == response_message.submission_id
    assert query_result_dict["status"] == "failed"


@pytest.mark.L2
def test_query_local_write_status_reports_not_found():
    """Unknown correlation IDs should resolve to not_found."""
    exec_ = PythonCogLangExecutor(_build_fixture_graph())

    assert exec_.query_local_write_status("corr-missing") == "not_found"
    assert exec_.peek_local_write_response_message("corr-missing") is None
    assert exec_.peek_local_write_submission_record("corr-missing") is None
    assert exec_.peek_local_write_submission_record_by_submission_id("sub-missing") is None
    assert exec_.query_local_write_submission_record_dict("corr-missing") is None
    query_result = exec_.query_local_write_result("corr-missing")
    assert query_result.status == "not_found"
    assert query_result.submission_id is None
    assert query_result.response is None
    assert query_result.record is None
    query_by_submission = exec_.query_local_write_result_by_submission_id("sub-missing")
    assert query_by_submission.status == "not_found"
    assert query_by_submission.correlation_id == ""
    assert query_by_submission.submission_id == "sub-missing"
    assert query_by_submission.response is None
    assert query_by_submission.record is None
    query_result_dict = exec_.query_local_write_result_dict("corr-missing")
    assert query_result_dict["correlation_id"] == "corr-missing"
    assert query_result_dict["submission_id"] is None
    assert query_result_dict["status"] == "not_found"
    query_result_dict_by_submission = exec_.query_local_write_result_dict_by_submission_id(
        "sub-missing"
    )
    assert query_result_dict_by_submission["correlation_id"] == ""
    assert query_result_dict_by_submission["submission_id"] == "sub-missing"
    assert query_result_dict_by_submission["status"] == "not_found"


@pytest.mark.L2
def test_export_local_write_submission_history_preserves_order():
    """History export should expose recorded local submission records in insertion order."""
    source_exec = PythonCogLangExecutor(_build_fixture_graph())
    target_exec = PythonCogLangExecutor(_build_fixture_graph())

    source_exec.execute(parse('Create["Entity", {"id": "dog_1", "name": "Dog"}]'))
    target_exec.submit_write_bundle_candidate_local_message(
        source_exec.consume_write_bundle_candidate(),
        correlation_id="corr-history-1",
    )

    source_exec.execute(parse('Create["Entity", {"id": "dog_2", "name": "Dog2"}]'))
    target_exec.submit_write_bundle_candidate_local_message(
        source_exec.consume_write_bundle_candidate(),
        correlation_id="corr-history-2",
    )

    history = target_exec.export_local_write_submission_history()

    assert [item["correlation_id"] for item in history] == ["corr-history-1", "corr-history-2"]
    assert history[0]["status"] == "committed"
    assert history[1]["status"] == "committed"

    query_results = target_exec.export_local_write_query_results()
    assert [item["correlation_id"] for item in query_results] == ["corr-history-1", "corr-history-2"]
    assert query_results[0]["status"] == "committed"
    assert query_results[1]["status"] == "committed"

    typed_results = target_exec.query_local_write_results()
    assert [item.correlation_id for item in typed_results] == ["corr-history-1", "corr-history-2"]
    assert [item.status for item in typed_results] == ["committed", "committed"]
    committed_only = target_exec.query_local_write_results(status="committed")
    assert [item.correlation_id for item in committed_only] == ["corr-history-1", "corr-history-2"]
    assert target_exec.query_local_write_results(status="failed") == []
    committed_only_dict = target_exec.export_local_write_query_results_by_status("committed")
    assert [item["correlation_id"] for item in committed_only_dict] == ["corr-history-1", "corr-history-2"]
    assert target_exec.export_local_write_query_results_by_status("failed") == []
