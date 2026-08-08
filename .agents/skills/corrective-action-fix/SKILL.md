---
name: corrective-action-fix
description: Create a corrective action report for a specified GitHub repository and branch, store the base branch under a work branch folder, build/load RAG, create a GitHub Issue, create a separate work/issue-XXX folder with feature/issue-XXX branch, implement fixes, test, request human startup/integration approval, then push. Use when the user selects /corrective-action-fix or asks to move from improvement report creation into corrective implementation.
---

# Corrective Action Fix

この Skill は、Codex が `/corrective-action-fix` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/corrective-action-fix.prompt.md`
- `docs/workflows/corrective-action-fix.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
