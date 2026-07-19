# Skill Discovery

このrepoでは、VS Code / GitHub Copilot Chat の slash prompt、Codex Skill、`aiwfctl help` の候補表示を分けて扱います。

## VS Code Prompt Discovery

VS Code / GitHub Copilot Chat の `/` 候補に出すpromptは次に置きます。

```text
.github/prompts/*.prompt.md
```

代表例:

```text
.github/prompts/requirement-discovery.prompt.md
.github/prompts/docs-sync.prompt.md
.github/prompts/corrective-action-fix.prompt.md
.github/prompts/corrective-action-report.prompt.md
.github/prompts/github-knowledge-maintenance.prompt.md
.github/prompts/rag-build.prompt.md
.github/prompts/rag-load.prompt.md
.github/prompts/ariadne-new-system.prompt.md
.github/prompts/ariadne-feature-maintenance.prompt.md
```

GitHub Knowledge Maintenance の prompt command は次です。

```text
/github-knowledge-maintenance
```

候補に出ない場合は、`C:\github\ariadne-ai-workflow-platform` をVS Code workspaceとして開いていることを確認し、Copilot Chat / VS Code windowをreloadします。

## Codex Skill Discovery

このrepositoryのSkill source of truthは次です。

```text
C:\github\ariadne-ai-workflow-platform\skills
```

ただし、repo-local `skills/` に置くだけではCodex Skill候補に出ない場合があります。Codex候補として表示するには、Codexが探索するlocal skill directoryから参照できる必要があります。

```text
C:\Users\User\.codex\skills\<skill-name>
  -> C:\github\ariadne-ai-workflow-platform\skills\<skill-name>
```

現在の標準接続はNTFS Junctionです。

GitHub Knowledge Maintenance のCodex Skillは次を確認します。

```text
C:\Users\User\.codex\skills\github-knowledge-maintenance
  -> C:\github\ariadne-ai-workflow-platform\skills\github-knowledge-maintenance
```

既存セッションで候補に出ない場合は、新しいCodexセッションで確認します。Copilot CLI系のskill候補を使う場合は、`/skills reload` 後に `/skills info github-knowledge-maintenance` で確認します。

## aiwfctl Help Discovery

`aiwfctl help` の候補は、workflow help registryから表示します。

```powershell
aiwfctl help search github knowledge
aiwfctl help show /github-knowledge-maintenance
```

sourceは次です。

```text
db/registries/registry.duckdb
```

`/github-knowledge-maintenance` は `aiwfctl help search github knowledge` と `aiwfctl help show /github-knowledge-maintenance` の両方で確認できます。

## Skill Index

Skill、slash command、prompt fileの対応は次にまとめます。

```text
skills/skill-index.json
```

新しいworkflowを追加した場合は、次を揃えます。

- `skills/<skill-name>/SKILL.md`
- `.github/prompts/<command>.prompt.md`
- `skills/skill-index.json`
- `db/registries/registry.duckdb`
- `docs/workflows/README.md`
- 必要に応じて `C:\Users\User\.codex\skills` のJunction

## Reload

候補が更新されない場合は、どの候補機構を見ているかでreload先が変わります。

- VS Code / GitHub Copilot Chat: VS Code window reload
- Codex Skill: 新しいCodexセッションで確認
- Copilot CLI Skill: `/skills reload`
- `aiwfctl help`: `aiwfctl help search <keyword>` でregistryを直接確認
