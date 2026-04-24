# CogLang Operator Catalog v1.1.0

## 0. 本文档的角色

本文档是 `CogLang_Specification_v1_1_0_Draft.md` 的预发布伴随目录文档。

它回答三个问题：

- `v1.1.0` 规范集中，哪些 operator 已经被显式收口
- 哪些 operator 仍沿用 `v1.0.2` 兼容口径，尚未迁入新版模板
- 哪些 operator 只应停留在 `Reserved / Experimental`

本文档是目录，不是权威语义来源。权威语义仍以主规范为准；它的作用是为实现者、编撰者和审稿者提供状态索引。

## 1. 目录读取规则

本目录中的条目分三类：

- `Explicit`
  已在 `v1.1.0` 主规范中用新版模板逐条写实。
- `Carry-forward`
  尚未在 `v1.1.0` 中逐条重写，但在不与新主线冲突的前提下，仍沿用 `v1.0.2` 语义。
- `Reserved / Experimental`
  仅冻结签名、方向或状态，不要求默认实现。

若发生冲突，优先级如下：

1. `CogLang_Specification_v1_1_0_Draft.md`
2. `CogLang_Migration_v1_0_2_to_v1_1_0.md`
3. `CogLang_Specification_v1_0_2.md`

## 2. Explicit Operators

以下 operator 已在 `v1.1.0` 主规范中显式收口。

| Operator | Status | Layer | Effect | Baseline | 备注 |
|---------|--------|-------|--------|----------|------|
| `Abstract` | `Core` | `language` | `meta` | 正常执行 | 只做原型提取与触发，不直接产规则 |
| `Equal` | `Core` | `language` | 继承参数求值 | 正常执行 | 结构相等判断；不解引用节点字符串 |
| `Compare` | `Core` | `language` | 继承参数求值 | 正常执行 | 诊断性 delta；最小 schema 已冻结 |
| `Unify` | `Core` | `language` | 参数规约后为 `pure` | 正常执行 | 项级/值级合一；错误值也可被结构匹配 |
| `Match` | `Core` | `language` | 与 `Unify` 相同 | 正常执行 | `Unify` 的精确别名，不得扩成图搜索 |
| `Get` | `Core` | `language` | `graph-read` | 正常执行 | 三路分派；不穿透 transport / UI 外层包装 |
| `Query` | `Core` | `language` | `graph-read` | 正常执行 | 二参兼容；三参引入 `k / mode` |
| `AllNodes` | `Core` | `language` | `graph-read` | 正常执行 | 返回可见节点稳定列表 |
| `Traverse` | `Core` | `language` | `graph-read` | 正常执行 | 一步出边遍历；起点不存在返回 `List[]` |
| `ForEach` | `Core` | `language` | 继承子表达式 | 正常执行 | 快照迭代；`collection` 为错误值时返回 `List[]` |
| `Do` | `Core` | `language` | 继承子表达式 | 正常执行 | 顺序容器；错误不自动中止后续步骤 |
| `If` | `Core` | `language` | 继承被执行分支 | 正常执行 | 真值分支；自动传播错误值在此按假值处理 |
| `IfFound` | `Core` | `language` | 继承被执行分支 | 正常执行 | 区分“结果可用”与“缺失/出错”；`List[]` 进入 then |
| `Compose` | `Core` | `language` | `meta` | 正常执行 | 注册图动态 operator 定义；公开返回值是 registration receipt，不暴露内部 `Operation` handle |
| `Create` | `Core` | `language` | `graph-write` | 正常执行 | 节点/边创建；公开节点 `type` 由第一参数决定 |
| `Update` | `Core` | `language` | `graph-write` | 正常执行 | 仅覆盖节点更新；`confidence = 0` 必须走 `Delete` |
| `Delete` | `Core` | `language` | `graph-write` | 正常执行 | 仅做 soft-delete；节点与边都保留历史 |
| `Trace` | `Core` | `observability` | `diagnostic` | 正常执行 | 值透明包装器 |
| `Assert` | `Core` | `observability` | `diagnostic` | 正常执行 | 非致命断言 |
| `Explain` | `Reserved` | `observability` | `meta` | `StubError[...]` | 签名冻结，计划对象 schema 未冻结 |

