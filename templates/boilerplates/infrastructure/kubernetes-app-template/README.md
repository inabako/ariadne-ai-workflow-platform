# Kubernetes App Template

Kubernetes / k3s 向けの最小 manifest scaffold です。

この template は、本番値を直接持ちません。`aiwfctl iac kubernetes generate` が要件定義や `spec-delta.json` から許可された仕様差分だけを取り込み、`work/<work-id>/implementation/kubernetes/manifests/` に展開します。

## Files

```text
manifests/
  namespace.yaml
  deployment.yaml
  service.yaml
  kustomization.yaml
values.example.json
spec-delta.example.json
docs/
  gap-checklist.md
  dry-run-runbook.md
```

## Spec Delta

仕様差分として取り込める key は以下です。

- `app_name`
- `namespace`
- `image`
- `port`
- `replicas`
- `health_path`
- `cpu_request`
- `memory_request`
- `cpu_limit`
- `memory_limit`
- `service_type`

これ以外の key は manifest に反映しません。環境固有値や秘密値は `Secret` / `ConfigMap` などの外部注入で扱い、この template には含めません。
