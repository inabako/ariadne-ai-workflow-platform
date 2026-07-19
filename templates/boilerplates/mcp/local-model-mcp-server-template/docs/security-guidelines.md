# Security Guidelines

- Reject absolute paths and traversal.
- Reject secret-like filenames by default.
- Reject binary reads unless the target project explicitly adds a safe binary reader.
- Do not expose arbitrary command execution as a generic tool.
- Do not include model weights, real secrets, runtime logs, or generated artifacts in the template.

