"""GraphBackend behavioral tests for the current CogLang graph runtime.

Coverage:
  [L1] methods instantiate and basic calls succeed
  [L2] Traverse: normal traversal, soft-deleted edge skipped, soft-deleted
       target node skipped, non-existent node returns List[]
  [L2] create_node: success, duplicate ID returns TypeError[]
  [L2] create_edge: success, missing endpoint returns NotFound[]
  [L2] update: success, non-existent target returns NotFound[], immutable and
       soft-deleted targets return PermissionError[]
  [L2] delete_node: soft-delete, idempotent NotFound[], immutable PermissionError[]
  [L2] delete_edge: soft-delete, non-existent returns NotFound[], idempotent NotFound[]
  [L2] to_dict / from_dict roundtrip: node/edge counts, attributes, _next_id
"""

import pytest
import networkx as nx

from logos.coglang.graph_backend import GraphBackend
from logos.coglang.parser import CogLangExpr


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def gb(fixture_graph):
    """GraphBackend wrapping the standard fixture graph."""
    return GraphBackend(fixture_graph)


@pytest.fixture
def empty_gb():
    """GraphBackend with an empty graph."""
    return GraphBackend()


# ---------------------------------------------------------------------------
# [L1] Basic: all methods callable without crash
# ---------------------------------------------------------------------------

@pytest.mark.L1
def test_instantiate_empty():
    """GraphBackend() creates an empty graph."""
    b = GraphBackend()
    assert isinstance(b.graph, nx.DiGraph)
    assert len(b.graph.nodes) == 0
    assert b._next_id == 0


@pytest.mark.L1
def test_instantiate_with_fixture(gb):
    """GraphBackend(fixture_graph) wraps the provided graph."""
    assert len(gb.graph.nodes) == 7
    assert len(gb.graph.edges) == 5


@pytest.mark.L1
def test_graph_sharing(fixture_graph):
    """GraphBackend and its caller share the same nx.DiGraph object."""
    gb = GraphBackend(fixture_graph)
    assert gb.graph is fixture_graph


@pytest.mark.L1
def test_traverse_basic_call(gb):
    """traverse() returns a CogLangExpr without crash."""
    result = gb.traverse("Einstein", "born_in")
    assert isinstance(result, CogLangExpr)


@pytest.mark.L1
def test_create_node_basic(empty_gb):
    """create_node() returns a string node ID."""
    result = empty_gb.create_node("Entity", {"name": "Tesla"})
    assert isinstance(result, str)


@pytest.mark.L1
def test_delete_node_basic(gb):
    """delete_node() returns without crash on a valid target."""
    result = gb.delete_node("Ulm")
    assert result == "Ulm"


# ---------------------------------------------------------------------------
# [L2] traverse
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_traverse_single_hop(gb):
    """traverse('Einstein', 'born_in') → List['Ulm']."""
    result = gb.traverse("Einstein", "born_in")
    assert result == CogLangExpr("List", ("Ulm",))


@pytest.mark.L2
def test_traverse_multiple_results(gb):
    """traverse returns multiple neighbors when multiple edges match."""
    # Einstein has born_in, nationality, awards, field edges (related_to conf=0 skipped)
    result = gb.traverse("Einstein", "awards")
    assert result == CogLangExpr("List", ("Nobel_Prize",))


@pytest.mark.L2
def test_traverse_nonexistent_node(gb):
    """traverse on a non-existent node returns List[]."""
    result = gb.traverse("NonExistent", "born_in")
    assert result == CogLangExpr("List", ())


@pytest.mark.L2
def test_traverse_nonexistent_edge_type(gb):
    """traverse with an edge type that has no matches returns List[]."""
    result = gb.traverse("Einstein", "no_such_relation")
    assert result == CogLangExpr("List", ())


@pytest.mark.L2
def test_traverse_skips_soft_deleted_edge(gb):
    """traverse skips edges where confidence=0 (soft-deleted edge)."""
    # Einstein→related_to→Deleted_Node has confidence=0
    result = gb.traverse("Einstein", "related_to")
    assert result == CogLangExpr("List", ())


