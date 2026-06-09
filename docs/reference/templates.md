# Templates

`templates/` は、workflow成果物のひな形を置く場所です。

## Template Directories

```text
templates/
  requirements/
    new-system/
    feature-maintenance/
  design-document/
  process-report/
  test-evidence/
  test-specifications/
  editorconfig/
```

## Current Templates

| Directory | Template | Purpose |
| --- | --- | --- |
| `templates/requirements/new-system/` | `robotics-new-system-requirements-template.md` | 新規system用の要件定義書 |
| `templates/requirements/feature-maintenance/` | `robotics-feature-maintenance-requirements-template.md` | 新機能 / 保守開発用の要件定義書 |
| `templates/design-document/` | `robotics-design-document-template.md` | 設計方針、責務境界、安全設計、test strategy |
| `templates/process-report/` | `robotics-process-report-template.md` | 工程入力、実行内容、判断、finding、handoff |
| `templates/test-evidence/` | `robotics-test-evidence-template.md` | テスト条件、結果、証跡、pass / fail判断 |
| `templates/test-specifications/` | `robotics-test-specification-template.md` | test strategy、test case table、PyQt QTest source plan、entry / exit criteria |
| `templates/editorconfig/` | `target-repository.editorconfig` | target repositoryのencoding / line ending補助 |

## Quality Rules

成果物は、後続Agent、人間、RAGが読み直せる形にします。

- front matterに project、receipt_id、repository、branch、commit、workflow、phase、status を残す。
- Intent、Decision、Reason、Evidence、Open QA を明示する。
- safety-critical な内容では STOP、communication loss、startup safe state、shutdown safe state を確認する。
- PyQt / Qt GUIでは、結合疎通試験のうちQTest化できるものと人間確認に残すものを分ける。
- 出力先は `work/<work-id>/` 配下の対応directoryにする。
- 生成後は可能な限り `work/<work-id>/context/artifact-index.json` に登録する。

## Requirements

要件定義書には `Repository Control` を必ず含めます。

Repository / branch は案件ごとに変わるため、`.env` ではなく要件定義書またはworkflow inputに書きます。

## Issue Template In Target Repositories

各target repositoryに `.github/ISSUE_TEMPLATE.md` がある場合、corrective action fixなどのIssue bodyの土台として使います。

Workflow側のfallback本文より、target repository固有のtemplateを優先します。
