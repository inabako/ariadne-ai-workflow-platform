# Platform Infrastructure Template

開発基盤、CI/CD基盤、監視基盤を Terraform で選択し、Docker Compose deploy unit として構築するためのboilerplateです。

このtemplateは Ariadne 本体の機能ではなく、Ariadne workflow が選択・コピー・検証する Infrastructure Boilerplate です。`realtime-gateway-infra-template/` とは責務を分けます。

## Responsibility

| Template | Responsibility |
| --- | --- |
| `realtime-gateway-infra-template/` | アプリケーション実行基盤、gateway runtime、port、network、observability |
| `platform-infra-template/` | GitLab、Jenkins、Grafana、Zabbix などの開発・CI/CD・監視platform |
| `database-infra-template/` | PostgreSQL、MySQL などの共通DB基盤。platform製品からも参照するが、このtemplate配下には実装しない |
| `middleware-infra-template/` | Redis などの共通middleware基盤。platform製品から参照する場合も、このtemplate配下には実装しない |
| `identity-infra-template/` | OpenLDAP などのidentity / directory基盤。GitLab、Jenkins、Grafana等から参照する場合も、このtemplate配下には実装しない |

## Terraform First

Terraform は platform component の選択、環境別設定、compose manifest、validation handoff を管理します。

Docker Compose は初期deploy targetです。各製品の `docker-compose/compose.yaml` と `integrated-platform/**/compose.yaml` は、Terraformの選択結果に従ってコピー先で適用します。

## Directory

```text
platform-infra-template/
  environments/
    local/
    dev/
    stg/
    prod/
  modules/
    platform_catalog/
    docker_compose_manifest/
  common/
  gitlab/
  jenkins/
  grafana/
  zabbix/
  integrated-platform/
  docs/
  scripts/
```

## Components

| Component | Default Port | Purpose |
| --- | ---: | --- |
| GitLab | 8080 | source control、merge request、CI entrypoint |
| GitLab Runner | n/a | GitLab pipeline runner |
| Jenkins | 8081 | CI/CD orchestration |
| Grafana | 3000 | dashboards、alerts |
| Zabbix Web | 8082 | monitoring console |
| Zabbix Server | 10051 | monitoring server |
| Zabbix Agent | 10050 | monitored node agent |

## Usage

1. このdirectoryをtarget repositoryのinfra directoryへコピーします。
2. コピー先で `environments/<env>/terraform.tfvars.example` を `terraform.tfvars` へコピーします。
3. `enabled_components` と `compose_profile` を選びます。
4. Terraformを実行します。
5. Terraform output の `compose_files` と `validation_checks` に従って Docker Compose と証跡取得を行います。

```powershell
terraform -chdir=environments/local init -backend=false
terraform -chdir=environments/local validate
terraform -chdir=environments/local plan
```

template静的検証:

```powershell
./scripts/check-template.ps1 -SkipTerraform
```

Terraform が利用可能な環境:

```powershell
./scripts/check-template.ps1
```

## Guardrails

- 実secret、production password、private keyを生成しない。
- 共通処理は `common/` に置き、製品依存処理は各製品directoryへ置く。
- GitLab / Jenkins / Grafana / Zabbix の責務を `realtime-gateway-infra-template/` と混ぜない。
- validation結果は `work/<receipt-id>/test-evidence/` またはtarget repoの `docs/evidence/` に保存する。
- prodではadmin CIDR、secret source、backup、restore、rollback、public exposureをHuman Check対象にする。
