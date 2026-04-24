"""Boundary behavior tests for the current CogLang runtime.

These tests exercise the boundary table and the higher-risk execution edges
that tend to drift during implementation updates.

Fixture graph quick reference (see conftest._build_fixture_graph):
  Einstein --born_in--> Ulm          (conf=1.0)
  Einstein --nationality--> Germany  (conf=0.9)
  Einstein --awards--> Nobel_Prize   (conf=1.0)
  Einstein --field--> Physics        (conf=1.0)
  Einstein --related_to--> Deleted_Node (conf=0.0, soft-deleted edge)
  Deleted_Node: confidence=0.0 (soft-deleted)
  Axiom_Node:   immutable=True
"""

import pytest

from coglang.parser import CogLangExpr, CogLangVar, parse
from coglang.executor import PythonCogLangExecutor
from tests.coglang.conftest import _build_fixture_graph


# ===========================================================================
# Traverse boundaries
# ===========================================================================

@pytest.mark.L1
def test_traverse_node_not_found(executor):
    """§2.5: Traverse on non-existent node → List[]."""
    result = executor.execute(parse('Traverse["NoSuchNode", "born_in"]'))
    assert result == CogLangExpr("List", ())


@pytest.mark.L1
def test_traverse_edge_type_not_found(executor):
    """§2.5: Traverse with non-existent edge type → List[]."""
    result = executor.execute(parse('Traverse["Einstein", "no_such_edge"]'))
    assert result == CogLangExpr("List", ())


@pytest.mark.L1
def test_traverse_empty_graph():
    """§2.5: Traverse on empty graph → List[]."""
    exec_ = PythonCogLangExecutor()  # empty graph
    result = exec_.execute(parse('Traverse["Einstein", "born_in"]'))
    assert result == CogLangExpr("List", ())


