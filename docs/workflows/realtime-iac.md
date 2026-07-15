# Realtime IaC

リアルタイムシステム向けの Docker Compose、systemd、firewall、reverse proxy、TURN / STUN、logrotate、monitoring などの IaC を扱う workflow です。

## Command

```text
/realtime-iac
```

## Required Input

完成版の要件定義書が必要です。

```text
work/requirements/<completed-requirements>.md
```

要件定義書には `Repository Control` を含めます。

`Repository Control` では、既存repositoryへ入れるのか、GitHubサイト側で作成済みの新規repositoryへ最終pushするのかを明確にします。

新規repositoryへpushする場合:

```text
Repository Mode: precreated-new
GitHub Owner: <owner>
GitHub Repository: <new-repository-name>
Initial Branch: main
Visibility: private
```

既存repositoryへ入れる場合:

```text
Repository Mode: existing
GitHub Repository URL: https://github.com/<owner>/<repo>.git
Target Branch: develop
```

## Context First Environment Gate

`/realtime-iac` は Docker、Linux runtime、network、systemd、firewall、observability など環境差が大きいworkflowです。
そのため、IaC設計・生成・検証へ進む前に Docker 用の environment-selection context を必須にします。

```powershell
aiwfctl env select docker --work-id <receipt-id>
uv run --project runtime python runtime/workflow/context_first.py `
  --work-dir work/<receipt-id> `
  require-environment --environment docker
```

`environment-selection.environment` が `docker` ではない場合、IaC設計へ進まずHuman Checkへ戻します。

## Shared Artifact Gate

IaC設計や生成へ進む前に、次の共有成果物が必要です。

- communication specification
- port definition list
- network boundary definition
- software inventory

推奨成果物:

- protocol definition
- public / private network policy
- system architecture diagram
- architecture decision records

`software inventory` では、基盤に入れるソフトウェアを要件受領の段階で確認します。

最低限の確認項目:

- software name
- purpose
- owner / responsibility boundary
- version or version policy
- runtime unit: container / systemd service / host package / proxy / sidecar / monitoring job
- required ports / protocols
- required environment variables and secret placeholders
- persistence / volume needs
- health check method
- license or distribution constraint when relevant

要件定義書に同等の構造が無い場合は、次のテンプレートを使います。

```text
templates/workflows/iac/software-inventory-template.md
templates/workflows/iac/communication-specification-template.md
```

不足している場合、AIは推測で補完せず、`work/<receipt-id>/design-document/open-questions.md` を作成して停止します。

## Flow

```text
Intake
  -> Repository Mode Decision
  -> Existing Repo: Repository Sync / Requirement Comparison / Issue / Working Branch
  -> Precreated New Repo: Local Bootstrap Workspace / Initial Push / Issue / Working Branch
  -> RAG Load / Prior Findings
  -> Shared Artifact Gate
  -> Requirements Organization
  -> Network / Security Design
  -> Runtime Design
  -> Observability Design
  -> Boilerplate Template Selection
  -> IaC Implementation
  -> Security Review
  -> Docker Desktop Validation
  -> Linux Runtime Validation
  -> Integration Validation
  -> Documentation
  -> Semantic Commit
```

## Boilerplate Template Selection

IaC実装前に、承認済みdesignとshared artifactsに対して利用可能なboilerplate templateを確認します。

候補:

| 対象 | Template | 詳細Docs |
| --- | --- | --- |
| Realtime gateway IaC / infrastructure | `templates/boilerplates/infrastructure/microservice-infra-template/` | `docs/workflows/realtime-iac.md` |
| Development / CI/CD / observability platform infrastructure | `templates/boilerplates/infrastructure/platform-infra-template/` | `docs/workflows/realtime-iac.md` |
| PostgreSQL / MySQL shared database infrastructure | `templates/boilerplates/infrastructure/database-infra-template/` | `docs/workflows/realtime-iac.md` |
| Redis shared middleware infrastructure | `templates/boilerplates/infrastructure/middleware-infra-template/` | `docs/workflows/realtime-iac.md` |
| OpenLDAP identity / directory infrastructure | `templates/boilerplates/infrastructure/identity-infra-template/` | `docs/workflows/realtime-iac.md` |

出力:

```text
work/<receipt-id>/process-report/boilerplate-template-selection.md
```

ルール:

- realtime gateway infrastructure が対象に含まれる場合は `microservice-infra-template/` を候補にします。
- GitLab、Jenkins、Grafana、Zabbixなどの開発・CI/CD・監視platformが対象に含まれる場合は `platform-infra-template/` を候補にします。
- PostgreSQL、MySQL、DB connection contract、backup / restore、migrationが対象に含まれる場合は `database-infra-template/` を候補にします。
- Redis、cache、session、temporary state、Pub/Sub補助、middleware connection contract、TTL、eviction、persistence、backup / restoreが対象に含まれる場合は `middleware-infra-template/` を候補にします。
- OpenLDAP、directory service、Base DN、OU、user / group、application bind account、identity connection contract、TLS、backup / restoreが対象に含まれる場合は `identity-infra-template/` を候補にします。
- template directoryが存在する場合は、templateをコピーしてコピー先だけを編集します。
- template本体は直接編集しません。
- templateが対象に合わない場合は、`decision: traditional-coding` と理由を記録して従来どおりIaCを生成します。
- template採用時も、shared artifacts、software inventory、public exposure、secret source、firewall policy、rollback、test case table、evidence planを省略しません。
- platform infrastructure template採用時は、Terraform component selection、Docker Compose profile、admin CIDR、secret source、backup / restore、product別validation evidenceを記録します。
- database infrastructure template採用時は、DB engine、DB version、database name、app user、connection source、persistence、backup / restore、migration、connection contract、secret redaction、evidenceを記録します。
- middleware infrastructure template採用時は、Redis purpose、version、connection source、auth secret ref、maxmemory、eviction policy、TTL、persistence、backup / restore、connection contract、secret redaction、evidenceを記録します。
- identity infrastructure template採用時は、OpenLDAP version、organization、domain、Base DN、OU layout、bind account separation、TLS、LDIF、backup / restore、identity connection contract、secret redaction、evidenceを記録します。
- `.env`、real secret、production password、private keyは生成しません。

