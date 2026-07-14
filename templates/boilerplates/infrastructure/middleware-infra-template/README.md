# Middleware Infrastructure Template

Redis を、アプリケーション横断の cache / session / temporary state / Pub/Sub 補助基盤として構築するための boilerplate です。

この template は `identity-infra-template/` や `database-infra-template/` の一部ではありません。Redis を利用する側は connection contract を参照し、Redis 構築処理を重複実装しません。

## Responsibility

| Template | Responsibility |
| --- | --- |
| `nextjs-app-template/` | Web application 本体 |
| `go-microservice-template/` | realtime gateway 本体 |
| `database-infra-template/` | PostgreSQL / MySQL shared database infrastructure |
| `middleware-infra-template/` | Redis shared middleware infrastructure |
| `identity-infra-template/` | OpenLDAP identity / directory infrastructure |
| `platform-infra-template/` | GitLab / Jenkins / Grafana / Zabbix platform infrastructure |

Redis は RDB の代替ではありません。永続性、消失許容度、TTL、eviction policy は用途ごとに要件定義します。

## Terraform First

Terraform は Redis の用途、environment、compose profile、persistence、backup / restore、evidence policy、connection contract を選択します。

Docker Compose は初期 deploy target です。Redis compose unit と integrated profile は、Terraform output に従ってコピー先で適用します。

## Directory

```text
middleware-infra-template/
  environments/
    local/
    dev/
    stg/
    prod/
  modules/
    redis_catalog/
    docker_compose_manifest/
  common/
  redis/
  integrated/
  docs/
  scripts/
  tests/
```

## Usage

1. この directory を target repository の middleware infrastructure directory へコピーします。
2. コピー先で `environments/<env>/terraform.tfvars.example` を `terraform.tfvars` へコピーします。
3. Redis の purpose、persistence、memory、backup、evidence を選びます。
4. Terraform で構成を検証します。
5. Terraform output の `compose_files`、`redis_connection_contract`、`validation_checks` に従って Docker Compose、backup / restore、evidence 取得を行います。

```powershell
terraform -chdir=environments/local init -backend=false
terraform -chdir=environments/local validate
terraform -chdir=environments/local plan
```

template 検証:

```powershell
./scripts/check-template.ps1
```

## Guardrails

- 実 password、token、完全な接続文字列を Git 管理しない。
- `.env.example` と placeholder だけを template に置く。
- 外部公開は default で無効にする。
- 起動確認だけで完了扱いにしない。
- PING、SET / GET、TTL、memory policy、persistence、backup、restore、evidence まで確認する。
- 完全な揮発性 cache として backup 不要にする場合は、要件定義と evidence に理由を残す。
- Session 永続保持と `allkeys-lru` のような消失リスクがある組み合わせは Human Check に送る。
- 初期実装では Redis ACL を完全実装しない。ACL が必要な場合は追加設計と Human Check を行う。