@pytest.mark.L2
def test_traverse_unbound_var(executor):
    """§2.5 + PG-3: Traverse with unbound CogLangVar node param → TypeError[].

    parse('Traverse[x_, "born_in"]') → x_ is CogLangVar("x"); not bound in env.
    execute(CogLangVar("x")) → TypeError["unbound_variable","x"] (unbound).
    Error propagation short-circuits before Traverse is called.
    Result head is "TypeError" — exact args differ from spec description but semantics hold.
    """
    result = executor.execute(parse('Traverse[x_, "born_in"]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"


@pytest.mark.L2
def test_traverse_deleted_node_as_source(executor):
    """§2.5 plan extra: Traverse from a soft-deleted source node → List[].

    Deleted_Node (confidence=0) exists in graph but has no outgoing edges.
    traverse() does NOT filter the source node by confidence — it proceeds
    normally and returns neighbors filtered by edge/target confidence.
    Result is List[] because Deleted_Node has no outgoing edges in fixture.
    """
    result = executor.execute(parse('Traverse["Deleted_Node", "related_to"]'))
    assert result == CogLangExpr("List", ())


# ===========================================================================
# Unify boundaries (§2.5 rows 5–6)
# ===========================================================================

@pytest.mark.L2
def test_unify_not_unifiable(executor):
    """§2.5: Unify on non-unifiable terms → NotFound[]."""
    result = executor.execute(parse('Unify[f[a], g[b]]'))
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_unify_free_variable(executor):
    """§2.5: Unify with free variables → binding dict {varname: value}."""
    result = executor.execute(parse('Unify[f[X_, b], f[a, Y_]]'))
    assert isinstance(result, dict)
    assert result.get("X") == "a"
    assert result.get("Y") == "b"


# ===========================================================================
# Abstract boundaries
# ===========================================================================

@pytest.mark.L1
def test_abstract_non_list_rejected(executor):
    """Abstract requires a List input."""
    result = executor.execute(parse('Abstract["Einstein"]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Abstract"
    assert result.args[1] == "instances"


@pytest.mark.L1
def test_abstract_empty_list_returns_non_triggered_summary(executor):
    """Abstract[List[]] is a normal non-triggered result, not an error."""
    result = executor.execute(parse("Abstract[List[]]"))
    assert isinstance(result, dict)
    assert result["instance_count"] == 0
    assert result["triggered"] == CogLangExpr("False", ())
    assert result["member_refs"] == CogLangExpr("List", ())


@pytest.mark.L1
def test_abstract_trigger_threshold_is_configurable():
    """Implementations may choose threshold via config without changing language shape."""
    exec_ = PythonCogLangExecutor(_build_fixture_graph(), abstract_trigger_min_instances=2)
    result = exec_.execute(parse('Abstract[List["Einstein", "Tesla"]]'))
    assert isinstance(result, dict)
    assert result["triggered"] == CogLangExpr("True", ())


# ===========================================================================
# Create boundaries (§2.5 row 7)
# ===========================================================================

@pytest.mark.L1
def test_create_duplicate_id(executor):
    """§2.5: Create with already-existing ID → TypeError["Create","id","node already exists",id]."""
    result = executor.execute(parse('Create["Entity", {"id": "Einstein"}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Create"
    assert result.args[1] == "id"
    assert "already exists" in result.args[2]
    assert result.args[3] == "Einstein"


@pytest.mark.L1
def test_create_reserved_type_key_rejected(executor):
    """Create with attrs['type'] must be rejected at the language layer."""
    result = executor.execute(parse('Create["Entity", {"type": "Person", "id": "x"}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Create"
    assert result.args[1] == "attrs"
    assert "reserved key type" in result.args[2]


@pytest.mark.L1
def test_create_invalid_public_node_type_rejected(executor):
    """Create must reject public node types outside Entity/Concept/Rule/Meta."""
    result = executor.execute(parse('Create["Person", {"id": "x"}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Create"
    assert result.args[1] == "type"


@pytest.mark.L1
def test_create_invalid_confidence_rejected(executor):
    """Create must reject confidence outside (0, 1]."""
    result = executor.execute(parse('Create["Entity", {"id": "x", "confidence": 0}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Create"
    assert result.args[1] == "confidence"


@pytest.mark.L1
def test_create_edge_missing_required_field(executor):
    """Create[\"Edge\", ...] must reject missing from/to/relation_type."""
    result = executor.execute(parse('Create["Edge", {"from": "Einstein", "to": "Ulm"}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Create"
    assert result.args[1] == "Edge"
    assert "missing required field" in result.args[2]


@pytest.mark.L1
def test_create_edge_invalid_field_type(executor):
    """Create[\"Edge\", ...] must reject non-string endpoint fields."""
    result = executor.execute(parse('Create["Edge", {"from": 7, "to": "Ulm", "relation_type": "born_in"}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Create"
    assert result.args[1] == "Edge"
    assert "invalid field type" in result.args[2]


# ===========================================================================
# Update boundaries (§2.5 rows 8 + plan: immutable)
# ===========================================================================

@pytest.mark.L1
def test_update_target_not_found(executor):
    """§2.5: Update non-existent target → NotFound[]."""
    result = executor.execute(parse('Update["NoSuchNode", {"name": "test"}]'))
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_update_immutable_node(executor):
    """§2.5 plan: Update immutable node → PermissionError["Update", target]."""
    result = executor.execute(parse('Update["Axiom_Node", {"name": "hacked"}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "PermissionError"
    assert result.args[0] == "Update"
    assert result.args[1] == "Axiom_Node"


@pytest.mark.L1
def test_update_soft_deleted_node_returns_permission_error(executor):
    """Update on soft-deleted target is denied, not treated as an absent node."""
    result = executor.execute(parse('Update["Deleted_Node", {"name": "ignored"}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "PermissionError"
    assert result.args[0] == "Update"
    assert result.args[1] == "Deleted_Node"


@pytest.mark.L1
def test_update_protected_type_field_rejected(executor):
    """Update must reject attempts to overwrite protected system fields such as type."""
    result = executor.execute(parse('Update["Einstein", {"type": "Rule"}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Update"
    assert result.args[1] == "changes"
    assert "writable field set" in result.args[2]
    assert result.args[3] == "type"


@pytest.mark.L1
def test_update_confidence_zero_rejected(executor):
    """Update must not use confidence=0 as a soft-delete shortcut."""
    result = executor.execute(parse('Update["Einstein", {"confidence": 0}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Update"
    assert result.args[1] == "changes"
    assert "use Delete for soft-delete" in result.args[2]


# ===========================================================================
# Delete node boundaries (§2.5 rows 9–11)
# ===========================================================================

@pytest.mark.L1
def test_delete_node_not_found(executor):
    """§2.5: Delete non-existent node → NotFound[] (idempotent)."""
    result = executor.execute(parse('Delete["NoSuchNode"]'))
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L1
def test_delete_already_soft_deleted(executor):
    """§2.5: Delete already-soft-deleted node (confidence=0) → NotFound[] (idempotent)."""
    result = executor.execute(parse('Delete["Deleted_Node"]'))
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_delete_immutable_node(executor):
    """§2.5: Delete confidence=1.0 immutable=True node → PermissionError["Delete", target]."""
    result = executor.execute(parse('Delete["Axiom_Node"]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "PermissionError"
    assert result.args[0] == "Delete"
    assert result.args[1] == "Axiom_Node"


# ===========================================================================
# Delete edge boundaries (§2.5 rows: edge not found / edge exists)
# ===========================================================================

@pytest.mark.L1
def test_delete_edge_not_found(executor):
    """§2.5: Delete["Edge", attrs] on a missing edge returns NotFound[]."""
    result = executor.execute(
        parse('Delete["Edge", {"from": "Einstein", "to": "Ulm", "relation_type": "no_such_relation"}]')
    )
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L1
def test_delete_edge_missing_required_field(executor):
    """Delete[\"Edge\", ...] must reject missing from/to/relation_type."""
    result = executor.execute(parse('Delete["Edge", {"from": "Einstein", "to": "Ulm"}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Delete"
    assert result.args[1] == "Edge"
    assert "missing required field" in result.args[2]


@pytest.mark.L1
def test_delete_edge_invalid_field_type(executor):
    """Delete[\"Edge\", ...] must reject non-string endpoint fields."""
    result = executor.execute(parse('Delete["Edge", {"from": 7, "to": "Ulm", "relation_type": "born_in"}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Delete"
    assert result.args[1] == "Edge"
    assert "invalid field type" in result.args[2]


@pytest.mark.L2
def test_delete_edge_exists(executor):
    """§2.5: Delete["Edge", attrs] → List[source, relation_type, target] + soft-delete.

    After soft-delete, Traverse should no longer find the target.
    """
    result = executor.execute(
        parse('Delete["Edge", {"from": "Einstein", "to": "Ulm", "relation_type": "born_in"}]')
    )
    assert result == CogLangExpr("List", ("Einstein", "born_in", "Ulm"))
    # Verify soft-delete: edge confidence=0, Traverse skips it
    after = executor.execute(parse('Traverse["Einstein", "born_in"]'))
    assert after == CogLangExpr("List", ())


# ===========================================================================
# If boundaries (§2.5 row: non-bool falsy conditions)
# ===========================================================================

@pytest.mark.L2
def test_if_false_value(executor):
    """§2.5: If[False[], then, else] → else branch."""
    result = executor.execute(parse('If[False[], "yes", "no"]'))
    assert result == "no"


@pytest.mark.L2
def test_if_error_value_is_falsy(executor):
    """§2.5: If[NotFound[], then, else] → else branch (error values are falsy)."""
    result = executor.execute(parse('If[NotFound[], "yes", "no"]'))
    assert result == "no"


@pytest.mark.L2
def test_if_empty_list_is_falsy(executor):
    """§2.5: If[List[], then, else] → else branch (empty List is falsy)."""
    result = executor.execute(parse('If[List[], "yes", "no"]'))
    assert result == "no"


@pytest.mark.L2
def test_if_all_error_heads_are_falsy(executor):
    """§2.5: All ERROR_HEADS values (TypeError, StubError, etc.) are falsy in If."""
    for head in ["TypeError", "PermissionError", "ParseError", "StubError", "RecursionError"]:
        result = executor.execute(
            CogLangExpr("If", (CogLangExpr(head, ("x",)), "yes", "no"))
        )
        assert result == "no", f"Expected {head}[] to be falsy, got {result!r}"


@pytest.mark.L1
def test_if_invalid_arity_returns_typeerror(executor):
    """If with missing or extra arguments must return a language error, not crash."""
    missing = executor.execute(parse('If[True[], "yes"]'))
    assert isinstance(missing, CogLangExpr)
    assert missing.head == "TypeError"
    assert missing.args[0] == "If"
    assert missing.args[1] == "arity"

    extra = executor.execute(parse('If[True[], "yes", "no", "extra"]'))
    assert isinstance(extra, CogLangExpr)
    assert extra.head == "TypeError"
    assert extra.args[0] == "If"
    assert extra.args[1] == "arity"


# ===========================================================================
# IfFound boundaries (§2.5 rows: empty-list is truthy / error is else)
# ===========================================================================

@pytest.mark.L2
def test_iffound_empty_list_goes_to_then(executor):
    """§2.5: IfFound[expr=List[], bind_, then, else] → then branch.

    List[] is NOT an error value. IfFound tests for error, not truthiness.
    bind_ is bound to List[]; body can use it.
    Distinct from If[List[]] which IS falsy (empty list → else in If).
    """
    # Traverse["Einstein", "no_edge"] → List[] (non-error, no results)
    result = executor.execute(
        parse('IfFound[Traverse["Einstein", "no_edge"], r_, "found_empty", "not_found"]')
    )
    assert result == "found_empty"


@pytest.mark.L2
def test_iffound_error_goes_to_else(executor):
    """§2.5: IfFound[expr=error, bind_, then, else] → else branch (bind_ not set)."""
    result = executor.execute(
        parse('IfFound[NotFound[], r_, "found", "not_found"]')
    )
    assert result == "not_found"


@pytest.mark.L1
def test_iffound_invalid_arity_returns_typeerror(executor):
    """IfFound with missing or extra arguments must return a language error, not crash."""
    missing = executor.execute(parse('IfFound[NotFound[], r_, "fallback"]'))
    assert isinstance(missing, CogLangExpr)
    assert missing.head == "TypeError"
    assert missing.args[0] == "IfFound"
    assert missing.args[1] == "arity"

    extra = executor.execute(
        parse('IfFound[NotFound[], r_, "then", "else", "extra"]')
    )
    assert isinstance(extra, CogLangExpr)
    assert extra.head == "TypeError"
    assert extra.args[0] == "IfFound"
    assert extra.args[1] == "arity"


# ===========================================================================
# Query boundaries (§2.5 row: no match → List[])
# ===========================================================================

@pytest.mark.L1
def test_query_no_match(executor):
    """§2.5: Query with no matching nodes → List[]."""
    result = executor.execute(
        parse('Query[n_, Equal[Get[n_, "type"], "NoSuchType"]]')
    )
    assert result == CogLangExpr("List", ())


@pytest.mark.L1
def test_query_with_options_default_mode(executor):
    """Query accepts explicit options when mode=default and k is well-typed."""
    result = executor.execute(
        parse('Query[n_, Equal[Get[n_, "type"], "Person"], {"k": 0, "mode": "default"}]')
    )
    assert result == CogLangExpr("List", ("Einstein",))


@pytest.mark.L1
def test_query_invalid_mode_type(executor):
    """Query must reject non-string mode values."""
    result = executor.execute(
        parse('Query[n_, Equal[Get[n_, "type"], "Person"], {"k": 1, "mode": 7}]')
    )
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Query"
    assert result.args[1] == "mode"


@pytest.mark.L1
def test_query_invalid_k_type(executor):
    """Query must reject k values outside non-negative int or \"inf\"."""
    result = executor.execute(
        parse('Query[n_, Equal[Get[n_, "type"], "Person"], {"k": "deep", "mode": "default"}]')
    )
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Query"
    assert result.args[1] == "k"


@pytest.mark.L1
def test_query_k_zero_blocks_graph_expansion(executor):
    """k=0 forbids Traverse-based graph expansion inside Query conditions."""
    result = executor.execute(
        parse(
            'Query[n_, IfFound[Get[Traverse[n_, "born_in"], 0], city_, True[], False[]], {"k": 0, "mode": "default"}]'
        )
    )
    assert result == CogLangExpr("List", ())


@pytest.mark.L1
def test_query_k_one_allows_single_hop_graph_expansion(executor):
    """k=1 allows single-hop Traverse inside Query conditions."""
    result = executor.execute(
        parse(
            'Query[n_, IfFound[Get[Traverse[n_, "born_in"], 0], city_, True[], False[]], {"k": 1, "mode": "default"}]'
        )
    )
    assert result == CogLangExpr("List", ("Einstein",))


@pytest.mark.L1
def test_query_k_two_allows_two_hop_graph_expansion():
    """Sequential dependent traversals require a budget covering both hops."""
    graph = _build_fixture_graph()
    graph.add_edge("Ulm", "Germany", relation_type="in_country", confidence=1.0)
    exec_ = PythonCogLangExecutor(graph)

    result = exec_.execute(
        parse(
            'Query[n_, IfFound[Get[Traverse[n_, "born_in"], 0], city_, '
            'IfFound[Get[Traverse[city_, "in_country"], 0], country_, Equal[country_, "Germany"], False[]], '
            'False[]], {"k": 2, "mode": "default"}]'
        )
    )
    assert result == CogLangExpr("List", ("Einstein",))

    blocked = exec_.execute(
        parse(
            'Query[n_, IfFound[Get[Traverse[n_, "born_in"], 0], city_, '
            'IfFound[Get[Traverse[city_, "in_country"], 0], country_, Equal[country_, "Germany"], False[]], '
            'False[]], {"k": 1, "mode": "default"}]'
        )
    )
    assert blocked == CogLangExpr("List", ())


# ===========================================================================
# ForEach boundaries (§2.5 rows: empty collection / non-List collection)
# ===========================================================================

@pytest.mark.L1
def test_foreach_empty_list(executor):
    """§2.5: ForEach over empty List[] → List[] (body never executed)."""
    result = executor.execute(parse('ForEach[List[], x_, Get[x_, "name"]]'))
    assert result == CogLangExpr("List", ())


@pytest.mark.L1
def test_foreach_non_list_collection(executor):
    """§2.5: ForEach with non-List collection → TypeError["ForEach","collection",...]."""
    result = executor.execute(parse('ForEach["hello", x_, Get[x_, "name"]]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "ForEach"
    assert result.args[1] == "collection"


@pytest.mark.L1
def test_foreach_invalid_arity_returns_typeerror(executor):
    """ForEach with missing or extra arguments must return a language error."""
    missing = executor.execute(parse("ForEach[List[]]"))
    assert isinstance(missing, CogLangExpr)
    assert missing.head == "TypeError"
    assert missing.args[0] == "ForEach"
    assert missing.args[1] == "arity"

    extra = executor.execute(parse('ForEach[List[], x_, x_, "extra"]'))
    assert isinstance(extra, CogLangExpr)
    assert extra.head == "TypeError"
    assert extra.args[0] == "ForEach"
    assert extra.args[1] == "arity"


# ===========================================================================
# Compose boundaries (§2.5 rows: override builtin / already registered)
# ===========================================================================

@pytest.mark.L2
def test_compose_override_builtin(executor):
    """§2.5: Compose with a builtin name (dispatch or special form) → TypeError[].

    "Traverse" is in _dispatch; "If" is in _special_forms.
    Both should be rejected.
    """
    result_dispatch = executor.execute(
        parse('Compose["Traverse", List[n_, e_], Traverse[n_, e_]]')
    )
    assert isinstance(result_dispatch, CogLangExpr)
    assert result_dispatch.head == "TypeError"

    result_special = executor.execute(
        parse('Compose["If", List[c_, t_, e_], If[c_, t_, e_]]')
    )
    assert isinstance(result_special, CogLangExpr)
    assert result_special.head == "TypeError"


@pytest.mark.L2
def test_compose_already_registered(executor):
    """§2.5: Compose with a name already registered as user op → TypeError[]."""
    # First registration succeeds
    result1 = executor.execute(
        parse('Compose["MyOp", List[n_], Traverse[n_, "born_in"]]')
    )
    assert result1 == {"operator_name": "MyOp", "scope": "graph-local"}

    # Second registration with same name fails
    result2 = executor.execute(
        parse('Compose["MyOp", List[n_], Traverse[n_, "field"]]')
    )
    assert isinstance(result2, CogLangExpr)
    assert result2.head == "TypeError"


@pytest.mark.L1
def test_compose_invalid_arity_returns_typeerror(executor):
    """Compose with missing or extra arguments must return a language error."""
    missing = executor.execute(parse('Compose["MyOp", List[n_]]'))
    assert isinstance(missing, CogLangExpr)
    assert missing.head == "TypeError"
    assert missing.args[0] == "Compose"
    assert missing.args[1] == "arity"

    extra = executor.execute(parse('Compose["MyOp", List[n_], n_, "extra"]'))
    assert isinstance(extra, CogLangExpr)
    assert extra.head == "TypeError"
    assert extra.args[0] == "Compose"
    assert extra.args[1] == "arity"


@pytest.mark.L1
def test_assert_invalid_arity_returns_typeerror(executor):
    """Assert with missing or extra arguments must return a language error."""
    missing = executor.execute(parse("Assert[]"))
    assert isinstance(missing, CogLangExpr)
    assert missing.head == "TypeError"
    assert missing.args[0] == "Assert"
    assert missing.args[1] == "arity"

    extra = executor.execute(parse('Assert[True[], "msg", "extra"]'))
    assert isinstance(extra, CogLangExpr)
    assert extra.head == "TypeError"
    assert extra.args[0] == "Assert"
    assert extra.args[1] == "arity"


@pytest.mark.L1
def test_do_invalid_arity_returns_typeerror(executor):
    """Do with zero arguments must return a language error."""
    missing = executor.execute(parse("Do[]"))
    assert isinstance(missing, CogLangExpr)
    assert missing.head == "TypeError"
    assert missing.args[0] == "Do"
    assert missing.args[1] == "arity"


# ===========================================================================
# Get boundaries (§2.5 rows: key missing / invalid source type)
# ===========================================================================

@pytest.mark.L1
def test_get_key_not_found(executor):
    """§2.5: Get key that doesn't exist → NotFound[].

    Covers: dict miss, List index out-of-range, node attribute miss.
    """
    # Dict key miss
    result = executor.execute(CogLangExpr("Get", ({"a": 1}, "no_such_key")))
    assert result == CogLangExpr("NotFound", ())

    # List index out of range
    result = executor.execute(CogLangExpr("Get", (CogLangExpr("List", ("x", "y")), 5)))
    assert result == CogLangExpr("NotFound", ())

    # Node attribute miss
    result = executor.execute(parse('Get["Einstein", "no_such_attr"]'))
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_get_invalid_source_type(executor):
    """§2.5: Get with source that is not str/dict/List → TypeError["Get","source",...]."""
    # 42 (int) is not a valid Get source
    result = executor.execute(CogLangExpr("Get", (42, "key")))
    assert isinstance(result, CogLangExpr)
    assert result.head == "TypeError"
    assert result.args[0] == "Get"
    assert result.args[1] == "source"
