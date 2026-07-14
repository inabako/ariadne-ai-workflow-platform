# Backup And Restore

| Component | Backup Target | Restore Evidence |
| --- | --- | --- |
| GitLab | config, logs, data, runner config | repository, pipeline, runner registration |
| Jenkins | `jenkins_home`, CasC, jobs | job listing, sample job |
| Grafana | data volume, provisioning | datasource, dashboard |
| Zabbix | database, server config, templates | host, item, problem, recovery |

Production completion requires restore evidence, not only backup job success.

