# test_iac_prepare_runtime.py

このファイルは `runtime/tests/test_iac_prepare_runtime.py` の pytest node id と確認観点を記録します。

| Item | Value |
| --- | ---: |
| cases | 3 |

## Cases

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_iac_prepare_runtime.py::test_iac_prepare_runs_deployment_then_kubernetes_flow
```

- 確認内容: `iac prepare` が Deployment Contract を作成した後、Kubernetes/k3s 指定を検出して manifest scaffold、dry-run evidence、integration E2E plan まで進めることを確認します。
- 入力値:
  - pytest node: 上記コードブロックの node id
  - source: `runtime/tests/test_iac_prepare_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: k3s、web API、image、port、health、Secret boundary、resources、E2E を含む要件ファイル
- 期待結果: `iac-prepare-report.json`、`iac-deployment-contract.json`、Kubernetes manifest、`integration-test-plan.json` が生成される。

#### RT-UT-CASE-AUTO-002

- pytest node id:

```text
runtime/tests/test_iac_prepare_runtime.py::test_iac_prepare_without_provider_stops_after_common_contract
```

- 確認内容: provider-specific IaC が検出されない場合、共通 Deployment Contract まで作成し、Kubernetes manifest 生成には進まないことを確認します。
- 入力値:
  - pytest node: 上記コードブロックの node id
  - source: `runtime/tests/test_iac_prepare_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: web、image、port のみを含む要件ファイル
- 期待結果: provider が `none` となり、next action に provider 詳細の追加または明示 command 実行が記録される。

#### RT-UT-CASE-AUTO-003

- pytest node id:

```text
runtime/tests/test_iac_prepare_runtime.py::test_aiwfctl_iac_prepare_routes
```

- 確認内容: `aiwfctl iac prepare` が CTL entrypoint から route され、prepare report artifact を返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックの node id
  - source: `runtime/tests/test_iac_prepare_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: minimal registry、k8s/web/image/port を含む要件ファイル、CLI args
- 期待結果: exit code が `0` となり、`work/<work-id>/process-report/iac-prepare-report.json` が生成される。
