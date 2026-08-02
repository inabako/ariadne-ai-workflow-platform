# test_kubernetes_runtime.py

このファイルは `runtime/tests/test_kubernetes_runtime.py` の pytest node id と確認観点を記録します。

| Item | Value |
| --- | ---: |
| cases | 5 |

## Cases

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_kubernetes_runtime.py::test_kubernetes_assessment_detects_k3s_and_required_gaps
```

- 確認内容: k3s 指定の要件から target、port、未確定 container image を検出し、compatibility assessment と gap report を保存できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックの node id
  - source: `runtime/tests/test_kubernetes_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: k3s、service port、readiness probe を含む要件ファイル
- 期待結果: `kubernetes-compatibility-assessment.json` と `kubernetes-gap-report.md` が生成され、container image 未確定が critical gap として残る。

#### RT-UT-CASE-AUTO-002

- pytest node id:

```text
runtime/tests/test_kubernetes_runtime.py::test_kubernetes_generate_dry_run_e2e_and_evidence_flow
```

- 確認内容: 要件から manifest scaffold、dry-run evidence、integration E2E plan、Kubernetes evidence を一連の runtime artifact として生成できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックの node id
  - source: `runtime/tests/test_kubernetes_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: Kubernetes、image、port、resources、Secret boundary、Service 方針を含む要件ファイル
- 期待結果: `deployment.yaml` に image と port が反映され、`dry-run.json` は非実行の `dry-run` として保存され、`integration-test-plan.json` と `kubernetes/evidence.json` が生成される。

#### RT-UT-CASE-AUTO-003

- pytest node id:

```text
runtime/tests/test_kubernetes_runtime.py::test_kubernetes_generate_applies_allowed_spec_delta_only
```

- 確認内容: `spec-delta.json` の許可 key だけが Kubernetes manifest に反映され、許可外 key は ignored evidence として残ることを確認します。
- 入力値:
  - pytest node: 上記コードブロックの node id
  - source: `runtime/tests/test_kubernetes_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: namespace、replicas、health_path、許可外の secret_value を含む spec delta
- 期待結果: namespace、replicas、health_path は manifest に反映され、`secret_value` は `ignored_spec_delta_keys` に残り、manifest には出力されない。

#### RT-UT-CASE-AUTO-004

- pytest node id:

```text
runtime/tests/test_kubernetes_runtime.py::test_kubernetes_dry_run_execute_requires_human_check
```

- 確認内容: `kubectl dry-run` の実行モードでも Human Check がない場合は kubectl を呼ばず、`human-check-required` として止めることを確認します。
- 入力値:
  - pytest node: 上記コードブロックの node id
  - source: `runtime/tests/test_kubernetes_runtime.py`
  - fixture/arg: `monkeypatch`, `tmp_path` (temporary filesystem)
  - inline input: `execute=True`, `human_check=pending`
- 期待結果: `kubectl` は実行されず、dry-run evidence の `status` が `human-check-required` になる。

#### RT-UT-CASE-AUTO-005

- pytest node id:

```text
runtime/tests/test_kubernetes_runtime.py::test_aiwfctl_iac_kubernetes_routes
```

- 確認内容: `aiwfctl iac kubernetes generate` が CTL entrypoint から route され、JSON artifact path と manifest scaffold を返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックの node id
  - source: `runtime/tests/test_kubernetes_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: minimal registry、k8s/image/port を含む要件ファイル、CLI args
- 期待結果: exit code が `0` となり、`work/<work-id>/context/kubernetes-manifest-generation.json` と `implementation/kubernetes/manifests/deployment.yaml` が生成される。
