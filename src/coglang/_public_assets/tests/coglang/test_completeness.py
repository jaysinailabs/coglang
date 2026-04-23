"""Completeness tests for the current CogLang Python runtime.

Expected outputs are derived from the fixture graph rather than from
implementation accidents, so this file remains a semantic drift guard.

Fixture graph quick reference (for derivation verification):
  Einstein --born_in--> Ulm          (conf=1.0)
  Einstein --nationality--> Germany  (conf=0.9)
  Einstein --awards--> Nobel_Prize   (conf=1.0, name="Nobel Prize in Physics")
  Einstein --field--> Physics        (conf=1.0)
  Einstein --related_to--> Deleted_Node (conf=0.0, SOFT-DELETED edge)
  Deleted_Node: confidence=0.0 (SOFT-DELETED node)
  Axiom_Node:   immutable=True
"""

import pytest

# ---------------------------------------------------------------------------
# Guarded imports keep the failure mode readable if the local runtime is broken.
# When unavailable, each test fails at the first assert with a clear message.
# ---------------------------------------------------------------------------
try:
    from logos.coglang.parser import parse, CogLangExpr, CogLangVar
    from logos.coglang.executor import PythonCogLangExecutor
    _LOGOS_AVAILABLE = True
except (ImportError, ModuleNotFoundError, AttributeError):
    _LOGOS_AVAILABLE = False


_IMPORT_GUARD_MSG = "logos.coglang import failed; runtime is not currently executable"


# ===========================================================================
# 基础图操作 (Tests 01–05)
# ===========================================================================

@pytest.mark.L2
def test_01_single_hop_traverse(fixture_graph):
    """单跳遍历：Einstein -born_in-> Ulm."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    # Derivation: edge Einstein→Ulm (born_in, conf=1.0) is visible; target Ulm conf=1.0.
    result = exec_.execute(parse('Traverse["Einstein", "born_in"]'))
    assert result == CogLangExpr("List", ("Ulm",))


@pytest.mark.L2
def test_02_multi_hop_chain(fixture_graph):
    """多跳推理链：traverse edge then access attribute of each result via ForEach."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    # Derivation:
    #   Traverse["Einstein","awards"] → List["Nobel_Prize"]
    #   ForEach over List["Nobel_Prize"]: Get["Nobel_Prize","name"] → "Nobel Prize in Physics"
    #   ForEach result → List["Nobel Prize in Physics"]
    result = exec_.execute(
        parse('ForEach[Traverse["Einstein", "awards"], prize_, Get[prize_, "name"]]')
    )
    assert result == CogLangExpr("List", ("Nobel Prize in Physics",))


@pytest.mark.L2
def test_03_match_unification(fixture_graph):
    """项级合一：Match = Unify alias，返回变量绑定字典（key 不含尾部 _）."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    # Derivation (Robinson unification):
    #   f(X, b) ~ f(a, Y) → X←a, Y←b → {"X": "a", "Y": "b"}
    result = exec_.execute(parse('Match[f[X_, b], f[a, Y_]]'))
    assert result == {"X": "a", "Y": "b"}


@pytest.mark.L2
def test_04_crud_complete(fixture_graph):
    """CRUD 完整流程：Create → Update → Delete (soft) → 幂等 Delete."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)

    # Create: returns node_id string
    node_id = exec_.execute(parse('Create["Entity", {"id": "Tesla", "name": "Nikola Tesla"}]'))
    assert node_id == "Tesla"

    # Update: returns True[]
    r_update = exec_.execute(parse('Update["Tesla", {"occupation": "inventor"}]'))
    assert r_update == CogLangExpr("True", ())

    # Soft delete: confidence→0, returns node_id
    r_delete = exec_.execute(parse('Delete["Tesla"]'))
    assert r_delete == "Tesla"

    # Idempotent: second delete on already-soft-deleted node returns NotFound[]
    r_delete2 = exec_.execute(parse('Delete["Tesla"]'))
    assert r_delete2 == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_05_soft_delete_traverse_skip(fixture_graph):
    """软删除：confidence=0 的边和目标节点被 Traverse 跳过."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    # Derivation: edge Einstein→Deleted_Node (related_to, conf=0.0) is soft-deleted.
    # Traverse skips edges with confidence=0 AND targets with confidence=0.
    result = exec_.execute(parse('Traverse["Einstein", "related_to"]'))
    assert result == CogLangExpr("List", ())


# ===========================================================================
# 逻辑与控制 (Tests 06–10)
# ===========================================================================

@pytest.mark.L2
def test_06_conditional_if(fixture_graph):
    """条件分支：Query 找到 Person 节点 → 非空 List 为真 → If 返回 then 分支."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    # Derivation:
    #   Query[n_, Equal[Get[n_,"type"],"Person"]]:
    #     Einstein (type="Person") → Equal→True[] → matches
    #     others (type="Entity"/"Attribute") → False[] → skip
    #     Deleted_Node (conf=0) → not visited
    #   → List["Einstein"] (non-empty)
    #   If[List["Einstein"], "found", "not_found"] → truthy → "found"
    result = exec_.execute(
        parse('If[Query[n_, Equal[Get[n_, "type"], "Person"]], "found", "not_found"]')
    )
    assert result == "found"


