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
```

`intake_requirements.py` は、要件定義書を `work/<採番ID>/design-document/` へ移動し、`context/*.json` を初期化します。

`task_runner.py` は、`task-plan.schema.json` に沿ったtask planを読み込み、sequential / parallel に処理して `process-report/` へ実行レポートを出力します。

`prepare_repository.py` は、target repository / branch を `work/<採番ID>/source/repository/` に準備します。

`compare_requirements.py` は、要件定義書と repository state の比較レポートを作成します。

`issue_manager.py` は、GitHub Issue draftを作成し、`--create` 指定時のみ GitHub CLI でIssueを作成します。

`create_issue_branch.py` は、Issue番号から `feature/issue-<issue-number>` branch を作成します。

`commit_changes.py` は、semantic commit message を検証してcommitします。

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
