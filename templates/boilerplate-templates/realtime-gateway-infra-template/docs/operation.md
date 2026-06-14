# Operation Guide

## 起動前確認

- shared artifacts の port definition と network boundary が最新である
- `terraform.tfvars` に実 secret が含まれていない
- `allowed_admin_cidrs` が運用者の許可範囲だけを含む
- health / metrics の公開範囲が設計書と一致している
- rollback 手順が対象 runtime に合わせて定義されている

## 標準操作

```powershell
make fmt ENV=dev
make validate ENV=dev
make plan ENV=dev
make apply ENV=dev
```

本番反映では、`plan` 結果を human review し、public exposure、firewall、secret source、rollback を確認してから `apply` します。

## 障害時確認

- service / container status
- connection count
- error count
- restart count
- last communication time
- firewall deny log
- health endpoint
- metrics endpoint

## Rollback

rollback は target runtime ごとに具体化します。

- Docker: previous image tag と compose config に戻す
- systemd: previous unit file と artifact に戻す
- k3s: previous manifest / Helm release に戻す
- ECS: previous task definition に戻す

rollback 実行後は health check、metrics、主要通信の疎通を確認します。
