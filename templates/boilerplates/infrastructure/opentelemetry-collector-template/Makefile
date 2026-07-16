PYTHON ?= python
SELECTION ?= examples/minimal/selection.yaml

.PHONY: init catalog select generate validate inspect-distribution build terraform-plan terraform-apply health smoke test evidence terraform-destroy reset

init:
	$(PYTHON) scripts/otel_template.py init

catalog:
	$(PYTHON) scripts/otel_template.py catalog

select:
	$(PYTHON) scripts/otel_template.py select --selection $(SELECTION)

generate:
	$(PYTHON) scripts/otel_template.py generate --selection $(SELECTION)

validate:
	$(PYTHON) scripts/otel_template.py validate --selection $(SELECTION)

inspect-distribution:
	$(PYTHON) scripts/otel_template.py inspect-distribution --selection $(SELECTION)

build:
	$(PYTHON) scripts/otel_template.py build --selection $(SELECTION)

terraform-plan:
	terraform -chdir=terraform init -backend=false
	terraform -chdir=terraform plan -var-file=terraform.tfvars.example

terraform-apply:
	terraform -chdir=terraform apply -var-file=terraform.tfvars.example

health:
	$(PYTHON) scripts/otel_template.py health

smoke:
	$(PYTHON) scripts/otel_template.py smoke

test:
	$(PYTHON) -m pytest tests

evidence:
	$(PYTHON) scripts/otel_template.py evidence --selection $(SELECTION)

terraform-destroy:
	terraform -chdir=terraform destroy -var-file=terraform.tfvars.example

reset:
	$(PYTHON) scripts/otel_template.py reset
