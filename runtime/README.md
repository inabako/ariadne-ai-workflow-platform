# Runtime

このディレクトリは、workflow を実行・補助するための runtime 機能を格納します。

`templates/` は成果物のひな形、`work/` は案件ごとの成果物実体、`runtime/` は workflow を動かす処理機能を置く場所です。

## Runtime Areas

| Directory | Purpose |
| --- | --- |
| `runtime/common/` | intake / retrieval で共通利用する utility |
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
runtime/retrieval/task_runner.py
runtime/scm/prepare_repository.py
runtime/scm/compare_requirements.py
runtime/scm/create_issue_branch.py
runtime/scm/commit_changes.py
runtime/github/issue_manager.py
runtime/rag/normalize_documents.py
runtime/rag/chunk_documents.py
runtime/rag/build_index.py
runtime/rag/embed_chunks.py
runtime/rag/retrieve_context.py
runtime/rag/rag_dispatcher.py
```

`intake_requirements.py` は、要件定義書を `work/<採番ID>/design-document/` へ移動し、`context/*.json` を初期化します。

`task_runner.py` は、`task-plan.schema.json` に沿ったtask planを読み込み、sequential / parallel に処理して `process-report/` へ実行レポートを出力します。

`prepare_repository.py` は、target repository / branch を `work/<採番ID>/source/repository/` に準備します。

`compare_requirements.py` は、要件定義書と repository state の比較レポートを作成します。

`issue_manager.py` は、GitHub Issue draftを作成し、`--create` 指定時のみ GitHub CLI でIssueを作成します。

`create_issue_branch.py` は、Issue番号から `feature/issue-<issue-number>` branch を作成します。

`commit_changes.py` は、semantic commit message を検証してcommitします。

`normalize_documents.py` は、Markdown report を metadata 付きの RAG document JSON に変換します。

`chunk_documents.py` は、normalized document を retrieval しやすい chunk JSON に分割します。

`build_index.py` は、document / chunk を JSONL index として `rag/indexes/` に集約します。

`embed_chunks.py` は、chunk index から deterministic sparse embedding を生成し、`rag/embeddings/` に出力します。

`retrieve_context.py` は、JSONL chunk index と local embeddings から query に合うchunkを選び、Agent投入用の圧縮済みcontext packを `rag/retrieval/` に出力します。

`rag_dispatcher.py` は、開発前RAG読み込み用に複数queryを計画し、`retrieve_context.py` を並列実行して、圧縮済みcontext packを集約します。

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
- `retrieval-result.json` / `context-pack.json` / `context-pack.md` の生成
- `rag-load-dispatch.json` / `rag-load-dispatch.md` の生成
- 将来の embeddings / vector DB 移行に備えた metadata の標準化
