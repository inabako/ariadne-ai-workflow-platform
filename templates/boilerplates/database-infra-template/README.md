# Database Infrastructure Template

PostgreSQL と MySQL を、アプリケーション基盤・リアルタイム基盤・platform基盤から共通利用できる独立データ基盤として構築するためのboilerplateです。

このtemplateは `platform-infra-template/` の一部ではありません。DBを利用する側は接続契約を参照し、DB構築処理を重複実装しません。

## Responsibility

| Template | Responsibility |
| --- | --- |
| `nextjs-webapp-template/` | Web application本体 |
| `gateway-template/` | realtime gateway本体 |
| `realtime-gateway-infra-template/` | application runtime infrastructure |
| `platform-infra-template/` | GitLab / Jenkins / Grafana / Zabbix platform infrastructure |
| `database-infra-template/` | PostgreSQL / MySQL shared database infrastructure |
| `middleware-infra-template/` | Redis shared middleware infrastructure |
| `identity-infra-template/` | OpenLDAP identity / directory infrastructure |

## Terraform First

Terraform は database engine、environment、compose profile、backup / restore / migration / evidence policy を選択します。

Docker Compose は初期deploy targetです。PostgreSQL / MySQL の compose unit と integrated profile は、Terraform output に従ってコピー先で適用します。

## Directory

```text
database-infra-template/
  environments/
    local/
    dev/
    stg/
    prod/
  modules/
    database_catalog/
    docker_compose_manifest/
  common/
  postgresql/
  mysql/
  integrated/
  docs/
  scripts/
  tests/
```

## Usage

1. このdirectoryをtarget repositoryのdatabase infrastructure directoryへコピーします。
2. コピー先で `environments/<env>/terraform.tfvars.example` を `terraform.tfvars` へコピーします。
3. `enabled_engines` と `compose_profile` を選びます。
4. Terraformで構成を検証します。
5. Terraform output の `compose_files` と `validation_checks` に従って Docker Compose、backup / restore、migration、evidence取得を行います。

```powershell
terraform -chdir=environments/local init -backend=false
terraform -chdir=environments/local validate
terraform -chdir=environments/local plan
```

template検証:

```powershell
./scripts/check-template.ps1
```

## Guardrails

- 実password、token、完全な接続文字列をGit管理しない。
- `.env.example` と placeholder だけをtemplateに置く。
- 管理者ユーザーとアプリケーションユーザーを分離する。
- 起動確認だけで完了扱いにしない。
- Read / Write、永続化、backup、restore、migration、evidenceまで確認する。
- Evidenceへ secret または完全な接続文字列を出力しない。
- PostgreSQL固有処理とMySQL固有処理を混在させない。
