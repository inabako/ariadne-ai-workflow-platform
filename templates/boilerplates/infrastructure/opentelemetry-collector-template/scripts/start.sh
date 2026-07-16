#!/usr/bin/env sh
set -eu
terraform -chdir=terraform apply -var-file=terraform.tfvars.example
