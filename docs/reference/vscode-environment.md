# VSCode Environment

このrepositoryは、VSCode Workspace as Codeとして `.vscode` を持ちます。

目的は、AI Agentと人間が同じterminal、task、debug、preflight、evidence flowを再現できるようにすることです。

## Modes

`/vscode-environment` は3つのmodeで動きます。

| Mode | Trigger | Target | Draft |
| --- | --- | --- | --- |
| self-provision | `/vscode-environment` | current repository | 不要 |
| target-workspace | `/vscode-environment <target-workspace-path>` | 指定workspace | 任意 |
| custom-design | `--custom-design` または特殊要件あり | current repositoryまたは指定workspace | 任意。複雑な設計意図の補助 |

self-provision modeでは、このrepositoryの `.vscode`、`runtime/windows-script`、`aiwfctl`、workflow registry、docs、testsを読んで、AI workflowを実行しやすい環境へ整えます。

custom-design modeでは、terminal構成、Docker、extension policy、launch設定、multi-root、personal/local-only pathなど、repo evidenceだけでは判断できない内容をHuman質問または任意draftで補います。

## Files

| File | Purpose |
| --- | --- |
| `.vscode/settings.json` | terminal profile、encoding、Markdown、Python基本設定 |
| `.vscode/tasks.json` | workflow entry task、preflight、JSON check、runtime smoke |
| `.vscode/launch.json` | Python runtime helper debug launch |
| `.vscode/extensions.json` | recommended VSCode extensions |

## Terminal Profiles

| Profile | Role |
| --- | --- |
| `Dispatcher PowerShell` | workflow repository rootでCodex / AI workflowを調整する |
| `Software Workflow PowerShell` | `uv run --project runtime python`、runtime helper、RAG script、testを実行する |
| `MSYS2 Localty MINGW64` | Localty GUI / GStreamer / PyQt smoke check用 |
| `IaC Workflow PowerShell` | Docker / Go / gateway / IaC作業用 |
| `Docker Test PowerShell` | Docker Desktop検証用 |
| `Evidence PowerShell` | logs、reports、human-check notes用 |

Default terminalは `Dispatcher PowerShell` です。

## Repo-local Tools PATH

`.vscode/settings.json` は、repo-local command toolをVSCode統合ターミナルから直接呼べるように、Windows terminal PATHへtools directoryを追加します。

このrepositoryでは `runtime/windows-script/aiwfctl.cmd` を使うため、次を設定します。

```json
{
  "terminal.integrated.env.windows": {
    "Path": "${workspaceFolder}\\runtime\\windows-script;${env:Path}",
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
    "AIWF_TEXT_ENCODING": "utf-8"
  }
}
```

この設定により、VSCode統合ターミナルでは次のように呼び出せます。

```powershell
aiwfctl help list
```

既に開いているterminalにはPATH変更が反映されません。terminalを閉じて開き直すか、現在のPowerShellで次を実行します。

```powershell
$env:Path = "$PWD\runtime\windows-script;$env:Path"
```

## UTF-8 First

このrepositoryは、日本語Markdown、prompt、workflow docsを多く扱います。VSCode workspaceを開いた時点で、ファイルとterminalの両方にUTF-8を先に宣言します。

推奨設定:

```json
{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": false,
  "files.eol": "\n",
  "terminal.integrated.env.windows": {
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
    "AIWF_TEXT_ENCODING": "utf-8"
  }
}
```

PowerShell profileの起動時設定:

```powershell
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
chcp 65001 > $null
```

`files.autoGuessEncoding` は `false` を推奨します。Windows環境では、日本語MarkdownをShift_JIS / CP932として誤推測すると、AIさんのpatch anchorやMarkdown preview確認が迷いやすくなるためです。

`.bat` / `.cmd` は例外です。Windows batch fileをShift_JIS / CP932で保持する必要がある場合は、`.editorconfig` の `[*.{bat,cmd}]` で境界を明示し、無理にUTF-8へ変換しません。

通常のPowerShellやWindows Terminalにも恒久的に反映する場合は、User Path登録用helperを実行します。

```powershell
.\runtime\windows-script\register-aiwfctl-path.cmd
```

`aiwfctl.cmd` から呼ぶ場合:

```powershell
.\runtime\windows-script\aiwfctl.cmd path register
```

登録後、すぐに `aiwfctl` が使えるPowerShell sessionを開く場合:

```powershell
.\runtime\windows-script\register-aiwfctl-path.cmd --shell
```

`aiwfctl.cmd` から登録と更新済みsession起動をまとめて行う場合:

```powershell
.\runtime\windows-script\aiwfctl.cmd path shell
```

登録後も同じPowerShellで `aiwfctl` が見つからない場合は、現在のPATHを壊さないように `runtime\windows-script` だけを先頭追加します。

```powershell
$env:Path = "$PWD\runtime\windows-script;$env:Path"
```

## Task Labels

Workflow entrypoint tasks:

```text
workflow:requirement-discovery
workflow:ariadne-new-system
workflow:ariadne-new-system-iac
workflow:ariadne-feature-maintenance
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
workflow:aiwfctl-path-shell
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

`workflow:aiwfctl-path-shell` は、`runtime/windows-script/register-aiwfctl-path.cmd --shell` を実行し、User Path登録後に `aiwfctl` が使えるPowerShell sessionを開くprovisioning taskです。同じ動作は `runtime/windows-script/aiwfctl.cmd path shell` からも呼べます。

## Preflight

実行例:

```powershell
uv run --project runtime python runtime/environment/preflight.py `
  --profile vscode-environment `
  --work-id vscode-environment `
  --source-dir C:\github\ariadne-ai-workflow-platform
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

Provisioning creates the local RAG backup directory tree under `work/db/<ARIADNE_KNOWLEDGE_REPOSITORY>/` if it is missing. This tree is a local backup/source area; provisioning does not clone, create `.git`, commit, or push.

再利用可能なVSCode environment knowledgeは、まずhuman-review可能なMarkdownへ保存します。

```text
work/db/ariadne-knowledge-platform/rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

Human approval後、最終的なUUID名RAG knowledge JSONへnormalizeします。

```powershell
uv run --project runtime python runtime/rag/normalize_documents.py `
  --source-dir work/db/ariadne-knowledge-platform/rag/workspace-environment `
  --output-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --document-type workspace-environment-pattern
```

最終着地:

```text
work/db/ariadne-knowledge-platform/rag/normalized/<uuid>.json
```

Chunk JSON、indexes、embeddings、retrieval packsは派生artifactです。

## Human Check

VSCodeでworkspaceを開いた後、次を確認します。

1. 各terminal profileを開く。
2. repository rootで起動することを確認する。
3. `test:vscode-json` を実行する。
4. `workflow:vscode-preflight` を実行する。
5. 必要に応じて `workflow:aiwfctl-path-shell` を実行し、新しいPowerShellで `aiwfctl help list` を確認する。
6. workflow label taskを1つ実行し、期待するCodex Skill commandが表示されることを確認する。
7. UI観察結果を `work/vscode-environment/test-evidence/workspace-test.md` に記録する。

## Guardrails

- `.vscode` にsecretを保存しない。
- 既存 `.vscode` 変更は、置き換え承認が無い限りadditiveにする。
- machine-specific valuesはdocument化し、review可能にする。
- inline PowerShellや `python -c` より、VSCode `process` taskとrepo-local helper scriptを優先する。
- workspace taskやgenerated install planに `ExecutionPolicy Bypass` を追加しない。
- CLIで証明できないVSCode UI behaviorはhuman-check evidenceとして扱う。
