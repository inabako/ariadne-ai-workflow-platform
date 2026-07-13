---
type: test-evidence
schema_version: "1.0"
project: ""
receipt_id: ""
repository: ""
branch: ""
commit: ""
workflow: ""
phase: verification
status: draft
language: ja-JP
owner_agent: ""
created_at: ""
updated_at: ""
test_specification: ""
related_issue: ""
tags:
  - ariadne
  - test-evidence
---

# Test Evidence: <test run title>

## 1. Test Identity

| Item | Value |
| --- | --- |
| Test Run ID |  |
| Test Specification |  |
| Test Case IDs |  |
| Test Type | unit / integration / simulation / hardware-mock / bench / limited-field / rollback-rehearsal |
| Tester |  |
| Execution Date |  |
| Result | pass / fail / blocked / inconclusive |

## 2. Intent

このテストで確認したい behavior、risk、requirement を記載します。

## 3. Repository State

| Item | Value |
| --- | --- |
| Repository |  |
| Branch |  |
| Commit |  |
| Build / Version |  |
| Related Issue |  |

## 4. Requirement / Test Traceability

| Requirement ID | Test Case ID | Risk / Behavior | Evidence ID | Result |
| --- | --- | --- | --- | --- |
| REQ-001 | TC-001 |  | EVD-001 | pass / fail / blocked |

## 5. Test Environment

| Item | Value |
| --- | --- |
| Location | lab / bench / field / CI / simulation |
| Robot / Device |  |
| OS / Runtime |  |
| Hardware Revision |  |
| Network Condition | LAN / VPN / relay / intermittent / offline |
| Operator |  |
| Observer |  |
| Safety Equipment |  |
| Configuration |  |

## 6. Preconditions

| ID | Precondition | Confirmed |
| --- | --- | --- |
| PRE-001 |  | yes / no |

## 7. Safety Readiness

| Item | Confirmed Behavior | Evidence | Blocking |
| --- | --- | --- | --- |
| STOP / emergency stop available |  |  | yes |
| Communication loss handling known |  |  | yes |
| Startup safe state confirmed |  |  | yes |
| Shutdown safe state confirmed |  |  | yes |
| Field stop condition known |  |  | yes / no |

## 8. Execution Steps

| Step | Action | Expected Result | Actual Result | Evidence ID | Result |
| --- | --- | --- | --- | --- | --- |
| 1 |  |  |  | EVD-001 | pass / fail / blocked |

## 9. Observed Results

| Observation ID | Observation | Severity | Related Step | Notes |
| --- | --- | --- | --- | --- |
| OBS-001 |  | critical / high / medium / low / info |  |  |

## 10. Evidence Files

| Evidence ID | Type | Path / Link | Description | Retention |
| --- | --- | --- | --- | --- |
| EVD-001 | log / screenshot / video / telemetry / command-output / photo / metric |  |  | keep / temporary |

## 11. Anomalies

| Anomaly ID | Description | Impact | Reproduction | Follow-up |
| --- | --- | --- | --- | --- |
| ANM-001 |  |  | yes / no / unknown |  |

## 12. Pass / Fail Judgment

| Item | Value |
| --- | --- |
| Overall Result | pass / fail / blocked / inconclusive |
| Reason |  |
| Known Limitations |  |
| Regression Impact | none / possible / confirmed / unknown |
| Release Impact | none / conditional / blocks release |

## 13. Follow-up Actions

| Priority | Action | Owner | Due | Related Finding |
| --- | --- | --- | --- | --- |
| high / medium / low |  |  |  |  |

## 14. Approval

| Role | Reviewer | Status | Comment | Date |
| --- | --- | --- | --- | --- |
| Tester |  | pending / accepted / rejected |  |  |
| Safety Reviewer |  | pending / accepted / rejected / not-applicable |  |  |
| Owner |  | pending / accepted / rejected |  |  |
