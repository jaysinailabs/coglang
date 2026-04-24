# CogLang Release Notes v1.1.0-pre

**状态**：预发布说明  
**版本标签**：`v1.1.0-pre`  
**适用对象**：第一次试用 `CogLang` 的外部读者、实现者、集成方  
**作用**：说明本次预发布到底公开承诺了什么、没有承诺什么，以及试用时应以哪些文档和工具入口为准

---

## 0. 发布定位

本次 `v1.1.0-pre` 的定位是：

- `experimental`
- `pre-release`
- `reference implementation`
- `language core + host bridge`

它的目标不是宣称“独立语言平台已经成熟”，而是提供一套**可以被外部试用、实现、验证和讨论**的最小公开基线。

当前还应把两层版本语义分开理解：

- `v1.1.0-pre` 是当前语言/规范/文档的公开 release label
- CLI 与安装分发元数据里的 `version` 仍反映当前源码分发版本

如果 `coglang info` 或 `coglang manifest` 同时出现这两层字段，对外讨论语言版本时以后者的 `language_release` 为准；对安装构件和分发排障时再看 distribution version。

---

## 1. 本次明确公开承诺的内容

以下内容属于当前预发布明确承诺的一部分。

### 1.1 文档基线

以下文档构成当前公开基线：

- `CogLang_Specification_v1_1_0_Draft.md`
- `CogLang_Quickstart_v1_1_0.md`
- `CogLang_Conformance_Suite_v1_1_0.md`
- `CogLang_Profiles_and_Capabilities_v1_1_0.md`
- `CogLang_Host_Runtime_Contract_v0_1.md`
- `CogLang_Standalone_Install_and_Release_Guide_v0_1.md`

如果这些文档之间存在冲突，仍以主规范与 conformance 为更高优先级。

### 1.2 最小工具入口

当前公开承诺存在并可调用的最小 CLI 命令为：

- `parse`
- `canonicalize`
- `validate`
- `execute`
- `conformance`
- `repl`
- `info`
- `manifest`
- `bundle`
- `doctor`
- `vocab`
- `examples`
- `smoke`
- `demo`
- `release-check`

若帮助输出中出现额外参考命令，它们不自动构成当前预发布的对外稳定承诺；当前仍以本节列出的最小命令子集为准。

当前 `manifest` / `bundle` 会把“对外建议入口”和“实现元数据”分开表达：  
对外入口以 `coglang` 为准；实现模块目标仍可作为 machine-readable metadata 出现，但不自动构成公开主入口承诺。

当前 `info` / `manifest` 也会把 `language_release` 与 distribution version 分开表达；  
公开版本叙述以 `language_release` 为准，不把当前源码分发版本误写成语言冻结版本。

### 1.3 最小安装与试用路径

当前公开承诺支持的最小试用路径是：

1. `pip install -e .`
2. `coglang bundle`
3. `coglang smoke`
4. `coglang demo`

这条路径的目标是证明：

- 包可安装
- CLI 可调用
- 最小发布工件齐全
- 最小 conformance 路径可运行
- 最小端到端内存工作流可运行

### 1.4 当前许可证方向

当前对外发布口径为：

- `Apache-2.0`

当前仓库应包含实际 `LICENSE` 文件，并与 `pyproject.toml` 和 CLI 发布检查路径一致。

### 1.5 一致性验证入口

当前公开承诺存在的 conformance suite 为：

- `smoke`
- `core`
- `full`

其中：

- `smoke` 用于最小发布前自检
- `core` 用于较高信心的一致性验证
- `full` 用于完整测试目录入口

### 1.6 语言定位

当前公开承诺的语言定位是：

- 图优先工作语言
- AI 系统中的结构化中间语言核心
- 表达式级执行语义 + 可观测性 + 宿主桥接边界

### 1.7 当前明确面向的使用场景

当前版本优先面向的是：

- 由语言模型生成的图操作与图查询表达式
- 需要把失败、回执、trace 和宿主边界显式保留下来的执行路径
- 需要 `profile / capability` 约束的宿主接入场景
- 需要把“语言表达式”和“宿主提交/审计边界”分层处理的实现者

