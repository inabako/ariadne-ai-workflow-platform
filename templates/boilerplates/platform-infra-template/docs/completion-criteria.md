# Completion Criteria

## Boilerplate

- `platform-infra-template/` is copied into the target repository.
- Terraform `fmt`, `validate`, and `plan` pass for the selected environment.
- Docker Compose profile is selected from Terraform output.
- Common and product-specific responsibilities remain separated.
- Evidence paths are recorded.

## GitLab

- Web UI is reachable.
- Admin login is confirmed.
- Runner is registered.
- Test Pipeline succeeds.

## Jenkins

- Web UI is reachable.
- Plugins load successfully.
- Agent connection succeeds when agents are used.
- Sample Job succeeds.

## Grafana

- Web UI is reachable.
- Datasource is registered.
- Dashboard is displayed.
- Test metrics are visible.

## Zabbix

- Server starts.
- Agent connects.
- Item data is collected.
- Problem and recovery are verified.

