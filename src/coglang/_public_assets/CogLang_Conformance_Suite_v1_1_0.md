# CogLang Conformance Suite v1.1.0

## 0. 本文档的角色

本文档是 `CogLang_Specification_v1_1_0_Draft.md` 的伴随测试与样例文档。

它的目标不是替代主规范，而是把以下内容写成可执行检查项：

- parser / validator 测试分组
- execution / trace / render 的最小通过条件
- golden examples

## 1. 适用范围

本文件当前服务于三个对象：

- `v1.1.0` 规范编撰者
- CogLang parser / validator / executor 的实现者
- 后续的回归测试与一致性审稿

本文件默认只覆盖：

- `Core`
- `Reserved` 中已冻结签名的最小条目

不覆盖：

- `Experimental` 的完整行为
- 宿主内部消息、存储或训练实现细节
- 外部 adapter 的真实联网行为

补充说明：

- 宿主或 adapter 专属的 fixture suite，应作为**独立的 companion suite** 维护，而不应混入当前 `Core / Reserved` conformance 主套件
- 这类 companion suite 不属于 `Core CLI` 冻结承诺

## 2. 通过准则

实现通过本套件，不代表实现与参考实现内部一致；只代表它在外部可观察行为上满足规范冻结的兼容性表面。

通过准则按以下优先级判定：

1. AST / canonical text 一致
2. validator 诊断一致
3. 语义返回值一致
4. trace / readable render 满足最小字段要求

若某实现的内部结构不同，但上述外部行为一致，则视为通过。

## 3. 测试分组

- `PARSER`
  词法、application、变量、字典、zero-arity application。
- `VALIDATOR`
  名称解析、变量位置、arity、作用域、validator 诊断字段。
- `EXEC`
  `Core` operator 的成功路径、边界路径、错误路径。
- `ERR`
  错误值默认传播与显式阻断点。
- `TRACE`
  `Trace` / `Assert` 的值透明、最小字段、事件类型。
- `RENDER`
  canonical text 与 readable render 的稳定输出。
- `EXT`
  注册表条目、profile-specific availability、未安装 operator、capability 失败。

## 4. Golden Examples

### GE-001 `operator head` vs `term head`

**目的**

验证小写结构化项合法，但不参与默认 operator 解析。

**输入**

```text
Unify[f[X_, b], f[a, Y_]]
```

**期望**

- parser 成功
- `f` 被识别为 `term head`
- 不触发 `§10` 的 operator 名称解析
- 执行结果：

```text
{"X": "a", "Y": "b"}
```

**必要性**

这是 `v1.0.2` 历史矛盾的修复锚点。

### GE-002 canonical text vs readable render

**目的**

验证单行 canonical text 与多行 readable render 不是同一层对象。

**输入 AST**

```text
ForEach[
  Query[n_, Equal[Get[n_, "category"], "Person"]],
  p_,
  Do[
    Trace[Traverse[p_, "born_in"]],
    Update[p_, {"visited": True[]}]
  ]
]
```

**期望**

- canonical text：

```text
ForEach[Query[n_, Equal[Get[n_, "category"], "Person"]], p_, Do[Trace[Traverse[p_, "born_in"]], Update[p_, {"visited": True[]}]]]
```

- readable render 允许多行缩进
- 两者 round-trip 到同一 AST

**必要性**

防止把显示层写成语义层。

补充说明：

- 本组样例中的 `category` 只是示例业务字段，不构成 `v1.1.0` 对统一业务分类键名的冻结

### GE-003 `Query` 基本成功路径

**前置图谱**

- `einstein`，`type = Entity`，`category = "Person"`，`confidence = 1.0`
- `tesla`，`type = Entity`，`category = "Person"`，`confidence = 1.0`
- `ulm`，`type = Entity`，`category = "City"`，`confidence = 1.0`

**输入**

```text
Query[n_, Equal[Get[n_, "category"], "Person"]]
```

**期望**

```text
List["einstein", "tesla"]
```

返回顺序按 canonical 节点 ID 稳定排序。

补充说明：

- 本样例使用 `category` 只是为了避免与公开主节点 `type` 冲突，不意味着业务分类字段名已被冻结

### GE-004 `Query.k` 的最小语义

**前置图谱**

- `einstein`，`type = Entity`，`category = "Person"`，`confidence = 1.0`

**输入 A**

```text
Query[n_, Equal[Get[n_, "category"], "Person"]]
```

**输入 B**

```text
Query[n_, Equal[Get[n_, "category"], "Person"], {"k": 0, "mode": "default"}]
```

