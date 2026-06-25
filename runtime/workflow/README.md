# Runtime Workflow

`runtime/workflow/` は、workflow 単位の補助コマンドを置くディレクトリです。

## コマンド

### `gui_mode.py`

`work/requirements/svg-input/<PREFIX>_*.svg` を確認し、対象SVGをIssue作業領域へ取り込んだうえで、共通拡張である GaC / UaC GUI Mode を実行します。

実行例:

```powershell
python runtime/workflow/gui_mode.py init-input
python runtime/workflow/gui_mode.py run --issue-id SYS-0001
python runtime/workflow/gui_mode.py validate --issue-id SYS-0001
```

Corrective Action 互換の実行例:

```powershell
python runtime/workflow/gui_mode.py run `
  --issue-id FIX-123 `
  --work-dir work/issue-123 `
  --mode corrective-improvement
```

`SYS_`、`FEAT_`、`FIX_` のファイル名prefixで親workflowを選別します。Issue作業領域が作成された後、対象ファイルは `work/<issue-id>/input/gui/` へ移動されます。SVGが無い場合は `status: skipped` を返します。生成された PyQt6 / QTest ファイルは `gac-uac/generated/` 配下の候補として扱い、target source へ自動コピーしません。

### `web_svg_layout_mode.py`

`work/requirements/svg-input/WEB_<PREFIX>_*.svg` を確認し、対象SVGをIssue作業領域へ取り込んだうえで、共通拡張である Web SVG Layout Mode を実行します。

実行例:

```powershell
python runtime/workflow/web_svg_layout_mode.py init-input
python runtime/workflow/web_svg_layout_mode.py run --issue-id SYS-0001
python runtime/workflow/web_svg_layout_mode.py validate --issue-id SYS-0001
```

Corrective Action 互換の実行例:

```powershell
python runtime/workflow/web_svg_layout_mode.py run `
  --issue-id FIX-123 `
  --work-dir work/issue-123 `
  --mode corrective-fix
```

`WEB_SYS_`、`WEB_FEAT_`、`WEB_FIX_` のファイル名prefixで Web UI mode を選別します。これにより、PyQt / Qt GUI mode の `SYS_`、`FEAT_`、`FIX_` と衝突しません。既存互換として `NEXT_SYS_`、`NEXT_FEAT_`、`NEXT_FIX_` の入力も受け付けます。対象ファイルはIssue作業領域作成後に `work/<issue-id>/input/web-ui/` へ移動されます。SVGが無い場合は `status: skipped` を返します。生成された React / Playwright ファイルは `web-ui/generated/` 配下の候補として扱い、target source へ自動コピーしません。

### `docs_sync.py`

docs sync 用の作業フォルダを初期化し、ドキュメント差分分析JSONのひな形と、GitHub Issue body を生成します。

実行例:

```powershell
python runtime/workflow/docs_sync.py init `
  --repository localty-system-gui `
  --target-branch develop

python runtime/workflow/docs_sync.py analysis-template `
  --work-id develop

python runtime/workflow/docs_sync.py issue-body `
  --work-id develop
```

主な成果物:

```text
work/<target-branch>/context/docs-drift-analysis.json
work/<target-branch>/process-report/docs-sync-issue-body-*.md
```

このコマンド単体では、GitHub Issue作成、docs変更、branch push、RAG登録、archive移動は行いません。

### `github_knowledge_maintenance.py`

GitHub Repository Knowledge Maintenance 用の作業フォルダを初期化し、分析JSONのひな形、修復案、GitHub同期案、RAG候補を生成します。

実行例:

```powershell
python runtime/workflow/github_knowledge_maintenance.py init `
  --repository localty-system-gui `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output

python runtime/workflow/github_knowledge_maintenance.py analysis-template `
  --work-id github-knowledge-localty-system-gui-recent

python runtime/workflow/github_knowledge_maintenance.py repair-plan `
  --work-id github-knowledge-localty-system-gui-recent

python runtime/workflow/github_knowledge_maintenance.py github-sync-plan `
  --work-id github-knowledge-localty-system-gui-recent

python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
  --work-id github-knowledge-localty-system-gui-recent
```

主な成果物:

```text
work/<work-id>/context/github-knowledge-analysis.json
work/<work-id>/process-report/github-knowledge-repair-plan-*.md
work/<work-id>/process-report/github-documentation-sync-plan-*.md
work/<work-id>/process-report/github-knowledge-rag-candidate-*.md
```

このコマンド単体では、GitHubの変更、repository clone、source code変更、Git履歴の書き換え、RAG公開は行いません。承認済みのsubcommand optionが指定された場合だけ、該当処理を実行します。

### `init_corrective_action_fix.py`

Corrective Action Fix workflow 用に、base作業フォルダとIssue作業フォルダを初期化します。

### `vscode_environment.py`

VSCode Environment workflow 用の作業フォルダを初期化し、要件定義・検証用のscaffoldを作成します。

実行例:

```powershell
python runtime/workflow/vscode_environment.py init `
  --work-id vscode-environment `
  --target-dir C:\github\localty-system-gui

python runtime/workflow/vscode_environment.py draft-template

python runtime/workflow/vscode_environment.py open-questions `
  --work-id vscode-environment

python runtime/workflow/vscode_environment.py requirements-template `
  --work-id vscode-environment

python runtime/workflow/vscode_environment.py validation-template `
  --work-id vscode-environment

python runtime/workflow/vscode_environment.py rag-template `
  --work-id vscode-environment `
  --topic localty-vscode-environment `
  --repository localty
```

主な成果物:

```text
work/<work-id>/design-document/workspace-requirements.md
work/<work-id>/design-document/open-questions.md
work/<work-id>/context/workspace-shared-artifact-validation.json
work/<work-id>/process-report/workspace-shared-artifact-validation.md
rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
rag/normalized/<uuid>.json
```

`workspace-environment` Markdown は、人間がreviewするためのsource noteです。人間承認後、再利用可能な最終知識は `rag/normalized/` 配下のUUID名JSONへ正規化します。

このコマンド単体では、target workspace の編集、tool install、VSCode file変更、RAG正規化pipelineの実行は行いません。

### `knowledge_capture.py`

完了済みIssue workflow向けに、最終knowledge capture packageを生成します。

実行例:

```powershell
python runtime/workflow/knowledge_capture.py `
  --issue issue-11 `
  --repository localty-system-gui `
  --branch feature/issue-11 `
  --base-work-id develop
```

出力:

```text
work/<issue-id>/process-report/pull-request-title.md
work/<issue-id>/process-report/pull-request-description.md
work/<issue-id>/process-report/merge-comment.md
work/<issue-id>/process-report/knowledge-capture-report.md
work/<issue-id>/process-report/knowledge-capture-*.json
```

このコマンド単体では、push、RAG登録、archive移動は行いません。人間承認に向けたreportとreadiness checkを準備します。

`--base-work-id` を指定した場合、reportには必要なbase work resetも記録されます。

```text
work/<base-work-id>/process-report
  -> work/close/<issue-id>/process-report/base-work-<base-work-id>
```

`work/<base-work-id>` は、上記copyが検証され、ユーザーが削除を承認した後にのみ削除します。
