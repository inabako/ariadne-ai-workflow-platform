---
type: port-definition
schema_version: "1.0"
project: ""
receipt_id: ""
repository: ""
branch: ""
commit: ""
workflow: robotics-new-system-iac
phase: shared-artifact-generation
status: draft
owner_agent: ""
created_at: ""
updated_at: ""
related_issue: ""
tags:
  - robotics
  - shared-artifacts
  - port-definition
---

# Port Definition: <title>

## 1. Intent

| Item | Value |
| --- | --- |
| Purpose | Define IaC-relevant ports and protocols |
| Source Communication Specification |  |
| Source Requirement |  |
| Completion Criteria | Every IaC-managed port has owner, protocol, exposure, bind address, firewall rule, and test mapping. |

## 2. Port List

| Port ID | Port / Range | Protocol | Direction | Owner | Used By Flow IDs | Bind Address | Exposure | Firewall Rule | Runtime Unit | Test Case ID |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PORT-001 |  | UDP / TCP | inbound / outbound / internal |  | FLOW-001 | 0.0.0.0 / 127.0.0.1 / host / container | private / public / host-only | allow / deny / not-applicable | container / systemd / proxy / host | IAC-TC-001 |

## 3. Conflict Check

| Check | Status | Notes |
| --- | --- | --- |
| No duplicate ownership | pending / pass / fail |  |
| No unexplained public exposure | pending / pass / fail |  |
| Firewall rule exists for exposed ports | pending / pass / fail |  |
| Test case exists for each required port | pending / pass / fail |  |

## 4. Open Questions

| QA ID | Question | Impact | Owner | Blocking |
| --- | --- | --- | --- | --- |
| QA-001 |  |  |  | yes / no |
