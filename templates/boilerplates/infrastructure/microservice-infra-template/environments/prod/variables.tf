variable "service_name" {
  type = string
}

variable "service_image" {
  type = string
}

variable "service_host" {
  type = string
}

variable "runtime_type" {
  type = string
}

variable "health_port" {
  type = number
}

variable "metrics_port" {
  type = number
}

variable "inbound_tcp_ports" {
  type    = list(number)
  default = []
}

variable "inbound_udp_ports" {
  type    = list(number)
  default = []
}

variable "allowed_client_cidrs" {
  type    = list(string)
  default = []
}

variable "allowed_device_cidrs" {
  type    = list(string)
  default = []
}

variable "allowed_admin_cidrs" {
  type    = list(string)
  default = []
}

variable "enable_metrics" {
  type    = bool
  default = true
}

variable "enable_dns" {
  type    = bool
  default = false
}

variable "gateway_domain" {
  type     = string
  default  = null
  nullable = true
}

variable "enable_alert" {
  type    = bool
  default = true
}

variable "alert_webhook_url" {
  type      = string
  default   = null
  nullable  = true
  sensitive = true
}
