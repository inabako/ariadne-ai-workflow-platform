module "identity_infra" {
  source = "../.."

  environment         = "prod"
  identity_stack_name = "ariadne-openldap-prod"
  openldap_version    = "1.5.0"
  compose_profile     = "openldap"
  organization_name   = "Example Organization"
  domain              = "example.local"
  base_dn             = "dc=example,dc=local"
  tls_enabled         = true
  certificate_mode    = "provided"
  external_exposure   = false
  apply_ldif          = true
  enable_backup       = true
  enable_restore_test = true
  evidence_enabled    = true
}

output "identity_connection_contract" {
  value     = module.identity_infra.identity_connection_contract
  sensitive = true
}

output "validation_checks" {
  value = module.identity_infra.validation_checks
}

output "human_check_items" {
  value = module.identity_infra.human_check_items
}

output "compose_files" {
  value = module.identity_infra.compose_files
}

