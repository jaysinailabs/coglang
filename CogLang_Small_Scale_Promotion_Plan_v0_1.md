# CogLang Small-Scale Promotion Plan v0.1

This document defines a narrow, evidence-first promotion plan for CogLang
1.1.5 and near-term source HEAD work.

It is not a growth campaign, paid launch plan, platform-publishing promise, or
claim that CogLang is production-ready for every graph workload.

## 1. Promotion Goal

The goal is to find a small number of technically aligned readers who can give
useful feedback or become the first external contributor in one of these areas:

- external generation-eval runner
- host or consumer implementation
- grammar or constrained-generation integration
- semantic-event audit workflow
- editor syntax or local developer-experience companion

The desired outcome is evidence and feedback, not broad attention.

## 2. Positioning

One-sentence positioning:

> CogLang is a small auditable language for LLM-generated graph operations,
> with canonicalization, validation, preflight effect and budget checks, and
> provider-neutral generation evaluation.

Short positioning:

CogLang sits between a language model and a graph-backed system. It gives the
host a structured expression to parse, canonicalize, validate, preflight,
review, hash, and replay before any write-like operation is trusted.

What to emphasize:

- LLM-generated graph operations need inspection before execution.
- Errors should remain explicit values, not hidden control-flow failures.
- Expression text should be canonical enough to hash, diff, and replay.
- Host capability checks and write-envelope evidence should stay explicit.
- Evaluation runners should be provider-neutral and local-first.

What not to claim:

- CogLang is not a general-purpose programming language.
- CogLang is not a graph database or native graph database replacement.
- CogLang is not a complete agent framework.
- CogLang is not a full observability, metrics, or interpretability stack.
- CogLang does not publish or maintain npm, VS Code Marketplace, or hosted
  playground surfaces from the main project.

## 3. Audience Segments

### 3.1 LLM Evaluation And Tooling Builders

Likely interest:

- provider-neutral request/response file contract
- deterministic scoring after arbitrary external model runs
- parse/canonicalize/validate signals for generated program text

Primary links:

- `CogLang_Generation_Eval_Request_Response_Contract_v0_1.md`
- `examples/generation_eval_offline_runner`
- `coglang generation-eval --export-requests --request-format jsonl`

Ask:

Try writing a small runner that converts exported requests into response JSONL
using the model provider or gateway you already use.

### 3.2 Constrained-Generation And Local LLM Users

Likely interest:

- companion Lark and GBNF grammar examples
- reducing malformed generated CogLang before parse/validate
- local model experiments without provider SDK coupling

Primary links:

- `examples/grammar`
- `coglang parse`
- `coglang validate`
- `coglang generation-eval`

Ask:

Try using the grammar files with an existing constrained-generation stack and
report the parts that need tighter examples or clearer boundaries.

### 3.3 Knowledge Graph And Semantic Infrastructure Builders

Likely interest:

- graph query and write intent as auditable symbolic values
- semantic-event audit records
- canonical expression hashes and preflight decisions

Primary links:

- `examples/semantic_event_audit`
- `coglang preflight --format text 'AllNodes[]'`
- `CogLang_Profiles_and_Capabilities_v1_1_0.md`

Ask:

Map one real or synthetic graph-intent event stream into CogLang expressions and
check whether the audit output gives enough review signal.

### 3.4 Host Or Consumer Implementers

Likely interest:

- narrow HRC v0.2 typed write-envelope evidence
- second-language consumer examples
- small executor surface

Primary links:

- `CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md`
- `CogLang_HRC_Companion_Asset_Classification_v0_1.md`
- `examples/node_host_consumer`
- `examples/node_minimal_host_runtime_stub`

Ask:

Open an issue before a large implementation PR and explain which HRC companion
asset or host boundary you plan to consume.

### 3.5 Editor And Local DX Contributors

Likely interest:

- TextMate syntax companion
- local packaging scaffold
- narrow contribution that does not require marketplace operations

Primary links:

- `examples/vscode_textmate_syntax`
- `CONTRIBUTING.md`

Ask:

Improve the local syntax package or add editor companion evidence without
turning the main project into a marketplace maintainer.

## 4. Channel Plan

### 4.1 Owned Channels

Owned channels should be updated first because they are the source material
that search tools, package indexes, and LLM-assisted readers will inspect.

- GitHub repository README and topics
- GitHub Release notes
- PyPI project metadata and project URLs
- `llms.txt` and `llms-full.txt`
- GitHub issues or discussions for narrowly scoped contribution invitations

Suggested GitHub topics:

- `llm`
- `dsl`
- `knowledge-graph`
- `graph`
- `auditing`
- `human-in-the-loop`
- `constrained-generation`
- `evals`
- `semantic-events`

### 4.2 Direct Outreach

Direct outreach should happen before broad community posting.

