# VSCode Environment

`/vscode-environment` は、VSCode Workspace-as-Code 環境を整備し、AIさんと人間が同じ手順で workflow、terminal、task、debug、検証、evidence を再現できるようにする workflow です。

## Command

```text
/vscode-environment
/vscode-environment <target-workspace-path>
/vscode-environment --custom-design
```

## 3つのMode

### 1. self-provision mode

引数なしで実行します。

```text
/vscode-environment
```

- target: current repository / workspace root
- 目的: このAI workflow repository自身を、AIさんが実行しやすいVSCode環境にする
- 記入済み草案: 不要
- 判断材料: `.vscode/`, `runtime/windows-script/`, `runtime/tools/`, `runtime/workflow/`, `db/registries/`, docs, prompts, tests

### 2. target-workspace mode

対象workspaceを明示して実行します。

```text
/vscode-environment C:\github\localty-system-gui
```

- target: 指定された repository / workspace
- 目的: 対象repoを読み、VSCode Workspace-as-Code環境を整える
- 記入済み草案: 任意
- 判断材料: 対象repoの既存 `.vscode`、README、tooling、test、workflow定義

### 3. custom-design mode

特殊なterminal構成、Docker利用、extension policy、launch設定、multi-root、個人path、local-only設定などがある場合に使います。

```text
/vscode-environment --custom-design
```

- target: current repository または指定workspace
- 記入済み草案: 任意。ただし複雑な設計意図を伝える補助入力として有効
- stop条件: repo evidenceだけでは安全に判断できない選択がある場合

custom-design用の任意draftは次に置きます。

```text
work/requirements/devlop-edit-draft/
```

`README.md` はscaffoldです。記入済みdraftを使う場合は `README_20260614.md` のように `README_*.md` として保存します。legacy `.txt` draftも必要に応じて確認対象にします。

## Outputs

Workflow artifacts:

```text
work/<work-id>/design-document/workspace-requirements.md
work/<work-id>/design-document/open-questions.md
work/<work-id>/design-document/vscode-design.md
work/<work-id>/design-document/terminal-design.md
work/<work-id>/context/workspace-shared-artifact-validation.json
work/<work-id>/context/vscode-environment-state.json
work/<work-id>/context/runtime-context.json
work/<work-id>/context/context-manifest.json
work/<work-id>/process-report/
work/<work-id>/test-evidence/
```

Local RAG backup artifacts:

```text
work/db/<ARIADNE_KNOWLEDGE_REPOSITORY>/
work/db/<ARIADNE_KNOWLEDGE_REPOSITORY>/rag/
work/db/<ARIADNE_KNOWLEDGE_REPOSITORY>/rag/{corrective-action-report,github-knowledge,workspace-environment,normalized,chunks,optimized-chunks,jsonized,indexes,embeddings,retrieval}/
```

Provisioning creates these directories when missing. This is a local backup area only; the workflow does not clone, create `.git`, commit, or push.

Target workspace artifacts:

```text
.vscode/settings.json
.vscode/tasks.json
.vscode/launch.json
.vscode/extensions.json
runtime/workflow/vscode_task_runner.py
```

Reference: [VSCode Environment](../reference/vscode-environment.md)

## Flow

1. modeを判定する。
2. target workspaceを決める。
   - 引数なし: self-provision modeとしてcurrent repositoryを対象にする。
   - path指定あり: target-workspace modeとして指定先を対象にする。
   - 特殊要件あり: custom-design modeとして追加確認を行う。
3. 既存 `.vscode` files、repo-local tools、workflow registry、docs、testsを読む。
4. custom-design modeで不足・空欄・`TODO`・矛盾がある場合のみ `open-questions.md` を作成して停止する。
5. `work/<work-id>` を初期化する。
6. `workspace-requirements.md` を作成または更新する。
7. shared artifactsを検証する。
8. environment preflightを実行する。
9. VSCode settings、tasks、launch configs、extensionsを設計する。multi-rootが必要な場合のみworkspace fileをoptionalで設計する。
10. terminal profilesとterminal rolesを設計する。
11. validation後に `.vscode` filesを実装する。
12. 長いinline PowerShellではなく、VSCode `process` taskとrepo-local helper scriptを優先する。
13. tasks、terminal startup、Docker/runtime integration、AI workflow entry tasksをtestする。
14. evidenceを記録する。
15. setup / troubleshooting docsを更新する。
16. 再利用可能なworkspace knowledgeを `work/db/ariadne-knowledge-platform/rag/workspace-environment/` にhuman-review可能なsource Markdownとして保存する。
17. Human approval後、source Markdownを `work/db/ariadne-knowledge-platform/rag/normalized/` のUUID名JSONへnormalizeする。
18. `work/db/ariadne-knowledge-platform/rag/normalized/<uuid>.json` を最終machine-readable knowledge artifactとして扱う。chunk、index、embedding、retrieval filesは派生物です。

## Stop Rules

次の場合は停止し、`open-questions.md` を作成します。

- custom-design modeで、terminal / Docker / extension / launch / local path / multi-root / evidence方針をrepo evidenceから安全に判断できない。
- optional draftに未解決の `TODO`、空欄、矛盾が残っている。
- target workspace pathが指定されているが存在しない、または読めない。
- 必須tool、extensions、terminal profiles、AI workflow entry tasks、evidence requirementsが不足または矛盾している。

次の場合はhuman approval前で停止します。

- tool / extensionをinstallする。
- 既存 `.vscode` filesを置き換える。
- default terminal behaviorを変更する。
- personal absolute pathやlocal-only設定を書き込む。
- `conditional-pass` を受け入れる。

`.vscode/tasks.json` では、`ExecutionPolicy Bypass`、nested PowerShell launcher、長いinline PowerShell command、複雑な `python -c` snippetに依存するtaskを生成しません。代わりに、commit済みhelper scriptを `process` taskから呼び出します。

