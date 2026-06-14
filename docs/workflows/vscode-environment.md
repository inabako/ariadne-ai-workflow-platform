# VSCode Environment

`/vscode-environment` は、target repository / workspace に対して再現可能なVSCode Workspace-as-Code環境を構築するworkflowです。

## Command

```text
/vscode-environment <target-workspace-path>
```

commandに引数が無い場合、workflowは次のdraft directoryを読みます。

```text
work/requirements/devlop-edit-draft/
```

このdirectoryでは、`README.md` がscaffoldです。記入済みdraftは `README_20260614.md` のように `README_*.md` として保存します。legacy `.txt` draftも必要に応じて確認対象にします。

例:

```text
/vscode-environment C:\github\localty-system-gui
```

## Outputs

Workflow artifacts:

```text
work/<work-id>/design-document/workspace-requirements.md
work/<work-id>/design-document/open-questions.md
work/<work-id>/design-document/vscode-design.md
work/<work-id>/design-document/terminal-design.md
work/<work-id>/context/workspace-shared-artifact-validation.json
work/<work-id>/process-report/
work/<work-id>/test-evidence/
```

Target workspace artifacts:

```text
.vscode/settings.json
.vscode/tasks.json
.vscode/launch.json
.vscode/extensions.json
.vscode/<repository-name>.code-workspace
runtime/workflow/vscode_task_runner.py
```

Reference: [VSCode Environment](../reference/vscode-environment.md)

## Flow

1. `work/requirements/devlop-edit-draft/README.md` にdraft README scaffoldを置く、または作成する。
2. `work/requirements/devlop-edit-draft/README_20260614.md` のような記入済みdraftを保存する。
3. 必須情報が不足、空欄、`TODO`、矛盾を含む場合は `open-questions.md` を作成する。
4. Human Reviewと承認を待つ。
5. 確定したtarget workspaceで `work/<work-id>` を初期化する。
6. workspace requirementsを分析する。
7. shared artifactsを検証する。
8. environment preflightを実行する。
9. VSCode settings、tasks、launch configs、extensions、workspace fileを設計する。
10. terminal profilesとterminal rolesを設計する。
11. validation後に `.vscode` filesを実装する。
12. 長いinline PowerShellではなく、VSCode `process` taskとrepo-local helper scriptを優先する。
13. tasks、terminal startup、Docker/runtime integration、AI workflow entry tasksをtestする。
14. evidenceを記録する。
15. setup / troubleshooting docsを更新する。
16. 再利用可能なworkspace knowledgeを `rag/workspace-environment/` にhuman-review可能なsource Markdownとして保存する。
17. Human approval後、source Markdownを `rag/normalized/` のUUID名JSONへnormalizeする。
18. `rag/normalized/<uuid>.json` を最終machine-readable knowledge artifactとして扱う。chunk、index、embedding、retrieval filesは派生物です。

## Stop Rules

次の場合は停止し、`open-questions.md` を作成します。

- commandにtarget argumentが無い。
- 記入済み `README_*.md` draftが存在しない。
- 未解決の `TODO` が残っている。
- 必須tool、extensions、terminal profiles、AI workflow entry tasks、evidence requirementsが不足または矛盾している。

次の場合はhuman approval前で停止します。

- tool / extensionをinstallする。
- 既存 `.vscode` filesを置き換える。
- default terminal behaviorを変更する。
- `conditional-pass` を受け入れる。

`.vscode/tasks.json` では、`ExecutionPolicy Bypass`、nested PowerShell launcher、長いinline PowerShell command、複雑な `python -c` snippetに依存するtaskを生成しません。代わりに、commit済みhelper scriptを `process` taskから呼び出します。

## RAG Capture

再利用可能なLocalty VSCode environment knowledgeは、source Markdownとして次へ保存します。

```text
rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

正しい名前のnoteを作る例:

```powershell
uv run python runtime/workflow/vscode_environment.py rag-template `
  --work-id "vscode-environment" `
  --topic "localty-vscode-environment" `
  --repository "localty"
```

Markdown noteはreview sourceです。最終knowledge artifactはUUID名JSONです。

Human approval後、`workspace-environment-pattern` としてnormalizeします。

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

normalize後、必要に応じて派生RAG artifactを生成します。

```powershell
uv run python runtime/rag/chunk_documents.py `
  --input-dir rag/normalized `
  --output-dir rag/chunks

uv run python runtime/rag/build_index.py `
  --normalized-dir rag/normalized `
  --chunks-dir rag/chunks `
  --output-dir rag/indexes

uv run python runtime/rag/embed_chunks.py `
  --chunks-index rag/indexes/chunks.jsonl `
  --output rag/embeddings/chunks-embeddings.jsonl
```

## Source Skill

```text
skills/vscode-environment/SKILL.md
```
