# OTLP Receiver

Receives traces, metrics, and logs over OTLP gRPC and HTTP.

Default ports:

- gRPC: `4317`
- HTTP: `4318`

Security notes:

- Do not expose OTLP ports publicly without network policy and authentication.
- Treat incoming telemetry as untrusted input.
