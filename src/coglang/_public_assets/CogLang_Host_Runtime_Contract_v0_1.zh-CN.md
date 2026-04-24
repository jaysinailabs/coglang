# CogLang Host Runtime Contract v0.1

**状态**：`informative companion note`  
**适用对象**：实现者、宿主运行时设计者、架构编撰者、未来第三方宿主  
**不属于**：`CogLang v1.1.0` 语言核心规范正文

## 1. 目的

这份文档回答一个稳定存在的问题：

- `CogLang` 语言层已经冻结了查询、更新、追踪、扩展边界
- 一旦进入任意具体宿主，就必须回答“宿主到底要提供什么”

本说明的目标不是把任何应用专属架构协议搬进语言规范，而是给出一层更小的宿主契约：

- 语言负责什么
- 宿主负责什么
- 宿主桥接对象应承担什么角色
- 哪些事项仍不属于本说明冻结范围

当前参考实现还提供了一个最小宿主门面：

- `LocalCogLangHost`

它的作用不是替代完整宿主协议，而是给外部使用者一个不必先理解应用专属架构即可试用下面这些动作的入口：

- 执行表达式
- 在一个最小源宿主中执行表达式，并向目标宿主提交写候选
- 直接执行并提交后返回关联的 typed trace / typed query result
- 捕获最新写候选
- 形成提交消息
- 本地提交
- 查询本地写结果
- 导出本地写提交历史与查询结果历史
- 导出最小宿主状态
- 直接导出最小宿主摘要的 JSON 载荷
- 直接导出 request / response / submission-record / typed trace / query-result history 的 JSON 载荷，并支持所有这几层按 `status` 过滤的最小 JSON 导出
- 从最小宿主状态重建本地宿主
- 在当前宿主实例上就地恢复一个 legacy state 导出
- 直接导出与恢复 legacy state 的 JSON 载荷
- 显式重置本地宿主图状态与写状态
- 克隆一个独立的最小本地宿主副本
- 在当前宿主实例上就地恢复一个最小宿主快照
- 直接导出与恢复最小宿主快照的 JSON 载荷

这层门面应被视为 `Host Runtime Contract v0.x` 的参考接入面，而不是最终协议形态。

## 2. 最小分层

实现 `CogLang` 的宿主至少应分清 4 层：

1. **Language Layer**
   - parser / validator
   - 表达式求值
   - `Core` / `Reserved` operator 语义
   - 表达式级 trace / error propagation
2. **Host Runtime Layer**
   - 图读取接口
   - 图写意图接收与提交流程
   - diagnostics / observer / capability 注入
3. **Host Protocol Layer**
   - 宿主消息对象
   - 提交回执
   - correlation / provenance / retry 策略
4. **Application / Architecture Layer**
   - 应用侧对象存储与索引
   - 应用侧消息或任务分发协议
   - 生命周期对象
   - 领域服务与模块边界

`CogLang v1.1.0` 只冻结第 1 层，并对第 2 层给出最小边界说明；它不冻结第 3、4 层的具体产品化协议。

## 3. 宿主必须提供什么

### 3.1 图读取能力

宿主必须允许执行器完成：

- 节点存在性检查
- 节点属性读取
- 邻接遍历
- 软删除可见性判断

语言层不要求宿主暴露某一种具体图数据库或某一种具体对象模型，但这些能力不可缺。

### 3.2 图写意图接收能力

对于 `Create / Update / Delete`，语言层冻结的是写意图与返回契约，不是最终持久化路径。

宿主至少应支持两阶段模型：

1. **求值阶段**
   - 执行器正常求值
   - 收集 `WriteBundleCandidate`
2. **提交阶段**
   - 宿主决定是否验证、转发、提交、拒绝或回滚

这意味着：

- 执行器可以帮助形成写入候选
- 但“是否真正提交”不是语言层决定的

对于 `Create`，宿主还必须满足一条更具体的语言-宿主接口约束：

- 若节点模式下 `attrs.id` 缺失，则唯一 ID 必须在形成内部写入请求、`WriteBundleCandidate`、bundle 校验输入或等价宿主提交对象之前被分配
- 同一个创建动作中，语言层返回值、后续同次表达式内部引用、以及宿主桥接对象中使用的该节点 ID 必须保持一致
- 持久化后端可以继续决定最终写入是否接受，但不得把“生成语言层采用 ID”推迟到提交成功之后

### 3.3 diagnostics / observer / capability 注入

宿主应负责：

