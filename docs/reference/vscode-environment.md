# VSCode Environment

この repository は、VSCode Workspace as Code として `.vscode` と workspace file を持ちます。

目的は、AI Agent と人間が同じ terminal、task、debug、preflight、evidence flow を再現できるようにすることです。

## Files

| File | Purpose |
| --- | --- |
| `.vscode/settings.json` | terminal profile、encoding、Markdown、Python基本設定 |
| `.vscode/tasks.json` | workflow entry task、preflight、JSON check、runtime smoke |
| `.vscode/launch.json` | Python runtime helper debug launch |
| `.vscode/extensions.json` | recommended VSCode extensions |
| `.vscode/intent-driven-robotics-ai-workflow.code-workspace` | workspace entry file。`path: ".."` で repository root を開く |

## Terminal Profiles

| Profile | Role |
| --- | --- |
| `Dispatcher PowerShell` | workflow repository root で Codex / AI workflow を調整する |
| `Software Workflow PowerShell` | `uv run python`、runtime helper、RAG script、test を実行する |
| `MSYS2 Localty MINGW64` | Localty GUI / GStreamer / PyQt smoke check 用 |
| `IaC Workflow PowerShell` | Docker / Go / gateway / IaC 作業用 |
| `Docker Test PowerShell` | Docker Desktop 検証用 |
| `Evidence PowerShell` | logs、reports、human-check notes 用 |

Default terminal は `Dispatcher PowerShell` です。

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

Slash command workflow tasks show the Codex command and Skill path. They do not mutate repository state by themselves.

`test:vscode-json` calls `runtime/workflow/validate_vscode_workspace.py` instead of inline `python -c` so PowerShell quoting does not break the task.

`workflow:vscode-preflight` and `test:go-version` refresh Machine/User PATH inside the task before checking Go. This avoids stale PATH problems when Go was installed while VSCode was already open.

## Preflight

Run:

```powershell
uv run python runtime/environment/preflight.py `
  --profile vscode-environment `
  --work-id vscode-environment `
  --source-dir C:\github\intent-driven-robotics-ai-workflow
```

The report is written under:

```text
work/vscode-environment/process-report/
```

## Evidence

VSCode environment evidence is stored under:

```text
work/vscode-environment/test-evidence/
```

Use `workspace-test.md` for command results and human-check notes.

## Knowledge Finalization

Reusable VSCode environment knowledge first lands as human-reviewable Markdown:

```text
rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

After human approval, normalize it into the final UUID-named RAG knowledge JSON:

```powershell
uv run python runtime/rag/normalize_documents.py `
  --source-dir rag/workspace-environment `
  --output-dir rag/normalized `
  --document-type workspace-environment-pattern
```

Final landing:

```text
rag/normalized/<uuid>.json
```

Chunk JSON, indexes, embeddings, and retrieval packs are derived artifacts.

## Human Check

After opening the workspace in VSCode:

1. Open each terminal profile.
2. Confirm it starts in the repository root.
3. Run `test:vscode-json`.
4. Run `workflow:vscode-preflight`.
5. Run one workflow label task and confirm it prints the expected Codex Skill command.
6. Record UI observations in `work/vscode-environment/test-evidence/workspace-test.md`.

## Guardrails

- Do not store secrets in `.vscode` or `.code-workspace`.
- Keep `.vscode` changes additive unless replacement is explicitly approved.
- Keep machine-specific values documented and reviewable.
- Treat VSCode UI behavior as human-check evidence when CLI cannot prove it.
