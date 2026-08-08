---
name: github-knowledge-maintenance
description: Maintain a GitHub repository as a long-lived knowledge asset without erasing Git history. Use when the user selects /github-knowledge-maintenance or asks to preserve GitHub Issues, PRs, docs, CARs, commit-source, commit-message, semantic-subject, Knowledge DB, or RAG candidates as reusable repository knowledge.
---

# Github Knowledge Maintenance

この Skill は、Codex が `/github-knowledge-maintenance` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/github-knowledge-maintenance.prompt.md`
- `docs/workflows/github-knowledge-maintenance.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
