locals {
  component_compose_files = {
    gitlab  = "gitlab/docker-compose/compose.yaml"
    jenkins = "jenkins/docker-compose/compose.yaml"
    grafana = "grafana/docker-compose/compose.yaml"
    zabbix  = "zabbix/docker-compose/compose.yaml"
  }

  integrated_compose_files = {
    development-platform   = "integrated-platform/development-platform/compose.yaml"
    observability-platform = "integrated-platform/observability-platform/compose.yaml"
    full-platform          = "integrated-platform/full-platform/compose.yaml"
  }

  selected_component_files = [
    for component, file in local.component_compose_files : file
    if contains(var.enabled_components, component)
  ]
}

