variable "collector_name" {
  type = string
}

variable "collector_image" {
  type = string
}

variable "collector_config_path" {
  type = string
}

variable "network_name" {
  type = string
}

variable "otlp_grpc_port" {
  type = number
}

variable "otlp_http_port" {
  type = number
}

variable "health_check_port" {
  type = number
}

variable "environment_variables" {
  type      = map(string)
  sensitive = true
  default   = {}
}
