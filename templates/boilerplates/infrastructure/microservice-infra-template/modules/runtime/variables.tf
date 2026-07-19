variable "environment" {
  type = string
}

variable "service_name" {
  type = string
}

variable "service_image" {
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
  type = list(number)
}

variable "inbound_udp_ports" {
  type = list(number)
}
