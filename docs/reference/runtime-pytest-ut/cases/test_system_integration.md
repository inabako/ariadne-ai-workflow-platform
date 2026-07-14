# test_system_integration.py

このファイルは `runtime/tests/test_system_integration.py` のpytest node id単位UT仕様です。

## 対象runtime

- `runtime/workflow/system_integration.py`
- `runtime/ctl.py`

## ケース

#### RT-UT-CASE-576

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_system_integration_analyze_registers_context_and_emulator_candidates
```

- 確認内容: SDK解析contextを入力として、システム統合品質workflowが統合context、レポート、Context First manifest登録、AWS/GCP/Stripeのエミュレータ候補を生成することを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:47`
  - `work/issue-123/context/sdk-analysis-context.json`
  - cloud provider: `multiple`
  - cloud services: `s3`, `pubsub`, `unknown-service`
  - payment vendor: `stripe`
  - target repository under `work/issue-123/source/repository`
- 期待結果:
  - `artifact_type == "system-integration-context"`
  - target repository exists
  - cloud providerが `multiple`
  - payment vendorが `stripe`
  - emulator candidatesに `aws`、`gcp`、`stripe` が含まれる
  - Context First manifestに `system-integration` が登録される
  - `system-integration-report.md` と `integration-context.json` が生成される

#### RT-UT-CASE-577

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_system_integration_verify_with_emulator_classifies_coverage
```

- 確認内容: `--with-emulator` 相当のverifyで、既知サービスを `emulator_verified`、未登録サービスを `real_cloud_verification_required` として分類し、Integration Test evidence状態を記録することを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:68`
  - `work/issue-456/context/sdk-analysis-context.json`
  - target repository with tests and docs/evidence
  - `with_emulator=True`
- 期待結果:
  - `s3` が `emulator_verified`
  - `pubsub` が `emulator_verified`
  - `unknown-service` が `real_cloud_verification_required`
  - verification modeが `with-emulator`
  - evidence statusが `available`

#### RT-UT-CASE-578

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_aiwfctl_integration_verify_command
```

- 確認内容: `aiwfctl integration verify --work-id <work-id> --with-emulator` からsystem integration runtimeを呼び出し、CLI出力に生成context pathが表示されることを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:88`
  - tmp_path repository with `.git`
  - `runtime/registries/workflow_help.json`
  - `work/issue-789/context/sdk-analysis-context.json`
  - target repository under `work/issue-789/source/repository`
  - CLI args: `--repo-root <repo> integration verify --work-id issue-789 --with-emulator`
- 期待結果:
  - exit codeが0または2
  - CLI outputに `System Integration Quality` が含まれる
  - CLI outputに `work/issue-789/context/integration-context.json` が含まれる

#### RT-UT-CASE-579

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_system_integration_emulator_prepare_copies_templates_and_context
```

- 確認内容: SDK解析contextから選定されたAWS/GCP/Stripeのemulator templateを `work/<work-id>/test-environment/emulator/` へコピーし、証跡ディレクトリ、`emulator-context.json`、Context First登録を生成することを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:115`
  - repository rootの `templates/boilerplates/integration/cloud-emulators/`
  - `work/<work-id>/context/sdk-analysis-context.json`
  - `work/<work-id>/source/repository`
  - `work_dir=<tmp>/work/<work-id>`
- 期待結果:
  - `artifact_type == "emulator-setup-context"`
  - statusが `prepared`
  - prepared providerが `aws`、`gcp`、`stripe`
  - localstack / gcp-emulators / stripe-cli の `docker-compose.yml` がwork配下にコピーされる
  - `work/<work-id>/test-evidence/emulator/aws` が作成される
  - `work/<work-id>/context/emulator-context.json` が生成される
  - Context First manifestに `emulator-setup` が登録される

#### RT-UT-CASE-580

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_system_integration_emulator_prepare_does_not_overwrite_without_force
```

- 確認内容: 既にコピー済みのemulator work directoryがある場合、既定では上書きせず `existing` として記録し、ローカル変更を保持することを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:141`
  - existing path: `work/<work-id>/test-environment/emulator/localstack/`
  - marker file: `local-only.txt`
  - `force=False`
- 期待結果:
  - aws/localstackのprepare statusが `existing`
  - marker fileの内容が保持される
  - template本体ではなくwork配下のコピーだけが対象になる

