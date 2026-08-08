---
name: system-integration-quality
description: Verify that generated or modified code integrates safely into an existing target system, including SDKs, external APIs, cloud services, payments, databases, async processing, UI, batch jobs, monitoring, infrastructure settings, tests, operation model, evidence layout, and Knowledge handoff. Use when the user selects /system-integration-quality or asks for integration quality checks.
---

# System Integration Quality

この Skill は、Codex が `/system-integration-quality` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/system-integration-quality.prompt.md`
- `docs/workflows/system-integration-quality.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
