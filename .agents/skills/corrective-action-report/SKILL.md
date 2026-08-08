---
name: corrective-action-report
description: Analyze the current state of a user-specified repository and branch, identify improvement points, risks, missing documentation, test gaps, architecture concerns, and workflow opportunities, then write a corrective action report for RAG accumulation. Use when the user selects /corrective-action-report or asks for a current improvement report, corrective action report, repository health review, or cross-project improvement findings.
---

# Corrective Action Report

この Skill は、Codex が `/corrective-action-report` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/corrective-action-report.prompt.md`
- `docs/workflows/corrective-action-report.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