**输入 C**

```text
Query[n_, Equal[Get[n_, "category"], "Person"], {"k": 2, "mode": "default"}]
```

**输入 D**

```text
Query[n_, Equal[Get[n_, "category"], "Person"], {"k": 1, "mode": 7}]
```

**期望**

- A/B/C 三次都成功
- 三次结果集相同：

```text
List["einstein"]
```

- D 返回：

```text
TypeError["Query", "mode", ...]
```

**必要性**

同时锁住二参数默认形式、`k` 的独立语义、以及 `mode` 的动态类型约束。

### GE-005 `Abstract` 只做原型提取与触发

**输入**

```text
Abstract[List["case_a", "case_b", "case_c"]]
```

**期望**

返回一个结构化摘要对象，至少含：

```text
{
  "cluster_id": ...,
  "instance_count": 3,
  "prototype_ref": ...,
  "equivalence_class_ref": ...,
  "selection_basis": ...,
  "triggered": True[] | False[]
}
```

并满足：

- 不直接返回规则对象
- 不直接写入主图谱
- 不替代 `Encoder -> Logic Engine -> draft/promote`

### GE-006 `Trace` 的值透明

**输入**

```text
Trace[Traverse["einstein", "born_in"]]
```

**期望**

- 语义返回值与直接执行 `Traverse["einstein", "born_in"]` 完全一致
- trace 至少记录：
  `expr_id`
  `parent_id`
  `canonical_expr`
  `result_summary`
  `duration_ms`
  `effect_class`

### GE-007 `Assert` 的非致命语义

**输入**

```text
Do[
  Assert[False[], "missing invariant"],
  "continued"
]
```

**期望**

- 不抛出宿主异常
- 不转成 CogLang 运行时错误
- 返回：

```text
"continued"
```

- trace / observer 中出现结构化 assertion / anomaly 事件
- 事件至少可回溯：
  `condition = False[]`
  `message = "missing invariant"`
  `passed = False[]`

### GE-008 `ParseError` 与 `partial_ast`

**输入**

```text
Traverse["Einstein",
```

**期望**

- 返回 canonical error expression：

```text
ParseError["unclosed_bracket", position]
```

- 诊断对象或 transport envelope 暴露 `partial_ast` 或 `partial_ast_ref`
- `partial_ast` 指向已恢复的 `Traverse[...]` 前缀结构

### GE-009 名称未解析不是 `ParseError`

**输入**

```text
NoSuchOperator["x"]
```

**期望**

- parser 成功
- validator 失败
- 诊断字段至少包含：
  `head`
  `attempted_resolution_scopes`
  `source_span`
  `diagnostic_code`
- 不把该问题表示为 `ParseError[...]`

### GE-010 `Operation` internal artifact 的对外标注

**前置条件**

实现用内部 `Operation` 节点承载 `Compose` 结果。

**输入**

```text
Compose["FindBirthplace", List[person_], Traverse[person_, "born_in"]]
```

**期望**

- 对外语义返回值至少包含：

```text
{
  "operator_name": "FindBirthplace",
  "scope": "graph-local"
}
```

- 对内可生成 executor-internal `Operation` 载体
- 若实现还保留内部 definition handle，它只能出现在 diagnostics / transport / 管理接口中，不得替代上面的公开返回契约
- 对外文档、管理界面、trace 或 render 不把它误标为公开主节点类型
- 公开知识节点类型口径仍保持：
  `Entity / Concept / Rule / Meta`

### GE-011 `Create` 中公开节点 `type` 的唯一来源

**输入 A**

```text
Create["Entity", {"id": "tesla_01", "label": "Tesla"}]
```

**输入 B**

```text
Create["Entity", {"id": "tesla_02", "type": "Person"}]
```

**期望**

- A 成功并返回：

```text
"tesla_01"
```

- B 返回：

```text
TypeError["Create", "attrs", ...]
```

- 对 A 创建出的节点，公开主类型必须是 `Entity`
- 不允许把 `attrs["type"]` 当作业务分类字段继续沿用

### GE-012 边调用面 alias 与公开返回值

**前置图谱**

- `einstein` 存在且可见
- `ulm` 存在且可见

**输入**

```text
Create["Edge", {"from": "einstein", "to": "ulm", "relation_type": "born_in"}]
```

**期望**

- 成功返回：

```text
List["einstein", "born_in", "ulm"]
```

- 实现内部可映射到 `source_id / target_id / relation`
- 但这种内部命名差异不得改变公开调用面与返回语义