@pytest.mark.L2
def test_07_unify_with_bindings(fixture_graph):
    """合一含变量绑定：Unify 返回 MGU 字典."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    # Derivation: same as test_03 but via Unify directly (not Match alias).
    result = exec_.execute(parse('Unify[f[X_, b], f[a, Y_]]'))
    assert result == {"X": "a", "Y": "b"}


@pytest.mark.L2
def test_08_unify_fails(fixture_graph):
    """不可合一：heads f≠g → Unify returns NotFound[]."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    # Derivation: f(a) ~ g(b) fails at head comparison (f ≠ g).
    result = exec_.execute(parse('Unify[f[a], g[b]]'))
    assert result == CogLangExpr("NotFound", ())


@pytest.mark.L2
def test_09_foreach_iteration(fixture_graph):
    """迭代：ForEach 对每个元素执行 body；item_ 词法作用域（body 外不可用）."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    # Derivation: ForEach[List["a","b"], item_, Get[item_, 0]]
    #   snapshot = ["a", "b"]
    #   "a" is a string; treated as node ID; "a" not in fixture graph → NotFound[]
    #   "b" similarly → NotFound[]
    #   ForEach result: List[NotFound[], NotFound[]]
    # (Lexical scope: item_ is only bound inside the body, not in outer env.)
    result = exec_.execute(parse('ForEach[List["a","b"], item_, Get[item_, 0]]'))
    assert result == CogLangExpr("List", (
        CogLangExpr("NotFound", ()),
        CogLangExpr("NotFound", ()),
    ))


@pytest.mark.L1
def test_10_empty_query_result(fixture_graph):
    """空结果处理：Query 无匹配 → List[]."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    # Derivation: no node in fixture has type="NonExistentType" → empty list.
    result = exec_.execute(
        parse('Query[n_, Equal[Get[n_, "type"], "NonExistentType"]]')
    )
    assert result == CogLangExpr("List", ())


# ===========================================================================
# 学习与归纳 (Tests 11–14)
# ===========================================================================

@pytest.mark.L1
def test_11_abstract_summary_contract(fixture_graph):
    """ABSTRACT 最小真实路径：返回摘要对象，不产规则、不写图。"""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    result = exec_.execute(parse('Abstract[List["Einstein", "Tesla"]]'))
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert result["instance_count"] == 2
    assert isinstance(result["cluster_id"], str)
    assert isinstance(result["prototype_ref"], str)
    assert isinstance(result["equivalence_class_ref"], str)
    assert isinstance(result["selection_basis"], str)
    assert result["triggered"] == CogLangExpr("False", ())
    assert result["member_refs"] == CogLangExpr("List", ("Einstein", "Tesla"))


@pytest.mark.L2
def test_12_compose_and_call(fixture_graph):
    """COMPOSE 注册新操作并可调用（含参数替换验证）."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    # Derivation:
    #   Compose["FindBirthplace", List[person_], Traverse[person_, "born_in"]]
    #   → registers OPERATION node "FindBirthplace" with body=Traverse[person_,"born_in"]
    #   FindBirthplace["Einstein"]
    #   → binds person_="Einstein", executes Traverse["Einstein","born_in"]
    #   → List["Ulm"]
    exec_.execute(
        parse('Compose["FindBirthplace", List[person_], Traverse[person_, "born_in"]]')
    )
    result = exec_.execute(parse('FindBirthplace["Einstein"]'))
    assert result == CogLangExpr("List", ("Ulm",))


@pytest.mark.L1
def test_13_probe_reserved_fallback(fixture_graph):
    """PROBE 当前走保留能力的默认回退：返回 StubError["Probe", ...]."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    result = exec_.execute(parse('Probe[List["rule"], {"context": "test"}]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "StubError"
    assert result.args[0] == "Probe"


@pytest.mark.L2
def test_14_rule_node_draft_layer(fixture_graph):
    """规则节点草稿层：confidence=0.5 > 0，Traverse 可见（未软删除）."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    # Derivation:
    #   Create Rule node with confidence=0.5 (draft, not soft-deleted)
    #   Add edge Einstein→TestRule (follows, conf=1.0)
    #   Traverse["Einstein","follows"] → confidence=0.5 > 0 → node IS visible
    #   → List["TestRule"]
    exec_.execute(
        parse('Create["Rule", {"id": "TestRule", "name": "test_rule", "confidence": 0.5}]')
    )
    exec_.execute(
        parse('Create["Edge", {"from": "Einstein", "to": "TestRule", '
              '"relation_type": "follows", "confidence": 1.0}]')
    )
    result = exec_.execute(parse('Traverse["Einstein", "follows"]'))
    assert result == CogLangExpr("List", ("TestRule",))


# ===========================================================================
# 消息与通信 (Tests 15–17)
# ===========================================================================

@pytest.mark.L1
def test_15_send_reserved_fallback(fixture_graph):
    """SEND 当前走保留能力的默认回退：返回 StubError["Send", ...]."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    result = exec_.execute(parse('Send["layer_2", "activate", "attention"]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "StubError"
    assert result.args[0] == "Send"


