---
name: ariadne-new-system
description: Start the Ariadne AI Workflow for creating a new target system, runtime, remote operation system, device integration, or architecture-level system launch. Use when the user selects /ariadne-new-system or asks to begin an Ariadne New System flow from a completed requirement document in work/requirements/.
---

# Ariadne New System

この Skill は、Codex が `/ariadne-new-system` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/ariadne-new-system.prompt.md`
- `docs/workflows/ariadne-new-system.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
