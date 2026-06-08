# Repository Structure

この repository は、robotics workflow を実行するための prompt、Skill、runtime、template、work artifact、RAG artifact を分けて管理します。

## Root Directories

```text
.github/
  agents/      role-based Agent prompt definitions
  prompts/     slash command style workflow prompts
  schemas/     JSON Schema contracts for shared Agent data
  shared/      common principles and operational rules

docs/
  workflows/   workflow usage guides
  reference/   repository / runtime / data reference

rag/
  corrective-action-report/
  external-web/
  normalized/
  chunks/
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
  requirements/
  design-document/
  process-report/
  test-evidence/
  test-specifications/

work/
  requirements/
  <work-id>/
  issue-<issue-number>/
  close/
```

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

## Requirement Intake Location

```text
work/requirements/draft/
work/requirements/
```

`work/requirements/draft/` は未完成草案置き場です。

開発workflowに渡す完成版要件定義書は、`work/requirements/` に1件だけ置きます。

`Repository Control` がない要件定義書は受領しません。