- 注册 observer
- 决定 capability manifest
- 决定阶段 profile 与 capability 的映射方式
- 决定 extension-backed operator 的实际可用性
- 决定 diagnostics 与 trace 如何汇入宿主观测体系

责任分工至少应满足：

- 执行器负责语言层已经冻结的参数验证、语义检查与错误值返回
- 执行器可以基于宿主注入的 capability / profile manifest 提前返回 `PermissionError[...]`
- 宿主是 capability 可用性的最终真相源；即使执行器侧未提前拒绝，宿主仍可在调度、提交或外部调用阶段拒绝该能力
- 若宿主存在阶段化权限包，`stage profile -> capability set` 的映射应由宿主或 adapter 层决定，而不是回写为 `CogLang Core` 语义
- 若 trace / replay 需要解释“为什么当前允许或拒绝某动作”，宿主宜把当前 `stage profile` 与最终 capability 集一起记录进治理层 trace
- 若宿主拒绝能力，请求失败必须能映射回结构化 `PermissionError[...]`、`ErrorReport` 或等价 typed failure envelope，而不是静默降级

## 4. 参考桥接对象族

一个宿主运行时通常需要一组桥接对象来承接语言级写意图与宿主级提交流程。

本说明使用如下对象族作为 reference bridge：

- `WriteBundleCandidate`
- `WriteBundleSubmissionMessage`
- `WriteBundleSubmissionResult`
- `WriteResult`
- `ErrorReport`
- `WriteBundleResponseMessage`
- `LocalWriteSubmissionRecord`
- `LocalWriteQueryResult`

这些对象在本说明中的角色是：

- 从语言层写意图过渡到宿主提交
- 为本地验证 / 原子回放 / typed round-trip 提供最小结构

它们**不是**以下对象的正式替代品：

- 应用侧知识或消息对象
- 完整宿主提交协议
- 完整 provenance 查询协议

在本说明边界内，这些对象应被视为：

> 宿主桥接层的 reference bridge，而不是已经完全独立冻结的跨系统标准协议。

### 4.1 `WriteBundleCandidate` 的最小字段

`WriteBundleCandidate` 至少应稳定包含以下字段：

| 字段 | 类型 | 含义 |
|------|------|------|
| `owner` | `string` | 当前宿主或桥接层所有者标识 |
| `base_node_ids` | `string[]` | 形成候选前已存在且可见的基线节点 ID 集 |
| `operations` | `WriteOperation[]` | 按顶层执行顺序捕获的写意图序列 |

其中 `WriteOperation` 至少包含：

| 字段 | 类型 | 含义 |
|------|------|------|
| `op` | `string` | 写操作种类，例如 `create_node / create_edge / update_node / delete_node / delete_edge` |
| `payload` | `object` | 与该操作对应的最小结构化数据 |

最小 JSON 例子：

```json
{
  "owner": "LocalCogLangHost",
  "base_node_ids": ["einstein"],
  "operations": [
    {
      "op": "create_node",
      "payload": {
        "id": "dog_1",
        "type": "Entity",
        "attrs": {
          "label": "Dog"
        }
      }
    },
    {
      "op": "create_edge",
      "payload": {
        "source_id": "einstein",
        "target_id": "dog_1",
        "relation": "knows"
      }
    }
  ]
}
```

若宿主采用 `source_id / target_id / relation` 等内部字段名，则 `from / to / relation_type` 的 call-surface alias 映射必须在形成该候选或等价内部写入请求时完成；不得把映射推迟到内部引用一致性检查之后。

## 5. 最小请求/响应对

一个宿主运行时至少应有一对结构化请求/响应 envelope。本说明采用如下最小对作为桥接基线：

### 5.1 请求侧

- `WriteBundleSubmissionMessage`
  - 包含 `correlation_id`
  - 包含 `submission_id`
  - 包含 `candidate`
  - 可导出 transport-safe dict envelope

### 5.2 响应侧

- `WriteBundleResponseMessage`
  - 包含 `correlation_id`
  - 包含 `submission_id`
  - 包含 `owner`
  - payload 为 `WriteResult` 或 `ErrorReport`

### 5.3 这层契约的定位

这对请求/响应对象的价值在于：

- 让宿主不必直接读执行器内部属性
- 让桥接层有结构化消息对，而不只是一堆裸 dict
- 为未来桥接更正式的宿主总线协议保留清晰落点

但它仍不等于：

- 完整跨进程消息协议
- 多宿主标准
- 独立开源运行时标准

### 5.4 本地查询层

若宿主实现了本地桥接层，至少可以额外保留一层最小的 provenance-style 查询能力：

