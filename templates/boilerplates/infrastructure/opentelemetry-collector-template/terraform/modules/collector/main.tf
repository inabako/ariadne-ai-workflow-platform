resource "docker_network" "collector" {
  name = var.network_name
}

resource "docker_image" "collector" {
  name = var.collector_image
}

resource "docker_container" "collector" {
  name  = var.collector_name
  image = docker_image.collector.image_id

  command = ["--config=/etc/otelcol/config.yaml"]

  env = [
    for key, value in var.environment_variables : "${key}=${value}"
  ]

  ports {
    internal = 4317
    external = var.otlp_grpc_port
  }

  ports {
    internal = 4318
    external = var.otlp_http_port
  }

  ports {
    internal = 13133
    external = var.health_check_port
  }

  volumes {
    host_path      = var.collector_config_path
    container_path = "/etc/otelcol/config.yaml"
    read_only      = true
  }

  networks_advanced {
    name = docker_network.collector.name
  }

  restart = "unless-stopped"
}
