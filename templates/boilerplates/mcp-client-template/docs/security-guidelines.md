# Security Guidelines

- Do not expose raw SDK session objects to application code.
- Do not treat resource URIs as local paths.
- Keep credentials in environment or a dedicated secret provider.
- Mask secret-like argument keys in audit logs.
- Applications must pass `server_id` and capability names explicitly.

