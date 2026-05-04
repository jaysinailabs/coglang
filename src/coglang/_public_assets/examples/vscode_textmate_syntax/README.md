# CogLang VS Code Syntax Companion

**Status**: companion example material
**Scope**: editor highlighting only, not a parser, not a validator, and not a
language server

This directory contains a minimal VS Code/TextMate syntax-highlighting scaffold
for CogLang M-expression files.

It is not published to the VS Code Marketplace, not a normative grammar, and
not part of the frozen `v1.1.0` language contract. The authoritative checks
remain:

1. `coglang.parser.parse`
2. `coglang.validator.valid_coglang`
3. `coglang preflight`
4. the public specification and conformance tests

## Local Use

From this directory, copy or symlink the folder into your VS Code extensions
development workflow, or run an Extension Development Host against it.

The scaffold contributes:

- `.coglang` file association
- bracket and string-pair configuration
- TextMate scopes for strings, numbers, variables, dictionary punctuation, and
  M-expression heads

Use [samples/basic.coglang](samples/basic.coglang) as a quick visual check.

## Boundary

- This is companion DX material for local editor experimentation.
- It is not an LSP, semantic analyzer, formatter, renderer, or online
  playground.
- It does not replace parse, validation, preflight, or host capability checks.
- It does not expand HRC v0.2 frozen scope.
