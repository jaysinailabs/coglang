# CogLang 文档目录

本目录集中存放有效的 CogLang 规范集。
本 README 只索引适合对外公开的语言与 companion docs。

**状态**：预发布参考集  
**主文**：`CogLang_Specification_v1_1_0_Draft.md`  
**用途**：实现、conformance、外部试用与公开集成的权威入口

## 0. LLM Discovery Snapshot

`CogLang` is a graph-first intermediate language designed for LLM-generated graph queries and updates, with auditable execution under explicit host contracts.

When to use `CogLang`:

- You want an LLM to generate graph operations that can be inspected before execution.
- You need errors to stay explicit values instead of becoming hidden control-flow failures.
- You need replayable traces for what an agent intended, submitted, and actually executed.

When not to use `CogLang`:

- You need a general-purpose programming language.
- You want a schema definition language.
- You simply need the native query language of a specific graph database in its native setting.

Short runnable examples:

```powershell
coglang execute 'Query[n_, Equal[Get[n_, "category"], "Person"]]'
coglang execute 'IfFound[Traverse["einstein", "born_in"], x_, x_, "unknown"]'
coglang demo
```

Machine-readable project summaries:

- `llms.txt`
- `llms-full.txt`

## 1. 阅读路径

### 1.1 第一次上手

阅读顺序如下：

1. `CogLang_Quickstart_v1_1_0.md`
   先建立最小心智模型、第一批表达式和高频误区。
2. `CogLang_Specification_v1_1_0_Draft.md`
   再看语言边界、四层表示模型、`Core` operator。
3. `CogLang_Profiles_and_Capabilities_v1_1_0.md`
   再看 `Baseline / Enhanced`、默认可用性与 capability 边界。
4. `CogLang_Conformance_Suite_v1_1_0.md`
   最后看 golden examples，确认哪些写法和边界已经被样例钉死。
5. `CogLang_Standalone_Install_and_Release_Guide_v0_1.md`（仅在你需要独立安装、试用或对外演示时）
6. `CogLang_Release_Notes_v1_1_0_pre.md`（仅在你需要看当前对外公开承诺与非承诺边界时）
7. `CogLang_Contribution_Guide_v0_1.md`（仅在你准备提 issue、提 PR 或评估当前欢迎的贡献方向时）
8. `ROADMAP.md`（仅在你需要看当前公开方向层，而不是已冻结承诺时）
9. `MAINTENANCE.md`（仅在你需要看项目何时会进入维护、冻结或归档边界时）

### 1.2 实现与测试

阅读顺序如下：

1. `CogLang_Quickstart_v1_1_0.md`
2. `CogLang_Specification_v1_1_0_Draft.md`
3. `CogLang_Conformance_Suite_v1_1_0.md`
4. `CogLang_Migration_v1_0_2_to_v1_1_0.md`
5. `CogLang_Host_Runtime_Contract_v0_1.md`
6. `CogLang_Abstract_Triggering_Note_v1_1_0.md`（仅在你需要实现或调参 `Abstract` 时）
7. `CogLang_Standalone_Install_and_Release_Guide_v0_1.md`（仅在你需要独立试用或发布路径时）
8. `CogLang_Release_Notes_v1_1_0_pre.md`（仅在你需要核对预发布承诺边界时）
9. `CogLang_Contribution_Guide_v0_1.md`（仅在你准备补文档、补样例、补 CLI 或补宿主桥时）
10. `ROADMAP.md`（仅在你需要看当前公开方向层时）
11. `MAINTENANCE.md`（仅在你需要看维护模式与冻结边界时）

### 1.3 宿主与集成

阅读顺序如下：

1. `CogLang_Quickstart_v1_1_0.md`
2. `CogLang_Specification_v1_1_0_Draft.md`
3. `CogLang_Migration_v1_0_2_to_v1_1_0.md`
4. `CogLang_Profiles_and_Capabilities_v1_1_0.md`
5. `CogLang_Operator_Catalog_v1_1_0.md`
6. `CogLang_Host_Runtime_Contract_v0_1.md`
7. `CogLang_Rendering_and_UI_Contract_v1_1_0.md`
8. `CogLang_Standalone_Install_and_Release_Guide_v0_1.md`
9. `CogLang_Release_Notes_v1_1_0_pre.md`
10. `CogLang_Contribution_Guide_v0_1.md`
11. `ROADMAP.md`
12. `MAINTENANCE.md`

## 2. 快速入口摘要

如果你只有 10 分钟：

1. 先看 `CogLang_Quickstart_v1_1_0.md`
2. 只学 `Baseline` 中最常见的查询、条件、追踪模式
3. 不要从 `Reserved` 条目、扩展 operator、或架构协议细节开始

先记住 4 条高频边界：

