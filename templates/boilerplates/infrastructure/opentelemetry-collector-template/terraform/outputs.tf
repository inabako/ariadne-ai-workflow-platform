output "collector_name" {
  value = module.collector.collector_name
}

output "collector_ports" {
  value = local.collector_ports
}

output "validation_checks" {
  value = [
    "collector container exists",
    "health endpoint responds",
    "OTLP gRPC port is reachable",
    "OTLP HTTP port is reachable",
    "debug exporter records smoke telemetry",
  ]
}
