# CogLang Announcement Kit v0.1

This file contains copy blocks for small-scale, targeted CogLang 1.1.5
promotion. Treat the text as a starting point. Edit each message for the
recipient and community before posting.

Do not copy-paste every block into multiple communities. Use one relevant
message per audience.

## 1. Short Descriptions

### 1.1 One Sentence

CogLang is a small auditable language for LLM-generated graph operations, with
canonicalization, validation, preflight effect and budget checks, and
provider-neutral generation evaluation.

### 1.2 One Paragraph

CogLang sits between a language model and a graph-backed system. Instead of
executing raw model output, a host can parse, canonicalize, validate, preflight,
hash, review, and replay the graph operation before trusting it. Version 1.1.5
adds AI-first developer-experience assets around provider-neutral generation
evaluation, constrained-generation grammar examples, TextMate syntax scaffolding,
Node.js companion examples, semantic-event audit, and local-first validation.

### 1.3 Boundary Statement

CogLang is not a general-purpose programming language, graph database,
full-agent framework, hosted runner, npm SDK, VS Code Marketplace extension, or
benchmark claim. It is an auditable IR-like language layer for LLM-produced
graph intent.

## 2. Direct Outreach Templates

### 2.1 External Generation-Eval Runner

Subject:

CogLang provider-neutral eval runner feedback?

Message:

Hi,

I am looking for feedback on CogLang's provider-neutral generation-eval file
contract. CogLang exports prompt request records, lets any external runner fill
JSON/JSONL response records, then scores the generated CogLang text with a
deterministic parser/canonicalizer/validator pipeline.

The useful part for you may be that it does not import OpenAI, Anthropic,
Ollama, or any provider SDK. Your existing runner can sit outside the project.

Relevant links:

- `CogLang_Generation_Eval_Request_Response_Contract_v0_1.md`
- `examples/generation_eval_offline_runner`

Concrete ask:

Would this file contract be enough for you to write a small runner, and what
field is missing?

### 2.2 Constrained-Generation User

Subject:

CogLang Lark/GBNF grammar feedback?

Message:

Hi,

CogLang is a small auditable language for LLM-generated graph operations. I
added companion Lark and GBNF grammar examples so local or constrained-generation
stacks can reduce malformed output before the normal parse/validate/preflight
checks.

Relevant link:

- `examples/grammar`

Concrete ask:

If you use GBNF, Lark, Outlines-style grammars, llama.cpp grammars, or a similar
tool, what would you need in the example to test CogLang generation cleanly?

### 2.3 Knowledge Graph Or Semantic Infrastructure Builder

Subject:

Auditable LLM graph-operation IR feedback?

Message:

Hi,

CogLang is aimed at cases where an LLM proposes graph queries or updates, but a
host needs to inspect, preflight, review, and replay the operation before
trusting it. The 1.1.5 source tree includes a semantic-event audit example that
converts external graph-intent JSONL into local audit records with canonical
expression text, expression hashes, preflight decisions, and derived actions.

Relevant link:

- `examples/semantic_event_audit`

Concrete ask:

Does this audit record shape match any graph-operation review workflow you have
seen, or is a different field more important?

### 2.4 Host Or Consumer Implementer

Subject:

CogLang host/consumer boundary feedback?

Message:

Hi,

CogLang keeps its host-runtime claims narrow. HRC v0.2 is frozen only for a
typed write-envelope evidence path, and companion examples show how a Node.js
consumer can read the schema pack and samples without importing the Python
runtime.

Relevant links:

- `CogLang_HRC_v0_2_Final_Freeze_2026_04_28.md`
- `CogLang_HRC_Companion_Asset_Classification_v0_1.md`
- `examples/node_host_consumer`

Concrete ask:

If you were implementing a consumer in another language, which part of the
boundary would be unclear first?

## 3. GitHub Discussion Or Issue Drafts

### 3.1 External Runner Invitation

Title:

External generation-eval runner feedback wanted

Body:

CogLang 1.1.5 includes a provider-neutral request/response file contract for
generation evaluation. The project exports request records, an external runner
produces response records, and CogLang scores the returned expression text
deterministically.

Useful starting points:

- `CogLang_Generation_Eval_Request_Response_Contract_v0_1.md`
- `examples/generation_eval_offline_runner`
- `coglang generation-eval --export-requests --request-format jsonl`

This issue is for feedback from anyone who wants to connect an external runner
without adding provider SDKs to CogLang itself.

Questions:

- Are the request fields sufficient?
- Are the response fields sufficient?
- Should runner metadata stay free-form?
- Which runner should be documented first as a companion example?

### 3.2 Semantic-Event Audit Feedback

Title:

Semantic-event audit example feedback wanted

Body:

CogLang source HEAD includes `examples/semantic_event_audit`, a no-provider
companion example that converts external graph-intent JSONL into local audit
records. It records canonical expression text, expression hash, preflight
decision, and a derived action.

