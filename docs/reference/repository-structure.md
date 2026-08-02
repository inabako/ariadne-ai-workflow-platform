# Repository Structure

この repository は、Ariadne workflow を実行するための prompt、Skill、runtime、template、work artifact、RAG artifact を分けて管理します。

## Root Directories

```text
.ariadne/
  agents/      role-based Agent prompt definitions
  prompts/     slash command style workflow prompts
  schemas/     JSON Schema contracts for shared Agent data
  shared/      common principles and operational rules

.github/
  workflows/   GitHub Actions workflows
  ISSUE_TEMPLATE/
  PULL_REQUEST_TEMPLATE/
  copilot-instructions.md
  instructions/
  prompts/     thin VS Code Copilot prompt stubs only

.cursor/
              thin Cursor project rule bridge into AGENTS.md and .ariadne/

.clinerules/
              thin Cline bridge rules into AGENTS.md and .ariadne/
.claude/
              thin Claude Code / Claude IDE bridge into AGENTS.md and .ariadne/
.kiro/
              thin Kiro steering bridge into AGENTS.md and .ariadne/

docs/
  workflows/   workflow usage guides
  reference/   repository / runtime / data reference

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

skills/
  <skill-name>/SKILL.md
  skill-index.json

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

`.ariadne/` は Ariadne のAI workflow資産を置く場所です。GitHub Actions、Issue template、PR template、Copilot bridge などGitHubが直接読むファイルだけを `.github/` に残します。

`.cursor/rules/ariadne-bridge.mdc`、`.clinerules/`、`.claude/CLAUDE.md`、`.kiro/steering/ariadne-bridge.md` は、Cursor、Cline、Claude Code / Claude 対応IDE、Kiro から Ariadne を扱うための薄い bridge です。source of truth は `AGENTS.md`、`.ariadne/`、`skills/` に置き、各IDE向けファイルへ workflow 定義を複製しない方針です。

`templates/registries/` は、fresh checkoutでも `db/registries/registry.duckdb` を再生成できるようにするbootstrap sourceです。`db/registries/registry.duckdb` はruntimeが読むread modelで、生成物として扱います。

## Work Directory Model

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

## Base And Issue Work Folders

Corrective action や docs-sync では、base調査用とIssue作業用を分けます。

```text
work/<target-branch>/source/repository
work/issue-<issue-number>/source/repository
```

Git branch は:

```text
feature/issue-<issue-number>
```

`work/<target-branch>` をそのまま実装修正用に使わないことで、base調査artifactとIssue作業artifactを混ぜないようにします。

## Artifact Directories

| Directory | Purpose |
| --- | --- |
| `design-document/` | 設計書、要件定義書、architecture documents |
| `process-report/` | 比較結果、Issue draft、review report、工程ごとのreport |
| `test-evidence/` | テスト証跡、実行ログ、スクリーンショット、観測結果 |
| `test-specifications/` | テスト仕様書、test case table、entry / exit criteria |
| `source/` | clone、差分、実装対象source |
| `context/` | Agent間共有JSON、handoff、artifact index |

## Test Artifact Storage

テスト成果物の詳細な保存先は [Test Artifact Storage](test-artifact-storage.md) を参照します。

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

## Requirement Intake Location

```text
work/requirements/draft/
work/requirements/
```

`work/requirements/draft/` は未完成草案置き場です。

`/requirement-discovery` は草案から完成版要件定義書を作成する前に Noise Reduction Phase を実行し、結果を `work/requirements/draft/<draft-stem>-noise-reduction/` に保存します。

開発workflowに渡す完成版要件定義書は、`work/requirements/` に1件だけ置きます。

`Repository Control` がない要件定義書は受領しません。
