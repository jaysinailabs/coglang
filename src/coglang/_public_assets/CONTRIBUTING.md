# Contributing to CogLang

CogLang accepts small, evidence-first changes that keep the language surface,
host boundary, package artifacts, and public documentation aligned.

Start here:

- Read [CogLang_Contribution_Guide_v0_1.md](CogLang_Contribution_Guide_v0_1.md)
  for contribution boundaries and review expectations.
- Check [ROADMAP.md](ROADMAP.md) to see whether the change matches the current
  direction.
- Check the latest package release notes before assuming a source-HEAD command
  is available from PyPI.

Choosing where to discuss a change:

- Use GitHub Discussions for exploratory design questions, early use-case
  reports, and "would this fit CogLang?" conversations.
- Use an issue when the proposal is actionable, especially for an external
  host, consumer, adapter, executor, or companion example.
- Use a draft PR when there is already a branch, fixture, or document sketch
  and early review would help before full validation evidence exists.
- Use a focused governance proposal before implementation when the change would
  expand language semantics, promote a reserved operator, or change HRC frozen
  scope.

Before opening a pull request:

- Use a local-first validation flow to conserve GitHub Actions minutes. Batch
  small commits locally, run the relevant checks in your checkout, and push only
  when the branch is ready for review or remote evidence.
- For a local simulation of the maintainer-triggered workflow, run
  `python scripts/local_ci.py --profile quick` during normal iteration,
  `python scripts/local_ci.py --profile ci --format json` before review, and
  `python scripts/local_ci.py --profile package` before release preparation.
  Paste the `ci` profile JSON summary, or a concise equivalent with the
  `ok`, `failed_step`, and validation date fields, into the PR description.
- If you need early remote discussion before CI evidence is useful, open a draft
  PR and keep iterating locally. The `ci` workflow is manual and should be run
  by a maintainer only when the PR is ready for merge review, release
  preparation, or platform-specific remote evidence.
- Keep the scope narrow and state the validation commands you ran.
- Use the pull request template in
  [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md).
- Run `coglang release-check` for release-facing or public documentation
  changes.
- Run `coglang smoke` for broad package and CLI smoke coverage when practical.
- If you change exact public documentation mirrors in a source checkout, run
  `coglang public-assets --sync` and then `coglang public-assets`.

For the first external host, consumer, adapter, or executor contribution:

- Open an issue with
  [.github/ISSUE_TEMPLATE/external_host_consumer.yml](.github/ISSUE_TEMPLATE/external_host_consumer.yml)
  before a large implementation PR.
- Use the first external host or consumer checklist in
  [CogLang_Contribution_Guide_v0_1.md](CogLang_Contribution_Guide_v0_1.md#41-first-external-host-or-consumer-pr-checklist).
- Keep host policy separate from language-core semantics.
- Do not present companion schema material as a normative JSON Schema contract.
- Do not expand HRC v0.2 frozen scope without a focused governance review.

Public-facing canonical docs are English-first. Chinese translations may be
added as companion files, but the English document, executable conformance
suite, and implementation tests take precedence if they disagree.
