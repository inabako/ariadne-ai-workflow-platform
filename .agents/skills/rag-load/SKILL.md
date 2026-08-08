---
name: rag-load
description: Load prior knowledge from the Ariadne AI Workflow file-based RAG before development work. Use when the user selects /rag-load, asks to read RAG, search RAG, load RAG context, retrieve prior corrective action reports, prepare context before development flow, or run parallel RAG retrieval and compression.
---

# Rag Load

この Skill は、Codex が `/rag-load` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/rag-load.prompt.md`
- `docs/workflows/rag-build-load.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
