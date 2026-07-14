locals {
  compose_files_by_profile = {
    openldap                = ["openldap/docker-compose/compose.yaml"]
    web-application-example = ["integrated/web-application-example/compose.yaml"]
  }
}

