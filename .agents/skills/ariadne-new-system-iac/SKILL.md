---
name: ariadne-new-system-iac
description: Run the integrated Ariadne New System plus realtime IaC workflow. Use when the user selects /ariadne-new-system-iac or asks to create a new target system and then generate validated Shared Artifacts for the realtime IaC workflow.
---

# Ariadne New System Iac

この Skill は、Codex が `/ariadne-new-system-iac` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/ariadne-new-system-iac.prompt.md`
- `docs/workflows/ariadne-new-system-iac.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
