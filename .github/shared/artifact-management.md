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
  noise-reduction/
  boilerplates/
    apps/
    services/
    infrastructure/
    integration/
    mcp/
  web-svg-layout/
```

| Template Directory | Purpose |
| --- | --- |
| `templates/design-document/` | 設計書 |
| `templates/process-report/` | プロセス毎のレポート |
| `templates/test-evidence/` | テスト証跡 |
| `templates/test-specifications/` | テスト仕様書、テストケース表 |
| `templates/noise-reduction/` | 要件定義前の未知用語、用語衝突、表記揺れ、資料矛盾、Human Interview、Glossary、Readiness |
| `templates/boilerplates/` | 新規service / app / IaC / MCP生成用のboilerplate source root |
| `templates/boilerplates/apps/` | Next.js / PyQt / Flutter app boilerplate |
| `templates/boilerplates/services/` | service boilerplate |
| `templates/boilerplates/infrastructure/` | realtime gateway / platform / database / middleware / identity IaC boilerplate |
| `templates/boilerplates/integration/` | integration test / emulator boilerplate |
| `templates/boilerplates/mcp/` | MCP Server / MCP Client / Agent Runtime / operation gateway boilerplate |
| `templates/web-svg-layout/` | Web画面向けSVG入力、responsive layout、React候補、Playwright候補 |

## Standard Template Files

| Template | Output Directory | Required Use |
| --- | --- | --- |
| `templates/design-document/ariadne-design-document-template.md` | `work/<採番ID>/design-document/` | architecture、responsibility boundary、safety design、test strategy を定義するとき |
| `templates/process-report/ariadne-process-report-template.md` | `work/<採番ID>/process-report/` | Agent / tool / review / comparison / implementation の工程結果を残すとき |
| `templates/test-evidence/ariadne-test-evidence-template.md` | `work/<採番ID>/test-evidence/` | test execution の条件、結果、証跡、pass / fail 判断を残すとき |
| `templates/test-specifications/ariadne-test-specification-template.md` | `work/<採番ID>/test-specifications/` | test strategy、test case table、entry / exit criteria を定義するとき |
| `templates/noise-reduction/` | `work/requirements/draft/<draft-stem>-noise-reduction/` | 要件review draft前にノイズ除去、Human Interview、Project Glossary、Readinessを作るとき |
| `templates/process-report/boilerplate-template-selection-report-template.md` | `work/<採番ID>/process-report/` | 新システム実装前にboilerplate template採用可否を判断するとき |
| `templates/web-svg-layout/` | `work/<採番ID>/web-ui/` | Web画面向けSVGからlayout / component / React / Playwright候補を作るとき |
| `templates/boilerplates/infrastructure/microservice-infra-template/` | target repositoryのIaC directoryまたは `work/<採番ID>/source/repository/` | realtime gateway infrastructure をtemplateから生成するとき |

## Artifact Quality Rule

artifact は、最低限以下を満たす必要があります。

- front matter に project、receipt_id、repository、branch、commit、workflow、phase、status を残す
- Intent、Decision、Reason、Evidence、Open QA を明示する
- safety-critical な内容では STOP、communication loss、startup safe state、shutdown safe state を確認する
- 要件定義前のNoise Reductionでは、Readinessが`BLOCK`のまま完成版要件定義書へ進めない
- boilerplate templateを使う場合は、コピー元、コピー先、採用理由、変更した責務境界、必要testを記録する
- IaC boilerplate templateを使う場合は、shared artifacts、software inventory、public exposure、secret source、firewall policy、rollback、Terraform validation結果も記録する
- Web SVG Layout Modeのgenerated候補はreview前にtarget sourceへ直接コピーしない
- 次のAgentまたは人間が、再探索せずに判断を継続できる粒度で書く

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
