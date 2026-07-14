locals {
  compose_files_by_profile = {
    redis                     = ["redis/docker-compose/compose.yaml"]
    application-stack-example = ["integrated/application-stack-example/compose.yaml"]
  }
}

