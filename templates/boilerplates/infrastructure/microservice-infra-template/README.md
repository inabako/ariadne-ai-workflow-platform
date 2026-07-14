# Realtime Gateway Infra Template

リアルタイム gateway / remote operation / 対象システム向け IaC の出発点です。
この template は、アプリケーション実装ではなく、network、runtime、security、observability、DNS の基盤構成を定義するために使います。

## 使い方

1. この directory を target repository の IaC 用 directory へコピーします。
2. コピー先だけを編集します。template 本体は案件実装中に直接編集しません。
3. `environments/<env>/terraform.tfvars.example` を `terraform.tfvars` へコピーし、案件固有値を設定します。
4. 実 secret は `.tfvars` に書かず、secret manager、CI secret、環境変数、または承認済みの secret source から注入します。
5. `make fmt ENV=<env>`、`make validate ENV=<env>`、`make plan ENV=<env>` の順で確認します。

## Scope

含めるもの:

- network boundary
- runtime infrastructure
- port exposure
- firewall / security group policy
- environment injection contract
- health check
- metrics
- logging
- restart policy
- optional DNS contract
- environment-specific configuration
- operation docs

含めないもの:

- application implementation
- business logic
- communication protocol implementation
- data transformation
- business flow
- application source code generation
- real secrets

## Directory

```text
microservice-infra-template/
  environments/
    local/
    dev/
    stg/
    prod/
  modules/
    network/
    runtime/
    security/
    observability/
    dns/
  scripts/
  docs/
```

## Runtime Priority

runtime は次の優先順で設計します。

1. Docker
2. systemd
3. k3s
4. ECS

最初の導入では Docker を標準にし、systemd / k3s / ECS は同じ変数契約から拡張できるようにします。

## Environments

| Environment | Policy |
| --- | --- |
| local | Docker Compose中心。DNSなし。firewall最小。mock connection可。 |
| dev | Dockerまたはsystemd。health / metrics有効。通信検証可能。 |
| stg | restart policy有効。firewall強化。log永続化。observability有効。 |
| prod | public ports最小。SSH制限。health / metricsは内部公開。alert hookとrollbackを必須扱い。 |

## Required Variables

| Variable | Purpose |
| --- | --- |
| `environment` | local / dev / stg / prod |
| `service_name` | gateway service name |
| `service_image` | container image or runtime artifact |
| `service_host` | host label or DNS target |
| `runtime_type` | docker / systemd / k3s / ecs |
| `health_port` | health endpoint port |
| `metrics_port` | metrics endpoint port |
| `inbound_tcp_ports` | allowed inbound TCP ports |
| `inbound_udp_ports` | allowed inbound UDP ports |
| `allowed_client_cidrs` | client source CIDRs |
| `allowed_device_cidrs` | device source CIDRs |
| `allowed_admin_cidrs` | admin source CIDRs |
| `enable_metrics` | metrics enable flag |
| `enable_dns` | DNS enable flag |
| `gateway_domain` | optional gateway domain |
| `enable_alert` | alert hook enable flag |
| `alert_webhook_url` | alert webhook placeholder or external secret reference |

## Security Policy

- 固定IP、固定port、固定CIDRを共通moduleに埋め込みません。
- public exposure は最小化し、共有成果物の port definition に追跡できるものだけ許可します。
- admin access は `allowed_admin_cidrs` で制限します。
- health / metrics は原則 internal exposure とし、公開が必要な場合は理由を設計書に残します。
- plaintext secret、token、private key、production password は生成しません。
- `.env` は生成せず、生成できるのは `.env.example` と placeholder だけです。

## Validation

```powershell
./scripts/check-template.ps1 -Env local
```

or

```bash
make fmt ENV=local
make validate ENV=local
make plan ENV=local
```

## Workflow Integration

新システム開発フローまたは `/realtime-iac` で IaC 対象が realtime gateway infrastructure を含む場合、この template を候補にします。
採用可否、コピー元、コピー先、変更した責務境界、必要 test は次に記録します。

```text
work/<receipt-id>/process-report/boilerplate-template-selection.md
```
