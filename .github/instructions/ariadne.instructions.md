---
applyTo: "**"
---

# Ariadne Workspace 指示

このファイルは、VS Code Copilot custom instructions 向けの薄いbridgeです。
repository guidance の正本は `AGENTS.md` です。
Ariadne AI workflow の正本は `.ariadne/` にあります。`.agents/skills/` は Codex Skill の入口です。

作業前に `AGENTS.md` を確認し、詳細なworkflow定義は `.ariadne/` から読んでください。Codex Skill 候補との対応は `.agents/skills/` を参照します。

## Ariadne Asset配置

- Workflow prompts: `.ariadne/prompts/*.prompt.md`
- Agent prompts: `.ariadne/agents/*.prompt.md`
- Schemas: `.ariadne/schemas/*.schema.json`
- Shared policies: `.ariadne/shared/*.md`
- Skill entrypoints: `.agents/skills/<workflow>/SKILL.md`

## 作業ルール

- 人間向けreport、docs、review、evidence、RAG source Markdownは既定で日本語にします。
- 実装前に Intent、Decision、Reason、Evidence、Risk、Human Gate を確認します。
- 副作用のある操作、公開、push、release、license判断は Human Gate の対象にします。
- workflow runtime は原則 `aiwfctl` または `runtime/ctl/ctl.py` 経由で呼び出します。
- `.ariadne/` の assets を `.github/` へ複製して正本を増やさないでください。
