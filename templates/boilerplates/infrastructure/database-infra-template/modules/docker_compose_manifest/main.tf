locals {
  engine_compose_files = {
    postgresql = "postgresql/docker-compose/compose.yaml"
    mysql      = "mysql/docker-compose/compose.yaml"
  }

  integrated_compose_files = {
    single-instance           = "integrated/single-instance/compose.yaml"
    multi-database            = "integrated/multi-database/compose.yaml"
    application-stack-example = "integrated/application-stack-example/compose.yaml"
  }

  selected_engine_files = [
    for engine, file in local.engine_compose_files : file
    if contains(var.enabled_engines, engine)
  ]
}