- 按 `correlation_id` 返回 `committed / failed / not_found`
- 按 `submission_id` 返回 `committed / failed / not_found`
- 按 `correlation_id` 返回本地 typed response envelope
- 按 `correlation_id` 或 `submission_id` 返回一条 `LocalWriteSubmissionRecord`
- 按 `correlation_id` 返回一条类型化的 `LocalWriteQueryResult`
- 按 `submission_id` 返回一条类型化的 `LocalWriteQueryResult`
- 按 `correlation_id` 或 `submission_id` 返回 transport-safe dict 形式的 `LocalWriteQueryResult`
- 按 `correlation_id` 或 `submission_id` 直接返回最小 `payload_kind`，让轻量宿主不必下钻 response header；这层最小字段也宜先由 runtime bridge 提供
- 按 `correlation_id` 或 `submission_id` 直接返回最小 `write_header`（`correlation_id / submission_id / status / payload_kind`），让轻量宿主不必分别查询多个字段
- 按 `correlation_id` 或 `submission_id` 直接返回类型化 `LocalWriteHeader`，让 typed 宿主不必从 dict 形态反推最小头信息；这层 typed header 宜先由 runtime bridge 提供，再由宿主门面薄封装
- companion CLI / demo 若同时展示 dict `write_header` 与 typed `LocalWriteHeader` 视图，typed header 宜来自宿主 typed query，而不应仅作为 dict header 的别名复用
- companion CLI / demo 若同时展示 `submission-message / response / submission-record / query-result` 与 `write_header`，这些公开视图里的 `correlation_id / submission_id / status / payload_kind` 对齐关系宜纳入成功判定，而不是只在测试中隐含成立
- companion CLI / demo 若额外公开顶层 `node_id` 或等价主对象 ID，该字段宜与 response payload 中的 touched object IDs 以及 snapshot graph 中的对象 ID 视图保持一致，并纳入成功判定
- companion CLI / demo 若同时公开 submission-message 中的 candidate / commit-plan 与顶层 `node_id`，则 candidate / commit-plan 中的 create-node 目标 ID 也宜与该顶层 ID 保持一致，并纳入成功判定
- companion CLI / demo 不宜只演示 `WriteResult` happy path；若同时承担契约示例职责，宜补一条最小 `ErrorReport` companion step，显式展示 `payload_kind=ErrorReport`、`status=failed` 与 typed response / query-result / trace 的对齐关系
- 通过宿主门面直接导出 `write_header` history，并支持按 `status` 过滤与最小 JSON 导出；对应的 dict/JSON/history 组装也宜先由 runtime bridge 提供
- 通过宿主门面直接导出 typed `LocalWriteHeader[]`，并支持最小 JSON 导出与按 `status` 过滤；对应 JSON wrapper 也宜先由 runtime bridge 提供
- 按 `correlation_id` 或 `submission_id` 返回最小 JSON 形式的 `LocalWriteQueryResult`；其 JSON wrapper 也宜先由 runtime bridge 提供
- 通过宿主门面直接执行 `execute_and_prepare_submission_message(...)`，把执行与 typed message 准备收成一步
- 通过宿主门面直接执行 `execute_and_prepare_submission_message_dict(...)`，把执行与 transport-safe message 准备收成一步
- 通过宿主门面直接读取/消费现有 `WriteBundleCandidate` 的 dict 形态，或把现有 candidate 直接转成 dict 形态的 submission message
- 通过宿主门面直接执行 `submit_message_dict(...)` 与 `submit_message_dict_and_query(...)`，让轻量脚本宿主可全程使用 dict 形态
- 通过宿主门面直接执行 `submit_*_and_query(...)`，把本地提交与 typed 查询收成一步
- 通过双宿主门面直接执行 `execute_and_submit_to_query(...)`，把源宿主执行、目标宿主提交与目标宿主 typed 查询收成一步
- 通过双宿主门面直接执行 `execute_and_submit_to_query_dict(...)`，把源宿主执行、目标宿主提交与目标宿主 dict 查询收成一步
- 通过宿主门面直接读取 typed response envelope 与单条 request / response record
- 通过宿主门面按 `submission_id` 直接读取 typed response envelope
- 通过宿主门面直接读取 transport-safe dict 形式的单条 response envelope 与单条 submission record
- 通过宿主门面直接读取最小 JSON 形式的单条 response envelope 与单条 submission record；对应 JSON wrapper 也宜先由 runtime bridge 提供
- 通过宿主门面按 `submission_id` 直接读取 transport-safe dict 形式的单条 response envelope
- 通过宿主门面按 `submission_id` 直接读取 transport-safe dict 形式的单条 submission record
- 通过宿主门面按 `correlation_id / submission_id` 直接读取 typed submission message
- 通过宿主门面按 `correlation_id / submission_id` 直接读取 transport-safe dict 形式的 submission message
- 通过宿主门面按 `correlation_id / submission_id` 直接读取最小 JSON 形式的 submission message；对应 JSON wrapper 也宜先由 runtime bridge 提供
- 通过宿主门面按 `correlation_id / submission_id` 直接读取一条相关联的 typed `LocalHostTrace`
- 通过宿主门面按 `correlation_id / submission_id` 直接读取 transport-safe dict 形式的 `LocalHostTrace`
- 通过宿主门面按 `correlation_id / submission_id` 直接读取最小 JSON 形式的 `LocalHostTrace`
- 这类 trace 视图可以由宿主门面直接暴露，但其底层相关联逻辑宜先在 runtime bridge 层提供，避免宿主重复手工拼接 request / response / record / query-result
- 对于 `query-result / response / submission-message / submission-record / trace` 这些对象，单条 JSON 查询与 history JSON 导出的组装都宜先由 runtime bridge 提供，再由宿主门面薄封装
- companion CLI / demo 若要展示这组对象，宜优先消费宿主门面公开的 query/view 接口，而不是直接下钻 typed trace 的内部字段
- 通过宿主门面直接导出 typed response history、dict response history 与 typed submission-record history
- 通过宿主门面直接导出 typed submission-message history 与 dict submission-message history
- 通过宿主门面按 `status` 直接返回 typed submission-message history，或导出按 `status` 过滤后的 dict submission-message history
- 通过宿主门面按 `status` 直接返回 typed response history / typed submission-record history，或导出按 `status` 过滤后的 dict history
- `submission_id` 查询在 `not_found` 时也应保留被查询的 `submission_id`，避免轻量宿主丢失定位键
- 通过宿主门面直接导出 typed trace history 与 dict trace history，并支持 typed `LocalHostTrace[]` 的最小 JSON 导出与按 `status` 过滤
- 通过宿主门面按 `status` 直接返回 typed `LocalHostTrace[]`，或导出按 `status` 过滤后的 trace history
- 通过宿主门面导出包含图状态、typed request/response/record histories、typed query results 与 typed traces 的完整快照对象
- 若快照中 typed trace 已存在，而 request/response/record histories 不完整，宿主可用 trace 作为恢复这些历史的后备来源
- 若快照只有匹配的 request/response 而没有 record，宿主应在恢复时合成最小 submission record，且不得重复追加 response history
- 通过宿主门面导出 typed summary 与 dict summary，供轻量宿主或 CLI 直接消费；summary 至少应包含 request / response / record / query-result / trace 的计数
- companion CLI / demo 若同时展示 `snapshot` 与 `summary`，其 `snapshot_summary` 宜由导出的 `snapshot` 显式重建，而不是仅复用另一份 summary 载荷
- companion CLI / demo 若同时展示 `trace`、`snapshot` 与其它公开视图，这些视图之间的 request / response / record / query-result 对齐关系宜纳入成功判定，而不是只在测试中隐含成立
- 通过宿主门面显式清空本地写状态，回到干净的 request / response / query 基线
- 导出按插入顺序排列的本地 `LocalWriteQueryResult` 历史
- 按 `status` 过滤并导出本地 `LocalWriteQueryResult`
- 通过宿主门面直接按 `status` 返回类型化 `LocalWriteQueryResult[]`

