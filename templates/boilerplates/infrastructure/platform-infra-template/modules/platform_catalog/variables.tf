variable "environment" {
  type = string
}

variable "platform_name" {
  type = string
}

variable "enabled_components" {
  type = set(string)
}

variable "admin_cidrs" {
  type = list(string)
}

variable "secret_source" {
  type = string
}

variable "enable_backup" {
  type = bool
}

