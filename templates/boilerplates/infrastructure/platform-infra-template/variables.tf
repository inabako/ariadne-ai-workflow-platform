variable "environment" {
  description = "Deployment environment."
  type        = string

  validation {
    condition     = contains(["local", "dev", "stg", "prod"], var.environment)
    error_message = "environment must be one of local, dev, stg, or prod."
  }
}

variable "platform_name" {
  description = "Platform name used for labels and generated manifests."
  type        = string
  default     = "ariadne-platform"

  validation {
    condition     = length(trimspace(var.platform_name)) > 0
    error_message = "platform_name is required."
  }
}

variable "enabled_components" {
  description = "Platform components to include."
  type        = set(string)
  default     = ["gitlab", "jenkins", "grafana", "zabbix"]

  validation {
    condition = alltrue([
      for component in var.enabled_components :
      contains(["gitlab", "jenkins", "grafana", "zabbix"], component)
    ])
    error_message = "enabled_components can contain only gitlab, jenkins, grafana, and zabbix."
  }
}

variable "compose_profile" {
  description = "Integrated compose profile."
  type        = string
  default     = "full-platform"

  validation {
    condition     = contains(["development-platform", "observability-platform", "full-platform"], var.compose_profile)
    error_message = "compose_profile must be development-platform, observability-platform, or full-platform."
  }
}

variable "admin_cidrs" {
  description = "CIDRs allowed for administrative access. Keep prod restrictive."
  type        = list(string)
  default     = ["127.0.0.1/32"]
}

variable "secret_source" {
  description = "External secret source reference. Do not put real secrets in tfvars."
  type        = string
  default     = "human-approved-secret-source"

  validation {
    condition     = length(trimspace(var.secret_source)) > 0
    error_message = "secret_source is required."
  }
}

variable "enable_backup" {
  description = "Whether backup jobs are required for selected services."
  type        = bool
  default     = true
}

