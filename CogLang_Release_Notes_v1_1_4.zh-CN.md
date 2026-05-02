# CogLang Release Notes v1.1.4

**状态**：Python package maintenance patch
**Python distribution version**：`1.1.4`
**Language release**：`v1.1.0`
**适用对象**：用户、发布维护者、审查者
**作用**：对齐 `1.1.3` 发布后的治理状态与 release-check 证据，不改变语言语义

---

## 0. 发布定位

CogLang `1.1.4` 是 stable `v1.1.0` 语言线上的包级维护 patch。

它不改变 CogLang 语言语法、算子语义、canonical text 规则，也不改变
`v1.1.0` conformance contract。

包版本变为 `1.1.4`，CLI 元数据继续报告：

- `version`：`1.1.4`
- `language_release`：`v1.1.0`

## 1. 变化内容

- `coglang release-check` 现在在 source 与 public-extract layout 下包含
  `public_assets_mirror` gate，使用已有 mirror checker 检查 exact
  package-data mirror 文件是否缺失或与根源文件漂移。
- installed package mode 下，source/mirror 比对会标记为不适用并通过，避免
  wheel 与 sdist 用户被要求比较包外不存在的根源文件。
- release-check 的 text 与 JSON 输出现在显式展示 public asset mirror 覆盖。
- roadmap 与 standalone install/release guide 已记录 v1.1.3 GitHub Release
  与 PyPI Trusted Publishing 的完成状态。
- standalone install/release guide 现在列出当前 public CLI surface，包括
  preflight、generation-eval、host-demo、reference-host-demo。

## 2. 没有改变什么

本版本不冻结：

- v1.2 语言语法
- public readable-render API
- `generation-eval` benchmark claim
- cross-language conformance program
- normative cross-language JSON Schema pack
- 由本仓库之外维护的 third-party host implementation

HRC v0.2 仍只冻结 `host-demo`、`reference-host-demo`、包测试和 companion
evidence 覆盖的 narrow typed write-envelope surface。

## 3. 建议检查

最小用户安装：

```powershell
pip install coglang
coglang info
coglang release-check
coglang execute 'Equal[1, 1]'
```

随包 smoke 与 conformance checks：

```powershell
pip install "coglang[dev]"
coglang doctor
coglang smoke
coglang conformance smoke
```

source checkout 发布门禁：

```powershell
python -m pytest
python -m coglang release-check --format text
```

## 4. 一句话总结

CogLang `1.1.4` 把 public asset mirror 漂移变成一等 `release-check` gate，
并记录已完成的 `1.1.3` 发布路径，同时保持 stable `v1.1.0` 语言语义不变。
