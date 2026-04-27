# CogLang Standalone Install and Release Guide v0.1

**状态**：稳定发布伴随文档
**适用对象**：第一次以独立语言组件视角试用 `CogLang` 的使用者、实现者、发布维护者
**作用**：说明当前如何以最小成本安装、验证、试用 `CogLang`，并区分稳定语言发布与宿主生态路线图工作

---

## 0. 这份文档解决什么问题

稳定 `v1.1.0` 的分发路径是通过 PyPI Trusted Publishing 发布。
如果只看项目源码入口，外部读者很容易知道“代码在哪里”，却不够清楚“如何把 `CogLang` 当作一个独立语言核心先试起来”。

这份文档只回答 4 个实际问题：

1. 现在怎么安装和运行 `CogLang`
2. 安装后先跑什么命令确认环境正常
3. 最小独立工具面现在包含什么
4. 哪些事项仍属于稳定语言发布之外的路线图工作

---

## 1. 当前支持的最小安装路径

稳定发布工件通过 PyPI 安装：

```powershell
pip install coglang
```

完成后，应至少能使用下面的入口：

```powershell
coglang info
```

说明：

- `CogLang` 已经有独立 console script `coglang`
- 稳定版通过 PyPI Trusted Publishing 发布，不使用长期 API token

源码开发使用：

```powershell
pip install -e ".[dev]"
```

stable `v1.1.0` 语言发布最初让 Python distribution version 与语言 release 对齐（tag `v1.1.0` 对应包版本 `1.1.0`）。后续 `1.1.x` Python distribution patch 可以只更新打包或文档，同时继续保持 `language_release = v1.1.0`。

`v1.1.0-pre.0` 这类预发布 tag 仍保持 GitHub-only，除非后续另有明确发布决策。

---

## 2. 安装后最小验收路径

安装后建议按下面顺序检查：

### 2.1 元数据与命令入口

```powershell
coglang info
```

这一步应告诉你：

- 当前 distribution version
- 当前 language release label
- 可用命令
- conformance suite 名称

在稳定发布形态下，这两层版本语义已对齐；在历史预发布或源码开发形态下，仍应分开理解：

- `version` 反映当前安装分发元数据版本
- `language_release` 反映当前 `CogLang` 语言/规范公开标签

stable `v1.1.0` 初始稳定发布让这两层有意收敛：GitHub tag 是 `v1.1.0`，Python 包版本是 `1.1.0`，`language_release` 报告 `v1.1.0`。后续包级 patch release 可以报告例如 `1.1.1` 的 Python 包版本，同时继续报告 `language_release = v1.1.0`。

### 2.2 环境自检

```powershell
coglang doctor
```

这一步应检查：

- Python 版本
- 临时目录
- parse / validate / execute 最小路径
- `pytest` 是否可用

### 2.3 最小发布工件检查

```powershell
coglang release-check
```

这一步当前应通过。
它检查的不是“语言所有能力是否完整”，而是“最小发布工件是否齐全”，例如：

- `pyproject.toml`
- `LICENSE`
- distribution metadata
- console script 声明
- runtime entry 完整性
- 主规范 / Quickstart / Conformance / Host Runtime Contract
- 对外公开入口文档：`README / ROADMAP / MAINTENANCE / llms.txt / llms-full.txt`

### 2.4 面向脚本和 CI 的单一发布摘要

```powershell
coglang bundle
```

这一步会把下面几层压成一份单一摘要：

- `manifest`
- `release-check`
- `doctor`

如果你要把 `CogLang` 接进脚本、CI 或最小发布流程，优先消费这份摘要，而不是分别解析多条命令输出。

当前 `manifest` / `bundle` 的 machine-readable 载荷还会保留一层实现元数据；
但对外建议使用的入口应始终以 `entrypoints.recommended = "coglang"` 为准，而不是把实现模块路径当作公开主入口。

### 2.5 最小一致性路径

```powershell
coglang conformance smoke
```

### 2.6 最小端到端示例

```powershell
coglang demo
```

### 2.7 宿主接入说明

