"""Shared fixtures for the CogLang test suite.

The standard fixture graph is reused across parser, executor, backend, and
conformance-aligned runtime tests so behavioral expectations stay consistent.
"""

import pytest
import networkx as nx


def _build_fixture_graph() -> nx.DiGraph:
    """Build the shared fixture graph used across the current CogLang tests.

    Each test receives a fresh copy to prevent cross-test interference.
    """
    g = nx.DiGraph()

    # Nodes: (node_id, type, confidence, extra attrs)
    g.add_node("Einstein",    type="Person",    confidence=1.0, name="Albert Einstein")
    g.add_node("Ulm",         type="Entity",    confidence=1.0, name="Ulm")
    g.add_node("Nobel_Prize", type="Entity",    confidence=1.0, name="Nobel Prize in Physics")
    g.add_node("Germany",     type="Entity",    confidence=1.0, name="Germany")
    g.add_node("Physics",     type="Attribute", confidence=1.0, name="Physics")
    g.add_node("Axiom_Node",  type="Entity",    confidence=1.0, immutable=True,
               name="Immutable Axiom")
    # Soft-deleted node (confidence=0) — Traverse skips it as origin or target
    g.add_node("Deleted_Node", type="Entity",   confidence=0.0, name="Already Deleted")

    # Edges: (source, target, relation_type, confidence)
    g.add_edge("Einstein", "Ulm",         relation_type="born_in",     confidence=1.0)
    g.add_edge("Einstein", "Germany",     relation_type="nationality",  confidence=0.9)
    g.add_edge("Einstein", "Nobel_Prize", relation_type="awards",       confidence=1.0)
    g.add_edge("Einstein", "Physics",     relation_type="field",        confidence=1.0)
    # Soft-deleted edge (confidence=0) — Traverse skips it
    g.add_edge("Einstein", "Deleted_Node", relation_type="related_to", confidence=0.0)

    return g


@pytest.fixture
def fixture_graph() -> nx.DiGraph:
    """pytest fixture: fresh copy of the standard test graph per test function."""
    return _build_fixture_graph()


@pytest.fixture
def executor(fixture_graph):
    """pytest fixture: PythonCogLangExecutor on the standard test graph.

    Kept as a small convenience wrapper so tests can share one fixture name
    while still constructing inline executors when they need custom setup.
    """
    from coglang.executor import PythonCogLangExecutor
    return PythonCogLangExecutor(fixture_graph)
