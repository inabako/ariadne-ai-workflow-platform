# Runtime Workflow

`runtime/workflow/` は、workflow単位の補助CLIを置くディレクトリです。

## `gui_mode.py`

`work/requirements/svg-input/<PREFIX>_*.svg` を確認し、対象SVGをIssue作業領域へ取り込んだうえで、共通拡張である GaC / UaC GUI Mode を実行します。

```powershell
python runtime/workflow/gui_mode.py init-input
python runtime/workflow/gui_mode.py run --issue-id SYS-0001
python runtime/workflow/gui_mode.py validate --issue-id SYS-0001
python runtime/workflow/gui_mode.py self-test
```

Corrective Action改善の実行例:

```powershell
python runtime/workflow/gui_mode.py run `
  --issue-id FIX-123 `
  --work-dir work/issue-123 `
  --mode corrective-improvement
```

`SYS_`、`FEAT_`、`FIX_` のprefixで親workflowを判別します。Issue作業領域が作成された後、対象SVGは `work/<issue-id>/input/gui/` へ移動されます。SVGが無い場合は `status: skipped` を返し、親workflowへ戻ります。生成された PyQt6 / QTest ファイルは `gac-uac/generated/` 配下の候補として扱い、target sourceへ自動コピーしません。

## `web_svg_layout_mode.py`

`work/requirements/svg-input/WEB_<PREFIX>_*.svg` を確認し、対象SVGをIssue作業領域へ取り込んだうえで、共通拡張である Web SVG Layout Mode を実行します。

```powershell
python runtime/workflow/web_svg_layout_mode.py init-input
python runtime/workflow/web_svg_layout_mode.py run --issue-id SYS-0001
python runtime/workflow/web_svg_layout_mode.py validate --issue-id SYS-0001
```

`WEB_SYS_`、`WEB_FEAT_`、`WEB_FIX_` のprefixでWeb UI modeを判別します。既存互換として `NEXT_SYS_`、`NEXT_FEAT_`、`NEXT_FIX_` も受け付けます。生成された React / Playwright ファイルは `web-ui/generated/` 配下の候補として扱い、target sourceへ自動コピーしません。

## `docs_sync.py`

docs-sync用の作業フォルダ初期化、ドキュメント差分JSONのひな形、GitHub Issue bodyを生成します。

このCLI単体では、GitHub Issue作成、docs変更、branch push、RAG登録、close archive準備は行いません。

## `github_knowledge_maintenance.py`

GitHub Repository Knowledge Maintenance用の作業フォルダ初期化、分析JSONひな形、修復案、GitHub同期案、RAG候補を生成します。

このCLI単体では、GitHub変更、repository clone、source code変更、Git履歴の書き換え、RAG公開は行いません。

## `init_corrective_action_fix.py`

Corrective Action Fix workflow用に、base作業フォルダとIssue作業フォルダを初期化します。

## `vscode_environment.py`

VSCode Environment workflow用に `work/<id>/` を初期化し、要件定義・検証用のscaffoldを作成します。

## `knowledge_capture.py`

完了済みIssue workflow向けに、最終knowledge capture packageを生成します。

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

このCLI単体では、push、RAG登録、close archive作成、archive pruningは行いません。人間承認に向けたreportとreadiness checkを準備します。

`--base-work-id` を指定した場合、base phaseのprocess reportは `work/close/improvement/<issue-id>/links.md` とsummary reportへ要約・リンク化してからbase work folderを削除します。

## `close_archive.py`

`work/close/<category>/<archive-id>` を軽量なreport-only archiveとして作成・監査・承認付きpruneします。

改善フローでは、既定で `work/close/improvement/<issue-id>/` を使います。
`prepare` は既定でRAG sourceを自動検出し、`00-summary.md`、`01-work-report.md`、`03-review-report.md`、`links.md`、`metadata.json` へ具体内容を反映します。

```powershell
python runtime/workflow/close_archive.py prepare --issue issue-11
python runtime/workflow/close_archive.py audit --issue issue-11
python runtime/workflow/close_archive.py prune --issue issue-11
```

新システム開発フロー:

```powershell
python runtime/workflow/close_archive.py prepare `
  --issue issue-123 `
  --category new-system-dev
```

GitHub knowledge maintenance:

```powershell
python runtime/workflow/close_archive.py prepare `
  --work-id github-knowledge-localty-system-robot-recent `
  --category github `
  --require-rag
```

VSCode Environment:

```powershell
python runtime/workflow/close_archive.py prepare `
  --work-id vscode-environment `
  --category vscode `
  --require-rag
```

重要なRAG sourceを必ず含めたい場合は `--source-rag` で明示指定します。複数指定できます。

```powershell
python runtime/workflow/close_archive.py prepare `
  --issue issue-11 `
  --source-rag rag/normalized/issue-11.md `
  --require-rag
```

RAG sourceが必須のcloseでは `--require-rag` を付けます。自動検出を止め、明示指定したRAGだけを使う場合は `--no-auto-rag` を使います。

`github` と `vscode` は `prepare` 時に `YYMMDDHHmmss_<random>` のarchive-idを生成します。以後のaudit / pruneでは、出力された `archive_id` または `archive_dir` を指定します。

`prune` は既定ではdry-runです。実削除には明示承認が必要です。

```powershell
python runtime/workflow/close_archive.py prune `
  --issue issue-11 `
  --execute `
  --human-check approved
```

共通の目標構成:

```text
work/close/<category>/<archive-id>/
  00-summary.md
  01-work-report.md
  02-test-report.md
  03-review-report.md
  04-human-check.md
  05-retrospective.md
  links.md
  metadata.json
```

`work/close` には source checkout、`.git`、`.venv`、`node_modules`、build output、cacheを残しません。