選定結果が未記録の場合、IaC Implementationへ進みません。

## Repository Modes

### Existing Repository Mode

既存GitHub repositoryにIaCを追加する場合です。

```text
Repository Sync
  -> Requirement Comparison
  -> GitHub Issue Draft / Create
  -> feature/issue-<issue-number> Branch Create
  -> Implementation / Validation
  -> Push issue branch
  -> Pull Request
```

### Precreated New Repository Mode

GitHubサイト側で先に作成した新しいrepositoryを指定し、最終的にそこへpushする場合です。

```text
Precreated owner/repository confirmation
  -> Local workspace generation under work/<receipt-id>/source/repository/
  -> Initial commit and initial branch push
  -> GitHub Issue Draft / Create
  -> feature/issue-<issue-number> Branch Create
  -> Continue implementation / validation on issue branch
  -> Push issue branch
  -> Pull Request
```

このmodeでは、GitHub repositoryは人間が先に作成します。`feature/issue-<issue-number>` branch は、initial branch pushの後に作ります。空repositoryにはbranchの起点になるcommitが無いためです。

補助CLI:

```powershell
uv run --project runtime python runtime/scm/bootstrap_repository.py --work-id <receipt-id> --github-repo <owner>/<repo> --push --human-check approved
uv run --project runtime python runtime/github/issue_manager.py --work-id <receipt-id> --github-repo <owner>/<repo> --title "<title>" --flow-label iac --create
uv run --project runtime python runtime/scm/create_issue_branch.py --work-id <receipt-id> --issue-number <number> --github-repo <owner>/<repo> --base-branch main --link-to-issue
```

## Main Artifacts

Design:

```text
work/<receipt-id>/design-document/requirements.md
work/<receipt-id>/design-document/open-questions.md
work/<receipt-id>/design-document/network-design.md
work/<receipt-id>/design-document/security-design.md
work/<receipt-id>/design-document/firewall-policy.md
work/<receipt-id>/design-document/runtime-design.md
work/<receipt-id>/design-document/docker-compose-design.md
work/<receipt-id>/design-document/observability-design.md
work/<receipt-id>/design-document/monitoring-policy.md
```

Review and validation:

```text
work/<receipt-id>/process-report/security-review.md
work/<receipt-id>/test-specifications/iac-test-cases.md
work/<receipt-id>/test-evidence/docker-test-plan.md
work/<receipt-id>/test-evidence/docker-test-result.md
work/<receipt-id>/test-evidence/runtime-validation.md
work/<receipt-id>/test-evidence/integration-test.md
work/<receipt-id>/context/
```

Target repository examples:

```text
docker-compose.yml
.env.example
deploy/systemd/*.service
deploy/reverse-proxy/*
deploy/turn-stun/*
deploy/logrotate/*
deploy/monitoring/*
docs/evidence/issue-<issue-number>/
```

## Stop Rules

次が未定義なら先へ進めません。

- communication specification
- port definition list
- network boundary definition
- software inventory
- public exposure scope
- system responsibility boundary
- repository mode
- planned repository name
- initial branch
- TLS / auth model
- secret source and rotation
- firewall policy
- validation target for Docker Desktop and Linux runtime

`.env` や実secretが必要になる場合も停止します。生成できるのは `.env.example` と placeholder だけです。

## Test Strategy

検証は次の順序で行います。

1. Docker Desktop validation
2. Linux runtime validation
3. Integration validation

Docker Desktop validation:

- `docker compose config`
- container startup
- health check
- environment variable loading
- port binding
- log output
- restart policy
- network isolation
- UDP communication when applicable

Linux runtime validation:

- systemd
- firewall
- logrotate
- service restart
- health check
- host permission

Integration validation:

- control communication
- video communication
- telemetry communication
- gateway communication
- failure recovery

## Evidence Storage

Target repositoryへ残す永続証跡:

```text
docs/evidence/issue-<issue-number>/test_specifications/iac-test-cases.md
docs/evidence/issue-<issue-number>/integration/docker-desktop/
docs/evidence/issue-<issue-number>/integration/linux-runtime/
docs/evidence/issue-<issue-number>/integration/iac-integration/
docs/evidence/issue-<issue-number>/human_check/
```

`iac-test-cases.md` には、Docker Desktop、Linux runtime、integration、human check のどれに属するかを明示します。

## Issue Title

IaC workflow の Issue title は、次のprefixを付けます。

```text
[IaC] <issue-title>
```

## Specialist Review Gate

次の領域に依存する場合は、実装前または検証前に Specialist Agent review を使います。

- realtime network protocol
- firewall / routing / NAT
- TURN / STUN
- reverse proxy
- TLS / auth / secret handling
- Docker networking
- systemd / Linux service behavior
- logrotate / monitoring
- evidence strategy

review結果は次に保存します。

```text
work/<receipt-id>/process-report/specialist-review-<domain>.md
```

High / critical finding がある場合、Shared Artifact Gate、Network / Security Design、Runtime Design、または Test Strategy へ戻します。

## Source Skill

```text
skills/realtime-iac/SKILL.md
```