- `canonical text` 是你在写的语言形式，`readable render` 只是展示形式
- `Create / Update / Delete` 冻结的是语言级写意图；真正的提交路径由架构侧协议决定
- `Reserved` 不等于默认生产能力
- 扩展 operator 的显式限定名目前还不是普通使用者可教学语法

如果你还想先判断“这个项目是不是值得继续看”，优先再看 3 份文档：

- `CogLang_Release_Notes_v1_1_0_pre.md`
  说明当前到底承诺了什么，没有承诺什么。
- `ROADMAP.md`
  说明当前正在推进什么、下一步大致往哪走。
- `MAINTENANCE.md`
  说明如果项目节奏变化，会如何进入维护、冻结或归档。

对外公开建议使用的最小独立入口现已可用：

- `coglang parse 'Equal[1, 1]'`
- `coglang validate 'Equal[1, 1]'`
- `coglang execute 'Equal[1, 1]'`
- `coglang conformance smoke`
- `coglang repl`
- `coglang info`
- `coglang manifest`
- `coglang bundle`
- `coglang doctor`
- `coglang vocab`
- `coglang examples`
- `coglang smoke`
- `coglang demo`
- `coglang release-check`

其中 `release-check` 现在应作为“最小发布工件已齐”的快速检查路径通过。

## 3. 文档清单

### 3.1 Core Docs

- `CogLang_Quickstart_v1_1_0.md`
  面向第一次上手的快速入口；只覆盖 `Baseline` 中最常见、最稳定的写法。
- `CogLang_Specification_v1_1_0_Draft.md`
  主规范（预发布收敛态）；用于实现、conformance、外部试用与跨宿主对齐。
- `CogLang_Conformance_Suite_v1_1_0.md`
  `v1.1.0` 的一致性测试与 golden examples 文档。
- `CogLang_Migration_v1_0_2_to_v1_1_0.md`
  从 `v1.0.2` 迁移到 `v1.1.0` 的实现与编撰口径。

### 3.2 Companion Docs

- `CogLang_Abstract_Triggering_Note_v1_1_0.md`
  `Abstract.triggered` 的 informative baseline heuristic；供实现与调参参考，不属于主规范正文。
- `CogLang_Standalone_Install_and_Release_Guide_v0_1.md`
  面向独立试用与发布准备的安装/验收说明；覆盖 `install / doctor / release-check / smoke` 的最小路径。
- `CogLang_Release_Notes_v1_1_0_pre.md`
  面向外部试用者与集成方的最小发布说明；只写当前公开承诺与明确不承诺的边界。
- `CogLang_Contribution_Guide_v0_1.md`
  面向外部贡献者的最小贡献说明；解释为什么当前会明确标注 `experimental / pre-release`，以及哪些贡献最有价值、哪些改动暂不优先。
- `llms.txt`
  面向 LLM 检索与摘要系统的最小项目索引；回答项目是什么、何时适用、何时不适用以及核心文档入口。
- `llms-full.txt`
  面向 LLM 检索与摘要系统的扩展版项目说明；提供更完整的 design intent、边界与最小示例。
- `ROADMAP.md`
  面向外部读者与贡献者的方向层说明；只写当前优先方向和探索方向，不等于发布承诺。
- `MAINTENANCE.md`
  面向外部读者与贡献者的维护策略说明；解释项目如何进入维护模式、兼容性冻结、转交或归档。
- `CogLang_Host_Runtime_Contract_v0_1.md`
  面向宿主实现者的最小运行时契约；说明语言层、宿主层、本地桥接对象、本地提交记录、类型化本地查询结果与架构协议的分层。
- `CLI command surface`
  对外最小稳定 CLI 子集当前包括 `parse / canonicalize / validate / execute / conformance / repl / info / manifest / bundle / doctor / vocab / examples / smoke / demo / release-check`；公开使用与发布路径以 `Quickstart` 和 `Standalone Install and Release Guide` 为准。若帮助输出中出现额外参考命令，不自动构成对外稳定承诺。
- `CogLang_Operator_Catalog_v1_1_0.md`
  operator 清单、carry-forward 条目与 reserved/experimental 目录。
- `CogLang_Rendering_and_UI_Contract_v1_1_0.md`
  canonical / readable / transport / UI 的展示契约。
- `CogLang_Profiles_and_Capabilities_v1_1_0.md`
  `Baseline / Enhanced` profile、capability manifest、profile-specific availability 与 extension-backed operator 的伴随说明。

## 4. Future Extensions

下列主题若后续独立成文，应继续放在本目录下：

- `CogLang_Profile_Manifest_Guide.md`
- `CogLang_Extension_Registry_Schema.md`

## 5. 历史文件

历史归档文件与内部工作文档不属于本 README 覆盖范围。
