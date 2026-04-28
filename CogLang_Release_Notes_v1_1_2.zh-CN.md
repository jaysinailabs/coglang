# CogLang Release Notes v1.1.2

**状态**：Python 包级 host-contract 证据补丁版
**Python distribution version**：`1.1.2`
**语言 release**：`v1.1.0`
**适用对象**：评估 CogLang host-runtime 边界的用户
**目的**：补充第二宿主证据，并记录 HRC v0.2 frozen typed write-envelope 范围；不改变语言语义

---

## 0. 发布定位

CogLang `1.1.2` 是 stable `v1.1.0` 语言线上的包级 patch release。

它不改变 CogLang 语言语法、operator 语义、canonical text 规则或
`v1.1.0` conformance contract。

包版本变为 `1.1.2`，CLI 元数据继续报告：

- `version`：`1.1.2`
- `language_release`：`v1.1.0`

## 1. 变更内容

本版补充公开、可执行的 host-runtime 评审证据：

- `coglang reference-host-demo` 展示一个最小第二宿主路径：消费
  `WriteBundleSubmissionMessage` JSON，返回 `WriteBundleResponseMessage`，
  且不依赖 `LocalCogLangHost`。
- `ReferenceTransportHost` 作为小型 reference host 导出，用于 typed
  write-envelope submission 以及本地 query/header lookup。
- `CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md` 记录 HRC v0.2 frozen typed
  write-envelope 的范围、证据、非范围和兼容性策略。
- 公开文档与 LLM 检索摘要已列出新的 host demo 与 HRC final freeze
  记录。

## 2. 未改变内容

本版不冻结：

- 网络传输协议
- 外部数据库持久化契约
- normative cross-language JSON Schema pack
- 由本仓库外部维护的第三方宿主实现
- 最终 `KnowledgeMessage` 跨服务标准
- capability-manifest negotiation

HRC v0.2 记录只冻结由 `host-demo`、`reference-host-demo` 和 package tests
覆盖的狭义 typed write-envelope surface。它不是最终 frozen 的多宿主标准。

## 3. 建议检查

最小用户安装路径：

```powershell
pip install coglang
coglang info
coglang release-check
coglang execute 'Equal[1, 1]'
```

host-runtime 证据路径：

```powershell
coglang host-demo
coglang reference-host-demo
```

如果要运行随包 smoke 和 conformance checks：

```powershell
pip install "coglang[dev]"
coglang doctor
coglang smoke
coglang conformance smoke
```

## 4. 一句话总结

CogLang `1.1.2` 增加最小第二宿主 demo，并冻结狭义 HRC v0.2 typed
write-envelope surface，同时保持 stable `v1.1.0` 语言语义不变。