@pytest.mark.L2
def test_traverse_skips_soft_deleted_target(empty_gb):
    """traverse skips edges whose target node has confidence=0."""
    g = empty_gb.graph
    g.add_node("A", type="Entity", confidence=1.0)
    g.add_node("B", type="Entity", confidence=0.0)  # soft-deleted target
    g.add_edge("A", "B", relation_type="links_to", confidence=1.0)
    result = empty_gb.traverse("A", "links_to")
    assert result == CogLangExpr("List", ())


@pytest.mark.L2
def test_traverse_args_are_tuple(gb):
    """traverse returns CogLangExpr with args as tuple (SCC-G1)."""
    result = gb.traverse("Einstein", "born_in")
    assert type(result.args) is tuple


@pytest.mark.L2
def test_traverse_non_string_node(gb):
    """traverse with non-string node argument returns TypeError[]."""
    result = gb.traverse(42, "born_in")
    assert result.head == "TypeError"
    assert type(result.args) is tuple


# ---------------------------------------------------------------------------
# [L2] create_node
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_create_node_success(empty_gb):
    """create_node returns node ID string and node is added to graph."""
    node_id = empty_gb.create_node("Entity", {"name": "Tesla"})
    assert isinstance(node_id, str)
    assert node_id in empty_gb.graph
    assert empty_gb.graph.nodes[node_id]["type"] == "Entity"
    assert empty_gb.graph.nodes[node_id]["confidence"] == 1.0


@pytest.mark.L2
def test_create_node_increments_next_id(empty_gb):
    """create_node increments _next_id after each creation."""
    empty_gb.create_node("Entity", {})
    empty_gb.create_node("Entity", {})
    assert empty_gb._next_id == 2


@pytest.mark.L2
def test_create_node_duplicate_id(empty_gb):
    """create_node with an already-existing ID returns TypeError[]."""
    empty_gb.create_node("Entity", {"id": "my_node"})
    result = empty_gb.create_node("Entity", {"id": "my_node"})
    assert result == CogLangExpr("TypeError", ("Create", "id", "node already exists", "my_node"))


@pytest.mark.L2
def test_create_node_attrs_with_type_key(empty_gb):
    """create_node ignores attrs['type'] and preserves explicit node_type."""
    result = empty_gb.create_node("Entity", {"type": "override_attempt", "name": "X"})
    assert isinstance(result, str)
    assert empty_gb.graph.nodes[result]["type"] == "Entity"
    assert empty_gb.graph.nodes[result]["name"] == "X"


@pytest.mark.L2
def test_create_node_with_custom_id(empty_gb):
    """create_node respects explicit 'id' in attrs."""
    result = empty_gb.create_node("Entity", {"id": "custom_id", "name": "X"})
    assert result == "custom_id"
    assert "custom_id" in empty_gb.graph


# ---------------------------------------------------------------------------
# [L2] create_edge
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_create_edge_success(gb):
    """create_edge between two existing nodes returns List[src, rel, tgt]."""
    result = gb.create_edge("Ulm", "Germany", "located_in")
    assert result == CogLangExpr("List", ("Ulm", "located_in", "Germany"))
    assert gb.graph.has_edge("Ulm", "Germany")


@pytest.mark.L2
def test_create_edge_missing_source(gb):
    """create_edge with non-existent source returns NotFound[] (SCC-G7)."""
    result = gb.create_edge("NoSuchNode", "Germany", "located_in")
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_create_edge_missing_target(gb):
    """create_edge with non-existent target returns NotFound[] (SCC-G7)."""
    result = gb.create_edge("Einstein", "NoSuchNode", "knows")
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_create_edge_both_missing(gb):
    """create_edge with both endpoints missing returns NotFound[] (SCC-G7)."""
    result = gb.create_edge("X", "Y", "rel")
    assert result == CogLangExpr("NotFound", ())


# ---------------------------------------------------------------------------
# [L2] update
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_update_success(gb):
    """update existing node returns True[]."""
    result = gb.update("Einstein", {"name": "A. Einstein"})
    assert result == CogLangExpr("True", ())
    assert gb.graph.nodes["Einstein"]["name"] == "A. Einstein"


@pytest.mark.L2
def test_update_nonexistent_node(gb):
    """update non-existent node returns NotFound[]."""
    result = gb.update("NoSuchNode", {"name": "X"})
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_update_soft_deleted_node(gb):
    """update soft-deleted node (confidence=0) returns PermissionError[]."""
    result = gb.update("Deleted_Node", {"name": "New"})
    assert result == CogLangExpr("PermissionError", ("Update", "Deleted_Node"))


