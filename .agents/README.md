# Codex Agent Bridge

この directory は、Codex 向けの repo-local bridge です。

Source of truth はこの file ではなく、次にあります。

- Project instructions: `AGENTS.md`
- Workflow prompts: `.ariadne/prompts/*.prompt.md`
- Agent prompts: `.ariadne/agents/*.prompt.md`
- Schemas: `.ariadne/schemas/*.schema.json`
- Shared policies: `.ariadne/shared/*.md`
- Repo-local Codex Skills: `.agents/skills/<skill-name>/SKILL.md`

## Rules

- Workflow 定義、Safety rule、Human Gate、artifact contract をこの file に複製しないでください。
- Codex Skill の入口は `.agents/skills/` に置いてください。
- Skill の `SKILL.md` には discovery 用の `name` と `description` を必ず置いてください。
- 詳細な workflow 判断は `.ariadne/` と `AGENTS.md` を読んでください。

## Discovery Notes

Codex は repo-local Skill として `.agents/skills/` を探索します。

既存 session で Skill 候補が更新されない場合は、新しい Codex session で確認してください。CLI 系の候補表示を使う場合は、必要に応じて `/skills reload` を実行します。
