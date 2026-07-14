variable "environment" {
  type = string
}

variable "service_name" {
  type = string
}

variable "health_port" {
  type = number
}

variable "metrics_port" {
  type = number
}

variable "enable_metrics" {
  type = bool
}

variable "enable_alert" {
  type = bool
}

variable "alert_webhook_url" {
  type      = string
  nullable  = true
  sensitive = true
}
