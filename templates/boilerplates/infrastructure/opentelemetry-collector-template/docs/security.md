# Security

Check every component addition for:

- New listening ports
- Public exposure
- Authentication and TLS
- Secret fields
- File-system access
- Docker socket access
- Cloud credentials
- Telemetry fields that may contain personal, payment, token, or request body data

Do not put literal secrets in generated config.
