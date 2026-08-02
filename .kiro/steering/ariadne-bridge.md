---
inclusion: always
---

# Ariadne Kiro Bridge

このファイルは、Kiro から Ariadne workspace を扱うための薄い steering bridge です。

Ariadne AI workflow の source of truth は、このファイルではなく次にあります。

- Repository guidance: `AGENTS.md`
- Workflow prompts: `.ariadne/prompts/*.prompt.md`
- Agent prompts: `.ariadne/agents/*.prompt.md`
- Schemas: `.ariadne/schemas/*.schema.json`
- Shared policies: `.ariadne/shared/*.md`
- Skill entrypoints: `skills/<workflow>/SKILL.md`

## 作業ルール

- 作業前に `AGENTS.md` を確認してください。
- 詳細な workflow 定義は `.ariadne/` と `skills/` から読んでください。
- 人間向け report、docs、review、evidence、RAG source Markdown は既定で日本語で書いてください。
- 実装前に Intent、Decision、Reason、Evidence、Risk、Human Gate を確認してください。
- 公開、push、release、license判断、外部環境への副作用がある操作は Human Gate 対象として扱ってください。
- runtime は原則として `aiwfctl` または `runtime/ctl/ctl.py` 経由で呼び出してください。
- `.ariadne/` の assets をこのファイルへ複製して source of truth を増やさないでください。

## Ariadne Asset

```text
.ariadne/
  agents/      role-based Agent prompts
  prompts/     workflow prompts
  schemas/     JSON Schema contracts
  shared/      shared policies and handoff guidance

skills/        workflow skill entrypoints
templates/     reusable artifact templates
runtime/       workflow runtime implementation
docs/          human-readable documentation
work/          generated or project-specific artifacts
```