### GE-013 `Equal` 的结构相等

**输入 A**

```text
Equal[f[a, b], f[a, b]]
```

**输入 B**

```text
Equal[f[a, b], f[a, c]]
```

**期望**

- A 返回：

```text
True[]
```

- B 返回：

```text
False[]
```

- `f` 必须按 `term head` 处理，不触发 `§10` 名称解析
- 比较依据是结构相等，而不是包装对象或 render 文本相等

### GE-014 `Compare` 的最小 delta schema

**输入 A**

```text
Compare["hello", "hello"]
```

**输入 B**

```text
Compare[f[a, b], f[a, c]]
```

**期望**

- A 返回：

```text
{}
```

- B 返回：

```text
{"arg1": {"expected": "b", "actual": "c"}}
```

- application 参数位差异必须使用 `argN` 命名
- 相等时必须返回空字典，而不是其他空值

### GE-015 `Unify` 的同名变量一致性

**输入 A**

```text
Unify[f[X_, X_], f[a, a]]
```

**输入 B**

```text
Unify[f[X_, X_], f[a, b]]
```

**期望**

- A 返回：

```text
{"X": "a"}
```

- B 返回：

```text
NotFound[]
```

- 同名命名变量必须代表同一个逻辑变量

### GE-016 `Unify` 对错误值的结构匹配

**输入**

```text
Unify[TypeError[X_, _, _, _], TypeError["Get", "source", "expected dict/List/string", 7]]
```

**期望**

```text
{"X": "Get"}
```

补充要求：

- `TypeError[...]` 在 `Unify` 中是可被结构匹配的正常目标项
- 不得因为它是错误值就再次自动向外传播

### GE-017 `Match` 是 `Unify` 的精确别名

**输入 A**

```text
Match[f[X_, b], f[a, Y_]]
```

**输入 B**

```text
Unify[f[X_, b], f[a, Y_]]
```

**期望**

- A 返回：

```text
{"X": "a", "Y": "b"}
```

- B 返回：

```text
{"X": "a", "Y": "b"}
```

- 两者的 parser / validator / execution 可观察结果必须一致

### GE-018 `Explain` 在 `Baseline` 中的默认留桩

**前置条件**

- 当前实现声明自己支持 `Baseline`
- 未额外声明 `Explain` 的增强实现

**输入**

```text
Explain[Query[n_, True[]]]
```

**期望**

- 返回：

```text
StubError["Explain", ...]
```

- 不得把该调用降格成名称未解析
- 不得伪装成 `ParseError[...]`
- 至少留下一个 `meta` 或 `stub` 事件

**必要性**

锁定 `Reserved` 条目的“签名已冻结，但默认基线可留桩”的最小行为。

### GE-019 extension-backed operator 的 capability denied

**前置条件**

- 运行时注册表中存在 `ExtFetch[uri]` 条目
- 该条目名称已解析
- 该条目要求 capability `external_io`
- 当前 manifest 未授予 `external_io`

**输入**

```text
ExtFetch["dummy://resource"]
```

**期望**

- 返回：

```text
PermissionError["ExtFetch", "external_io"]
```

- 不得回退成名称未解析
- 不得返回 `ParseError[...]`
- 不得真的尝试访问外部资源
- trace / diagnostic 中应能看见 capability denied 事件

**必要性**

锁定“名称已解析但 capability 不足”的失败形态，防止与未安装实现或未解析名称混同。

### GE-020 名称已解析但实现未安装

**前置条件**

- 运行时注册表中存在 `ExtRank[input]` 条目的元数据
- 名称解析能够命中该条目
- 对应执行实现未安装或当前不可用

**输入**

```text
ExtRank["sample"]
```

**期望**

- 返回：

```text
StubError["ExtRank", "operator_unavailable"]
```

- 不得被归类成名称未解析
- 不得被归类成 `ParseError[...]`
- 这一路径与 `GE-009` 的“根本未解析”必须可区分

**必要性**

锁定 extension-backed operator 在“已解析但不可执行”时的最小失败行为。

### GE-021 `If` 对自动传播错误值的条件分支处理

**输入**

```text
If[Get[1, "type"], "then", "else"]
```

**期望**

- 返回：

```text
"else"
```

- `condition` 中产生的自动传播错误值不得继续自动向外传播
- trace 中必须能区分 `condition_result_kind = error` 与 `branch_taken = else`

**必要性**

锁定 `If` 在自动系统中最容易漂移的语义边界：错误值按假值处理，但不等于静默吞掉 trace。

