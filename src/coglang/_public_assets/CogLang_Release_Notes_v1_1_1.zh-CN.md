# CogLang Release Notes v1.1.1

**状态**：Python 包文档补丁版
**Python distribution version**：`1.1.1`
**语言 release**：`v1.1.0`
**适用对象**：第一次从 PyPI 安装 CogLang 的用户
**目的**：修正 first-run 安装指引，不改变语言语义

---

## 0. 发布定位

CogLang `1.1.1` 是 stable `v1.1.0` 语言线上的包级 patch release。

它不改变 CogLang 语言表面、operator 语义、conformance suite 或 Host Runtime Contract 口径。

包版本变为 `1.1.1`，但 CLI 元数据继续报告：

- `version`：`1.1.1`
- `language_release`：`v1.1.0`

## 1. 变更内容

本版修正 PyPI 包和 README 中的 first-run 文档：

- 最小 PyPI 安装验证路径改为 `coglang info`、`coglang release-check` 和 `coglang execute 'Equal[1, 1]'`。
- `coglang smoke`、`coglang doctor` 和随包 conformance checks 明确要求 `pytest`，通常通过 `pip install "coglang[dev]"` 安装。
- Quickstart 的状态措辞改为稳定发布口径，不再沿用预发布措辞。

## 2. 未改变内容

本版不改变：

- parser 行为
- validator 行为
- executor 行为
- canonical text 规则
- 已文档化的 operator 语义
- public language release label
- PyPI Trusted Publishing 策略

## 3. 建议安装检查

最小用户安装路径：

```powershell
pip install coglang
coglang info
coglang release-check
coglang execute 'Equal[1, 1]'
```

如果要运行随包 smoke 和 conformance checks：

```powershell
pip install "coglang[dev]"
coglang doctor
coglang smoke
coglang conformance smoke
```

## 4. 一句话总结

CogLang `1.1.1` 修正 PyPI first-run 指引，避免用户在未安装 development extra 前运行依赖 pytest 的 smoke checks。