This does not define a stable event schema, hosted runner, provider SDK
integration, transport envelope, or HRC expansion.

Feedback wanted:

- Is the audit record useful for graph-operation review?
- Which fields would a host need before queueing human review?
- Should future examples show batched review, rejection summaries, or replay?

### 3.3 Grammar Integration Feedback

Title:

Constrained-generation grammar example feedback wanted

Body:

CogLang includes companion Lark and GBNF grammar examples under
`examples/grammar`. They are intended for constrained-generation experiments and
do not replace CogLang's parser, validator, or preflight checks.

Feedback wanted:

- Which constrained-generation stack should the example target first?
- Is the grammar too strict, too permissive, or unclear?
- What minimal model-runner example would be useful without turning CogLang into
  a provider SDK integration?

## 4. Community Post Drafts

### 4.1 Technical Blog Or Personal Site

Title:

CogLang 1.1.5: an auditable language layer for LLM-generated graph operations

Body:

CogLang is a small language for LLM-generated graph queries and updates. The
design goal is not to let a model directly mutate a graph. The goal is to keep
the model's graph intent in a structured form that a host can parse,
canonicalize, validate, preflight, hash, review, and replay.

Version 1.1.5 focuses on AI-first developer-experience assets:

- provider-neutral generation-eval request/response files
- companion Lark and GBNF grammars for constrained-generation experiments
- semantic-event audit example for external graph-intent JSONL
- Node.js companion examples for host-runtime evidence
- local-first CI profiles to conserve GitHub Actions minutes

The project is intentionally narrow. It is not a graph database, general-purpose
agent framework, npm SDK, marketplace extension, hosted playground, or benchmark
claim. The best-fit use case is "LLM proposes graph operation; host inspects and
preflights before execution."

Repository:

https://github.com/jaysinailabs/coglang

### 4.2 Hacker News Candidate

Use only if the linked material is technically substantive and the account is a
normal participant, not only a promotion account.

Candidate title:

CogLang: an auditable language layer for LLM-generated graph operations

Submission URL:

https://github.com/jaysinailabs/coglang

Optional first comment:

I built this to explore a narrow problem: if an LLM proposes graph queries or
updates, how can a host inspect, canonicalize, preflight, and replay that intent
before trusting it? The current release includes provider-neutral generation
evaluation, companion grammar files, semantic-event audit, and a frozen narrow
typed write-envelope evidence path. It is not a graph database, full agent
framework, hosted runner, or npm/marketplace package.

### 4.3 Local LLM Or Constrained Generation Community

Title:

GBNF/Lark grammar examples for an auditable LLM graph-operation language

Body:

CogLang is a small auditable language for LLM-generated graph operations. I
added companion GBNF and Lark examples under `examples/grammar` so local model
and constrained-generation users can experiment with producing valid CogLang
text before running normal parse/validate/preflight checks.

The grammar files are companion examples, not the normative parser. I am looking
for feedback from people who use llama.cpp grammars, Lark, Outlines-style
generation, or similar stacks.

Repository:

https://github.com/jaysinailabs/coglang

### 4.4 Knowledge Graph Community

Title:

Auditable LLM-generated graph operations with preflight and semantic-event audit

Body:

CogLang is a small language layer for cases where an LLM proposes graph queries
or updates, but the host needs to inspect and preflight the operation before
execution. It has canonical expression text, validation, effect/budget
preflight, explicit capability boundaries, and a semantic-event audit example
for external graph-intent JSONL.

The project is not trying to replace native graph query languages. It is for the
boundary where graph operation intent is generated by a model and needs review.

Repository:

https://github.com/jaysinailabs/coglang

## 5. Short Social Posts

### 5.1 Short Technical Post

CogLang 1.1.5 is out. It is a small auditable language for LLM-generated graph
operations: parse, canonicalize, validate, preflight, review, hash, and replay
before trusting model-written graph intent.

New focus: provider-neutral eval files, grammar examples, semantic-event audit,
Node companion evidence, and local-first CI.

https://github.com/jaysinailabs/coglang

### 5.2 Contributor Invitation

If you build LLM eval runners, constrained-generation tooling, knowledge graph
systems, or host/runtime consumers, CogLang has a narrow contribution path:
external runner, grammar integration, semantic-event audit feedback, or host
consumer evidence. No platform publishing obligation required.

https://github.com/jaysinailabs/coglang

## 6. Posting Checklist

Before posting:

- Confirm the link works.
- Use one community-specific message, not every message.
- Include one limitation or non-goal.
- Include one concrete ask.
- Do not ask for upvotes, stars, or reposts.
- Do not imply npm, Marketplace, playground, or SDK support exists.
- Record the post in the outreach log from
  `CogLang_Small_Scale_Promotion_Plan_v0_1.md`.

After posting:

- Answer technical questions directly.
- Convert repeated confusion into docs or issues.
- Do not debate out-of-scope platform requests; route them to contribution
  ownership if the requester wants to maintain them.
- Wait before posting to another broad community.