### GE-022 `IfFound` 对 `NotFound[]`、错误值与 `List[]` 的分流

**输入 A**

```text
IfFound[NotFound[], x_, x_, "fallback"]
```

**期望 A**

- 返回 `"fallback"`

**输入 B**

```text
IfFound[List[], x_, x_, "fallback"]
```

**期望 B**

- 返回 `List[]`

**必要性**

锁定 `IfFound` 与 `If` 的分层：`NotFound[]` 与自动传播错误值进入 `else`，`List[]` 不是错误值。

### GE-023 `ForEach` 的稳定映射与结果保留

**输入**

```text
ForEach[List["a", "b"], x_, Equal[x_, x_]]
```

**期望**

- 返回：

```text
List[True[], True[]]
```

- 结果顺序必须与输入快照顺序一致
- trace 中必须能看见快照大小为 `2`

**必要性**

锁定 `ForEach` 的最小稳定性：一次求值快照、逐项映射、顺序不漂移。

### GE-024 `Do` 的顺序执行与非自动中止

**输入**

```text
Do[
  Get[1, "type"],
  Trace["still_runs"]
]
```

**期望**

- 返回：

```text
"still_runs"
```

- `Do` 的返回值必须是最后一个已执行子表达式的结果，而不是全部步骤结果的聚合
- 第一条子表达式产生的错误值不得自动中止第二条
- trace 中必须能看见两个步骤都被执行

**必要性**

锁定 `Do` 最容易被实现者“顺手修成异常即中断”的行为边界。

### GE-025 `Inspect` 在 `Baseline` 中的默认留桩

**输入**

```text
Inspect["einstein"]
```

**期望**

- 返回：

```text
StubError["Inspect", "einstein"]
```

- trace 中必须能留下 `stub` 或 `meta` 类事件
- 不得因为 `Inspect` 留桩而触发 graph write

**必要性**

锁定 `Inspect` 作为 `Reserved` 条目的最小可靠性：签名冻结、默认失败形态冻结、可观测性要求冻结。

### GE-026 `IfFound` 的 bind-and-continue 惯用法

**输入**

```text
IfFound[
  Get["einstein", "label"],
  label_,
  List[label_, Equal[label_, "Einstein"]],
  "missing"
]
```

**期望**

- 返回：

```text
List["Einstein", True[]]
```

- `Get["einstein", "label"]` 的结果必须被绑定到 `label_`
- `thenExpr` 必须只在绑定成功时求值
- trace 中必须能看见 `branch_taken = then`

**必要性**

锁定 `IfFound` 在当前 `v1.1.0` 中作为 bind-and-continue 官方惯用法的最小可依赖行为，而不改变 `Do` 的步间不绑定语义。

### GE-027 `AllNodes` 的可见性与稳定顺序

**前置图谱**

- `einstein`，`type = Entity`，`confidence = 1.0`
- `tesla`，`type = Entity`，`confidence = 1.0`
- `ghost`，`type = Entity`，`confidence = 0`

**输入**

```text
AllNodes[]
```

**期望**

```text
List["einstein", "tesla"]
```

- 结果中不得出现 `ghost`
- 结果顺序必须稳定；默认按 canonical 节点 ID 升序

**必要性**

锁定 `AllNodes` 的默认可见性与稳定排序，避免不同实现把 soft-deleted / hidden 节点重新暴露出来。

### GE-028 `Update` 的成功路径与 `confidence = 0` 拒绝

**前置图谱**

- `einstein`，`type = Entity`，`label = "Einstein"`，`confidence = 1.0`

**输入 A**

```text
Update["einstein", {"label": "Albert Einstein"}]
```

**期望 A**

- 返回：

```text
True[]
```

- 后续执行：

```text
Get["einstein", "label"]
```

  必须返回：

```text
"Albert Einstein"
```

**输入 B**

```text
Update["einstein", {"confidence": 0}]
```

**期望 B**

- 返回：

```text
TypeError["Update", "changes", "use Delete for soft-delete", ...]
```

**必要性**

同时锁定 `Update` 的正常字段覆盖路径与“不得借 `confidence = 0` 模拟删除”的硬边界。

### GE-029 `Delete` 的 soft-delete 与幂等性

**前置图谱**

- `tesla`，`type = Entity`，`confidence = 1.0`

**输入 A**

```text
Delete["tesla"]
```

**期望 A**

- 返回：

```text
"tesla"
```

**输入 B**

```text
Delete["tesla"]
```

**期望 B**

