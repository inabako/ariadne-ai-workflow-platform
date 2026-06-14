output "contract" {
  description = "Observability contract."
  value       = terraform_data.observability_contract.output
  sensitive   = true
}