@pytest.mark.L2
def test_update_immutable_node(gb):
    """update immutable node returns PermissionError[]."""
    result = gb.update("Axiom_Node", {"name": "changed"})
    assert result == CogLangExpr("PermissionError", ("Update", "Axiom_Node"))


# ---------------------------------------------------------------------------
# [L2] delete_node (SCC-G3: three idempotency paths)
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_delete_node_success(gb):
    """delete_node soft-deletes node (confidence→0) and returns node ID."""
    result = gb.delete_node("Ulm")
    assert result == "Ulm"
    assert gb.graph.nodes["Ulm"]["confidence"] == 0.0


@pytest.mark.L2
def test_delete_node_nonexistent(gb):
    """delete_node on non-existent node returns NotFound[] (SCC-G3a)."""
    result = gb.delete_node("NoSuchNode")
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_delete_node_already_deleted(gb):
    """delete_node on already-soft-deleted node returns NotFound[] (SCC-G3b)."""
    result = gb.delete_node("Deleted_Node")
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_delete_node_immutable(gb):
    """delete_node on immutable node returns PermissionError[] (SCC-G3c)."""
    result = gb.delete_node("Axiom_Node")
    assert result == CogLangExpr("PermissionError", ("Delete", "Axiom_Node"))


# ---------------------------------------------------------------------------
# [L2] delete_edge
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_delete_edge_success(gb):
    """delete_edge soft-deletes edge (confidence→0) and returns List triplet."""
    result = gb.delete_edge("Einstein", "Ulm", "born_in")
    assert result == CogLangExpr("List", ("Einstein", "born_in", "Ulm"))
    edge_data = gb.graph.get_edge_data("Einstein", "Ulm")
    assert edge_data["confidence"] == 0.0


@pytest.mark.L2
def test_delete_edge_nonexistent_nodes(gb):
    """delete_edge with non-existent endpoints returns NotFound[]."""
    result = gb.delete_edge("X", "Y", "rel")
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_delete_edge_nonexistent_edge(gb):
    """delete_edge when edge triplet doesn't match returns NotFound[]."""
    result = gb.delete_edge("Einstein", "Ulm", "no_such_relation")
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_delete_edge_already_deleted(gb):
    """delete_edge on already-soft-deleted edge returns NotFound[] (idempotent)."""
    # Einstein→related_to→Deleted_Node already has confidence=0
    result = gb.delete_edge("Einstein", "Deleted_Node", "related_to")
    assert result == CogLangExpr("NotFound", ())


# ---------------------------------------------------------------------------
# [L2] to_dict / from_dict roundtrip (SCC-G6)
# ---------------------------------------------------------------------------

@pytest.mark.L2
def test_to_dict_from_dict_roundtrip(gb):
    """to_dict/from_dict preserves node count, edge count, and attributes."""
    data = gb.to_dict()
    restored = GraphBackend.from_dict(data)

    assert len(restored.graph.nodes) == len(gb.graph.nodes)
    assert len(restored.graph.edges) == len(gb.graph.edges)

    # Spot-check attributes
    assert restored.graph.nodes["Einstein"]["confidence"] == 1.0
    assert restored.graph.nodes["Deleted_Node"]["confidence"] == 0.0
    assert restored.graph.nodes["Axiom_Node"].get("immutable") is True

    edge = restored.graph.get_edge_data("Einstein", "Ulm")
    assert edge["relation_type"] == "born_in"
    assert edge["confidence"] == 1.0


@pytest.mark.L2
def test_from_dict_restores_next_id(empty_gb):
    """from_dict restores _next_id so new node IDs don't collide (SCC-G6)."""
    empty_gb.create_node("Entity", {})  # node_0
    empty_gb.create_node("Entity", {})  # node_1
    assert empty_gb._next_id == 2

    data = empty_gb.to_dict()
    restored = GraphBackend.from_dict(data)
    assert restored._next_id == 2

    # Creating a new node should not collide
    new_id = restored.create_node("Entity", {"name": "new"})
    assert new_id not in ("node_0", "node_1")
