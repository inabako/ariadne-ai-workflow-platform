# Runtime

このディレクトリは、workflow を実行・補助するための runtime 機能を格納します。

`templates/` は成果物のひな形、`work/` は案件ごとの成果物実体、`runtime/` は workflow を動かす処理機能を置く場所です。

## Runtime Areas

| Directory | Purpose |
| --- | --- |
| `runtime/common/` | intake / retrieval で共通利用する utility |
| `runtime/environment/` | workflow 前の tool / package preflight と install list 作成 |
| `runtime/intake/` | 投入された要件定義書を受付ID単位の `work/<採番ID>/` へ移動・初期化する機能 |
| `runtime/retrieval/` | task を順次または並列で処理し、必要なcontextやartifactを取り出す機能 |
| `runtime/scm/` | target repository の取得、要件比較、Issue branch作成、semantic commit |
| `runtime/github/` | GitHub Issue のdraft作成または実作成 |
| `runtime/rag/` | report / artifact を file-based RAG 用 document、chunk、index に変換する機能 |

## Environment Files

GitHub / SCM 連携情報は repository root の環境ファイルで管理します。

```text
.env.example   共有可能なキー一覧
.env           ローカル実値、commit禁止
.gitignore     .env を除外し、.env.example は追跡対象
```

Runtime は `runtime/common/env.py` を通じて `.env` を読み込みます。

## Implemented CLI

```text
runtime/intake/intake_requirements.py
runtime/environment/preflight.py
runtime/workflow/init_corrective_action_fix.py
runtime/workflow/vscode_environment.py
runtime/workflow/web_svg_layout_mode.py
runtime/workflow/close_archive.py
runtime/retrieval/task_runner.py
runtime/scm/prepare_repository.py
runtime/scm/compare_requirements.py
runtime/scm/create_issue_branch.py
runtime/scm/commit_changes.py
runtime/scm/push_branch.py
runtime/github/issue_manager.py
runtime/github/pull_request_manager.py
runtime/rag/normalize_documents.py
runtime/rag/chunk_documents.py
runtime/rag/build_index.py
runtime/rag/embed_chunks.py
runtime/rag/retrieve_context.py
runtime/rag/rag_dispatcher.py
runtime/rag/jsonize_rag_tree.py
runtime/rag/standardize_corrective_report_names.py
```

`intake_requirements.py` は、要件定義書を `work/<採番ID>/design-document/` へ移動し、`context/*.json` を初期化します。

`preflight.py` は、workflow や target repository の作業前に必要な executable / Python module / Python package / MSYS2 package / fallback support repository を確認し、不足時は install list を `work/<id>/process-report/` に出力します。`--install --human-check approved` が指定された場合のみ install を実行します。Localty の MSYS2 profile では公開済み `localty-system-protocol>=0.1.0` を優先し、取得できない場合だけ `localty-system-protocol` repository を support repository として準備します。

`init_corrective_action_fix.py` は、corrective action fix 用に repository / branch 引数から `work/<branch>/` または `work/issue-<issue-number>/` と初期contextを作成します。

`vscode_environment.py` は、VSCode Environment workflow 用に `work/<id>/` を初期化し、`workspace-requirements.md` と `workspace-shared-artifact-validation` のscaffoldを作成します。

`gui_mode.py` は、`work/requirements/svg-input/`の`SYS_*.svg`、`FEAT_*.svg`、`FIX_*.svg`をIssue作業領域へ取り込み、Semantic Layout Graph、Widget Mapping、Layout Spec、PyQt6候補、QTest候補を`gac-uac/`へ生成します。SVGが無い場合は`skipped`で親workflowへ戻り、生成候補をtarget sourceへ自動コピーしません。

`web_svg_layout_mode.py` は、`work/requirements/svg-input/`の`WEB_SYS_*.svg`、`WEB_FEAT_*.svg`、`WEB_FIX_*.svg`をIssue作業領域へ取り込み、route layout map、component mapping、responsive layout spec、React候補、Playwright候補を`web-ui/`へ生成します。SVGが無い場合は`skipped`で親workflowへ戻り、生成候補をtarget sourceへ自動コピーしません。