## 3. Carry-forward Operators

以下 operator 尚未在 `v1.1.0` 主规范中逐条迁入新版模板，但在没有与新主线直接冲突的前提下，仍沿用 `v1.0.2` 兼容口径。

### 3.1 图查询与数据访问

| Operator | Status | 备注 |
|---------|----------|------|
| 无 | — | 本小节高优先级条目均已迁入 `Explicit` |

### 3.2 控制流与绑定

| Operator | Status | 备注 |
|---------|----------|------|
| 无 | — | 本小节高优先级条目均已迁入 `Explicit` |

### 3.3 图写入与定义

| Operator | Status | 备注 |
|---------|----------|------|
| 无 | — | 本小节高优先级条目均已迁入 `Explicit` |

### 3.4 阶段性与外围能力

| Operator | Status | 备注 |
|---------|----------|------|
| `Send` | `Carry-forward` | 继续视为阶段性能力；`P1` 默认可按 `StubError[...]` 处理。若 `v1.2.0` 前跨实例协议、默认失败形态与最小 trace 要求冻结，则可升入主规范；否则应降为 `Reserved` |

## 4. Reserved / Experimental Directions

以下方向不应被误当成“默认可用的稳定 operator”。

### 4.1 Reserved

| 方向 | Status | 备注 |
|------|----------|------|
| `Inspect` | `Reserved` | 对象结构检视边界已写明，默认实现仍可留桩 |
| 非默认 `Query.mode` | `Reserved` | 不要求默认实现 |
| 查询 `cost / gain` 相关元推理接口 | `Reserved` | 键名已预留，完整 schema 未冻结 |
| 规则候选 envelope | `Reserved` | 为后续规则归纳与验证阶段预留桥接点 |
| 规则发布 / 回滚链 schema | `Reserved` | 不在 `v1.1` 冻结 |
| 显式限定名称的具体表面语法 | `Reserved` | 仅冻结“存在该能力”，不冻结写法；属于实现者保留能力，不属于普通使用者可教学语法 |

### 4.2 Experimental

| 方向 | Status | 备注 |
|------|----------|------|
| `Recover[...]` | `Experimental` | 不进入 `v1.1` 核心语法 |
| 更强的 `InspectSelf[...]` | `Experimental` | 涉及权限与自修改边界 |
| 规则自修改 operator | `Experimental` | 高风险 |
| adapter 专用高耦合 operator | `Experimental` | 依赖宿主环境，不宜进入核心目录 |

### 4.3 Architecture-Owned Future Directions（Non-v1.1）

以下方向属于 `P3/P4` 阶段的潜在架构演化，不应被误解为 `v1.1` 排期，也不构成语言核心目录：

| 方向 | Status | 备注 |
|------|----------|------|
| 受限过程性策略执行 | `Future` | 只作为 `P3` 方向性占位，不进入 `v1.1` |
| 完整程序执行域能力 | `Future` | 属于 `P4` 方向；不进入 `v1.1` 语言主干 |
| 程序性语法扩展 | `Future` | 如需出现，应先经 profile / extension / reserved 路径，而不是直接进入 `Core` |

## 5. 目录维护原则

- 先更新主规范，再更新本目录
- `Carry-forward` 不是永久状态；一旦条目迁入主规范，应从本节移出
- 若某旧 operator 与 `v1.1.0` 新主线直接冲突，应先在迁移文档中显式标出，再决定是重写、降级还是移出

## 6. Carry-forward Exit Conditions

`Carry-forward` 仅剩少数边界尚未收稳的条目。退出条件如下：

1. `Send`
   若 `v1.2.0` 前跨实例协议、默认失败形态与最小 trace 要求冻结，则可升入主规范；
   若这些边界在 `v1.2.0` 前仍未冻结，则应从 `Carry-forward` 降为 `Reserved`，避免无限期停留在模糊状态。
