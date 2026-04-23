# CogLang Profiles and Capabilities v1.1.0

## 0. 本文档的角色

本文档是 `CogLang_Specification_v1_1_0_Draft.md` 的预发布伴随文档。

它回答三个问题：

- `Baseline / Enhanced` profile 在 `v1.1.0` 中分别承载什么
- profile-specific availability 应如何写入 operator 条目与实现 manifest
- capability 声明与 extension-backed operator 的最小契约是什么

本文档不重写主规范中的语言语义。若与主规范冲突，以主规范为准。对 `v1.1.0` 的 profile / capability 边界判断，应将本文视为预发布权威来源。

术语边界说明：

- 本文中的 `capability` 指运行时执行能力、权限字符串与 manifest 项
- 它不指任何应用侧认知能力分类或其他领域能力维度
- 若两者需要同时出现，应用侧能力分类与 `CogLang` 运行时 capability 应明确分层命名

## 1. 设计目的

`v1.1.0` 通过 profile 承接“执行可用性差异”和“受控扩展能力”，而不是通过扩大 `Core` 主干来吸收所有变化。

profile 的作用是：

- 让 `Baseline` 保持图优先主链和最小一致性
- 让 `Enhanced` 承载仍不适合进入 `Core` 的扩展能力
- 让实现者明确区分“语言已冻结的语义”与“实现可选择提供的能力包”

profile 不是新的语言层级，也不是新的 AST 种类。它只影响：

- `Baseline Availability`
- capability 检查
- 默认可调用能力集合
- conformance 断言范围

## 2. Profile 总览

### 2.1 `Baseline`

`Baseline` 是 `v1.1.0` 的默认基线 profile。

它承载：

- 图优先主链
- 最小组合能力
- 基础错误模型
- 基础可观测性
- 主规范中 `Core` 的最低一致性要求

`Baseline` 的目标不是“功能尽量多”，而是“图主链尽量稳”。

### 2.2 `Enhanced`

`Enhanced` 是 `Baseline` 之上的增强 profile。

它承载：

- 非默认查询模式
- 已冻结签名但未要求默认实现的 `Reserved` 能力
- 受控的 extension-backed operator
- 受 capability 约束的外部能力
- 仍不适合进入 `Core` 主干的增强执行能力

`Enhanced` 的目标不是替代 `Baseline`，而是在不破坏 `Core` 语义的前提下承接扩展。

## 3. Profile 关系约束

`Baseline` 与 `Enhanced` 的关系必须满足：

- `Enhanced` **MUST** 保持对 `Baseline` 兼容性表面的兼容
- `Enhanced` **MUST NOT** 改写既有 `Core` operator 的规范语义
- 某能力若仅在 `Enhanced` 中可用，其 operator 条目 **MUST** 显式写出 profile 条件
- `Baseline` **SHOULD NOT** 承载高风险、强宿主耦合、或架构级协议能力
- `Enhanced` 可以提供更强能力，但这些能力默认仍不等于“自动入图”、“程序执行域”或“公开知识层对象”

## 4. 能力分配

### 4.1 `Baseline` 必备能力

以下能力应被视为 `Baseline` 的最小能力集合：

- `Abstract`
- `Equal`
- `Compare`
- `Unify`
- `Match`
- `Get`
- `Query` 的默认 `mode`
- `AllNodes`
- `Traverse`
- `ForEach`
- `Do`
- `If`
- `IfFound`
- `Compose`
- `Create`
- `Update`
- `Delete`
- `Trace`
- `Assert`

以及以下基础模型：

- 四层表示模型
- 错误是值
- 显式写图边界
- 名称解析的默认优先级
- `Readable Render` 最低契约

### 4.2 `Enhanced` 承载能力

以下能力在本版边界内归入 `Enhanced`：

- 非默认 `Query.mode`
- `Explain`
- `Inspect`
- 查询 `cost / gain` 相关元推理接口
- extension-backed operator
- 受 capability 约束的外部能力
- 更强的 profile-specific 调试/元观察接口

### 4.3 最小 operator × profile 矩阵

下表用于关闭“profile-specific availability 只有局部说明、缺少统一矩阵”的歧义。若与主规范逐条 operator 条目冲突，以主规范为准。

| Operator / 能力 | Profile Baseline | Profile Enhanced |
|------|------|------|
| `Abstract` | 正常执行 | 正常执行 |
| `Equal` | 正常执行 | 正常执行 |
| `Compare` | 正常执行 | 正常执行 |
| `Unify` | 正常执行 | 正常执行 |
| `Match` | 正常执行 | 正常执行 |
| `Get` | 正常执行 | 正常执行 |
| `Query`（省略 `options` 或 `mode="default"`） | 正常执行 | 正常执行 |
| `Query`（非默认 `mode`） | `StubError["Query", "mode", ...]` | profile-specific / implementation-defined |
| `AllNodes` | 正常执行 | 正常执行 |
| `Traverse` | 正常执行 | 正常执行 |
| `ForEach` | 正常执行 | 正常执行 |
| `Do` | 正常执行 | 正常执行 |
| `If` | 正常执行 | 正常执行 |
| `IfFound` | 正常执行 | 正常执行 |
| `Compose` | 正常执行 | 正常执行 |
| `Create` | 正常执行 | 正常执行 |
| `Update` | 正常执行 | 正常执行 |
| `Delete` | 正常执行 | 正常执行 |
| `Trace` | 正常执行 | 正常执行 |
| `Assert` | 正常执行 | 正常执行 |
| `Explain` | `StubError["Explain", ...]` | 正常执行 |
| `Inspect` | `StubError["Inspect", ...]` | profile-specific / implementation-defined |
| `Send` | `StubError["Send", ...]` | profile-specific / implementation-defined |
| extension-backed operator | `PermissionError[...]` 或 `StubError[...]` | profile-specific / capability-gated |