Target size:

- 5 to 15 technically aligned readers

Target profiles:

- people building LLM eval runners
- people using constrained decoding
- people working on knowledge graph operations
- people building host/runtime integrations
- people who review small language/tooling projects

Message shape:

- one sentence on what CogLang is
- one sentence on why the recipient might care
- one precise ask
- one link to the most relevant document or example

### 4.3 Community Channels

Use each community only when the post is useful without requiring the reader to
adopt CogLang.

Recommended first-wave channels:

- GitHub Discussions or issues in the CogLang repository
- small LLM engineering Discord or Slack groups where self-promotion is allowed
- constrained-generation or local LLM communities, if the grammar files are the
  focus
- knowledge graph communities, if the semantic-event audit example is the focus
- personal X, Bluesky, LinkedIn, or blog post

Recommended later-wave channels:

- Hacker News, only after there is a technical post or repository link that can
  stand on intellectual curiosity rather than promotion
- Reddit, only in communities whose rules allow project posts and only with a
  technical example

Avoid for now:

- Product Hunt
- paid promotion
- broad copy-pasted cross-posting
- claims of benchmark superiority
- announcing npm, VS Code Marketplace, LSP, hosted playground, or stable
  cross-language runtime support

## 5. Suggested Sequence

### Stage 0: Readiness Check

Complete before posting:

- PyPI package is published and installable.
- GitHub Release exists.
- `README.md`, `llms.txt`, and `llms-full.txt` describe 1.1.5 accurately.
- Release notes state what changed and what did not change.
- Contribution path explains local-first validation.

### Stage 1: Owned Surface Alignment

Tasks:

- Add promotion plan, use-case, and announcement kit documents.
- Link them from README and LLM-oriented summaries.
- Ensure public assets mirror and release-check remain clean.
- Set or review GitHub repository topics manually in the GitHub UI.
- Confirm PyPI project URLs point to the repository, issues, and docs.

### Stage 2: First Direct Outreach

Tasks:

- Pick 5 recipients.
- Send only the most relevant variant from the announcement kit.
- Track recipient, channel, date, link sent, and response.
- Ask for one concrete action, not a general opinion.

Exit criteria:

- at least 2 useful responses, or
- one external issue/PR opened, or
- one clear objection that changes the roadmap.

### Stage 3: Small Community Post

Tasks:

- Choose one community.
- Use a technical title, not a marketing title.
- Link to the repository or a technical document.
- Include limitations and non-goals.
- Do not ask for upvotes or reposts.

Exit criteria:

- collect questions and objections
- open follow-up issues for real bugs or unclear docs
- do not immediately post the same material to multiple communities

### Stage 4: Review And Decide

After 7 to 14 days:

- summarize responses
- categorize feedback as bug, documentation gap, integration request, or
  out-of-scope platform operation
- decide whether to continue with targeted outreach, prepare a broader
  technical article, or return to core engineering work

## 6. Quality Bar For Public Claims

Every public claim should map to a repository artifact.

Claim examples:

- "CogLang has provider-neutral generation evaluation."
  Evidence: `CogLang_Generation_Eval_Request_Response_Contract_v0_1.md`,
  `examples/generation_eval_offline_runner`, and `coglang generation-eval`.

- "CogLang provides constrained-generation companion grammars."
  Evidence: `examples/grammar`.

- "CogLang can support semantic-event audit workflows."
  Evidence: `examples/semantic_event_audit`.

- "CogLang has non-Python HRC consumption evidence."
  Evidence: `examples/node_host_consumer`.

- "CogLang keeps local-first CI discipline."
  Evidence: `scripts/local_ci.py` and manually triggered GitHub `ci`.

Avoid claims that require external adoption before the adoption exists.

## 7. Success Metrics

Use low-volume, high-signal metrics:

- one external issue from a realistic runner, host, grammar, or audit use case
- one external PR that passes local-first validation
- one useful technical review
- one reproducible confusion report that leads to a doc or example fix
- one maintainer-quality objection that changes a boundary or roadmap

Do not use raw stars, impressions, or likes as the primary success signal.

## 8. Outreach Log Template

Use this table privately or in a maintainer note:

| Date | Channel | Person or community | Segment | Link sent | Ask | Result | Follow-up |
| --- | --- | --- | --- | --- | --- | --- | --- |
| YYYY-MM-DD | direct | name | eval runner | contract doc | try runner | pending | none |

## 9. Maintenance Boundary

Promotion must not silently create new maintenance obligations.

Do not promise:

- npm publication
- VS Code Marketplace publication
- hosted playground operation
- managed model-provider runner
- stable cross-language conformance suite beyond existing evidence
- support for every graph database

If a reader wants one of those surfaces, route them through an issue and ask
whether they are willing to own implementation and ongoing maintenance.

