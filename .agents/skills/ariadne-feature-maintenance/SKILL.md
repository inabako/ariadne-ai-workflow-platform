---
name: ariadne-feature-maintenance
description: Start the Ariadne AI Workflow for adding a new feature to an existing target system or performing maintenance development such as bug fix, hardware replacement, network change, deployment change, field issue response, or operational improvement. Use when the user selects /ariadne-feature-maintenance or asks to begin feature or maintenance work from a completed requirement document in work/requirements/.
---

# Ariadne Feature Maintenance

この Skill は、Codex が `/ariadne-feature-maintenance` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/ariadne-feature-maintenance.prompt.md`
- `docs/workflows/ariadne-feature-maintenance.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