@pytest.mark.L1
def test_16_inspect_reserved_fallback(fixture_graph):
    """INSPECT 当前走保留能力的默认回退：返回 StubError["Inspect", ...]."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    result = exec_.execute(parse('Inspect["Einstein"]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "StubError"
    assert result.args[0] == "Inspect"


@pytest.mark.L1
def test_17_send_with_type_param_reserved_fallback(fixture_graph):
    """SEND 带 type 参数的调用当前仍走默认回退路径。"""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    result = exec_.execute(parse('Send["target", "message", "broadcast"]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "StubError"


# ===========================================================================
# 预算控制 (Tests 18–20)
# ===========================================================================

@pytest.mark.L1
def test_18_estimate_reserved_fallback(fixture_graph):
    """ESTIMATE 当前走保留能力的默认回退：返回 StubError["Estimate", ...]."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    result = exec_.execute(parse('Estimate["Traverse", List["Einstein", "born_in"]]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "StubError"
    assert result.args[0] == "Estimate"


@pytest.mark.L1
def test_19_defer_reserved_fallback(fixture_graph):
    """DEFER 当前走保留能力的默认回退：返回 StubError["Defer", ...]."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    result = exec_.execute(parse('Defer["some_complex_task"]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "StubError"
    assert result.args[0] == "Defer"


@pytest.mark.L1
def test_20_decompose_reserved_fallback(fixture_graph):
    """DECOMPOSE 当前走保留能力的默认回退：返回 StubError["Decompose", ...]."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)
    result = exec_.execute(parse('Decompose["FindBirthplace", 100]'))
    assert isinstance(result, CogLangExpr)
    assert result.head == "StubError"
    assert result.args[0] == "Decompose"


# ===========================================================================
# 执行语义 (Tests 21–22)
# ===========================================================================

@pytest.mark.L2
def test_21_error_propagation(fixture_graph):
    """错误自动传播：错误值作为参数时 eager eval 后短路返回，操作不执行."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG
    exec_ = PythonCogLangExecutor(fixture_graph)

    # Derivation (Traverse[NotFound[], "born_in"]):
    #   Eager eval args[0]: execute(NotFound[]) → CogLangExpr("NotFound",())
    #   Error propagation: NotFound in ERROR_HEADS → short-circuit → return NotFound[]
    #   Traverse handler never called.
    r1 = exec_.execute(parse('Traverse[NotFound[], "born_in"]'))
    assert r1 == CogLangExpr("NotFound", ())

    # Derivation (Update[TypeError["x"], {}]):
    #   Eager eval args[0]: execute(TypeError["x"]) → CogLangExpr("TypeError",("x",))
    #   Error propagation: TypeError in ERROR_HEADS → short-circuit → return TypeError["x"]
    #   Update handler never called.
    r2 = exec_.execute(parse('Update[TypeError["x"], {}]'))
    assert r2 == CogLangExpr("TypeError", ("x",))


@pytest.mark.L2
def test_22_coglang_var_parsing(fixture_graph):
    """CogLangVar 解析正确：x_ → CogLangVar，_ → 匿名 CogLangVar，不是字符串."""
    assert _LOGOS_AVAILABLE, _IMPORT_GUARD_MSG

    # x_ → CogLangVar(name="x", is_anonymous=False)
    # Derivation: token "x_" ends with "_" and len>1 → rule 2 → CogLangVar
    expr = parse('ForEach[List[], x_, Get[x_, "name"]]')
    bindvar = expr.args[1]
    assert isinstance(bindvar, CogLangVar), \
        f"Expected CogLangVar for x_, got {type(bindvar)} (value: {bindvar!r})"
    assert bindvar.name == "x"
    assert not bindvar.is_anonymous

    # _ → CogLangVar(is_anonymous=True)
    # Derivation: token "_" is exactly single underscore → rule 1 → anonymous var
    unify_expr = parse('Unify[_, X_]')
    anon = unify_expr.args[0]
    assert isinstance(anon, CogLangVar), \
        f"Expected CogLangVar for _, got {type(anon)} (value: {anon!r})"
    assert anon.is_anonymous

    named = unify_expr.args[1]
    assert isinstance(named, CogLangVar)
    assert named.name == "X"
    assert not named.is_anonymous

