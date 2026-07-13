---
type: shared-artifacts-index
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
---

# Shared Artifacts Index: <title>

## 1. Intent

| Item | Value |
| --- | --- |
| Purpose | Handoff from new system workflow to realtime IaC workflow |
| Source Requirement |  |
| Target IaC Repository Mode | existing / precreated-new |
| Target Repository |  |
| Target Branch / Initial Branch |  |

## 2. Artifact List

| Artifact ID | Artifact | Path | Required | Status | Owner | Consumed By |
| --- | --- | --- | --- | --- | --- | --- |
| SA-REQ | Requirements | work/<receipt-id>/design-document/requirements.md | yes | draft / ready / blocked |  | new-system / iac |
| SA-COMM | Communication Specification | work/<receipt-id>/design-document/communication-specification.md | yes | draft / ready / blocked |  | iac |
| SA-PORT | Port Definition | work/<receipt-id>/design-document/port-definition.md | yes | draft / ready / blocked |  | iac |
| SA-NET | Network Boundary Definition | work/<receipt-id>/design-document/network-boundary-definition.md | yes | draft / ready / blocked |  | iac |
| SA-ADR | Architecture Decision Record | work/<receipt-id>/design-document/architecture-decision-record.md | yes | draft / ready / blocked |  | new-system / iac |
| SA-SW | Software Inventory | work/<receipt-id>/design-document/software-inventory.md | conditional | draft / ready / blocked / not-applicable |  | iac |

## 3. Validator Summary

| Item | Value |
| --- | --- |
| Validator Output | work/<receipt-id>/process-report/shared-artifact-validation.md |
| JSON Output | work/<receipt-id>/context/shared-artifact-validation.json |
| Judgment | pass / conditional-pass / fail |
| Blocked Areas |  |
| Residual Risks |  |

## 4. Handoff

| Item | Value |
| --- | --- |
| Handoff File | work/<receipt-id>/context/realtime-iac-handoff.json |
| Next Workflow | /realtime-iac |
| Required Human Approval |  |
| Stop Conditions |  |
