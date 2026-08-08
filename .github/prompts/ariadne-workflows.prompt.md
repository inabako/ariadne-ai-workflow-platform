---
description: Ariadne workflow assets under .ariadne を参照して作業を開始する
---

# Ariadne Workflow Bridge

この prompt は、VS Code Copilot Chat の `/` prompt 候補に表示するための bridge です。

workflow 本体は `.ariadne/prompts/`、agent prompt は `.ariadne/agents/`、schema は `.ariadne/schemas/` にあります。
作業前に `AGENTS.md` と `.github/copilot-instructions.md` の方針を確認してください。

## References

- #file:../../AGENTS.md
- #file:../../.agents/skills/skill-index.json
- #file:../../docs/workflows/README.md
- #file:../../docs/reference/skill-discovery.md
- `.ariadne/prompts/`
- `.ariadne/agents/`
- `.ariadne/schemas/`
- `.ariadne/shared/`

## Task

ユーザーの依頼内容から該当 workflow を選び、必要な `.ariadne/prompts/<workflow>.prompt.md` と `docs/workflows/<workflow>.md` を読んでください。
Codex Skill 候補との対応が必要な場合だけ、`.agents/skills/<workflow>/SKILL.md` を入口として参照してください。
該当 workflow が明確でない場合は、候補を短く提示して確認してください。
