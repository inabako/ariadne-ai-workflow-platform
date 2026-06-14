# VSCode Environment

このrepositoryは、VSCode Workspace as Codeとして `.vscode` とworkspace fileを持ちます。

目的は、AI Agentと人間が同じterminal、task、debug、preflight、evidence flowを再現できるようにすることです。

## Files

| File | Purpose |
| --- | --- |
| `.vscode/settings.json` | terminal profile、encoding、Markdown、Python基本設定 |
| `.vscode/tasks.json` | workflow entry task、preflight、JSON check、runtime smoke |
| `.vscode/launch.json` | Python runtime helper debug launch |
| `.vscode/extensions.json` | recommended VSCode extensions |
| `.vscode/intent-driven-robotics-ai-workflow.code-workspace` | workspace entry file。`path: ".."` でrepository rootを開く |

## Terminal Profiles

| Profile | Role |
| --- | --- |
| `Dispatcher PowerShell` | workflow repository rootでCodex / AI workflowを調整する |
| `Software Workflow PowerShell` | `uv run python`、runtime helper、RAG script、testを実行する |
| `MSYS2 Localty MINGW64` | Localty GUI / GStreamer / PyQt smoke check用 |
| `IaC Workflow PowerShell` | Docker / Go / gateway / IaC作業用 |
| `Docker Test PowerShell` | Docker Desktop検証用 |
| `Evidence PowerShell` | logs、reports、human-check notes用 |

Default terminalは `Dispatcher PowerShell` です。

## Task Labels

Workflow entrypoint tasks:

```text
workflow:requirement-discovery
workflow:robotics-new-system
workflow:robotics-new-system-iac
workflow:robotics-feature-maintenance
workflow:realtime-iac
workflow:corrective-action-report
workflow:corrective-action-fix
workflow:docs-sync
workflow:github-knowledge-maintenance
workflow:vscode-environment
workflow:knowledge-capture
workflow:rag-build
workflow:rag-load
```

Support / test tasks:

```text
workflow:vscode-open-questions
workflow:vscode-preflight
test:vscode-json
test:vscode-helper-help
test:msys2-localty-smoke
test:docker-version
test:go-version
```

slash command workflow taskは、Codex commandとSkill pathを表示します。task単体ではrepository stateを変更しません。

Workflow taskとsmoke-check taskは、`runtime/workflow/vscode_task_runner.py` を通じてVSCode `process` taskとして実行します。これにより、長いinline PowerShell command、nested PowerShell startup、`ExecutionPolicy Bypass` patternを避け、AMSI / security-product heuristicに引っかかりにくくします。

`test:vscode-json` はinline `python -c` ではなく `runtime/workflow/validate_vscode_workspace.py` を呼び出します。PowerShell quotingの崩れを避けるためです。

`workflow:vscode-preflight` と `test:go-version` は、Go確認前にPython task runner内でMachine/User PATHを再読込します。VSCode起動後にGoをinstallした場合の古いPATH問題を避けます。

## Preflight

実行例:

```powershell
uv run python runtime/environment/preflight.py `
  --profile vscode-environment `
  --work-id vscode-environment `
  --source-dir C:\github\intent-driven-robotics-ai-workflow
```

reportは次へ保存します。

```text
work/vscode-environment/process-report/
```

## Evidence

VSCode environment evidenceは次へ保存します。

```text
work/vscode-environment/test-evidence/
```

command resultとhuman-check notesは `workspace-test.md` に記録します。

## Knowledge Finalization

再利用可能なVSCode environment knowledgeは、まずhuman-review可能なMarkdownへ保存します。

```text
rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

Human approval後、最終的なUUID名RAG knowledge JSONへnormalizeします。

```powershell
uv run python runtime/rag/normalize_documents.py `
  --source-dir rag/workspace-environment `
  --output-dir rag/normalized `
  --document-type workspace-environment-pattern
```

最終着地:

```text
rag/normalized/<uuid>.json
```

Chunk JSON、indexes、embeddings、retrieval packsは派生artifactです。

## Human Check

VSCodeでworkspaceを開いた後、次を確認します。

1. 各terminal profileを開く。
2. repository rootで起動することを確認する。
3. `test:vscode-json` を実行する。
4. `workflow:vscode-preflight` を実行する。
5. workflow label taskを1つ実行し、期待するCodex Skill commandが表示されることを確認する。
6. UI観察結果を `work/vscode-environment/test-evidence/workspace-test.md` に記録する。

## Guardrails

- `.vscode` や `.code-workspace` にsecretを保存しない。
- 既存 `.vscode` 変更は、置き換え承認が無い限りadditiveにする。
- machine-specific valuesはdocument化し、review可能にする。
- inline PowerShellや `python -c` より、VSCode `process` taskとrepo-local helper scriptを優先する。
- workspace taskやgenerated install planに `ExecutionPolicy Bypass` を追加しない。
- CLIで証明できないVSCode UI behaviorはhuman-check evidenceとして扱う。
