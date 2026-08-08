---
name: docs-sync
description: Compare implementation and docs on a target branch, store docs drift analysis as JSON, create a GitHub Issue, create feature/issue-XXX from the target branch, update docs only, push after human approval, then prepare RAG capture and archive. Use when the user selects /docs-sync or asks to synchronize repository docs with implementation.
---

# Docs Sync

この Skill は、Codex が `/docs-sync` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/docs-sync.prompt.md`
- `docs/workflows/docs-sync.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
