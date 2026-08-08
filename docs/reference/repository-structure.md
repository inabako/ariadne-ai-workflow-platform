# リポジトリ構成

このリポジトリは、Ariadne workflow を実行するための prompt、Skill、runtime、template、作業成果物、RAG成果物を分けて管理します。

## ルートディレクトリ

```text
.ariadne/
  agents/      役割別 Agent prompt 定義
  prompts/     slash command 形式の workflow prompt
  schemas/     Agent 間共有データの JSON Schema 契約
  shared/      共通原則と運用ルール

.agents/
  README.md    AGENTS.md と .ariadne/ への薄い Codex bridge
  skills/
    <skill-name>/SKILL.md
    skill-index.json

.github/
  workflows/   GitHub Actions workflow
  ISSUE_TEMPLATE/
  PULL_REQUEST_TEMPLATE/
  copilot-instructions.md
  instructions/
  prompts/     VS Code Copilot 用の薄い prompt stub のみ

.cursor/
              AGENTS.md と .ariadne/ への薄い Cursor project rule bridge

.clinerules/
              AGENTS.md と .ariadne/ への薄い Cline bridge rule
.claude/
              AGENTS.md と .ariadne/ への薄い Claude Code / Claude IDE bridge
.kiro/
              AGENTS.md と .ariadne/ への薄い Kiro steering bridge

docs/
  workflows/   workflow 利用ガイド
  reference/   リポジトリ / runtime / data の参照資料

work/db/ariadne-knowledge-platform/
  rag/corrective-action-report/
  rag/external-web/
  rag/specialist-review/

db/registries/
  registry.duckdb

db/rag/
  normalized/
  chunks/
  optimized-chunks/
  jsonized/
  evidence/
  indexes/
  embeddings/
  retrieval/

runtime/
  common/
  environment/
  github/
  intake/
  rag/
  retrieval/
  scm/
  workflow/

templates/
  registries/
  requirements/
  design-document/
  noise-reduction/
  web-svg-layout/
  process-report/
  test-evidence/
  test-specifications/

work/
  requirements/
  <work-id>/
  issue-<issue-number>/
  close/
```

`.ariadne/` は Ariadne のAI workflow資産を置く場所です。`.agents/` は Codex 向けの薄い bridge と repo-local Skill の入口を置く場所です。GitHub Actions、Issue template、PR template、Copilot bridge などGitHubが直接読むファイルだけを `.github/` に残します。

`.cursor/rules/ariadne-bridge.mdc`、`.clinerules/`、`.claude/CLAUDE.md`、`.kiro/steering/ariadne-bridge.md` は、Cursor、Cline、Claude Code / Claude 対応IDE、Kiro から Ariadne を扱うための薄い bridge です。正本は `AGENTS.md`、`.ariadne/`、`.agents/skills/` に置き、各IDE向けファイルへ workflow 定義を複製しない方針です。

`templates/registries/` は、新規 checkout でも `db/registries/registry.duckdb` を再生成できるようにする bootstrap 元です。`db/registries/registry.duckdb` は runtime が読む参照用 read model で、生成物として扱います。

## 作業ディレクトリモデル

受付後は、案件ごとに `work/<work-id>/` を作ります。

```text
work/<work-id>/
  design-document/
  process-report/
  test-evidence/
  test-specifications/
  source/
  context/
    agent-context.json
    artifact-index.json
    scm-state.json
```

## Base調査用とIssue作業用フォルダ

Corrective action や docs-sync では、base調査用とIssue作業用を分けます。

```text
work/<target-branch>/source/repository
work/issue-<issue-number>/source/repository
```

Git branch は:

```text
feature/issue-<issue-number>
```

`work/<target-branch>` をそのまま実装修正用に使わないことで、base調査成果物とIssue作業成果物を混ぜないようにします。

## 成果物ディレクトリ

| ディレクトリ | 用途 |
| --- | --- |
| `design-document/` | 設計書、要件定義書、architecture document |
| `process-report/` | 比較結果、Issue draft、review report、工程ごとのreport |
| `test-evidence/` | テスト証跡、実行ログ、スクリーンショット、観測結果 |
| `test-specifications/` | テスト仕様書、test case table、entry / exit criteria |
| `source/` | clone、差分、実装対象source |
| `context/` | Agent間共有JSON、handoff、artifact index |

## テスト成果物の保存先

テスト成果物の詳細な保存先は [テスト成果物の保存先](test-artifact-storage.md) を参照します。

target repositoryにpushする永続証跡は、原則として次へ保存します。

```text
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/
  README.md
  test_specifications/
    unit-test-cases.md
    integration-test-cases.md
    human-check-list.md
  ut/
  integration/
    qtest/
    manual/
    startup/
  human_check/
```

存在しない場合、Knowledge Capture実行時に上記のscaffoldと各フォルダの `README.md` を自動生成します。
ただし、scaffold `README.md` だけではpush可能なテスト証跡とはみなしません。

## 要件受付場所

```text
work/requirements/draft/
work/requirements/
```

`work/requirements/draft/` は未完成草案置き場です。

`/requirement-discovery` は草案から完成版要件定義書を作成する前に Noise Reduction Phase を実行し、結果を `work/requirements/draft/<draft-stem>-noise-reduction/` に保存します。

開発workflowに渡す完成版要件定義書は、`work/requirements/` に1件だけ置きます。

`Repository Control` がない要件定義書は受領しません。
