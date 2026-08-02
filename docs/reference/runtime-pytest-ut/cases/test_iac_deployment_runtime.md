# test_iac_deployment_runtime.py

このファイルは `runtime/tests/test_iac_deployment_runtime.py` の pytest node id と確認観点を記録します。

| Item | Value |
| --- | ---: |
| cases | 3 |

## Cases

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_iac_deployment_runtime.py::test_iac_deployment_assessment_contract_and_gap_report
```

- 確認内容: 要件定義から app runtime assessment、deployment contract、IaC deployment gap report を作成できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックの node id
  - source: `runtime/tests/test_iac_deployment_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: web API、image、port、health、Secret boundary、resources、observability、E2E を含む要件ファイル
- 期待結果: `iac-deployment-contract.json` / `.md` が生成され、app name、image、health path が contract に保存される。

#### RT-UT-CASE-AUTO-002

- pytest node id:

```text
runtime/tests/test_iac_deployment_runtime.py::test_kubernetes_assessment_uses_iac_deployment_contract
```

- 確認内容: Kubernetes runtime が `iac-deployment-contract.json` を参照し、image、port、app name を manifest generation に反映できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックの node id
  - source: `runtime/tests/test_iac_deployment_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: k3s、web service、image、port、health endpoint を含む要件ファイル
- 期待結果: `kubernetes-compatibility-assessment.json` に deployment contract path が記録され、生成 manifest に contract の値が反映される。

#### RT-UT-CASE-AUTO-003

- pytest node id:

```text
runtime/tests/test_iac_deployment_runtime.py::test_aiwfctl_iac_deployment_routes
```

- 確認内容: `aiwfctl iac deployment contract` が CTL entrypoint から route され、deployment contract artifact を返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックの node id
  - source: `runtime/tests/test_iac_deployment_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: minimal registry、web/image/port を含む要件ファイル、CLI args
- 期待結果: exit code が `0` となり、`work/<work-id>/context/iac-deployment-contract.json` が生成される。
