#!/usr/bin/env sh
set -eu
terraform -chdir=terraform destroy -var-file=terraform.tfvars.example
