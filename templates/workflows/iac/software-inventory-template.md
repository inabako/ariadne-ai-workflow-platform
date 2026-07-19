---
type: software-inventory
schema_version: "1.0"
project: ""
receipt_id: ""
repository: ""
branch: ""
commit: ""
workflow: realtime-iac
phase: intake
status: draft
owner_agent: ""
created_at: ""
updated_at: ""
source_requirements:
  - ""
related_issue: ""
tags:
  - ariadne
  - realtime
  - iac
  - software-inventory
---

# Software Inventory: <title>

## 1. Intent

| Item | Value |
| --- | --- |
| Target Infrastructure |  |
| Target Environment | Docker Desktop / Linux / edge host / cloud VM / other |
| Inventory Owner |  |
| Used By | IaC design / Docker Compose / systemd / firewall / monitoring / docs |
| Completion Criteria | Every software item installed, packaged, started, supervised, proxied, monitored, or documented by IaC is listed. |

## 2. Intake Gate

| Gate | Status | Blocking Notes |
| --- | --- | --- |
| All runtime software is listed | pending / met / not-met |  |
| All supporting infrastructure software is listed | pending / met / not-met |  |
| Version policy is defined | pending / met / not-met |  |
| Runtime unit is defined | pending / met / not-met |  |
| Port / protocol impact is linked | pending / met / not-met |  |
| Env / secret placeholders are listed | pending / met / not-met |  |
| Health check method is defined | pending / met / not-met |  |
| License / distribution constraint is checked | pending / met / not-met / not-applicable |  |

## 3. Software Inventory

| Software ID | Software | Purpose | Owner / Boundary | Version / Version Policy | Runtime Unit | Install / Package Source | Ports / Protocols | Env / Secret Placeholders | Persistence | Health Check | License / Distribution Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SW-001 |  |  |  | pinned / range / OS-package / latest-prohibited | container / systemd / host-package / proxy / sidecar / monitoring-job | image / apt / binary / source / bundled |  |  | none / volume / host-path |  |  |

## 4. Dependency And Startup Order

| Order | Software ID | Depends On | Startup Condition | Failure If Missing | Recovery / Restart |
| --- | --- | --- | --- | --- | --- |
| 1 | SW-001 |  | config present / network ready / dependency healthy |  |  |

## 5. Responsibility Boundary

| Software ID | IaC Owns | Application Owns | Human / Operator Owns | Notes |
| --- | --- | --- | --- | --- |
| SW-001 | install / package / start / supervise / monitor / document | protocol behavior / business logic / control logic | secret value / credential approval / host approval |  |

## 6. Configuration And Secrets

| Config ID | Software ID | Variable / File | Required | Secret | Placeholder In `.env.example` | Source Of Real Value | Rotation / Update Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CFG-001 | SW-001 |  | yes / no | yes / no | yes / no | human / vault / host env / CI secret / not-applicable |  |

## 7. Persistence And Data

| Data ID | Software ID | Path / Volume | Data Type | Retention | Backup Needed | Risk |
| --- | --- | --- | --- | --- | --- | --- |
| DATA-001 | SW-001 |  | logs / state / cache / config / recording |  | yes / no |  |

## 8. Observability

| Software ID | Log Location | Metric / Health Signal | Alert Condition | Evidence Needed |
| --- | --- | --- | --- | --- |
| SW-001 |  |  |  |  |

## 9. Requirement Traceability

| Requirement ID | Software ID | Reason Included | Related Communication / Port | Test Case ID |
| --- | --- | --- | --- | --- |
| REQ-001 | SW-001 |  |  | IAC-TC-001 |

## 10. Open Questions

| QA ID | Question | Impact | Owner | Blocking |
| --- | --- | --- | --- | --- |
| QA-001 |  |  |  | yes / no |

## 11. Approval

| Role | Reviewer | Status | Comment | Date |
| --- | --- | --- | --- | --- |
| Infrastructure Owner |  | pending / approved / rejected / conditional-pass |  |  |
| Security Reviewer |  | pending / approved / rejected / conditional-pass |  |  |
| Operator / Owner |  | pending / approved / rejected / conditional-pass |  |  |