说明：

- `Enhanced` 不得改变任何 `Core` operator 在 `Baseline` 中已经冻结的规范语义
- `Enhanced` 中省略 `options` 的 `Query[...]` 仍默认落到 `mode="default"`；`Enhanced` 不得把“省略 `mode`”解释为其他默认执行策略
- `profile-specific / implementation-defined` 只允许出现在已经被主规范或 catalog 标注为 `Reserved / Carry-forward / extension-backed` 的能力上

### 4.4 `v1.1` Out-of-Scope Directions

以下方向即使未来需要，也不应在 `v1.1` 作为 `Baseline` 或默认 `Enhanced` 能力提前冻结：

- 程序性语法扩展
- 通用 `Recover[...]`
- 面向人类手写舒适度的语法糖
- 强宿主耦合的 adapter 专用高风险能力
- 完整程序执行域能力

这些方向若要继续推进，应进入 `Reserved / Experimental` 或后续版本。

本节列出的 future direction 只用于防止误写 `v1.1` 边界，不构成近端路线图。

## 5. `Baseline Availability` 的书写规范

主规范中的 `Baseline Availability` 字段只允许写：

- `正常执行`
- `StubError[...]`
- `PermissionError[...]`
- `Profile <name>: ...`

当能力依赖 profile 时，采用以下写法：

```text
Baseline Availability:
Profile Baseline: StubError["Explain", ...]
Profile Enhanced: 正常执行
```

若采用 profile-specific 写法，伴随文档或 manifest **MUST** 对该 profile 给出正式定义。

## 6. Capability Manifest 的最小字段

每个实现若支持 capability 检查，至少应提供以下字段：

| 字段 | 要求 |
|------|------|
| `profile_name` | 当前实现所属 profile 名 |
| `capabilities` | 可用 capability 的稳定字符串集合 |
| `extensions` | 已安装扩展或注册表条目标识 |
| `default_enabled` | 哪些扩展默认开启 |
| `denied_by_default` | 哪些能力默认拒绝 |
| `version` | manifest 自身版本 |

最小示意：

```json
{
  "profile_name": "Enhanced",
  "capabilities": ["graph_write", "trace_write", "external_io"],
  "extensions": ["query.mode.rank", "meta.explain"],
  "default_enabled": ["meta.explain"],
  "denied_by_default": ["external_io"],
  "version": "v1.1.0"
}
```

## 7. Capability 字符串的约束

`v1.1.0` 不冻结完整 capability 词表，但要求：

- capability 名称 **MUST** 是稳定字符串
- 同一实现内不得把相同 capability 名称复用于不相容语义
- profile manifest **MUST** 公布精确 capability 字符串
- capability 检查失败时 **MUST** 返回 `PermissionError[...]`，不得静默降级

实现至少应能区分：

- `graph_write`
- `trace_write`
- `external_io`
- `cross_instance`
- `self_modify`

## 8. Extension-backed Operator 的最小契约

extension-backed operator 指由注册表、插件、或外部 adapter 提供执行能力的 operator。

它们至少必须声明：

- 名称是否已冻结
- 签名是否已冻结
- 默认在哪些 profile 中可用
- 需要哪些 capability
- 未安装实现时返回什么错误
- capability 不足时返回什么错误
- 是否属于 `Baseline` 外增强能力

最小契约示意：

```text
Operator: Explain
Status: Reserved
Layer: observability
Profiles:
- Profile Baseline: StubError["Explain", ...]
- Profile Enhanced: 正常执行
Capabilities:
- none
On missing implementation:
- StubError["Explain", ...]
On capability denied:
- PermissionError["Explain", ...]
```

## 9. Conformance 最低要求

若某实现声明支持 `Enhanced`，其一致性测试至少应增加：

- profile-specific availability 测试
- capability denied 测试
- extension missing vs extension installed 的分流测试
- `Baseline` 与 `Enhanced` 的共同 `Core` 行为一致性测试

若某实现只声明 `Baseline`，不得因未实现 `Enhanced` 能力而被判定为不符合 `v1.1.0`。

## 10. 与未来扩展的关系

本文件只定义 `v1.1.0` 的 profile 与 capability 边界。

它不意味着：

- `v1.1.0` 已引入程序性语法
- `v1.1.0` 已承诺程序执行域
- `Enhanced` 已经等于未来 `P3/P4` 的程序层

更强的过程性能力应优先通过：

- 新 profile
- `Reserved / Experimental` 条目
- extension registry
- 伴随文档扩展

来承接，而不是直接改写当前 `Core` 主干。
