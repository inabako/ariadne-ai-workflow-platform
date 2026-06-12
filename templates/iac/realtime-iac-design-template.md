---
type: iac-design
schema_version: "1.0"
project: ""
receipt_id: ""
repository: ""
branch: ""
commit: ""
workflow: realtime-iac
phase: design
status: draft
owner_agent: ""
created_at: ""
updated_at: ""
source_requirements:
  - ""
related_issue: ""
tags:
  - robotics
  - realtime
  - iac
---

# Realtime IaC Design: <title>

## 1. Intent

| Item | Value |
| --- | --- |
| Primary Intent |  |
| Target System |  |
| Target Runtime | Docker Desktop / Linux / Raspberry Pi / edge host / other |
| Success Criteria |  |
| Non-goals |  |

## 2. Shared Artifact Gate

| Artifact | Path / Source | Status | Blocking Notes |
| --- | --- | --- | --- |
| Communication specification |  | present / missing / conflicting |  |
| Port definition list |  | present / missing / conflicting |  |
| Network boundary definition |  | present / missing / conflicting |  |
| Software inventory |  | present / missing / conflicting |  |
| Protocol definition |  | present / missing / conflicting / not-applicable |  |
| Public / private network policy |  | present / missing / conflicting / not-applicable |  |
| Architecture diagram |  | present / missing / conflicting / not-applicable |  |
| ADR |  | present / missing / conflicting / not-applicable |  |

## 3. Decision

| ID | Decision | Status | Owner |
| --- | --- | --- | --- |
| DEC-001 |  | proposed / accepted / rejected / superseded |  |

## 4. Reason

| Decision ID | Reason | Alternatives Considered | Rejected Reason |
| --- | --- | --- | --- |
| DEC-001 |  |  |  |

## 5. Scope

| Area | In Scope | Out of Scope |
| --- | --- | --- |
| Docker Compose |  |  |
| systemd |  |  |
| Firewall |  |  |
| Reverse Proxy |  |  |
| TURN / STUN |  |  |
| Secrets / Env |  |  |
| Logs / Metrics |  |  |
| Application Logic |  |  |

## 6. Software Inventory

| Software | Purpose | Owner / Boundary | Version Policy | Runtime Unit | Ports / Protocols | Env / Secret Placeholders | Persistence | Health Check | License / Distribution Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | pinned / range / latest-prohibited / OS-package | container / systemd / host-package / proxy / sidecar / monitoring-job |  |  | none / volume / host-path |  |  |

## 7. Repository State

| Item | Value |
| --- | --- |
| Repository |  |
| Branch |  |
| Commit |  |
| Related GitHub Issue |  |
| Requirement Document |  |
| Compared Baseline |  |

## 8. Responsibility Boundary

| Component / Artifact | Owns | Does Not Own | Failure Domain | Observability |
| --- | --- | --- | --- | --- |
| docker-compose.yml |  |  |  |  |
| systemd unit |  |  |  |  |
| firewall policy |  |  |  |  |
| reverse proxy |  |  |  |  |
| application |  |  |  |  |

## 9. Port / Protocol Traceability

| Port / Range | Protocol | Direction | Owner | Source Artifact | Public Exposure | Test Case ID |
| --- | --- | --- | --- | --- | --- | --- |
|  | UDP / TCP | inbound / outbound / internal |  |  | yes / no |  |

## 10. Network / Security Design

| Item | Design | Source Artifact | Risk | Verification |
| --- | --- | --- | --- | --- |
| Network boundary |  |  |  |  |
| Firewall policy |  |  |  |  |
| TLS |  |  |  |  |
| Authentication |  |  |  |  |
| Authorization |  |  |  |  |
| Secret handling |  |  |  |  |
| TURN / STUN |  |  |  |  |
| Reverse proxy |  |  |  |  |

## 11. Runtime Design

| Runtime Item | Design | Reason | Failure / Recovery |
| --- | --- | --- | --- |
| Service model |  |  |  |
| Startup order |  |  |  |
| Restart policy |  |  |  |
| Health check |  |  |  |
| Graceful shutdown |  |  |  |
| Volumes / permissions |  |  |  |
| Environment variables |  |  |  |
| Rollback unit |  |  |  |

## 12. Generated IaC Artifacts

| Artifact | Path | Source Design Section | Contains Secret | Review Status |
| --- | --- | --- | --- | --- |
| docker-compose.yml |  |  | no | draft / reviewed / approved |
| .env.example |  |  | no | draft / reviewed / approved |
| systemd unit |  |  | no | draft / reviewed / approved |
| firewall policy |  |  | no | draft / reviewed / approved |
| logrotate config |  |  | no | draft / reviewed / approved |
| monitoring config |  |  | no | draft / reviewed / approved |

## 13. Observability

| Signal | Purpose | Location | Retention | Used For |
| --- | --- | --- | --- | --- |
| Log |  |  |  | debugging / audit / incident |
| Metric |  |  |  | health / trend |
| Health check |  |  |  | runtime gate |
| Test evidence |  |  |  | verification |

## 14. Test Strategy

| Test ID | Test Type | Scenario | Required Evidence | Related Risk |
| --- | --- | --- | --- | --- |
| IAC-TC-001 | docker-desktop / linux-runtime / integration / human-check |  |  |  |

## 15. Security Review

| Finding ID | Severity | Finding | Evidence | Required Action |
| --- | --- | --- | --- | --- |
| SEC-001 | critical / high / medium / low / info |  |  |  |

## 16. Open Questions

| QA ID | Question | Impact | Owner | Blocking | Due |
| --- | --- | --- | --- | --- | --- |
| QA-001 |  |  |  | yes / no |  |

## 17. Evidence

| Evidence ID | Type | Path / Link | Summary |
| --- | --- | --- | --- |
| EVD-001 | requirement / code / command-output / log / test / review |  |  |

## 18. Approval

| Role | Reviewer | Status | Comment | Date |
| --- | --- | --- | --- | --- |
| Infrastructure Owner |  | pending / approved / rejected / conditional-pass |  |  |
| Security Reviewer |  | pending / approved / rejected / conditional-pass |  |  |
| Runtime Reviewer |  | pending / approved / rejected / conditional-pass |  |  |
| Operator / Owner |  | pending / approved / rejected / conditional-pass |  |  |

## 19. Change History

| Date | Author | Change | Reason |
| --- | --- | --- | --- |
|  |  |  |  |
