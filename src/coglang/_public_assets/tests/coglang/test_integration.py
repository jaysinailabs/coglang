"""Integration and baseline-performance tests for the current CogLang runtime.

These tests validate the end-to-end path:
  parse -> execute -> canonicalize -> transport-safe textual output

They catch failures that component-level tests often miss:
  - execute() result not serializable by canonicalize()
  - output wrapper format drifting
  - error value roundtrip instability

The slow performance test records a local baseline on a larger graph. It is a
regression guard, not a product-stage milestone.
"""

import pytest
import statistics
import time

import networkx as nx

from coglang.parser import CogLangExpr, parse, canonicalize
from coglang.validator import valid_coglang
from coglang.executor import PythonCogLangExecutor
from tests.coglang.conftest import _build_fixture_graph


# ===========================================================================
# Contract-style integration tests
# ===========================================================================

@pytest.mark.L2
def test_single_step_integration_contract():
    """§4.6 #1: parse → execute → result correct + §2.8 Encoder output format.

    Validates:
    1. execute(parse('Traverse[...]')) returns the expected CogLangExpr.
    2. The §2.8 format (canonicalize + newline + <|end_coglang|>) is correct.
    """
    exec_ = PythonCogLangExecutor(_build_fixture_graph())
    result = exec_.execute(parse('Traverse["Einstein", "born_in"]'))
    assert result == CogLangExpr("List", ("Ulm",))

    # §2.8 Encoder output format
    canonical = canonicalize(parse('Traverse["Einstein", "born_in"]'))
    training_item = canonical + "\n<|end_coglang|>"
    assert training_item == 'Traverse["Einstein", "born_in"]\n<|end_coglang|>'


@pytest.mark.L2
def test_multi_step_integration_contract():
    """§4.6 #2: Multi-step Do expression valid + parse/canonicalize roundtrip.

    Validates:
    1. valid_coglang() accepts a multi-step Do expression.
    2. parse(canonicalize(expr)) == expr (roundtrip guarantee per §2.7).
    """
    program = 'Do[Traverse["Einstein", "born_in"], Traverse["Einstein", "awards"]]'
    expr = parse(program)
    assert valid_coglang(expr)
    assert parse(canonicalize(expr)) == expr


@pytest.mark.L2
def test_error_value_integration_format():
    """§4.6 #3: Error value canonicalize format is stable.

    Encoder must learn error paths; the canonical format of error values must
    be deterministic and roundtrip-safe.
    """
    error_expr = CogLangExpr("TypeError", ("Traverse", "node", "expected string", "bad"))
    s = canonicalize(error_expr)
    assert s == 'TypeError["Traverse", "node", "expected string", "bad"]'
    assert parse(s) == error_expr


# ===========================================================================
# Performance baseline — run with: pytest -m slow
# ===========================================================================

@pytest.mark.slow
def test_performance_baseline_1000_nodes():
    """§4.5: 1000-node graph, Traverse + Match 100x each. Prints p50/p95 latency.

    This test is not a pass/fail assertion on latency (hardware varies).
    It records a local baseline for future regression comparison.
    A hard ceiling of 500ms/call is enforced only to catch catastrophic regressions.

    Run: pytest -m slow tests/coglang/test_integration.py -s
    """
    # Build 1000-node graph with ~500 edges
    g = nx.DiGraph()
    for i in range(1000):
        g.add_node(f"node_{i}", type="Entity", confidence=1.0)
    for i in range(0, 999, 2):
        g.add_edge(f"node_{i}", f"node_{i+1}", relation_type="links_to", confidence=1.0)

    exec_ = PythonCogLangExecutor(g)

    # Traverse 100 times
    traverse_expr = parse('Traverse["node_0", "links_to"]')
    traverse_times = []
    for _ in range(100):
        t0 = time.perf_counter()
        exec_.execute(traverse_expr)
        traverse_times.append((time.perf_counter() - t0) * 1000)

    # Match 100 times
    match_expr = parse('Match[f[X_, b], f[a, Y_]]')
    match_times = []
    for _ in range(100):
        t0 = time.perf_counter()
        exec_.execute(match_expr)
        match_times.append((time.perf_counter() - t0) * 1000)

    traverse_p50 = statistics.median(traverse_times)
    traverse_p95 = sorted(traverse_times)[94]  # 95th percentile (index 94 of 100)
    match_p50 = statistics.median(match_times)
    match_p95 = sorted(match_times)[94]

    print(f"\n[Performance Baseline] 1000-node graph, 100 calls each:")
    print(f"  Traverse: p50={traverse_p50:.3f}ms  p95={traverse_p95:.3f}ms")
    print(f"  Match:    p50={match_p50:.3f}ms  p95={match_p95:.3f}ms")

    # Hard ceiling: 500ms/call is a sign of catastrophic regression
    assert traverse_p95 < 500, f"Traverse p95 too slow: {traverse_p95:.1f}ms"
    assert match_p95 < 500, f"Match p95 too slow: {match_p95:.1f}ms"
