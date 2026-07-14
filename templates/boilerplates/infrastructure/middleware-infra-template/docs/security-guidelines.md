# Security Guidelines

- Do not commit real Redis passwords.
- Reject default passwords during target implementation validation.
- Keep Redis internal-only unless exposure is explicitly approved.
- Do not log secret values.
- Do not emit secret values to evidence.
- Treat TLS as required for production-like plaintext credential paths.