#### RT-UT-CASE-581

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_aiwfctl_integration_emulator_prepare_command
```

- 確認内容: `aiwfctl integration emulator prepare --work-id <work-id>` からemulator prepare runtimeを呼び出し、CLI出力に生成context pathが表示され、templateがwork配下へコピーされることを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:165`
  - tmp_path repository with `.git`
  - temporary `templates/boilerplates/integration/cloud-emulators/*`
  - `work/<work-id>/context/sdk-analysis-context.json`
  - CLI args: `--repo-root <repo> integration emulator prepare --work-id <work-id>`
- 期待結果:
  - exit codeが0
  - CLI outputに `System Integration Emulator Prepare` が含まれる
  - CLI outputに `work/<work-id>/context/emulator-context.json` が含まれる
  - localstack templateが `work/<work-id>/test-environment/emulator/localstack/` へコピーされる

#### RT-UT-CASE-582

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_system_integration_emulator_health_checks_prepared_templates
```

- 確認内容: `emulator prepare` 後にhealthを実行し、展開済みtemplate、evidence directory、Context First manifest登録、health summaryを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:196`
  - repository rootの `templates/boilerplates/integration/cloud-emulators/`
  - `work/<work-id>/context/emulator-context.json`
  - prepared provider: `aws`, `gcp`, `stripe`
  - `work_dir=<tmp>/work/<work-id>`
- 期待結果:
  - `artifact_type == "emulator-health-context"`
  - statusが `ready`、`warning`、`human-check-required` のいずれか
  - checksに `aws`、`gcp`、`stripe` が含まれる
  - destination / evidence directory が存在する
  - compose file、`.env.example`、README、health docが検出される
  - Context First manifestに `emulator-health` が登録される
  - `emulator-health-context.json` と `test-evidence/emulator/health-summary.md` が生成される

#### RT-UT-CASE-583

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_system_integration_emulator_health_reports_missing_setup
```

- 確認内容: `emulator-context.json` が未生成の場合、healthがHuman Check requiredとして停止理由と証跡を出力することを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:226`
  - empty `work/<work-id>/`
  - `aiwfctl integration emulator prepare` 未実行
- 期待結果:
  - `artifact_type == "emulator-health-context"`
  - statusが `human-check-required`
  - checksが空
  - human_checksに `emulator-context.json` 未生成とprepare実行指示が含まれる
  - `emulator-health-context.json` と `health-summary.md` が生成される

#### RT-UT-CASE-584

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_aiwfctl_integration_emulator_health_command
```

- 確認内容: `aiwfctl integration emulator health --work-id <work-id>` からhealth runtimeを呼び出し、CLI出力と生成artifactを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:241`
  - tmp_path repository with `.git`
  - temporary `templates/boilerplates/integration/cloud-emulators/*`
  - `aiwfctl integration emulator prepare --work-id <work-id>` 実行済み
  - CLI args: `--repo-root <repo> integration emulator health --work-id <work-id>`
- 期待結果:
  - exit codeが0または2
  - CLI outputに `System Integration Emulator Health` が含まれる
  - CLI outputに `work/<work-id>/context/emulator-health-context.json` が含まれる
  - `emulator-health-context.json` と `test-evidence/emulator/health-summary.md` が生成される

#### RT-UT-CASE-585

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_system_integration_test_plan_creates_runbook_and_manifest
```

- 確認内容: integration context、emulator setup、emulator healthを前提に、Integration Test plan context、runbook、Context First manifest登録を生成することを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:284`
  - `work/<work-id>/context/integration-context.json`
  - `work/<work-id>/context/emulator-context.json`
  - `work/<work-id>/context/emulator-health-context.json`
  - target repository under `work/<work-id>/source/repository`
- 期待結果:
  - `artifact_type == "integration-test-plan-context"`
  - statusが `planned` または `human-check-required`
  - phaseが `environment-setup` から `cleanup` まで9段階で並ぶ
  - mutable操作を含むphaseにHuman Checkが設定される
  - `do_not_start_emulator_in_plan == true`
  - Context First manifestに `integration-test-plan` が登録される
  - `integration-test-plan-context.json` と `integration-test-runbook.md` が生成される