`LocalWriteSubmissionRecord` 的定位是：

- 保存一次本地提交尝试的 request / response 对
- 为宿主调试、测试和后续接入正式 provenance 层提供稳定落点

`LocalWriteQueryResult` 的定位是：

- 把 `status / response / record` 三块本地查询结果收成一个类型化返回对象
- 为后续接入正式 `ProvenanceStore.query_by_correlation_id` 保留一致的查询心智模型

它仍不等于正式的 `ProvenanceStore.query_by_correlation_id`，但它让本地桥不再只有“一次提交的即时返回值”。

### 5.5 面向治理层宿主的预留协作面

若宿主进一步把 `CogLang` 用作治理层 / 调度层 / 审计层，则宿主通常还会需要一层**请求型治理动作**，例如：

- `request_harness_run`
- `request_snapshot_rollback`
- `pause_for_review`
- `hold`

这类对象当前更适合被视为：

- host runtime / adapter 层动作 schema
- governance / approval / replay / audit 的编排对象

而不是：

- `CogLang Core` operator
- 语言层直接执行的副作用协议

对于这类治理动作，本说明当前只建议宿主满足下面这些最小约束：

- 动作请求与实际执行结果必须可区分
- 若动作需要审批，宿主应显式记录 `requires_approval` 或等价字段
- 若动作被拒绝，失败必须能映射回结构化 typed error，而不是 silent fallback
- `shadow` 与 `live` 的差异应落在宿主治理层 trace / diff 中，而不是通过改写动作语义边界来表达
- 外部 harness、rollback executor、tool invocation 的真实执行协议仍属于宿主层，不在本说明冻结

