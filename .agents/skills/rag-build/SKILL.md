---
name: rag-build
description: Build or refresh the Ariadne AI Workflow file-based RAG artifacts from Markdown reports. Use when the user selects /rag-build, asks to create RAG, update RAG, accumulate corrective action reports into RAG, normalize reports, chunk documents, build indexes, or create local embeddings.
---

# Rag Build

この Skill は、Codex が `/rag-build` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/rag-build.prompt.md`
- `docs/workflows/rag-build-load.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
