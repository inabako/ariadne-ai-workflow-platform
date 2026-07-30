---
description: Ariadne workflow assets under .ariadne を参照して作業を開始する
---

# Ariadne Workflow Bridge

このpromptは VS Code Copilot Chat の `/` prompt候補向けbridgeです。
workflow本体は `.ariadne/prompts/`、agent promptは `.ariadne/agents/`、schemaは `.ariadne/schemas/` にあります。

まず `AGENTS.md` と `.github/copilot-instructions.md` の方針を優先してください。

## References

- #file:../../AGENTS.md
- #file:../../skills/skill-index.json
- #file:../../docs/workflows/README.md
- #file:../../docs/reference/skill-discovery.md
- `.ariadne/prompts/`
- `.ariadne/agents/`
- `.ariadne/schemas/`
- `.ariadne/shared/`

## Task

ユーザーの依頼内容から該当workflowを選び、必要な `.ariadne/prompts/<workflow>.prompt.md` と `skills/<workflow>/SKILL.md` を読んでください。
該当workflowが曖昧な場合は、候補を短く提示して確認してください。
