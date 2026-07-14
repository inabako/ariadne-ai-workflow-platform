# Identity Infrastructure Template

OpenLDAP を、認証・組織情報・ユーザー・グループ管理のための directory service infrastructure として構築する boilerplate です。

この template は `middleware-infra-template/` の一部ではありません。OpenLDAP を利用する application / platform template は identity connection contract を参照し、OpenLDAP 構築処理を重複実装しません。

## Responsibility

| Template | Responsibility |
| --- | --- |
| `nextjs-app-template/` | Web application 本体 |
| `go-microservice-template/` | realtime gateway 本体 |
| `middleware-infra-template/` | Redis shared middleware infrastructure |
| `database-infra-template/` | PostgreSQL / MySQL shared database infrastructure |
| `identity-infra-template/` | OpenLDAP identity / directory infrastructure |
| `platform-infra-template/` | GitLab / Jenkins / Grafana / Zabbix platform infrastructure |

OpenLDAP は単なる login container ではありません。Base DN、OU、schema、user、group、service account、TLS、backup / restore を基盤責務として扱います。

## Terraform First

Terraform は organization、domain、Base DN、OU、TLS、compose profile、bootstrap、backup / restore、evidence policy、identity connection contract を選択します。

Docker Compose は初期 deploy target です。OpenLDAP compose unit と integrated profile は、Terraform output に従ってコピー先で適用します。

## Directory

```text
identity-infra-template/
  environments/
    local/
    dev/
    stg/
    prod/
  modules/
    identity_catalog/
    docker_compose_manifest/
  common/
  openldap/
  integrated/
  docs/
  scripts/
  tests/
```

## Usage

1. この directory を target repository の identity infrastructure directory へコピーします。
2. コピー先で `environments/<env>/terraform.tfvars.example` を `terraform.tfvars` へコピーします。
3. Base DN、OU、bind account、TLS、bootstrap、backup、evidence を選びます。
4. Terraform で構成を検証します。
5. Terraform output の `compose_files`、`identity_connection_contract`、`validation_checks` に従って Docker Compose、LDIF、bind/search、backup / restore、evidence 取得を行います。

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

- Base DN、OU、user/group placement を推測で確定しない。
- 管理者 DN と application bind account を分離する。
- 連携先 application に管理者 DN を渡さない。
- 本番 secret、password hash、private key、実ユーザーデータを Git 管理しない。
- `.env.example` と LDIF template には dummy data のみ置く。
- 起動確認だけで完了扱いにしない。
- Bind、user search、group search、membership、TLS、backup、restore、evidence まで確認する。
- TLS が必要な環境で certificate source が未定の場合は Human Check に送る。

