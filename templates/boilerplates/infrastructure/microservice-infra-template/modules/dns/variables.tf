variable "environment" {
  type = string
}

variable "service_name" {
  type = string
}

variable "service_host" {
  type = string
}

variable "enable_dns" {
  type = bool
}

variable "gateway_domain" {
  type     = string
  nullable = true
}