- 返回：

```text
NotFound[]
```

- 后续执行：

```text
AllNodes[]
```

  不得再包含 `tesla`

**必要性**

锁定 `Delete` 的 soft-delete 语义、幂等性与默认可见性后果。

### GE-030 `ForEach` 对 body 错误的结果保留

**输入**

```text
ForEach[List["einstein", "missing"], x_, Get[x_, "label"]]
```

**期望**

- 返回：

```text
List["Einstein", NotFound[]]
```

- 第二个位置的 `NotFound[]` 必须保留在结果列表中
- 第一项成功不得因第二项缺失而被抹去
- 整轮迭代不得提前中止

**必要性**

锁定 `ForEach` 的“逐项保留结果”语义，避免实现把 body 错误重新做成全局失败。

### GE-031 `Get` 的 `Dict / List / node_attr` 三路分派

**输入 A**

```text
Get[{"name": "Einstein"}, "name"]
```

**期望 A**

```text
"Einstein"
```

**输入 B**

```text
Get[List["a", "b"], 1]
```

**期望 B**

```text
"b"
```

**输入 C**

```text
Get["einstein", "label"]
```

**期望 C**

```text
"Einstein"
```

**输入 D**

```text
Get[List["a"], "name"]
```

**期望 D**

```text
TypeError["Get", "key", ...]
```

**必要性**

锁定 `Get` 的三路运行时分派、`0-based` 列表索引与“分派确定后再校验 key 类型”的错误语义。

### GE-032 `Create` 缺省 ID 的唯一分配与返回一致性

**前置图谱**

- `einstein` 存在且可见

**输入**

```text
IfFound[
  Create["Entity", {"label": "Dog"}],
  dog_id_,
  Create["Edge", {"from": "einstein", "to": dog_id_, "relation_type": "knows"}],
  False[]
]
```

**期望**

- 整体成功
- 最终返回：

```text
List["einstein", "knows", "<allocated_id>"]
```

- 其中 `<allocated_id>` 必须是本次创建为节点分配的唯一 ID
- 该 ID 必须在语言层节点返回值、后续同次表达式内部引用、以及内部写入候选中保持一致
- 实现不得把该 ID 延迟到持久化提交成功后再回填生成

**必要性**

锁定 `Create` 在 `attrs.id` 缺失时的冻结语义：唯一 ID 必须在内部写入请求形成前就被分配，并成为本次表达式后续引用的共同标识。

### GE-033 `Create["Edge", ...]` 的 alias 归一化早于内部引用校验

**前置图谱**

- `einstein` 存在且可见

**输入**

```text
Do[
  Create["Entity", {"id": "dog_1", "label": "Dog"}],
  Create["Edge", {"from": "einstein", "to": "dog_1", "relation_type": "knows"}]
]
```

**期望**

- 整体成功
- 最终返回最后一步结果：

```text
List["einstein", "knows", "dog_1"]
```

- 若实现内部存在字段映射、键名归一化或等价的调用面转换步骤，则这些步骤必须在任何内部引用一致性检查、宿主提交校验或本地引用完整性检查前完成
- 对外冻结的是“映射早于任何内部引用一致性检查”的时序约束，而不是某一种宿主内部字段名或某一种桥接对象实现
- 不允许出现“公开调用面合法，但仅因实现内部尚未完成调用面归一化而失败”的行为

**必要性**

锁定边调用面 alias 与内部提交对象之间的时序约束，避免不同实现把字段映射放在过晚阶段，从而破坏本地引用一致性。

## 5. 最小回归集合

每次规范改动后，至少应回归以下样例：

- `GE-001`
- `GE-002`
- `GE-003`
- `GE-004`
- `GE-005`
- `GE-006`
- `GE-007`
- `GE-008`
- `GE-009`
- `GE-010`
- `GE-011`
- `GE-012`
- `GE-013`
- `GE-014`
- `GE-015`
- `GE-016`
- `GE-017`
- `GE-018`
- `GE-019`
- `GE-020`
- `GE-021`
- `GE-022`
- `GE-023`
- `GE-024`
- `GE-025`
- `GE-026`
- `GE-027`
- `GE-028`
- `GE-029`
- `GE-030`
- `GE-031`
- `GE-032`
- `GE-033`

## 6. 扩展说明

本文件会随 `v1.1.0` 收敛继续增长，但增长原则应保持克制：

- 优先补“能证明语义边界”的样例
- 不用大量相似样例堆砌覆盖率幻觉
- 不把宿主内部实现细节写进 golden example
