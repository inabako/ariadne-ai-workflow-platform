# Kubernetes / k3s Runtime

要件定義に Kubernetes / k3s が指定された場合は、実装や E2E の前に `aiwfctl iac deployment` でアプリの最終的な実行状態を確認し、その後 `aiwfctl iac kubernetes` で実行環境の成立性を確認します。

この runtime は、実クラスタへの適用を目的にしません。要件から compatibility を評価し、gap を report に残し、constrained な manifest scaffold を生成し、`kubectl --dry-run` 相当の evidence を作ってから E2E / integration test runtime へ渡します。

manifest は `templates/boilerplates/infrastructure/kubernetes-app-template/` を source として展開します。runtime は template 本体を直接変更せず、要件定義または `spec-delta.json` から許可された仕様差分だけを取り込みます。

## Flow

```text
App Runtime Assessment
  -> Deployment Contract
  -> Compatibility Assessment
  -> Gap Report
  -> Kubernetes manifest scaffold
  -> kubectl dry-run evidence
  -> integration E2E plan
  -> final evidence
```

## Commands

```powershell
.\runtime\windows-script\aiwfctl.cmd iac kubernetes assess --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd iac kubernetes gap-report --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd iac kubernetes generate --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd iac kubernetes dry-run --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd iac kubernetes e2e-plan --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd iac kubernetes evidence --work-id <work-id>
```

Kubernetes runtime は `work/<work-id>/context/iac-deployment-contract.json` が存在する場合、その image、port、app name、health path、resources、storage 方針を優先して参照します。

仕様差分だけを明示して反映する場合:

```powershell
.\runtime\windows-script\aiwfctl.cmd iac kubernetes generate `
  --work-id <work-id> `
  --spec-delta work/<work-id>/context/spec-delta.json
```

`dry-run` は既定では kubectl を実行せず、実行予定 command と evidence を保存します。実際に `kubectl apply --dry-run=client -k ...` を実行する場合は Human Check を明示します。

```powershell
.\runtime\windows-script\aiwfctl.cmd iac kubernetes dry-run `
  --work-id <work-id> `
  --execute `
  --human-check approved
```

## Artifacts

| Artifact | Location |
| --- | --- |
| Compatibility Assessment | `work/<work-id>/context/kubernetes-compatibility-assessment.json` |
| Gap Report | `work/<work-id>/process-report/kubernetes-gap-report.json`, `.md` |
| Manifest Scaffold | `work/<work-id>/implementation/kubernetes/manifests/` |
| Dry-run Evidence | `work/<work-id>/test-evidence/kubernetes/dry-run.json`, `.md` |
| Integration E2E Plan | `work/<work-id>/test-specifications/integration-test-plan.json`, `.md` |
| Final Evidence | `work/<work-id>/test-evidence/kubernetes/evidence.json`, `.md` |

## Rules

- template source は `templates/boilerplates/infrastructure/kubernetes-app-template/` です。
- manifest は scaffold として扱い、秘密値や本番固有値を生成しません。
- image、port、probe、resources、Secret/ConfigMap、storage などが未確定でも削除せず、constrained として gap report に残します。
- `spec-delta.json` で manifest に反映できる key は `app_name`、`namespace`、`image`、`port`、`replicas`、`health_path`、`cpu_request`、`memory_request`、`cpu_limit`、`memory_limit`、`service_type` のみです。
- 許可外 key は `ignored_spec_delta_keys` として generation evidence に残し、manifest には出力しません。
- 実クラスタへの apply はこの runtime の責務外です。dry-run と E2E evidence を確認した後、Human Check を通して別工程で扱います。
- k3s は Kubernetes の軽量実行環境として評価します。k3s 固有の制約は gap report と E2E evidence に残します。
