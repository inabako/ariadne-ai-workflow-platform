output "collector_name" {
  value = docker_container.collector.name
}

output "network_name" {
  value = docker_network.collector.name
}
