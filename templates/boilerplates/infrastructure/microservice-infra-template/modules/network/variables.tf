variable "environment" {
  type = string
}

variable "service_name" {
  type = string
}

variable "service_host" {
  type = string
}

variable "inbound_tcp_ports" {
  type = list(number)
}

variable "inbound_udp_ports" {
  type = list(number)
}

variable "allowed_client_cidrs" {
  type = list(string)
}

variable "allowed_device_cidrs" {
  type = list(string)
}

variable "allowed_admin_cidrs" {
  type = list(string)
}