## Repo-local Tools PATH

target workspace に `runtime/windows-script/*.cmd` などのrepo-local command scriptがある場合、`.vscode/settings.json` の `terminal.integrated.env.windows.Path` にwindows-script directoryを追加します。

このworkflow repositoryでは次を設定します。

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

これにより、VSCode統合ターミナルでは `aiwfctl help list` のように呼び出せます。

## UTF-8 First

Windows上の日本語Markdown、prompt、JSON、workflow docsを扱うworkspaceでは、VSCode provisioningの最初に「このworkspaceはUTF-8で扱う」と宣言します。

`runtime/workflow/vscode_environment.py init` は `runtime-context.json` に `encoding_contract` を出力します。後続Agentはこのcontractを読み、`.vscode/settings.json`、`.editorconfig`、PowerShell terminal profileのUTF-8設定を初期構築に含めます。

Codexの `~/.codex/config.toml` / `.codex/config.toml` はCodexが認識する設定のためのファイルです。UTF-8を強制する標準の `[encoding]` tableとして扱わず、Codex向けの方針共有は `AGENTS.md` やworkflow docsに書きます。機械チェックは `aiwfctl doctor --fail-on-warning` で行います。

`.vscode/settings.json` では、文字コードの自動推測に頼らずUTF-8を明示します。

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

PowerShell terminal profileでは、起動時に入出力をUTF-8へ寄せます。

```powershell
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
chcp 65001 > $null
```

これにより、AIさんが日本語行を読み間違えたり、PowerShell表示だけを根拠に文字化けと誤判定したりするリスクを下げます。

文字化けの疑いがある場合は、PowerShell表示だけで判断せず、repo-local toolで実ファイルを検査します。

```powershell
uv run --project runtime python runtime/tools/text_encoding_convert.py --repo-root . preview --paths docs --extensions .md --bytes 160 --chars 120
uv run --project runtime python runtime/tools/text_encoding_convert.py --repo-root . inspect --paths docs --extensions .md
uv run --project runtime python runtime/tools/text_encoding_guard.py --repo-root . scan --paths docs --extensions .md --fail-on-finding
uv run --project runtime python runtime/tools/utf8_bom.py --repo-root . scan --paths skills .github docs runtime --extensions .md .py .json .yaml .yml --fail-on-finding
```

PowerShell由来のShift_JIS / CP932文書をUTF-8へ寄せる場合は、`inspect` の推奨encodingを確認してから変換します。

```powershell
uv run --project runtime python runtime/tools/text_encoding_convert.py --repo-root . convert --paths docs --extensions .md --from-encoding cp932 --write
uv run --project runtime python runtime/tools/utf8_bom.py --repo-root . strip --paths skills .github docs runtime --extensions .md .py .json .yaml .yml --write
```

保存済み文字化け候補は、固定markerでは断定せず、`preview` のhex bytesとencoding別previewで確認します。連続した疑問符のように情報が失われた箇所は自動復元対象にしません。

ただし、`.bat` / `.cmd` をShift_JISやCP932で保持するrepositoryでは、その境界を `.editorconfig` で例外化し、無理にUTF-8へ変換しません。

通常のPowerShellやWindows Terminalからも `aiwfctl` を使う必要がある場合、VSCode provisioning taskとして次を実行します。

```text
workflow:aiwfctl-path-shell
```

このtaskは次を実行します。

```powershell
.\runtime\windows-script\register-aiwfctl-path.cmd --shell
```

同じ処理は `aiwfctl.cmd` からも呼び出せます。

```powershell
.\runtime\windows-script\aiwfctl.cmd path shell
```

既に開いているterminalにはPATH変更が反映されません。terminalを閉じて開き直すか、現在のPowerShellで次を実行します。

```powershell
$env:Path = "$PWD\runtime\windows-script;$env:Path"
```

## RAG Capture

再利用可能なLocalty VSCode environment knowledgeは、source Markdownとして次へ保存します。

```text
work/db/ariadne-knowledge-platform/rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

正しい名前のnoteを作る例:

```powershell
uv run --project runtime python runtime/workflow/vscode_environment.py rag-template `
  --work-id "vscode-environment" `
  --topic "localty-vscode-environment" `
  --repository "localty"
```

Markdown noteはreview sourceです。最終knowledge artifactはUUID名JSONです。

Human approval後、`workspace-environment-pattern` としてnormalizeします。

```powershell
uv run --project runtime python runtime/workflow/vscode_environment.py rag-template `
  --work-id "vscode-environment" `
  --topic "localty-vscode-environment" `
  --repository "localty" `
  --status approved
```

Draft RAG source notes are not cleanup evidence. After approval, refresh the source with `--status approved`, then normalize it:

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

normalize後、必要に応じて派生RAG artifactを生成します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl work cleanup-check --work-id vscode-environment
.\runtime\windows-script\aiwf.cmd ctl work cleanup-apply --work-id vscode-environment --human-check approved
```

After long-lived Knowledge absorption is confirmed, verify temporary work cleanup through the generic ctl. Then continue derived RAG artifact generation as needed:

```powershell
uv run --project runtime python runtime/rag/chunk_documents.py `
  --input-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --output-dir work/db/ariadne-knowledge-platform/rag/chunks

uv run --project runtime python runtime/rag/build_index.py `
  --normalized-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --chunks-dir work/db/ariadne-knowledge-platform/rag/chunks `
  --output-dir work/db/ariadne-knowledge-platform/rag/indexes

uv run --project runtime python runtime/rag/embed_chunks.py `
  --chunks-index work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl `
  --output work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl
```

## Source Skill

```text
skills/vscode-environment/SKILL.md
```
