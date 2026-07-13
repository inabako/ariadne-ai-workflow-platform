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
  shared-artifacts/
  iac/
  editorconfig/
  noise-reduction/
  boilerplates/
  gui-mode/
  web-svg-layout/
  self-improvement/
```

## Current Templates

| Directory | Template | Purpose |
| --- | --- | --- |
| `templates/requirements/new-system/` | `ariadne-new-system-requirements-template.md` | 新規system用の要件定義書 |
| `templates/requirements/feature-maintenance/` | `ariadne-feature-maintenance-requirements-template.md` | 新機能 / 保守開発用の要件定義書 |
| `templates/design-document/` | `ariadne-design-document-template.md` | 設計方針、責務境界、安全設計、test strategy |
| `templates/process-report/` | `ariadne-process-report-template.md`, `boilerplate-template-selection-report-template.md`, `nextjs-webapp-implementation-prep-template.md` | 工程入力、実行内容、判断、finding、handoff、boilerplate採用可否、Next.js画面実装前準備 |
| `templates/test-evidence/` | `ariadne-test-evidence-template.md` | テスト条件、結果、証跡、pass / fail判断 |
| `templates/test-specifications/` | `ariadne-test-specification-template.md` | test strategy、test case table、PyQt QTest source plan、entry / exit criteria |
| `templates/shared-artifacts/` | `shared-artifacts-index-template.md`, `port-definition-template.md`, `network-boundary-definition-template.md`, `architecture-decision-record-template.md` | 新システム設計からIaCへ渡す要件、port、network boundary、ADRの共有成果物 |
| `templates/iac/` | `software-inventory-template.md`, `communication-specification-template.md`, `realtime-iac-design-template.md`, `realtime-iac-test-specification-template.md` | リアルタイムシステム向けIaCの受領gate、設計、Docker Desktop / Linux / integration検証 |
| `templates/editorconfig/` | `target-repository.editorconfig` | target repositoryのencoding / line ending補助 |
| `templates/noise-reduction/` | `*-report-template.md`, `human-interview-sheet-template.md`, `project-glossary-template.md`, `readiness-report-template.md` | 要件定義前の未知用語、用語衝突、表記揺れ、資料矛盾、曖昧表現、Human Interview、Glossary、Readiness成果物 |
| `templates/boilerplates/` | `gateway-template/`, `nextjs-webapp-template/`, `pyqt-template/`, `realtime-gateway-infra-template/`, `platform-infra-template/`, `cloud-emulators/`, `flutter/` | 新規Go gateway / Next.js webapp / PyQt GUI / realtime gateway IaC / platform infrastructure / cloud emulator / Flutter multi-platform環境をtemplateから生成するためのboilerplate置き場 |
| `templates/gui-mode/` | `README.md` | SVG入力、GaC / UaC生成、親workflowへの安全な返却方法 |
| `templates/web-svg-layout/` | `README.md` | Web画面向けSVG入力、layout / React / Playwright候補、親workflowへの安全な返却方法 |
| `templates/self-improvement/` | `workflow-feedback-template.md`, `self-improvement-issue-template.md`, `self-improvement-checklist.md` | workflow摩擦のFeedback report、Issue body、採用判断checklist |

## Quality Rules

成果物は、後続Agent、人間、RAGが読み直せる形にします。

- front matterに project、receipt_id、repository、branch、commit、workflow、phase、status を残す。
- 人間向け本文は既定で日本語にし、front matterに `language: ja-JP` を残す。
- Intent、Decision、Reason、Evidence、Open QA を明示する。
- GitHub knowledge maintenanceでは、Issue / PR / comment / docs / CAR のsource reference、approval status、Git history non-modificationを明示する。
- safety-critical な内容では STOP、communication loss、startup safe state、shutdown safe state を確認する。
- PyQt / Qt GUIでは、結合疎通試験のうちQTest化できるものと人間確認に残すものを分ける。
- SVG入力がある場合はGaC / UaC GUI Modeで論理Layoutへ変換し、generated候補を既存sourceへ直接上書きしない。
- Web画面向けSVG入力がある場合はWeb SVG Layout Modeでresponsive layoutへ変換し、React / Playwright候補を既存sourceへ直接上書きしない。
- 要件定義前のNoise Reduction Phaseでは、`templates/noise-reduction/` を使い、Readinessが`BLOCK`の場合は完成版要件定義書へ進めない。
- 新システム実装では、`templates/boilerplates/` に一致するboilerplateがあるか確認し、採用または不採用の理由をprocess reportに残す。
- Next.js画面機能を実装する場合、Implementation前に `templates/process-report/nextjs-webapp-implementation-prep-template.md` を使い、新規/既存分類、画面契約、API契約、auth、env、test evidenceを確認する。
- Self-Improvement Workflowでは、Feedback reportを `work/feedback/` 直下に保存し、テンプレートは `templates/self-improvement/` を使う。
- IaC工程では、realtime gateway infrastructure が対象に含まれる場合 `realtime-gateway-infra-template/` を候補にし、shared artifacts、software inventory、secret source、firewall policy、rollbackを確認してからコピーする。
- IaC工程で開発基盤、CI/CD基盤、監視基盤が対象に含まれる場合 `platform-infra-template/` を候補にし、Terraform component selection、Docker Compose profile、admin CIDR、secret source、backup / restore、product別validation evidenceを確認してからコピーする。
- System Integration Quality workflowでクラウドまたは外部サービスSDKが検出された場合、`templates/boilerplates/cloud-emulators/` を候補にし、`work/<work-id>/test-environment/emulator/` へコピーしてから起動する。本番credentialは使わない。
- Flutter Multi-platform workflowでは、`templates/boilerplates/flutter/` を候補にし、`work/<work-id>/implementation/flutter-project/` へコピーする。対象platform未指定時は全platform対応と推測しない。
- テスト成果物の保存先は [Test Artifact Storage](test-artifact-storage.md) に従う。
- 出力先は `work/<work-id>/` 配下の対応directoryにする。
- 生成後は可能な限り `work/<work-id>/context/artifact-index.json` に登録する。
- 生成後は必要に応じて `uv run --project runtime python runtime/workflow/validate_output_language.py --paths work rag docs --fail-on-violation` で英語主体の成果物を検出する。

## Requirements

要件定義書には `Repository Control` を必ず含めます。

Repository / branch は案件ごとに変わるため、`.env` ではなく要件定義書またはworkflow inputに書きます。

## Issue Template In Target Repositories

各target repositoryに `.github/ISSUE_TEMPLATE.md` がある場合、corrective action fixなどのIssue bodyの土台として使います。

Workflow側のfallback本文より、target repository固有のtemplateを優先します。
