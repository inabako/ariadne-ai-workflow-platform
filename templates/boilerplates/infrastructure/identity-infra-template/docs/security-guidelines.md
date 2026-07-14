# Security Guidelines

- Do not commit real passwords or password hashes.
- Separate administrator and application bind accounts.
- Do not pass administrator DN to applications.
- Keep LDAP internal-only unless exposure is explicitly approved.
- Do not log secret values.
- Do not emit secret values or real user data to evidence.
- Require encrypted credential paths for production-like environments.

