# Skill Discovery

このrepoでは、VS Code / GitHub Copilot Chat の slash prompt と、Codex Skill の候補表示を分けて考えます。

## VS Code Prompt Discovery

VS Code / GitHub Copilot Chat の `/` 候補に出すpromptは、次に置きます。

```text
.github/prompts/*.prompt.md
```

代表例:

```text
.github/prompts/requirement-discovery.prompt.md
.github/prompts/docs-sync.prompt.md
.github/prompts/corrective-action-fix.prompt.md
.github/prompts/corrective-action-report.prompt.md
.github/prompts/rag-build.prompt.md
.github/prompts/rag-load.prompt.md
.github/prompts/robotics-new-system.prompt.md
.github/prompts/robotics-feature-maintenance.prompt.md
```

候補に出ない場合は、`C:\github\ariadne-ai-workflow-platform` をworkspaceとして開いているか確認します。

## Codex Skill Discovery

このrepositoryのSkill source of truthは次です。

```text
C:\github\ariadne-ai-workflow-platform\skills
```

ただし、repo-local `skills/` に置くだけではCodex候補に出ない場合があります。

Codex候補として表示するには、Codexが探索するlocal skill directoryからも見える必要があります。

```text
C:\Users\User\.codex\skills\<skill-name>
  -> C:\github\ariadne-ai-workflow-platform\skills\<skill-name>
```

この接続は、NTFS Junctionで行います。

## Skill Index

Skillとslash commandの対応は次にまとめます。

```text
skills/skill-index.json
```

新しいworkflowを追加した場合は、次を揃えます。

- `skills/<skill-name>/SKILL.md`
- `.github/prompts/<command>.prompt.md`
- `skills/skill-index.json`
- 必要に応じて `C:\Users\User\.codex\skills` のJunction
- `docs/workflows/README.md`

## Reload

候補が更新されない場合は、Codex / VS Code のreloadまたは新sessionが必要な場合があります。
