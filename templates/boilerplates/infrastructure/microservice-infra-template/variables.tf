variable "environment" {
  description = "Deployment environment."
  type        = string

  validation {
    condition     = contains(["local", "dev", "stg", "prod"], var.environment)
    error_message = "environment must be one of local, dev, stg, or prod."
  }
}

variable "service_name" {
  description = "Gateway service name."
  type        = string

  validation {
    condition     = length(trimspace(var.service_name)) > 0
    error_message = "service_name is required."
  }
}

variable "service_image" {
  description = "Container image or runtime artifact reference."
  type        = string

  validation {
    condition     = length(trimspace(var.service_image)) > 0
    error_message = "service_image is required."
  }
}

variable "service_host" {
  description = "Host label, DNS target, or deployment target identifier."
  type        = string

  validation {
    condition     = length(trimspace(var.service_host)) > 0
    error_message = "service_host is required."
  }
}

variable "runtime_type" {
  description = "Runtime target."
  type        = string

  validation {
    condition     = contains(["docker", "systemd", "k3s", "ecs"], var.runtime_type)
    error_message = "runtime_type must be one of docker, systemd, k3s, or ecs."
  }
}

variable "health_port" {
  description = "Health endpoint port."
  type        = number

  validation {
    condition     = var.health_port > 0 && var.health_port < 65536
    error_message = "health_port must be between 1 and 65535."
  }
}

variable "metrics_port" {
  description = "Metrics endpoint port."
  type        = number

  validation {
    condition     = var.metrics_port > 0 && var.metrics_port < 65536
    error_message = "metrics_port must be between 1 and 65535."
  }
}

variable "inbound_tcp_ports" {
  description = "Inbound TCP ports allowed by shared port definition."
  type        = list(number)
  default     = []

  validation {
    condition     = alltrue([for port in var.inbound_tcp_ports : port > 0 && port < 65536])
    error_message = "inbound_tcp_ports must contain valid ports."
  }
}

variable "inbound_udp_ports" {
  description = "Inbound UDP ports allowed by shared port definition."
  type        = list(number)
  default     = []

  validation {
    condition     = alltrue([for port in var.inbound_udp_ports : port > 0 && port < 65536])
    error_message = "inbound_udp_ports must contain valid ports."
  }
}

variable "allowed_client_cidrs" {
  description = "Client source CIDRs allowed to reach gateway endpoints."
  type        = list(string)
  default     = []
}

variable "allowed_device_cidrs" {
  description = "Device source CIDRs allowed to reach gateway endpoints."
  type        = list(string)
  default     = []
}

variable "allowed_admin_cidrs" {
  description = "Admin source CIDRs allowed for administrative access."
  type        = list(string)
  default     = []
}

variable "enable_metrics" {
  description = "Enable metrics exposure contract."
  type        = bool
  default     = true
}

variable "enable_dns" {
  description = "Enable DNS contract."
  type        = bool
  default     = false
}

variable "gateway_domain" {
  description = "Gateway domain. Required when enable_dns is true."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition     = var.gateway_domain == null || length(trimspace(var.gateway_domain)) > 0
    error_message = "gateway_domain cannot be blank when set."
  }
}

variable "enable_alert" {
  description = "Enable alert hook contract."
  type        = bool
  default     = false
}

variable "alert_webhook_url" {
  description = "Alert webhook placeholder or external secret reference."
  type        = string
  default     = null
  nullable    = true
  sensitive   = true
}
