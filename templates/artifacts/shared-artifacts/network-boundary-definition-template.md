---
type: network-boundary-definition
schema_version: "1.0"
project: ""
receipt_id: ""
repository: ""
branch: ""
commit: ""
workflow: ariadne-new-system-iac
phase: shared-artifact-generation
status: draft
owner_agent: ""
created_at: ""
updated_at: ""
related_issue: ""
tags:
  - ariadne
  - shared-artifacts
  - network-boundary
---

# Network Boundary Definition: <title>

## 1. Intent

| Item | Value |
| --- | --- |
| Purpose | Define network zones and allowed/blocked communication for IaC |
| Source Architecture |  |
| Source Communication Specification |  |
| Completion Criteria | Every boundary has allowed flows, blocked flows, enforcement point, and evidence method. |

## 2. Network Zones

| Zone ID | Zone Name | Description | Trust Level | Owner | Examples |
| --- | --- | --- | --- | --- | --- |
| ZONE-001 |  |  | trusted / semi-trusted / untrusted |  | host / container / LAN / VPN / internet / field |

## 3. Boundary Rules

| Boundary ID | From Zone | To Zone | Allowed Flow IDs | Blocked Flow IDs | Enforcement Point | IaC Artifact | Evidence Required |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NB-001 | ZONE-001 | ZONE-002 | FLOW-001 |  | firewall / reverse-proxy / VPN / container-network / host-route |  | command-output / packet-capture / log |

## 4. Public Exposure Review

| Exposure ID | Public Endpoint | Justification | Auth / TLS | Rate / Abuse Control | Human Approval |
| --- | --- | --- | --- | --- | --- |
| PUB-001 |  |  |  |  | yes / no |

## 5. Open Questions

| QA ID | Question | Impact | Owner | Blocking |
| --- | --- | --- | --- | --- |
| QA-001 |  |  |  | yes / no |
