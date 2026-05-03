# CogLang Release Notes v1.1.5

**状态**：Python package maintenance patch
**Python distribution version**：`1.1.5`
**Language release**：`v1.1.0`
**适用对象**：用户、发布维护者、宿主实现者和审查者
**作用**：发布 local-first validation 与 AI-first developer experience 维护批次，不改变语言语义

---

## 0. 发布定位

CogLang `1.1.5` 是 stable `v1.1.0` 语言线上的包级维护 patch。

它不改变 CogLang 语言语法、算子语义、canonical text 规则，也不改变
`v1.1.0` conformance contract。

包版本变为 `1.1.5`，CLI 元数据继续报告：

- `version`：`1.1.5`
- `language_release`：`v1.1.0`

## 1. 变化内容

本版发布 `1.1.4` 之后积累的 source-maintenance 批次：

- 公开 GitHub `ci` workflow 改为手动触发，以节省 Actions minutes；远程证据
  触发前应先完成本地验证。
- `scripts/local_ci.py` 提供 `quick`、`ci`、`package` 三个本地模拟 profile，
  覆盖 release-check、smoke、HRC host demos，以及 wheel/sdist 安装验证。
- `examples/grammar` 提供 companion Lark 与 GBNF grammar 示例，用于
  constrained generation。这些文件可以减少模型输出畸形，但不替代 `parse`
  或 `valid_coglang`。
- `coglang generation-eval` 现在支持 provider-neutral request export 和
  response-file scoring，因此外部模型 runner 可以被评分，而不需要把 provider
  SDK 加入 CogLang 依赖。记录格式现在由
  `CogLang_Generation_Eval_Request_Response_Contract_v0_1.md` 明确文档化。
- `examples/generation_eval_offline_runner` 提供无 provider 的三用例 dry run，
  用于验证 generation-eval request/response 文件契约。
- `examples/semantic_event_audit` 提供无 provider 的 semantic-event audit
  dry run，把外部 runner 的 graph-intent JSONL 转成本地 preflight audit
  records。它是 companion example material，不是 hosted runner、protocol、
  transport envelope、benchmark 或 HRC 扩展。
- `examples/vscode_textmate_syntax` 提供 private、可本地安装的
  VS Code/TextMate syntax companion，用于 `.coglang` 文件。它只是 editor-only
  companion material，不是 parser、validator、LSP、formatter、renderer 或
  normative grammar。
- `examples/node_host_consumer` 现在包含 private npm scaffold，用于本地
  `npm test` 和 `npm pack --dry-run` 检查。它仍然是 example packaging
  evidence，不是已发布的 JavaScript SDK，也不是第二个 CogLang runtime API。
- `coglang release-check`、public extract 测试、package data、
  machine-readable summaries 和 public asset mirrors 都已覆盖这些新的
  companion examples 与 local-first validation assets。

## 2. 没有改变什么

本版本不冻结：

- v1.2 语言语法
- public readable-render API
- `generation-eval` benchmark claim
- normative constrained-generation grammar
- VS Code Marketplace extension 发布
- 已发布的 npm package 或稳定 JavaScript SDK
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

source checkout 在消耗远程 workflow minutes 前的本地验证：

```powershell
python -m pytest
python scripts/local_ci.py --profile quick
python scripts/local_ci.py --profile package
```

companion semantic-event、Node 与 editor-package dry run：

```powershell
python examples/semantic_event_audit/audit_events.py examples/semantic_event_audit/fixtures/external_events.jsonl .tmp_semantic_event_audit.jsonl
npm --prefix examples/node_host_consumer test
npm --prefix examples/node_host_consumer run pack:dry
Push-Location examples/vscode_textmate_syntax
npm pack --dry-run
Pop-Location
```

## 4. 一句话总结

CogLang `1.1.5` 打包 local-first validation workflow 和第一批 AI-first
developer-experience companion assets，同时保持 stable `v1.1.0` 语言语义不变。
