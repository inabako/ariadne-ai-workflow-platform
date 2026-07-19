# /runtime-health-check

## Purpose

Ariadne AI Workflow Platform 自身の runtime health を確認する自己診断workflowです。

このworkflowは、target repositoryの実装作業ではなく、AIワークフロー基盤そのものの健全性を確認します。

## 実行担当

主担当:

- `.github/agents/runtime-quality-gate-agent.prompt.md`

## 入力

必須引数はありません。

任意:

- `work_id`: Context First test-evidence 登録用のwork id。既定は `runtime-health-check`。
- `report_dir`: report出力先。既定は `runtime/.pytest_cache`。

## 処理概要

1. runtime pytestを実行する。
2. UT仕様書とpytest実体の同期を確認する。
3. 同期チェック結果をJSON / Markdown reportとして保存する。
4. Context First manifestへ `test-evidence` として登録する。
5. `workflow_doctor` を実行する。
6. `aiwfctl doctor` を実行する。
7. 日本語Markdown品質ガードを実行する。
8. 結果を人間と後続Agentが読める形で報告する。

## 成功条件

- pytestが全件passする。
- UT仕様書同期チェックが `status: ok` を返す。
- `workflow_doctor --fail-on-warning` がpassする。
- `aiwfctl doctor --json --fail-on-warning` がpassする。
- `pytest-ut-spec-sync-report.json` と `pytest-ut-spec-sync-report.md` が生成される。
- Context First manifestに `test-evidence` が登録される。
- 日本語Markdown品質ガードがpassする。

## 重要な境界

- GitHub Actions workflowは作成しない。
- `.github/workflows/` は使用しない。
- local evidenceは原則 `runtime/.pytest_cache` 配下に保存し、Git管理しない。repository root直下の `pytest.ini` と `.pytest_cache` は生成しない。
- runtime、tests、docs/reference、Context First、aiwfctl、schema、agent promptを変更した後の自己診断として使う。

## 標準コマンド

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime

.\tools\uv.cmd run --project . --group dev pytest tests -q

.\tools\uv.cmd run --project . --group dev python tools\pytest_ut_spec_sync.py `
  --spec ..\docs\reference\runtime-pytest-ut-case-specification.md `
  --runtime-root . `
  check `
  --repo-root .. `
  --work-dir runtime\.pytest_cache\runtime-health-check `
  --report .pytest_cache\pytest-ut-spec-sync-report.json `
  --markdown .pytest_cache\pytest-ut-spec-sync-report.md `
  --register-context `
  --required-context

.\tools\uv.cmd run --project . --group dev python workflow\workflow_doctor.py `
  --repo-root .. `
  --fail-on-warning

.\tools\uv.cmd run --project . --group dev python ctl.py `
  --repo-root .. `
  doctor `
  --json `
  --fail-on-warning

.\tools\uv.cmd run --project . --group dev python workflow\validate_output_language.py `
  --paths ..\docs\reference\runtime-pytest-ut-test-items.md ..\docs\reference\runtime-pytest-ut-case-specification.md ..\.github\schemas\README.md ..\.github\agents\runtime-quality-gate-agent.prompt.md `
  --fail-on-violation
```
