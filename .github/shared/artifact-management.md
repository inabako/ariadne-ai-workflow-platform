# Artifact Management

## Purpose

Agent が生成する document、review、test evidence、report の扱いを定義します。

artifact は、`templates/` にあるひな形を元に作成し、実案件ごとに `work/<採番ID>/` 配下へ保存します。

この共通ルールでは、artifact を迷子にしないための index 管理と保存先規約を定義します。

## Artifact Index Rule

生成物を作ったAgentは、可能な限り `artifact-index.schema.json` に沿って以下を記録します。

- artifact id
- title
- path
- type
- status
- owner agent
- depends on
- consumed by
- summary
- unresolved items

## Status Meaning

| Status | Meaning |
| --- | --- |
| draft | 作成中、未レビュー |
| in-review | review中 |
| approved | 承認済み |
| conditional-pass | 条件付きで次へ進める |
| rejected | 採用不可 |
| superseded | 新しいartifactに置き換え済み |

## Template Directories

成果物のひな形は以下に格納します。

```text
templates/
  design-document/
  process-report/
  test-evidence/
  test-specifications/
```

| Template Directory | Purpose |
| --- | --- |
| `templates/design-document/` | 設計書 |
| `templates/process-report/` | プロセス毎のレポート |
| `templates/test-evidence/` | テスト証跡 |
| `templates/test-specifications/` | テスト仕様書、テストケース表 |

## Work Artifact Directories

実案件の成果物は、採番IDごとに以下へ保存します。

```text
work/
  <採番ID>/
    design-document/
    process-report/
    test-evidence/
    test-specifications/
    source/
```

| Work Directory | Purpose |
| --- | --- |
| `work/<採番ID>/design-document/` | 案件固有の設計書 |
| `work/<採番ID>/process-report/` | 各phase / Agent の実行レポート |
| `work/<採番ID>/test-evidence/` | 実行したテストの証跡 |
| `work/<採番ID>/test-specifications/` | テスト仕様書、テストケース表 |
| `work/<採番ID>/source/` | 実装対象source、clone、差分、生成物 |

## Storage Rule

Agent は成果物を作るとき、原則として上記の work directory に保存します。

保存後、`artifact-index.schema.json` に `path`、`type`、`status`、`owner_agent` を記録します。

採番IDが未確定の場合、Agent は次のどちらかを行います。

- user に保存先を確認する
- 一時保存した上で `artifact-index` に `status: draft` として記録する

## Path Rule

artifact path は、可能な限り repository relative path で書きます。

別repositoryや外部ディレクトリに保存する場合は、absolute path を使っても構いません。ただし、その理由を summary に残します。
