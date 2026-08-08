---
name: knowledge-capture
description: Finalize a completed corrective action issue by generating PR material, checking docs evidence placement, extracting RAG/docs candidates, and preparing archive readiness without changing implementation. Use when the user selects /knowledge-capture or asks to run finalization and knowledge recovery for work/issue-XXX.
---

# Knowledge Capture

この Skill は、Codex が `/knowledge-capture` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/knowledge-capture.prompt.md`
- `docs/workflows/knowledge-capture.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