如果你要从宿主实现者视角接入 `CogLang`，当前不建议从本安装指南直接学习参考实现细节。
更合适的入口是：

- `CogLang_Host_Runtime_Contract_v0_1.md`

本安装指南只保留对外可公开的最小安装、命令和试用途径。

---

## 3. 当前对外公开建议使用的最小独立工具面

当前对外公开建议使用的独立工具入口如下：

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

这意味着当前 `CogLang` 已经不只是“有规范和参考运行时”，也已经具备一组可以独立试用的最小工具入口。
若帮助输出里出现额外参考命令，它们不自动构成对外稳定承诺。

---

## 4. 当前可以对外怎么说

当前更适合这样描述：

- `stable language release`
- `reference implementation`
- `language core + host bridge`

当前不适合这样描述：

- 成熟独立语言平台
- 完整宿主无关运行时
- 已稳定扩展生态
- 多宿主一致发布产品

---

## 5. 当前还不是什么

即使已经可以安装和试用，当前也仍然不是：

1. 通用编程语言
2. 已冻结的多宿主运行时标准
3. 成熟扩展生态
4. 已经过多个独立宿主验证的成熟平台

因此，“稳定语言发布”和“已经成为成熟独立平台”应严格区分。

---

## 6. stable v1.1.0 发布策略

stable `v1.1.0` 是第一个应把包索引发布纳入正常路径的目标版本。

发布策略如下：

- `v1.1.0-pre.0` 这类 GitHub 预发布保持 source-only，不回补发布到 PyPI。
- stable GitHub tag 是 `v1.1.0`。
- 初始 stable Python distribution version 是 `1.1.0`；包级 patch release 可以使用后续 `1.1.x` Python distribution version。
- PyPI 发布使用 GitHub Actions Trusted Publishing。
- 常规发布不使用长期 PyPI API token。
- 发布 workflow 必须先校验 tag 与 `pyproject.toml` 包版本一致，才能上传工件。

首次 PyPI 上传前，项目所有者需要在 PyPI 配置 Trusted Publishing：

- PyPI project：`coglang`
- GitHub repository：`jaysinailabs/coglang`
- Workflow filename：`publish.yml`（仓库内文件路径是 `.github/workflows/publish.yml`）
- Environment name：`pypi`

仓库中的 publish workflow 对普通 push 是惰性的；它只在匹配 tag 时运行，并拒绝非 stable tag 或版本不匹配的工件。

---

## 7. stable v1.1.0 之后还差什么

从当前状态走到更成熟的独立发布，下一层最现实的差距主要在：

1. **Trusted Publishing 配置**
   在推送 stable tag 前确认 PyPI project 与 GitHub environment 配置。
2. **发布元数据与版本节奏**
   让包发布、工件校验和语言 release label 更容易理解。
3. **更稳的 Host Runtime Contract**
   让外部宿主可以更低成本接入。
4. **至少一个非参考宿主 demo**
   证明这不是项目内私有 DSL。
5. **更完整的 release automation**
   例如 release notes 生成和发布后校验。

---

## 8. 当前建议的实际使用顺序

如果你只是想先验证 `CogLang` 是否能从 PyPI 独立安装和运行，建议先做最小路径：

1. `pip install coglang`
2. `coglang info`
3. `coglang release-check`
4. `coglang execute 'Equal[1, 1]'`

如果要运行随包 smoke 和 conformance checks，需要先安装 development extra：

1. `pip install "coglang[dev]"`
2. `coglang smoke`
3. `coglang demo`
4. `coglang conformance smoke`

如果这些检查通过，再去看：

- `CogLang_Quickstart_v1_1_0.md`
- `CogLang_Specification_v1_1_0_Draft.md`
- `CogLang_Host_Runtime_Contract_v0_1.md`
- `CogLang_Release_Notes_v1_1_0.md`

---

## 9. 一句话结论

当前 `CogLang` 已经具备**稳定语言发布路径、最小命令入口、最小一致性运行、最小发布工件检查**。
这足以支撑稳定语言使用；多宿主成熟度与生态工具仍属于明确的路线图工作。
