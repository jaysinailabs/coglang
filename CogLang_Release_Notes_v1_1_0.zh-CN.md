# CogLang Release Notes v1.1.0

**状态**：稳定语言版本
**版本标签**：`v1.1.0`
**Python 分发版本**：`1.1.0`
**受众**：用户、实现者、宿主集成者和贡献者
**目的**：声明 CogLang v1.1.0 的公开承诺与非承诺边界

---

## 0. 发布定位

CogLang v1.1.0 是一个稳定语言版本和参考实现，面向由 LLM 生成的图查询与图更新，采用图优先的中间语言设计。

它适合作为语言模型与图宿主系统之间的一层：让生成出来的操作先经过解析、校验、检查、追踪和拒绝判定，再决定是否允许影响宿主系统。

本版本对齐三个公开版本面：

- GitHub release tag：`v1.1.0`
- Python 分发版本：`1.1.0`
- CLI `language_release`：`v1.1.0`

## 1. 本版本承诺什么

CogLang v1.1.0 承诺以下公开表面：

- `CogLang_Specification_v1_1_0_Draft.md` 中记录的 canonical M-expression 语言形式。
- 公开 CLI 入口 `coglang`。
- `coglang info`、`coglang manifest`、`coglang bundle`、`coglang smoke`、`coglang release-check` 暴露的文档化命令表面。
- `CogLang_Conformance_Suite_v1_1_0.md` 中记录且由测试套件覆盖的可执行 conformance case。
- 已文档化语言 operator 的 error-as-value 行为。
- `CogLang_Profiles_and_Capabilities_v1_1_0.md` 中记录的 profile 与 capability 边界。
- `CogLang_Operator_Catalog_v1_1_0.md` 中记录的 operator 状态与调用表面。
- 可审查的本地参考宿主桥接，以及 Host Runtime Contract v0.x 材料。
- 英文优先的公开文档；如提供中文文档，则作为伴随译本。
- 公开仓库采用 Apache-2.0 许可。

## 2. 本版本不承诺什么

CogLang v1.1.0 不声称以下内容：

- 它不是通用编程语言。
- 它不是 schema 定义语言。
- 它不是 Cypher、SPARQL、GQL 或任何图数据库原生查询语言在其原生场景下的替代品。
- 它不声称在 benchmark 上优于其他图语言。
- 除非明确文档化，否则 Python 内部模块不是稳定公开 API。
- 它不冻结完整的多宿主运行时标准。
- 它不承诺本版本具备成熟扩展生态、LSP 集成或 IDE 支持。

## 3. 稳定性范围

v1.1.0 的稳定承诺适用于：

- 当前版本文档化的语言语法与 canonicalization 行为
- 文档化 operator 语义与 conformance 示例
- 公开 CLI 命令名与文档化 JSON payload 形态
- `manifest`、`bundle`、`release-check` 使用的发布元数据路径
- 公开文档边界与非目标声明

v1.1.0 的稳定承诺不适用于：

- 私有 helper 函数
- Python 内部模块布局
- experimental 或 reserved operator 超出其文档状态的部分
- 未来 Host Runtime Contract v0.2+ 决策
- 尚未发布的生态工具

## 4. 从 v1.1.0-pre 升级的说明

稳定版保留预发布阶段形成的语言目标，并关闭公开发布元数据缺口：

- `COGLANG_LANGUAGE_RELEASE` 从 `v1.1.0-pre` 改为 `v1.1.0`。
- Python 包版本从 `0.1.0` 改为 `1.1.0`。
- 当前 release notes 从 `CogLang_Release_Notes_v1_1_0_pre.md` 改为 `CogLang_Release_Notes_v1_1_0.md`。
- PyPI 发布使用 Trusted Publishing，不使用长期 PyPI API token。
- GitHub-only 预发布 tag 保持为历史 source release，不回补发布到 PyPI。

## 5. 安装

稳定发布工件：

```powershell
pip install coglang
coglang manifest
coglang release-check
```

源码开发：

```powershell
pip install -e .[dev]
python -m pytest
```

## 6. 发布检查

发布工件应通过：

- `python -m pytest`
- `python -m build`
- 全新虚拟环境 wheel 安装
- `coglang manifest`
- `coglang release-check`
- `coglang smoke`

公开发布 workflow 只发布 tag 名与 Python 分发版本匹配的稳定 `v*` tag。

## 7. 一句话总结

CogLang v1.1.0 是面向可审计 LLM 生成图操作的稳定语言与 CLI 版本，并明确区分哪些已经稳定、哪些仍属于宿主契约工作、哪些刻意不在本版本范围内。
