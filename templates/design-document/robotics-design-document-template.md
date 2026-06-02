---
type: design-document
schema_version: "1.0"
project: ""
receipt_id: ""
repository: ""
branch: ""
commit: ""
workflow: ""
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
  - design-document
---

# Robotics Design Document: <title>

## 1. Intent

この設計で達成したい目的、現場価値、守るべき安全・運用上の前提を記載します。

| Item | Value |
| --- | --- |
| Primary Intent |  |
| Target User / Operator |  |
| Target Robot / Device |  |
| Target Environment | lab / indoor / outdoor / field / other |
| Success Criteria |  |
| Non-goal Summary |  |

## 2. Decision

採用する設計方針を短く明示します。

| ID | Decision | Status | Owner |
| --- | --- | --- | --- |
| DEC-001 |  | proposed / accepted / rejected / superseded |  |

## 3. Reason

なぜその設計を採用するのか、代替案と比較して説明します。

| Decision ID | Reason | Alternatives Considered | Rejected Reason |
| --- | --- | --- | --- |
| DEC-001 |  |  |  |

## 4. Scope

| Area | In Scope | Out of Scope |
| --- | --- | --- |
| Control |  |  |
| Video |  |  |
| Telemetry |  |  |
| Safety |  |  |
| Network |  |  |
| Runtime |  |  |
| UI / Operator |  |  |
| Deployment |  |  |
| Documentation |  |  |

## 5. Repository State

| Item | Value |
| --- | --- |
| Repository |  |
| Branch |  |
| Commit |  |
| Related GitHub Issue |  |
| Requirement Document |  |
| Compared Baseline |  |

## 6. Requirement Traceability

| Requirement ID | Requirement Summary | Design Section | Test ID | Status |
| --- | --- | --- | --- | --- |
| REQ-001 |  |  | TEST-001 | draft / covered / uncovered |

## 7. System Context

現場、operator、robot / device、network、外部systemとの関係を記載します。

| Actor / System | Responsibility | Input | Output | Failure Impact |
| --- | --- | --- | --- | --- |
| Operator |  |  |  |  |
| Robot / Device |  |  |  |  |
| Runtime Process |  |  |  |  |
| Remote Gateway |  |  |  |  |
| External Service |  |  |  |  |

## 8. Responsibility Boundary

責務境界を明確にし、safety responsibility が特定componentに隠れないようにします。

| Component | Owns | Does Not Own | Failure Domain | Observability |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 9. Architecture

## 9.1 Component Design

| Component | Purpose | Interface | State | Notes |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 9.2 Data / Control Flow

| Flow ID | Source | Destination | Data / Command | Timing | Failure Behavior |
| --- | --- | --- | --- | --- | --- |
| FLOW-001 |  |  |  |  |  |

## 9.3 Interface Contract

| Interface | Protocol / API | Owner | Compatibility Requirement | Error Handling |
| --- | --- | --- | --- | --- |
| Control |  |  |  |  |
| Video |  |  |  |  |
| Telemetry |  |  |  |  |
| Network |  |  |  |  |
| Runtime |  |  |  |  |

## 10. Safety Design

| Safety Item | Defined Behavior | Verification Method | Blocking |
| --- | --- | --- | --- |
| STOP / emergency stop |  |  | yes |
| Communication loss |  |  | yes |
| Startup safe state |  |  | yes |
| Shutdown safe state |  |  | yes |
| Sensor failure |  |  |  |
| Process crash |  |  |  |
| Wrong robot connection |  |  |  |

## 11. Runtime Design

| Runtime Item | Design | Reason | Failure / Recovery |
| --- | --- | --- | --- |
| Process lifecycle |  |  |  |
| Watchdog / supervisor |  |  |  |
| Health check |  |  |  |
| Restart behavior |  |  |  |
| Configuration |  |  |  |
| Logging / metrics |  |  |  |

## 12. Network / Deployment Design

| Item | Design | Risk | Rollback |
| --- | --- | --- | --- |
| Network topology |  |  |  |
| Remote access |  |  |  |
| Port / protocol |  |  |  |
| Deployment unit |  |  |  |
| Rollback unit |  |  |  |

## 13. Observability

| Signal | Purpose | Location | Retention | Used For |
| --- | --- | --- | --- | --- |
| Log |  |  |  | debugging / audit / incident |
| Metric |  |  |  | health / trend |
| Trace / Event |  |  |  | timeline |
| Test evidence |  |  |  | verification |

## 14. Test Strategy

| Test ID | Test Type | Scenario | Required Evidence | Related Risk |
| --- | --- | --- | --- | --- |
| TEST-001 | unit / integration / simulation / bench / limited-field |  |  |  |

## 15. Rollback / Recovery

| Scenario | Detection | Recovery Action | Owner | Evidence Required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 16. Risks

| Risk ID | Severity | Risk | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| RISK-001 | critical / high / medium / low |  |  |  | open |

## 17. Open Questions

| QA ID | Question | Impact | Owner | Blocking | Due |
| --- | --- | --- | --- | --- | --- |
| QA-001 |  |  |  | yes / no |  |

## 18. Evidence

| Evidence ID | Type | Path / Link | Summary |
| --- | --- | --- | --- |
| EVD-001 | requirement / code / log / test / review |  |  |

## 19. Approval

| Role | Reviewer | Status | Comment | Date |
| --- | --- | --- | --- | --- |
| Architect |  | pending / approved / rejected / conditional-pass |  |  |
| Safety Reviewer |  | pending / approved / rejected / conditional-pass |  |  |
| Runtime Reviewer |  | pending / approved / rejected / conditional-pass |  |  |
| Operator / Owner |  | pending / approved / rejected / conditional-pass |  |  |

## 20. Change History

| Date | Author | Change | Reason |
| --- | --- | --- | --- |
|  |  |  |  |
