# CogLang graph operations backend using NetworkX.
# DL-013 (Method B): GraphBackend accepts an external nx.DiGraph and is its
# sole owner. PythonCogLangExecutor does NOT hold self.graph directly.
from __future__ import annotations

from typing import Union

import networkx as nx

from .parser import CogLangExpr


class GraphBackend:
    """NetworkX-backed CogLang graph operations.

    Design principle: every method returns a CogLang value (str / CogLangExpr).
    No Python exceptions escape to the CogLang layer (CogLang Principle 3:
    errors are values).

    Node attributes:
        type:       str  — PascalCase entity category
        confidence: float ∈ [0.0, 1.0]  — 0.0 = soft-deleted
        immutable:  bool  — True = axiom node, cannot be modified or deleted
        name:       str (optional)

    Edge attributes:
        relation_type: str
        confidence:    float ∈ [0.0, 1.0]  — 0.0 = soft-deleted
    """

    def __init__(self, graph: nx.DiGraph = None):
        # DL-013 method B: accept external graph so executor can share it.
        # If no graph is supplied, create a fresh one.
        self.graph: nx.DiGraph = graph if graph is not None else nx.DiGraph()
        self._next_id: int = self._compute_next_id()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_next_id(self) -> int:
        """Compute _next_id from existing node_NNN IDs to avoid collisions."""
        ids = [
            int(n[5:]) + 1
            for n in self.graph.nodes
            if n.startswith("node_") and n[5:].isdigit()
        ]
        return max(ids, default=0)

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def traverse(self, node: str, edge_type: str) -> CogLangExpr:
        """Return neighbor nodes reachable via edges of the given type.

        Soft-deleted edges (confidence=0) and soft-deleted target nodes
        (confidence=0) are both filtered out. Returns List[] for missing
        nodes or edge types.
        """
        if not isinstance(node, str):
            return CogLangExpr("TypeError", ("Traverse", "node", "expected string", repr(node)))
        if node not in self.graph:
            return CogLangExpr("List", ())
        results = tuple(
            target
            for _, target, data in self.graph.out_edges(node, data=True)
            if data.get("relation_type") == edge_type
            and data.get("confidence", 1.0) > 0
            and self.graph.nodes[target].get("confidence", 1.0) > 0
        )
        return CogLangExpr("List", results)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_node(self, node_type: str, attrs: dict) -> Union[str, CogLangExpr]:
        """Create a node and return its ID; return TypeError[] if ID already exists.

        KNOWN LIMITATION (TD-001): node_id must not be a CogLang error head string
        (e.g. "NotFound", "TypeError", "PermissionError").  If a node is named
        after an error head, PythonCogLangExecutor's eager-eval pass will treat the
        traverse result as an error value rather than a node ID, causing silent
        mis-routing.  P0 fixture graph avoids this naming; fix target: S2c-2
        (_dispatch transparent constructors isolate error values from node IDs).

        NOTE: attrs["type"] is treated as a reserved key at the language layer.
        The backend does not let attrs override the explicit node_type parameter;
        any stray "type" key is ignored here so internal callers do not
        accidentally mutate the public node type contract.
        """
        node_id = attrs.get("id") or f"node_{self._next_id}"
        if node_id in self.graph:
            return CogLangExpr("TypeError", ("Create", "id", "node already exists", node_id))
        self._next_id += 1
        # Build merged dict first to avoid duplicate keyword argument error.
        # Public node type always comes from the explicit node_type parameter;
        # attrs["type"] is ignored at this layer.
        merged = {"type": node_type, "confidence": 1.0}
        merged.update({k: v for k, v in attrs.items() if k not in {"id", "type"}})
        self.graph.add_node(node_id, **merged)
        return node_id

    def create_edge(self, source: str, target: str, relation_type: str,
                    confidence: float = 1.0) -> CogLangExpr:
        """Create a directed edge; return NotFound[] if either endpoint is missing."""
        if source not in self.graph or target not in self.graph:
            return CogLangExpr("NotFound", ())
        self.graph.add_edge(source, target, relation_type=relation_type, confidence=confidence)
        return CogLangExpr("List", (source, relation_type, target))

    def update(self, target: str, changes: dict) -> CogLangExpr:
        """Update node attributes; return True[] on success, error value otherwise.

        Returns NotFound[] if target does not exist or is soft-deleted.
        Returns PermissionError[] if target is immutable.
        """
        if target not in self.graph:
            return CogLangExpr("NotFound", ())
        node_data = self.graph.nodes[target]
        if node_data.get("confidence", 1.0) == 0.0:
            return CogLangExpr("PermissionError", ("Update", target))
        if node_data.get("immutable"):
            return CogLangExpr("PermissionError", ("Update", target))
        node_data.update(changes)
        return CogLangExpr("True", ())

    def delete_node(self, target: str) -> Union[str, CogLangExpr]:
        """Soft-delete a node (confidence → 0.0); return node ID on success.

        Idempotent: returns NotFound[] if target doesn't exist or is already deleted.
        Returns PermissionError[] if target is immutable.
        """
        if target not in self.graph:
            return CogLangExpr("NotFound", ())
        node_data = self.graph.nodes[target]
        if node_data.get("confidence", 1.0) == 0.0:
            return CogLangExpr("NotFound", ())  # idempotent — already soft-deleted
        if node_data.get("immutable"):
            return CogLangExpr("PermissionError", ("Delete", target))
        node_data["confidence"] = 0.0
        return target

    def delete_edge(self, source: str, target: str, relation_type: str) -> CogLangExpr:
        """Soft-delete a directed edge (confidence → 0.0).

        Returns List[source, relation_type, target] on success.
        Returns NotFound[] if the edge triplet does not exist.
        Idempotent: returns NotFound[] if edge is already soft-deleted.
        """
        if source not in self.graph or target not in self.graph:
            return CogLangExpr("NotFound", ())
        edge_data = self.graph.get_edge_data(source, target)
        if edge_data is None or edge_data.get("relation_type") != relation_type:
            return CogLangExpr("NotFound", ())
        if edge_data.get("confidence", 1.0) == 0.0:
            return CogLangExpr("NotFound", ())  # idempotent — already soft-deleted
        edge_data["confidence"] = 0.0
        return CogLangExpr("List", (source, relation_type, target))

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the graph to a JSON-compatible dict (node_link_data format)."""
        return nx.node_link_data(self.graph)

    @classmethod
    def from_dict(cls, data: dict) -> "GraphBackend":
        """Restore a GraphBackend from to_dict() output."""
        backend = cls()
        backend.graph = nx.node_link_graph(data)
        backend._next_id = backend._compute_next_id()
        return backend
