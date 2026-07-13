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
language: ja-JP
owner_agent: ""
created_at: ""
updated_at: ""
source_requirements:
  - ""
related_design_document: ""
related_issue: ""
tags:
  - ariadne
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

## 5. Change-Based Test Viewpoints

| Change ID | Planned Change / Fix Point | Affected File / Component | Behavior To Prove | Risk | Test Viewpoint | Test Case IDs | Untestable Reason / Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHG-001 |  |  | normal / boundary / error / regression / safety / observability | low / medium / high / critical |  | TC-001 |  |

## 6. Test Strategy

| Test Layer | Purpose | Required | Reason |
| --- | --- | --- | --- |
| Unit |  | yes / no |  |
| Integration |  | yes / no |  |
| PyQt QTest Integration |  | yes / no / not-applicable |  |
| Simulation |  | yes / no |  |
| Hardware Mock |  | yes / no |  |
| Bench |  | yes / no |  |
| Limited Field |  | yes / no |  |
| Rollback Rehearsal |  | yes / no |  |

## 7. Test Environment Matrix

| Environment ID | Location | Robot / Device | Network | Runtime / OS | Purpose |
| --- | --- | --- | --- | --- | --- |
| ENV-001 | CI / lab / bench / field |  | LAN / VPN / relay / intermittent |  |  |

## 8. Entry Criteria

| Criteria ID | Criteria | Required | Status |
| --- | --- | --- | --- |
| ENT-001 | Requirement document is accepted. | yes | pending / met / not-met |
| ENT-002 | Target branch and commit are known. | yes | pending / met / not-met |
| ENT-003 | STOP behavior is defined for safety-related tests. | yes | pending / met / not-met |
| ENT-004 | Test environment is prepared. | yes | pending / met / not-met |

## 9. Test Case Table

| Test Case ID | Priority | Test Type | Requirement ID | Scenario | Preconditions | Steps | Expected Result | Required Evidence | Pass Criteria |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-001 | critical / high / medium / low | unit / integration / simulation / bench / limited-field | REQ-001 |  |  |  |  | log / screenshot / telemetry / video / command-output |  |

## 10. PyQt QTest Source Plan

PyQt / Qt GUIを使う場合、結合疎通試験のうち自動化できるケースはQTestソース化します。

| Test Case ID | QTest Candidate | Target Test Source | Fixture / Stub | External I/O Policy | GUI Actions | Assertions | Human Check Still Required |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TC-001 | yes / no / partial | src/tests/qt/test_<feature>_integration.py |  | real / stubbed / disabled | QTest.mouseClick / QTest.keyClick / QTest.qWait | widget state / signal / log / packet display | yes / no |

QTestにできない結合疎通試験は、理由と残リスクを記録します。

| Test Case ID | Not Automated Reason | Residual Risk | Manual / Human Evidence |
| --- | --- | --- | --- |
| TC-002 | hardware / camera / safety / timing / external device |  |  |

## 11. Safety Gate Test Cases

| Safety Item | Test Case ID | Scenario | Expected Safe Behavior | Evidence Required | Blocking |
| --- | --- | --- | --- | --- | --- |
| STOP / emergency stop |  |  |  |  | yes |
| Communication loss |  |  |  |  | yes |
| Startup safe state |  |  |  |  | yes |
| Shutdown safe state |  |  |  |  | yes |
| Sensor failure |  |  |  |  |  |
| Process crash |  |  |  |  |  |

## 12. Regression Matrix

| Existing Behavior | Risk | Test Case ID | Expected Preservation |
| --- | --- | --- | --- |
|  |  |  |  |

## 13. Evidence Plan

| Evidence ID | Test Case ID | Evidence Type | Save Location | Required |
| --- | --- | --- | --- | --- |
| EVD-001 | TC-001 | log / screenshot / telemetry / video / command-output | work/<receipt-id>/test-evidence/<category>/ | yes / no |

Target repository docs location:

```text
docs/evidence/issue-<issue-number>/test_specifications/unit-test-cases.md
docs/evidence/issue-<issue-number>/test_specifications/integration-test-cases.md
docs/evidence/issue-<issue-number>/test_specifications/human-check-list.md
docs/evidence/issue-<issue-number>/ut/
docs/evidence/issue-<issue-number>/integration/
docs/evidence/issue-<issue-number>/human_check/
```

UT、結合試験、人間確認は同じIssue配下に保存しますが、test case tableは上記3ファイルへ分けます。
単一の包括的な `test-specification.md` を併用する場合も、各テストケースがUT、integration、human checkのどれに属するかを明示します。

## 14. Exit Criteria

| Criteria ID | Criteria | Required | Status |
| --- | --- | --- | --- |
| EXT-001 | Required test cases are executed. | yes | pending / met / not-met |
| EXT-002 | Critical / high findings are resolved or explicitly accepted. | yes | pending / met / not-met |
| EXT-003 | Test evidence is saved and linked. | yes | pending / met / not-met |
| EXT-004 | Rollback behavior is verified when applicable. | yes | pending / met / not-met |
| EXT-005 | PyQt QTest candidates are implemented or explicitly marked manual-only. | yes / no / not-applicable | pending / met / not-met |

## 15. Open Questions

| QA ID | Question | Impact | Owner | Blocking |
| --- | --- | --- | --- | --- |
| QA-001 |  |  |  | yes / no |

## 16. Approval

| Role | Reviewer | Status | Comment | Date |
| --- | --- | --- | --- | --- |
| Test Owner |  | pending / approved / rejected / conditional-pass |  |  |
| Safety Reviewer |  | pending / approved / rejected / conditional-pass |  |  |
| Product / Operation Owner |  | pending / approved / rejected / conditional-pass |  |  |
