# Ariadne Copilot Instructions

このファイルは VS Code Copilot Chat 向けのbridgeです。
Ariadne AI workflow の source of truth は `.ariadne/` と `skills/` にあります。

作業前に `AGENTS.md` をrepository guidanceとして確認してください。

## Ariadne Asset Locations

- Workflow prompt: `.ariadne/prompts/*.prompt.md`
- Specialist agent prompt: `.ariadne/agents/*.prompt.md`
- Structured contract: `.ariadne/schemas/*.schema.json`
- Shared policy: `.ariadne/shared/*.md`
- Codex Skill entrypoint: `skills/<workflow>/SKILL.md`

`.github/` 配下は GitHub native files と Copilot integration bridge の置き場です。
`.github/prompts/` にあるprompt fileは薄い入口として扱い、workflow本体を `.ariadne/prompts/` から読んでください。

## Working Rules

- 人間向けreport、docs、review、evidence、RAG source Markdownは既定で日本語にします。
- 実装前に Intent、Decision、Reason、Evidence、Risk、Human Gate を確認します。
- 副作用のある操作、公開、push、release、license判断は Human Gate の対象にします。
- workflow runtime は原則 `aiwfctl` または `runtime/ctl/ctl.py` 経由で呼び出します。
- `.ariadne/` の assets を `.github/` へ複製して source of truth を増やさないでください。
