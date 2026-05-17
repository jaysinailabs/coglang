# CogLang Release Notes v1.1.6

**状态**：Python package maintenance patch
**Python distribution version**：`1.1.6`
**Language release**：`v1.1.0`
**适用对象**：用户、发布维护者、宿主实现者、下游实验维护者和审查者
**作用**：发布由 Rosetta 反馈驱动的 runtime 与文档维护补丁，不改变语言语义

---

## 0. 发布定位

CogLang `1.1.6` 是 stable `v1.1.0` 语言线上的包级维护 patch。

它不改变 CogLang 语言语法、canonical text 规则，也不改变 `v1.1.0`
conformance contract。

包版本变为 `1.1.6`，CLI 元数据继续报告：

- `version`：`1.1.6`
- `language_release`：`v1.1.0`

## 1. 为什么需要这个 patch

本版本回应一个下游 model-to-model communication 实验的真实反馈。该实验把
CogLang 作为 symbolic relay 与 executable evidence layer 使用。

反馈暴露了三个集成层面的实际问题：

- host-runtime write-envelope 名称容易被误解成可调用的 CogLang expression
  head；
- `Unify[]` 和 `Match[]` 在错误参数个数下可能漏出 Python `IndexError`，
  而不是返回 CogLang error value；
- 下游 prompt 与测试需要一个公开方式枚举可执行 expression head，而不是依赖
  executor 私有内部字段。

## 2. 变化内容

- `Unify` 和 `Match` 在错误参数个数下现在返回 CogLang 错误值：
  `TypeError[head, "arity", "expected 2 args"]`。
- `LocalCogLangHost.available_operators()` 返回当前 host executor 的可执行
  expression heads。
- `LocalCogLangHost.operator_inventory()` 分开返回 executable heads、eager
  dispatch heads、special forms、user-defined heads，以及 host API-only names。
- `coglang info --operators` 通过 CLI 以 JSON 或 text 形式暴露同一份
  operator inventory。
- 公开文档现在明确把 `WriteBundleCandidate`、
  `WriteBundleSubmissionMessage` 和 `WriteResult` 分类为 host API-only typed
  envelope names，而不是 `Do[...]` 可调用的 expression operators。
- public asset mirrors 与 package data 已包含更新后的发布侧文档和本 release
  note。

## 3. 没有改变什么

本版本不：

- 把 `WriteBundleCandidate`、`WriteBundleSubmissionMessage` 或 `WriteResult`
  提升为可执行 CogLang expression heads；
- 改变 `Create / Update / Delete` graph-write 语言表面；
- 扩大 HRC v0.2 的 narrow typed write-envelope evidence path；
- 增加 provider SDK 依赖；
- 改变 parser syntax、canonical serialization 或 stable `v1.1.0`
  conformance examples；
- 发布新的 JavaScript SDK、VS Code Marketplace extension 或 multi-host runtime
  standard。

下游 sender 仍应使用 `Create / Update / Delete` 等普通 CogLang graph-write
operators 表达写入意图，然后通过 `LocalCogLangHost.execute_with_candidate(...)`
或 `prepare_submission_message(...)` 等 host API 检查或提交捕获到的 typed
envelope。

## 4. 建议检查

最小用户安装：

```powershell
pip install coglang
coglang info
coglang info --operators
coglang release-check
coglang execute 'Equal[1, 1]'
```

source checkout 在消耗远程 workflow minutes 前的本地验证：

```powershell
python -m pytest
python scripts/local_ci.py --profile quick
python scripts/local_ci.py --profile package
```

下游 prompt regression 检查：

```python
from coglang import LocalCogLangHost

host = LocalCogLangHost()
assert {"Create", "Query", "Trace"}.issubset(host.available_operators())
assert "WriteBundleCandidate" in host.operator_inventory()["host_api_only"]
assert "WriteBundleCandidate" not in host.available_operators()
```

## 5. 一句话总结

CogLang `1.1.6` 打包一次下游反馈驱动的维护 patch：保持 stable `v1.1.0`
语言线不变，同时修复 `Unify` / `Match` 参数个数错误，并明确可执行 operator
discovery。