`task_runner.py` は、`task-plan.schema.json` に沿ったtask planを読み込み、sequential / parallel に処理して `process-report/` へ実行レポートを出力します。

`prepare_repository.py` は、target repository / branch を `work/<採番ID>/source/repository/` に準備します。

`compare_requirements.py` は、要件定義書と repository state の比較レポートを作成します。

`issue_manager.py` は、GitHub Issue draftを作成し、`--create` 指定時のみ GitHub REST API でIssueを作成します。Issue body は `--body-file`、target repository の `.github/ISSUE_TEMPLATE.md`、runtime fallback の順に選択します。Issue titleはworkflowに応じて `[新規機能フロー]`、`[改善フロー]`、`[初期開発]` のprefixを付けます。

`create_issue_branch.py` は、Issue番号からGitHub上に `feature/issue-<issue-number>` branchを作成し、work配下へclone / checkoutします。

`commit_changes.py` は、semantic commit message を検証してcommitします。

`push_branch.py` は、人間チェック承認後に `feature/issue-<issue-number>` branch をpushし、push recordを保存します。

`pull_request_manager.py` は、Issue branch push後に `develop` へのPull Request draft / createを行います。PR titleはIssue titleを使い、PR bodyにはMermaid sequence diagramを含めます。

`normalize_documents.py` は、Markdown report を metadata 付きの RAG document JSON に変換します。

`chunk_documents.py` は、normalized document を retrieval しやすい chunk JSON に分割します。

`build_index.py` は、document / chunk を JSONL index として `rag/indexes/` に集約します。

`embed_chunks.py` は、chunk index から deterministic sparse embedding を生成し、`rag/embeddings/` に出力します。

`retrieve_context.py` は、JSONL chunk index と local embeddings から query に合うchunkを選び、Agent投入用の圧縮済みcontext packを `rag/retrieval/` に出力します。

`rag_dispatcher.py` は、開発前RAG読み込み用に複数queryを計画し、`retrieve_context.py` を並列実行して、圧縮済みcontext packを集約します。

`jsonize_rag_tree.py` は、`rag/` 配下の非UUID JSON、JSONL、Markdown、text artifact を UUID名の JSON wrapper に変換します。
`standardize_corrective_report_names.py` は、`rag/corrective-action-report/` 配下のMarkdown reportを `YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md` に統一します。

## Intake Role

`runtime/intake/` は、投入された要件定義書を受け付け、受付ID単位の作業領域へ移動する責務を持ちます。

想定処理:

- 受付IDの採番
- `work/<採番ID>/` の作成
- `design-document/`、`process-report/`、`test-evidence/`、`test-specifications/`、`source/`、`context/` の初期化
- 投入された要件定義書の移動
- `agent-context.json` と `artifact-index.json` の初期生成

## Retrieval Role

`runtime/retrieval/` は、workflow task の実行時に必要な情報を取り出し、順次または並列処理へ渡す責務を持ちます。

想定処理:

- task queue / task graph の読み取り
- 前工程artifactの取得
- `context/*.json` の読み取り
- Agentに渡すhandoff packageの組み立て
- sequential / parallel task execution の補助
- 実行結果のartifact index更新

## RAG Role

`runtime/rag/` は、review report や corrective action report を future Agent が再利用できる知識へ変換する責務を持ちます。

想定処理:

- source Markdown report の読み取り
- front matter / heading / content の抽出
- normalized RAG document JSON の生成
- chunk JSON の生成
- `documents.jsonl` / `chunks.jsonl` index の生成
- local sparse embedding の生成
- keyword retrieval、embedding cosine similarity、hybrid reranking、extractive context compression
- UUID-named `rag-retrieval-result` / `rag-context-pack` JSON の生成
- UUID-named `rag-load-dispatch` JSON の生成
- UUID filename policy と JSON content / metadata search
- 将来の embeddings / vector DB 移行に備えた metadata の標準化