#### RT-UT-CASE-586

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_system_integration_test_plan_requires_prior_contexts
```

- 確認内容: 事前contextが未生成の場合、Integration Test planがHuman Check requiredとして不足contextと証跡を出力することを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:334`
  - empty `work/<work-id>/`
  - `integration-context.json` 未生成
  - `emulator-health-context.json` 未生成
- 期待結果:
  - `artifact_type == "integration-test-plan-context"`
  - statusが `human-check-required`
  - human_checksに `integration-context.json` 未生成が含まれる
  - human_checksに `emulator-health-context.json` 未生成が含まれる
  - `integration-test-plan-context.json` と `integration-test-runbook.md` が生成される

#### RT-UT-CASE-587

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_aiwfctl_integration_test_plan_command
```

- 確認内容: `aiwfctl integration test-plan --work-id <work-id>` からIntegration Test plan runtimeを呼び出し、CLI出力と生成artifactを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:349`
  - tmp_path repository with `.git`
  - temporary `templates/boilerplates/integration/cloud-emulators/*`
  - `aiwfctl integration verify --work-id <work-id> --with-emulator` 実行済み
  - `aiwfctl integration emulator prepare --work-id <work-id>` 実行済み
  - `aiwfctl integration emulator health --work-id <work-id>` 実行済み
  - CLI args: `--repo-root <repo> integration test-plan --work-id <work-id>`
- 期待結果:
  - exit codeが0または2
  - CLI outputに `System Integration Test Plan` が含まれる
  - CLI outputに `work/<work-id>/context/integration-test-plan-context.json` が含まれる
  - `integration-test-plan-context.json` と `test-evidence/integration-test/integration-test-runbook.md` が生成される

#### RT-UT-CASE-588

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_system_integration_finalize_collects_evidence_and_report
```

- 確認内容: Integration Test後のEvidenceを収集し、完了条件、違和感、Context First manifest登録、最終レポートを生成することを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:402`
  - `integration-context.json`
  - `emulator-health-context.json`
  - `integration-test-plan-context.json`
  - `test-evidence/integration-test/unit-pytest.log`
  - `test-evidence/integration-test/integration-test-result.md`
  - `test-evidence/integration-test/regression-report.md`
- 期待結果:
  - `artifact_type == "integration-finalization-context"`
  - statusが `complete`、`complete-with-warnings`、`incomplete`、`human-check-required` のいずれか
  - Evidence listに `integration-test-result.md` が含まれる
  - completion checksの `integration-test` が `pass`
  - `do_not_execute_tests_in_finalize == true`
  - Context First manifestに `integration-finalization` が登録される
  - `integration-finalization-context.json` と `system-integration-final-report.md` が生成される

#### RT-UT-CASE-589

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_system_integration_finalize_requires_prior_contexts
```

- 確認内容: finalizeに必要な事前contextが未生成の場合、Human Check requiredとして不足contextと最終証跡を出力することを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:443`
  - empty `work/<work-id>/`
  - `integration-context.json` 未生成
  - `emulator-health-context.json` 未生成
  - `integration-test-plan-context.json` 未生成
- 期待結果:
  - `artifact_type == "integration-finalization-context"`
  - statusが `human-check-required`
  - human_checksに3つの不足contextが含まれる
  - `integration-finalization-context.json` と `system-integration-final-report.md` が生成される

#### RT-UT-CASE-590

- pytest node id:

```text
runtime/tests/test_system_integration.py::test_aiwfctl_integration_finalize_command
```

- 確認内容: `aiwfctl integration finalize --work-id <work-id>` からfinalize runtimeを呼び出し、CLI出力と生成artifactを確認します。
- 入力値:
  - source: `runtime/tests/test_system_integration.py:459`
  - tmp_path repository with `.git`
  - `aiwfctl integration verify --work-id <work-id> --with-emulator` 実行済み
  - `aiwfctl integration emulator prepare --work-id <work-id>` 実行済み
  - `aiwfctl integration emulator health --work-id <work-id>` 実行済み
  - `aiwfctl integration test-plan --work-id <work-id>` 実行済み
  - `test-evidence/integration-test/integration-test-result.md`
  - CLI args: `--repo-root <repo> integration finalize --work-id <work-id>`
- 期待結果:
  - exit codeが0または2
  - CLI outputに `System Integration Finalization` が含まれる
  - CLI outputに `work/<work-id>/context/integration-finalization-context.json` が含まれる
  - `integration-finalization-context.json` と `reports/system-integration-final-report.md` が生成される
