---
name: requirement-discovery
description: Create a completed target-system requirement document from a human bullet-list draft in work/requirements/draft by inspecting it, asking blocking clarification questions, using optional RAG context, preparing a review draft, and saving the final document to work/requirements only after human OK. Use when the user selects /requirement-discovery or asks to create requirements from draft bullets.
---

# Requirement Discovery

この Skill は、Codex が `/requirement-discovery` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/requirement-discovery.prompt.md`
- `docs/workflows/requirement-discovery.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
