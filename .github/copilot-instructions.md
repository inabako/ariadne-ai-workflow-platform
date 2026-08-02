# Ariadne Copilot Instructions

このファイルは、VS Code Copilot Chat 向けの薄い bridge です。

Ariadne AI workflow の source of truth は、次の場所にあります。

- Repository guidance: `AGENTS.md`
- Workflow prompts: `.ariadne/prompts/*.prompt.md`
- Agent prompts: `.ariadne/agents/*.prompt.md`
- Schemas: `.ariadne/schemas/*.schema.json`
- Shared policies: `.ariadne/shared/*.md`
- Skill entrypoints: `skills/<workflow>/SKILL.md`

`.github/` 配下には GitHub native files と Copilot integration bridge だけを置きます。
`.github/prompts/` の prompt file は VS Code Copilot Chat の入口であり、workflow 本体ではありません。

## 作業ルール

- 人間向けの report、docs、review、evidence、RAG source Markdown は既定で日本語にします。
- 実装前に Intent、Decision、Reason、Evidence、Risk、Human Gate を確認します。
- 公開、push、release、license 判断など副作用のある操作は Human Gate 対象として扱います。
- workflow runtime は原則 `aiwfctl` または `runtime/ctl/ctl.py` 経由で呼び出します。
- `.ariadne/` の assets を `.github/` へ複製して source of truth を増やさないでください。
