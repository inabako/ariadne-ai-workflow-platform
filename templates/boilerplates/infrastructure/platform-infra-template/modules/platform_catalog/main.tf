locals {
  service_catalog = {
    gitlab = {
      ports      = [8080, 2222]
      role       = "source-control-and-ci-entrypoint"
      validation = ["web-ui", "admin-login", "runner-registration", "test-pipeline"]
    }
    jenkins = {
      ports      = [8081, 50000]
      role       = "ci-cd-orchestration"
      validation = ["web-ui", "plugin-load", "agent-connection", "sample-job"]
    }
    grafana = {
      ports      = [3000]
      role       = "dashboard-and-alerting"
      validation = ["web-ui", "datasource", "dashboard", "test-metrics"]
    }
    zabbix = {
      ports      = [8082, 10050, 10051]
      role       = "monitoring-and-recovery"
      validation = ["server", "agent", "item", "problem", "recovery"]
    }
  }

  selected_services = {
    for name, service in local.service_catalog : name => merge(service, {
      environment   = var.environment
      platform_name = var.platform_name
      backup        = var.enable_backup
      secret_source = var.secret_source
      admin_cidrs   = var.admin_cidrs
    }) if contains(var.enabled_components, name)
  }

  validation_checks = flatten([
    for name, service in local.selected_services : [
      for check in service.validation : "${name}:${check}"
    ]
  ])
}

