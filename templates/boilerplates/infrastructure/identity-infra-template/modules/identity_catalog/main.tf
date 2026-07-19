locals {
  user_search_base  = "${var.users_ou},${var.base_dn}"
  group_search_base = "${var.groups_ou},${var.base_dn}"

  identity_connection_contract = {
    provider                   = "openldap"
    host_ref                   = "ldap.host"
    port_ref                   = "ldap.port"
    base_dn_ref                = "ldap.base_dn"
    bind_dn_secret_ref         = var.app_bind_dn_secret_ref
    bind_password_secret_ref   = var.app_bind_password_secret_ref
    administrator_secret_ref   = var.admin_bind_dn_secret_ref
    administrator_password_ref = var.admin_password_secret_ref
    user_search = {
      base                   = local.user_search_base
      filter                 = "(${var.user_id_attribute}={username})"
      id_attribute           = var.user_id_attribute
      display_name_attribute = "cn"
      email_attribute        = "mail"
    }
    group_search = {
      base         = local.group_search_base
      filter       = "(member={user_dn})"
      id_attribute = var.group_id_attribute
    }
    tls = {
      enabled            = var.tls_enabled
      verify_certificate = var.tls_enabled
      certificate_mode   = var.certificate_mode
    }
    timeout_seconds = 5
  }

  validation_checks = [
    "OpenLDAP server is running",
    "LDAP or LDAPS port is reachable from approved sources",
    "administrator DN bind succeeds",
    "application bind account bind succeeds",
    "test user bind succeeds",
    "invalid password bind is rejected",
    "Base DN exists",
    "Users OU exists",
    "Groups OU exists",
    "user search succeeds",
    "group search succeeds",
    "membership search succeeds",
    "LDIF apply succeeds",
    "LDIF reapply does not create unexpected duplicates",
    "TLS connection succeeds when TLS is enabled",
    "backup file exists and has non-zero size when backup is enabled",
    "restore test verifies bind and search when restore test is enabled",
    "unnecessary external exposure is absent",
  ]

  human_check_items = concat(
    [
      "Base DN and OU layout must be approved before target implementation."
    ],
    var.tls_enabled && var.certificate_mode == "none" ? [
      "TLS is enabled but certificate mode is none. Provide certificate source or change TLS decision."
    ] : [],
    var.external_exposure ? [
      "External LDAP exposure is enabled. Confirm source restrictions and TLS policy."
    ] : []
  )

  evidence_plan = {
    requirement            = true
    openldap_version       = var.openldap_version
    organization_name      = var.organization_name
    domain                 = var.domain
    base_dn                = var.base_dn
    users_ou               = var.users_ou
    groups_ou              = var.groups_ou
    services_ou            = var.services_ou
    admins_ou              = var.admins_ou
    tls_enabled            = var.tls_enabled
    certificate_mode       = var.certificate_mode
    apply_ldif             = var.apply_ldif
    backup_enabled         = var.enable_backup
    restore_test_enabled   = var.enable_restore_test
    retention_days         = var.retention_days
    external_exposure      = var.external_exposure
    secret_values_redacted = true
    output_enabled         = var.evidence_enabled
  }
}

