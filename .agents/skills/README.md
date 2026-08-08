# Codex Skill Entrypoints

この directory は、Ariadne workflow を Codex の Skill 候補として見せるための repo-local entrypoint です。

各 `SKILL.md` は discovery 用の `name` / `description` と、正本への routing だけを持ちます。Workflow 定義、phase、runtime command、artifact contract、Human Check gate はここに複製しません。

## 正本

- Project instructions: `AGENTS.md`
- Workflow prompts: `.ariadne/prompts/*.prompt.md`
- Workflow docs: `docs/workflows/*.md`
- Shared rules: `.ariadne/shared/*.md`
- Shared schemas: `.ariadne/schemas/*.schema.json`
- Skill index: `.agents/skills/skill-index.json`

## 運用ルール

- Task action の前に、該当 Skill が示す prompt と docs を読んでください。
- Agent 間共有 artifact を作成または検証する場合は、`.ariadne/schemas/*.schema.json` を使ってください。
- GitHub Issue、branch、push、install、RAG公開、field trial、release などの外部副作用は、参照先 workflow が許可し、必要な Human Check が満たされるまで実行しないでください。
- 人間向けの report、review note、evidence、handoff Markdown は既定で日本語にしてください。

## Discovery

Codex は repo-local Skill として `.agents/skills/` を探索します。旧運用の user-local Junction は通常不要です。

既存 session で候補が更新されない場合は、新しい Codex session で確認してください。CLI 系の候補表示を使う場合は、必要に応じて `/skills reload` を実行します。
