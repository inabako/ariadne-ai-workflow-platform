variable "environment" {
  type = string
}

variable "compose_profile" {
  type = string
}

variable "enabled_components" {
  type = set(string)
}

