# Security Guidelines

- Do not commit real secrets.
- Restrict admin access with `admin_cidrs`.
- Replace placeholder passwords in approved secret sources before any shared environment.
- Record public exposure and owner before opening ports.
- Validate backup and restore before production use.
- Treat GitLab runner tokens, Jenkins credentials, Grafana admin password, and Zabbix DB password as secret material.

