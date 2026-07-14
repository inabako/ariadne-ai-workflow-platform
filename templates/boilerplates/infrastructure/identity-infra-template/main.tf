module "identity_catalog" {
  source = "./modules/identity_catalog"

  environment                  = var.environment
  identity_stack_name          = var.identity_stack_name
  openldap_version             = var.openldap_version
  organization_name            = var.organization_name
  domain                       = var.domain
  base_dn                      = var.base_dn
  users_ou                     = var.users_ou
  groups_ou                    = var.groups_ou
  services_ou                  = var.services_ou
  admins_ou                    = var.admins_ou
  ldap_port                    = var.ldap_port
  ldaps_port                   = var.ldaps_port
  external_exposure            = var.external_exposure
  tls_enabled                  = var.tls_enabled
  certificate_mode             = var.certificate_mode
  admin_bind_dn_secret_ref     = var.admin_bind_dn_secret_ref
  admin_password_secret_ref    = var.admin_password_secret_ref
  app_bind_dn_secret_ref       = var.app_bind_dn_secret_ref
  app_bind_password_secret_ref = var.app_bind_password_secret_ref
  user_id_attribute            = var.user_id_attribute
  group_id_attribute           = var.group_id_attribute
  volume_name                  = var.volume_name
  apply_ldif                   = var.apply_ldif
  enable_backup                = var.enable_backup
  enable_restore_test          = var.enable_restore_test
  retention_days               = var.retention_days
  evidence_enabled             = var.evidence_enabled
}

module "docker_compose_manifest" {
  source = "./modules/docker_compose_manifest"

  environment     = var.environment
  compose_profile = var.compose_profile
}

