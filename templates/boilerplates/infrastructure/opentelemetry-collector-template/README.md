# OpenTelemetry Collector Infrastructure Template

This boilerplate builds an extensible OpenTelemetry Collector infrastructure unit.

It is a source template. Copy it to a work or target infrastructure directory before editing generated configuration, Terraform variables, or component selections.

## Responsibility

| Area | Responsibility |
| --- | --- |
| This template | Collector configuration, component manifests, distribution compatibility checks, Terraform deployment unit, smoke evidence |
| Platform templates | Grafana, Tempo, Prometheus, Loki, CI/CD, and dashboards |
| Application templates | Instrumented services that send OTLP telemetry |
| Ariadne Runtime | Template selection, copy, health routing, and evidence registration |

The Collector is not a storage backend or visualization platform. Tempo, Prometheus, Loki, and Grafana must remain separate templates or target-repository components.

## Initial Components

| Type | Component | Signals | Distribution |
| --- | --- | --- | --- |
| receiver | `otlp` | traces, metrics, logs | core |
| processor | `memory_limiter` | traces, metrics, logs | core |
| processor | `batch` | traces, metrics, logs | core |
| exporter | `debug` | traces, metrics, logs | core |
| extension | `health_check` | n/a | contrib-compatible |

## Usage

```powershell
make init
make catalog
make generate
make validate
make smoke
make evidence
```

Terraform validation:

```powershell
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
terraform -chdir=terraform plan -var-file=terraform.tfvars.example
```

## Generated Files

```text
config/generated/collector.yaml
config/generated/selection.resolved.yaml
config/generated/component-inventory.json
config/generated/generation-report.md
evidence/smoke-test-result.json
evidence/implementation-report.md
```

## Extension Contract

Each component package must contain:

```text
manifest.yaml
config.yaml
test-config.yaml
examples/
tests/
README.md
```

Register every component in `manifests/catalog.yaml`. A component directory without a catalog entry is treated as incomplete.

## Guardrails

- Do not store real secrets in this template.
- Do not switch to a custom distribution without Human Check.
- Do not include Tempo, Prometheus, Loki, or Grafana here.
- Do not consider Terraform success alone complete; run Collector health and telemetry smoke checks.
- Keep processor order explicit in the selection manifest.
- Treat `config/generated/` and `evidence/` as generated outputs after copying.