这是一种 design intent，不是竞品比较声明。  
当前公开口径描述的是“为什么这样设计”，不是“比别的系统强多少”。

---

## 2. 本次明确不承诺的内容

以下内容**不属于**本次 `v1.1.0-pre` 的公开承诺。

### 2.1 不承诺成熟独立平台

当前不承诺：

- 发布到包索引
- 多宿主稳定运行
- 成熟扩展生态
- 完整发布自动化

### 2.2 不承诺所有 companion note 都是稳定协议

以下文档仍属于伴随说明或路线材料，不应被误读成稳定核心协议：

- `CogLang_Decoupling_and_Open_Source_Roadmap_v0_1.md`
- `CogLang_V4_Boundary_Note_v1_1_0.md`
- `CogLang_Abstract_Triggering_Note_v1_1_0.md`

### 2.3 不承诺扩展调用语法已面向普通用户冻结

当前不承诺：

- extension-backed operator 的普通用户可教学显式限定名语法
- 完整扩展生态接口

### 2.4 不承诺完整宿主无关运行时

当前 `Host Runtime Contract` 仍是 `v0.x`，它说明的是最小桥接基线，不等于已经完成成熟宿主无关平台化。

### 2.5 不承诺未来预留能力已可用

`Reserved / Experimental` 仍不等于默认可依赖能力。  
未来方向、路线图或伴随说明里的想法，不应被当作本次公开发布的现成能力。

### 2.6 当前明确不是的东西

当前版本不应被理解成：

- 通用编程语言
- schema definition language
- 某个特定图数据库的原生查询替代层
- 对其他图查询语言或知识表示系统的优劣结论

如果某个场景本来就应该直接使用其原生图查询语言、原生事务语义或原生 schema 工具，那么 `CogLang` 当前并不声称要替代它们。

---

## 3. 外部使用者应如何理解本次版本

如果你是第一次接触 `CogLang` 的外部使用者，本次版本最正确的理解方式是：

- 它已经足够被试用、被阅读、被实现、被做最小集成
- 它还不应被当作成熟独立语言平台采购或长期锁定
- 它最适合被理解成“面向可审计宿主执行的图优先表达式语言核心”，而不是通用语言替代品

也就是说：

- **可以开始用**
- **可以开始接**
- **可以开始验证**
- **但还不应过度承诺长期稳定外部平台边界**

---

## 4. 推荐对外表述

如果需要对外一句话说明当前版本，建议使用：

> `CogLang v1.1.0-pre` 是一个实验性、预发布的图优先语言核心与参考实现，已经具备最小安装、最小 CLI、最小 conformance、自检和发布工件检查路径，但尚未完成成熟独立平台化。

---

## 5. 贡献与反馈边界

当前欢迎外部贡献，但最欢迎的是：

- 文档澄清
- conformance / golden examples
- CLI 与工具面
- Host Runtime Contract 边界收口
- 非参考宿主的最小示例与宿主 demo
- 规范与实现对齐型 bug fix

当前不应把下列方向误读成“当前公开承诺的默认贡献主线”：

- 大幅扩语言表面
- 把路线图设想直接写进主规范
- 把宿主专属协议写回语言核心
- 把公开定位写成竞品对比表或证据不足的宣传话术

更完整的贡献边界见：

- `CogLang_Contribution_Guide_v0_1.md`

另外，如果你想区分“当前承诺”与“未来方向 / 维护边界”，再看：

- `ROADMAP.md`
- `MAINTENANCE.md`

---

## 6. 方向层与维护层

当前公开文档集现在把三层信息分开表达：

- `Release Notes`: 当前承诺与非承诺
- `ROADMAP.md`: 当前方向层与探索层
- `MAINTENANCE.md`: 项目若放缓、冻结、转交或归档时的公开处理方式

这几份文档不应被混读：

- `ROADMAP.md` 不是发布承诺
- `MAINTENANCE.md` 不是“项目准备停止”的暗示
- `Release Notes` 也不应被当成长期愿景文档

---

## 7. 一句话结论

本次 `v1.1.0-pre` 真正承诺的是：  
**一套可试用、可验证、可集成讨论的最小公开基线。**  
它承诺最小可用，不承诺过度成熟。
