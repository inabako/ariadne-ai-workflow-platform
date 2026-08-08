# Skill Discovery

この repository では、VS Code / GitHub Copilot Chat の slash prompt、Codex Skill、`aiwfctl help` の候補表示を分けて扱います。

## VS Code Prompt Discovery

VS Code / GitHub Copilot Chat の `/` 候補に出る prompt は次に置きます。

```text
.ariadne/prompts/*.prompt.md
```

代表例:

```text
.ariadne/prompts/requirement-discovery.prompt.md
.ariadne/prompts/docs-sync.prompt.md
.ariadne/prompts/corrective-action-fix.prompt.md
.ariadne/prompts/corrective-action-report.prompt.md
.ariadne/prompts/github-knowledge-maintenance.prompt.md
.ariadne/prompts/rag-build.prompt.md
.ariadne/prompts/rag-load.prompt.md
.ariadne/prompts/ariadne-new-system.prompt.md
.ariadne/prompts/ariadne-feature-maintenance.prompt.md
```

候補に出ない場合は、この repository を VS Code workspace として開いていることを確認し、Copilot Chat / VS Code window を reload します。

## Codex Skill Discovery

この repository の Codex Skill source of truth は次です。

```text
.agents/skills/
```

Codex は repo-local skill として `.agents/skills` を探索します。したがって、この repository を Codex session の working directory または repo root として開けば、`$requirement-discovery` などの skill 候補として検出されます。

`.agents/README.md` は Codex 向けの薄い bridge です。Workflow 定義や Safety rule は複製せず、`AGENTS.md`、`.ariadne/`、`.agents/skills/` への入口だけを置きます。

旧運用では `C:\Users\User\.codex\skills` から repository の `skills/` へ NTFS Junction を張っていました。現在は `.agents/skills` を Git 管理するため、通常は Junction は不要です。

既存 session で候補に出ない場合は、新しい Codex session で確認します。CLI 系の skill 候補を使う場合は、必要に応じて `/skills reload` 後に `/skills info requirement-discovery` で確認します。

## aiwfctl Help Discovery

`aiwfctl help` の候補は workflow help registry から表示します。

```powershell
aiwfctl help search github knowledge
aiwfctl help show /github-knowledge-maintenance
```

source は次です。

```text
db/registries/registry.duckdb
```

`aiwfctl help` は Codex Skill discovery とは別経路です。Skill path を変更した場合は、registry template と read model の同期も確認してください。

## Skill Index

Skill、slash command、prompt file の対応は次にまとめます。

```text
.agents/skills/skill-index.json
```

新しい workflow を追加した場合は、次を揃えます。

- `.agents/skills/<skill-name>/SKILL.md`
- `.ariadne/prompts/<command>.prompt.md`
- `.agents/skills/skill-index.json`
- `templates/registries/workflow_help.json`
- `db/registries/registry.duckdb`
- `docs/workflows/README.md`

## Reload

候補が更新されない場合は、候補機構ごとに reload 先が変わります。

- VS Code / GitHub Copilot Chat: VS Code window reload
- Codex Skill: 新しい Codex session で確認
- Copilot CLI Skill: `/skills reload`
- `aiwfctl help`: `aiwfctl help search <keyword>` で registry を直接確認
