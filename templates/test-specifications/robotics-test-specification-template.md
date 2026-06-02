---
type: test-specification
schema_version: "1.0"
project: ""
receipt_id: ""
repository: ""
branch: ""
commit: ""
workflow: ""
phase: test-planning
status: draft
owner_agent: ""
created_at: ""
updated_at: ""
source_requirements:
  - ""
related_design_document: ""
related_issue: ""
tags:
  - robotics
  - test-specification
---

# Test Specification: <title>

## 1. Test Objective

このテスト仕様で確認する目的、risk、release判断への使い方を記載します。

| Item | Value |
| --- | --- |
| Objective |  |
| Target System / Feature |  |
| Risk Level | low / medium / high / critical |
| Required Before | implementation / bench / field / release |
| Owner |  |

## 2. Scope

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

## 3. Repository / Artifact State

| Item | Value |
| --- | --- |
| Repository |  |
| Branch |  |
| Commit / Baseline |  |
| Requirement Document |  |
| Design Document |  |
| Related Issue |  |

## 4. Requirement Traceability

| Requirement ID | Requirement Summary | Risk | Test Case IDs | Coverage |
| --- | --- | --- | --- | --- |
| REQ-001 |  | low / medium / high / critical | TC-001 | covered / partial / uncovered |

## 5. Test Strategy

| Test Layer | Purpose | Required | Reason |
| --- | --- | --- | --- |
| Unit |  | yes / no |  |
| Integration |  | yes / no |  |
| Simulation |  | yes / no |  |
| Hardware Mock |  | yes / no |  |
| Bench |  | yes / no |  |
| Limited Field |  | yes / no |  |
| Rollback Rehearsal |  | yes / no |  |

## 6. Test Environment Matrix

| Environment ID | Location | Robot / Device | Network | Runtime / OS | Purpose |
| --- | --- | --- | --- | --- | --- |
| ENV-001 | CI / lab / bench / field |  | LAN / VPN / relay / intermittent |  |  |

## 7. Entry Criteria

| Criteria ID | Criteria | Required | Status |
| --- | --- | --- | --- |
| ENT-001 | Requirement document is accepted. | yes | pending / met / not-met |
| ENT-002 | Target branch and commit are known. | yes | pending / met / not-met |
| ENT-003 | STOP behavior is defined for safety-related tests. | yes | pending / met / not-met |
| ENT-004 | Test environment is prepared. | yes | pending / met / not-met |

## 8. Test Case Table

| Test Case ID | Priority | Test Type | Requirement ID | Scenario | Preconditions | Steps | Expected Result | Required Evidence | Pass Criteria |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-001 | critical / high / medium / low | unit / integration / simulation / bench / limited-field | REQ-001 |  |  |  |  | log / screenshot / telemetry / video / command-output |  |

## 9. Safety Gate Test Cases

| Safety Item | Test Case ID | Scenario | Expected Safe Behavior | Evidence Required | Blocking |
| --- | --- | --- | --- | --- | --- |
| STOP / emergency stop |  |  |  |  | yes |
| Communication loss |  |  |  |  | yes |
| Startup safe state |  |  |  |  | yes |
| Shutdown safe state |  |  |  |  | yes |
| Sensor failure |  |  |  |  |  |
| Process crash |  |  |  |  |  |

## 10. Regression Matrix

| Existing Behavior | Risk | Test Case ID | Expected Preservation |
| --- | --- | --- | --- |
|  |  |  |  |

## 11. Evidence Plan

| Evidence ID | Test Case ID | Evidence Type | Save Location | Required |
| --- | --- | --- | --- | --- |
| EVD-001 | TC-001 | log / screenshot / telemetry / video / command-output | work/<receipt-id>/test-evidence/ | yes / no |

## 12. Exit Criteria

| Criteria ID | Criteria | Required | Status |
| --- | --- | --- | --- |
| EXT-001 | Required test cases are executed. | yes | pending / met / not-met |
| EXT-002 | Critical / high findings are resolved or explicitly accepted. | yes | pending / met / not-met |
| EXT-003 | Test evidence is saved and linked. | yes | pending / met / not-met |
| EXT-004 | Rollback behavior is verified when applicable. | yes | pending / met / not-met |

## 13. Open Questions

| QA ID | Question | Impact | Owner | Blocking |
| --- | --- | --- | --- | --- |
| QA-001 |  |  |  | yes / no |

## 14. Approval

| Role | Reviewer | Status | Comment | Date |
| --- | --- | --- | --- | --- |
| Test Owner |  | pending / approved / rejected / conditional-pass |  |  |
| Safety Reviewer |  | pending / approved / rejected / conditional-pass |  |  |
| Product / Operation Owner |  | pending / approved / rejected / conditional-pass |  |  |
