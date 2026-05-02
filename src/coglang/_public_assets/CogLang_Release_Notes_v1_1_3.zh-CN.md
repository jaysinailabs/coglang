# CogLang Release Notes v1.1.3

**状态**：Python 包级证据与维护补丁版
**Python distribution version**：`1.1.3`
**语言 release**：`v1.1.0`
**适用对象**：试用当前包的用户、宿主实现者和评审者
**目的**：发布 `1.1.2` 之后新增的可执行维护证据；不改变语言语义

---

## 0. 发布定位

CogLang `1.1.3` 是 stable `v1.1.0` 语言线上的包级 patch release。

它不改变 CogLang 语言语法、operator 语义、canonical text 规则或
`v1.1.0` conformance contract。

包版本变为 `1.1.3`，CLI 元数据继续报告：

- `version`：`1.1.3`
- `language_release`：`v1.1.0`

## 1. 变更内容

本版发布 `1.1.2` 之后新增的维护证据：

- `coglang preflight` 和 `coglang preflight-fixture` 暴露候选 v1.2 静态
  preflight 路径，覆盖 effect summary、graph budget、budget estimate 和
  preflight decision。
- 静态 preflight 现在把 `estimated_traversal_depth` 解释为嵌套 `Traverse`
  深度，而不是 `Traverse` 出现总数。
- `coglang generation-eval` 随包提供确定性的 L1-L3 fixture，用于检查生成的
  CogLang 文本是否能 parse、canonicalize、validate，是否匹配预期顶层 head，
  是否包含幻觉算子，并输出 maturity summary 与 preflight decision。
- generation-eval 的 maturity summary 现在区分 fixture-defined levels 与
  evaluated levels，因此 L4-L6 会明确显示为未评估，而不是被暗示已经覆盖。
- 抽象 `CogLangExecutor` surface 保持最小化：二次实现只需要实现
  `execute()` 和 `validate()`。
- `examples/node_host_consumer` 展示 Node.js 标准库消费 HRC schema pack 与
  envelope samples，不导入 Python runtime。
- `examples/node_minimal_host_runtime_stub` 展示一个小型 companion Node.js
  host/runtime stub，覆盖 `execute`、`validate` 以及 typed write-envelope
  成功/失败路径。
- 公开治理与规划文档新增 v1.2 evolution boundary、effect-budget preflight
  vocabulary、reserved operator promotion criteria、`Send` carry-forward exit
  criteria、HRC companion asset classification、readable-render boundary、
  readable-render candidate examples、readable-render API promotion gates 和当前
  review-response priorities。
- release-check 与 CI 证据覆盖 public asset mirror、built wheel 和 sdist
  validation、HRC host demos、Node examples、generation-eval 和 preflight
  fixtures。
- schema version 标识符现在集中到 `schema_versions.py` registry，并由 Python
  runtime payload 生产模块引用；既有 payload 值不变。
- readable-render golden example candidates 现在有随包 JSON fixture，用于固定
  canonical text 与 candidate display strings；这不新增 renderer API，也不声明
  readable output 已稳定。
- public asset mirror 维护现在有可复用的 check 与 sync helper，source/extracted
  tree 可以检测并修复镜像 drift；这不改变 public release contract。
- `coglang doctor` 现在会把 `build/`、`dist/` 等本地生成目录报告为非失败型
  清理提示，方便 source checkout 维护。
- `coglang smoke` 与 `coglang conformance` 现在会在受控临时目录下显式传入
  pytest `--basetemp`，避免 Windows tempdir 清理竞争，同时保留用户自定义
  `--basetemp` 的覆盖权。
- 仓库元数据新增 `.mailmap`，将历史提交中的
  `xinjingshun <xinjingshun@foxmail.com>` 归并显示为
  `Jason Xin <xinjingshun@foxmail.com>`，不重写 Git 历史。

## 2. 未改变内容

本版不冻结：

- v1.2 语言语法
- `EffectSummary`、`GraphBudget`、`GraphBudgetEstimate` 或
  `PreflightDecision` 作为 stable v1.1 语法
- public readable-render API
- `to_readable()`
- `coglang render`
- `--format readable`
- `generation-eval` benchmark claim
- cross-language conformance program
- 网络传输协议
- normative cross-language JSON Schema pack
- 由本仓库外部维护的第三方宿主实现

HRC v0.2 仍只冻结由 `host-demo`、`reference-host-demo`、package tests 和
companion evidence 覆盖的狭义 typed write-envelope surface。

## 3. 建议检查

最小用户安装路径：

```powershell
pip install coglang
coglang info
coglang release-check
coglang preflight --format text 'AllNodes[]'
coglang preflight-fixture
coglang generation-eval --summary-only
coglang execute 'Equal[1, 1]'
```

host-runtime 证据路径：

```powershell
coglang host-demo
coglang reference-host-demo
node examples/node_host_consumer/consume_hrc_envelopes.mjs
node examples/node_minimal_host_runtime_stub/run_demo.mjs
```

如果要运行随包 smoke 和 conformance checks：

```powershell
pip install "coglang[dev]"
coglang doctor
coglang smoke
coglang conformance smoke
```

## 4. 一句话总结

CogLang `1.1.3` 发布 `1.1.2` 之后新增的 preflight、generation-eval、Node
companion evidence 和治理评审资产，同时保持 stable `v1.1.0` 语言语义不变。