### 5.6 Schema companion pack 的当前定位

当前 `Host Runtime Contract` 已有一组内部 schema companion pack，覆盖：

- `header / result / error / response`
- `query-result / submission-record / trace`
- `summary`

并已配套：

- `schema-pack.json`
- sample payload pack
- 最小 versioning / reference 规则
- `candidate / seed_only` promotion boundary
- candidate 对象的最小字段面与最易误升格 detail 字段边界

当前对这组材料更合适的定位是：

- 它已经足以成为 `HRC v0.2` 的 **recommended companion**
- 它不等于 `HRC v0.2` 的默认冻结阻塞项
- 它也不等于正式的跨宿主 JSON Schema export surface

这意味着：

- 若宿主实现者想快速理解当前 reference bridge 的最小对象形状，这组 schema pack 已值得优先参考
- 但宿主实现是否通过 `v0.2` 冻结讨论，不应默认取决于“是否已经对外发布 full-pack schema”
- `Freeze Checklist` 里一部分对象视图条目虽然可被归为 `schema-assisted`，但这层分类当前主要用于冻结材料的阅读与分流，不应自动回写成 `HRC` 正文里的逐对象 shape 承诺
- `LocalHostSnapshot`、第三方宿主 stub 互通、以及更正式的 formal export 策略，仍应留给后续版本判断

换句话说，当前 schema companion pack 的角色是：

> 推荐随 `HRC v0.2` 一起阅读和对照的 companion 材料，而不是 `v0.2` 本身的冻结阻塞条件。

## 6. 对宿主实现者的最低要求

如果你正在实现一个第三方宿主，至少应满足：

- 能接收 `WriteBundleCandidate` 或等价写意图对象
- 能决定提交 / 拒绝 / 延迟提交
- 能返回结构化成功或失败结果
- 能保留 `correlation_id`
- 能保留稳定的 `submission_id`
- 能将语言级 `ErrorExpr` 与宿主提交失败区分开

如果连这些都不能满足，那么你只是“能执行部分表达式”，还不能算实现了一个可集成的 `CogLang` 宿主。

## 7. 仍未冻结的事项

本说明刻意不冻结以下内容：

- 最终 `KnowledgeMessage` schema
- `WriteBundle` 的跨服务提交协议
- `ProvenanceStore.query_by_correlation_id` 的标准查询接口
- 外部 harness / rollback / tool invocation 的正式动作 schema
- `stage profile` 的标准枚举与跨宿主统一命名
- owning-module 的枚举表
- 多宿主互通格式
- 独立 reference runtime 的发布边界

这些应由架构文档、实现文档或未来更高版本的宿主契约承接。

## 8. 与其他文档的关系

- 看语言语义：`CogLang_Specification_v1_1_0_Draft.md`
- 看 profile / capability：`CogLang_Profiles_and_Capabilities_v1_1_0.md`
- 看迁移门：`CogLang_Migration_v1_0_2_to_v1_1_0.md`
- 看独立安装与试用路径：`CogLang_Standalone_Install_and_Release_Guide_v0_1.md`
- 看公开发布边界：`CogLang_Release_Notes_v1_1_0_pre.md`
- 看 schema companion pack 的当前范围与定位：`CogLang_HRC_JSON_Schema_Seed_v0_1.md`
- 看 schema companion pack 的 promotion boundary：`CogLang_HRC_JSON_Schema_Promotion_Boundary_v0_1.md`
- 看 candidate 对象的最小字段面：`CogLang_HRC_JSON_Schema_Candidate_Field_Boundary_v0_1.md`
- 看 `§5.4` 当前 freeze 判断与 gate：`CogLang_HRC_v0_2_Freeze_Decision_Note_v0_1.md`、`CogLang_HRC_v0_2_Freeze_Gate_v0_1.md`、`CogLang_HRC_v0_2_Freeze_Decision_Record_Template_v0_1.md`
