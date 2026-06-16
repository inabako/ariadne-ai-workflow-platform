# Gateway Template

This is a boilerplate for Go gateway services. Copy this directory to a new service directory, then edit only the copy.

## Responsibilities

- `cmd/gateway`: process entrypoint only
- `internal/app`: composition, lifecycle, and graceful shutdown
- `internal/config`: environment-backed configuration
- `internal/logger`: structured logging
- `internal/transport`: protocol parsing and external I/O boundaries
- `internal/dispatcher`: command and event routing
- `internal/session`: connection/session state
- `internal/worker`: asynchronous processing
- `internal/health`: `/healthz` and `/readyz`
- `internal/metrics`: counters and future metrics hooks

## Default Ports

| Purpose | Default |
| --- | --- |
| HTTP health | `8080` |
| WebSocket | `8081` |
| UDP control | `5005` |
| UDP announce | `5006` |
| UDP telemetry | `5007` |

## Commands

```powershell
make run
make test
make lint
make build
make docker-build
make docker-up
make docker-down
```

## Environment

See `configs/config.example.env`.

## Test Policy

Unit tests use package-level fakes and do not require external network services. Integration tests that open real sockets should be added separately and mapped to issue test cases.

## Extension Points

- Replace protocol parsing in `internal/transport/udp` and `internal/transport/websocket`.
- Add service-specific handlers in `internal/dispatcher`.
- Add bounded queues and fan-out workers under `internal/worker`.
- Add Prometheus or OpenTelemetry exporters under `internal/metrics`.

## Guardrails

- Do not put business logic in `cmd/gateway/main.go`.
- Do not put business decisions in transport packages.
- Do not start goroutines without context cancellation.
- Do not change ports, protocols, or safety behavior without approved architecture.
