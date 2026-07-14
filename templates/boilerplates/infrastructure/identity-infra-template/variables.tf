variable "environment" {
  type        = string
  description = "Deployment environment."
  default     = "local"

  validation {
    condition     = contains(["local", "dev", "stg", "prod"], var.environment)
    error_message = "environment must be local, dev, stg, or prod."
  }
}

variable "identity_stack_name" {
  type        = string
  description = "Logical OpenLDAP identity stack name."
  default     = "ariadne-openldap"
}

variable "openldap_version" {
  type        = string
  description = "OpenLDAP image version. Do not use latest."
  default     = "1.5.0"
}

variable "compose_profile" {
  type        = string
  description = "Docker Compose profile to apply."
  default     = "openldap"

  validation {
    condition     = contains(["openldap", "web-application-example"], var.compose_profile)
    error_message = "compose_profile must be openldap or web-application-example."
  }
}

variable "organization_name" {
  type        = string
  description = "Directory organization name."
  default     = "Example Organization"
}

variable "domain" {
  type        = string
  description = "Directory domain."
  default     = "example.local"
}

variable "base_dn" {
  type        = string
  description = "Base DN. Must be human-approved for target systems."
  default     = "dc=example,dc=local"
}

variable "users_ou" {
  type        = string
  description = "User OU relative DN."
  default     = "ou=people"
}

variable "groups_ou" {
  type        = string
  description = "Group OU relative DN."
  default     = "ou=groups"
}

variable "services_ou" {
  type        = string
  description = "Service account OU relative DN."
  default     = "ou=services"
}

variable "admins_ou" {
  type        = string
  description = "Administrator OU relative DN."
  default     = "ou=admins"
}

variable "ldap_port" {
  type        = number
  description = "LDAP port."
  default     = 389
}

variable "ldaps_port" {
  type        = number
  description = "LDAPS port."
  default     = 636
}

variable "external_exposure" {
  type        = bool
  description = "Expose LDAP outside the internal Docker network."
  default     = false
}

variable "tls_enabled" {
  type        = bool
  description = "Whether TLS is required."
  default     = false
}

variable "certificate_mode" {
  type        = string
  description = "Certificate source mode."
  default     = "generated-for-local"

  validation {
    condition     = contains(["none", "generated-for-local", "provided"], var.certificate_mode)
    error_message = "certificate_mode must be none, generated-for-local, or provided."
  }
}

variable "admin_bind_dn_secret_ref" {
  type        = string
  description = "Secret reference for administrator bind DN."
  default     = "ldap.admin.bind_dn"
}

variable "admin_password_secret_ref" {
  type        = string
  description = "Secret reference for administrator password."
  default     = "ldap.admin.password"
}

variable "app_bind_dn_secret_ref" {
  type        = string
  description = "Secret reference for application bind DN."
  default     = "ldap.application.bind_dn"
}

variable "app_bind_password_secret_ref" {
  type        = string
  description = "Secret reference for application bind password."
  default     = "ldap.application.password"
}

variable "user_id_attribute" {
  type        = string
  description = "User identifier attribute."
  default     = "uid"
}

variable "group_id_attribute" {
  type        = string
  description = "Group identifier attribute."
  default     = "cn"
}

variable "volume_name" {
  type        = string
  description = "OpenLDAP persistent data volume name."
  default     = "openldap_data"
}

variable "apply_ldif" {
  type        = bool
  description = "Apply bootstrap LDIF."
  default     = true
}

variable "enable_backup" {
  type        = bool
  description = "Enable backup flow."
  default     = true
}

variable "enable_restore_test" {
  type        = bool
  description = "Enable restore validation flow."
  default     = true
}

variable "retention_days" {
  type        = number
  description = "Backup retention days."
  default     = 7
}

variable "evidence_enabled" {
  type        = bool
  description = "Enable evidence output."
  default     = true
}

