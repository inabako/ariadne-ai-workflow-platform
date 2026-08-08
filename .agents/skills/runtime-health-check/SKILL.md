---
name: runtime-health-check
description: Check the Ariadne AI Workflow Platform runtime itself, including pytest, workflow doctor checks, aiwfctl doctor, Context First test evidence, and Japanese Markdown output quality. Use when the user selects /runtime-health-check or asks to diagnose Ariadne runtime health.
---

# Runtime Health Check

この Skill は、Codex が `/runtime-health-check` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/runtime-health-check.prompt.md`
- `docs/workflows/runtime-health-check.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
