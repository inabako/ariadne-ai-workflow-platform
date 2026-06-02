---
type: process-report
schema_version: "1.0"
project: ""
receipt_id: ""
repository: ""
branch: ""
commit: ""
workflow: ""
phase: ""
status: draft
owner_agent: ""
created_at: ""
updated_at: ""
related_issue: ""
input_artifacts:
  - ""
output_artifacts:
  - ""
tags:
  - robotics
  - process-report
---

# Process Report: <phase or task title>

## 1. Process Identity

| Item | Value |
| --- | --- |
| Workflow |  |
| Phase |  |
| Agent / Tool |  |
| Start Time |  |
| End Time |  |
| Status | draft / completed / blocked / failed / conditional-pass |
| Receipt ID |  |

## 2. Intent

この工程で達成する目的を記載します。

## 3. Input Artifacts

| Artifact ID | Type | Path / Link | Status | Notes |
| --- | --- | --- | --- | --- |
|  | requirement / design / source / context / test |  |  |  |

## 4. Repository State

| Item | Value |
| --- | --- |
| Repository |  |
| Branch |  |
| Commit |  |
| Working Tree State | clean / dirty / unknown |
| Related Issue |  |
| Compared Baseline |  |

## 5. Actions Performed

| Step | Action | Command / Method | Result |
| --- | --- | --- | --- |
| 1 |  |  |  |

## 6. Findings

| ID | Severity | Area | Finding | Evidence | Recommended Action |
| --- | --- | --- | --- | --- | --- |
| FIND-001 | critical / high / medium / low / info |  |  |  |  |

## 7. Decisions

| Decision ID | Decision | Reason | Alternatives | Impact |
| --- | --- | --- | --- | --- |
| DEC-001 |  |  |  |  |

## 8. Safety / Risk Check

| Item | Status | Notes | Blocking |
| --- | --- | --- | --- |
| STOP / emergency stop behavior | defined / undefined / not-applicable |  | yes / no |
| Communication loss behavior | defined / undefined / not-applicable |  | yes / no |
| Startup safe state | defined / undefined / not-applicable |  | yes / no |
| Shutdown safe state | defined / undefined / not-applicable |  | yes / no |
| Rollback plan | defined / undefined / not-applicable |  | yes / no |
| Observability | sufficient / insufficient / unknown |  | yes / no |

## 9. Generated Artifacts

| Artifact ID | Type | Path | Status | Consumed By |
| --- | --- | --- | --- | --- |
|  | design / report / test-evidence / test-specification / source / context |  | draft / approved / conditional-pass |  |

## 10. Blockers

| Blocker ID | Description | Impact | Required Resolution | Owner |
| --- | --- | --- | --- | --- |
| BLK-001 |  |  |  |  |

## 11. Open Questions

| QA ID | Question | Impact | Owner | Blocking |
| --- | --- | --- | --- | --- |
| QA-001 |  |  |  | yes / no |

## 12. Next Actions

| Priority | Action | Owner | Due | Depends On |
| --- | --- | --- | --- | --- |
| high / medium / low |  |  |  |  |

## 13. Handoff Summary

次のAgent / reviewer / user が最初に読むべき要約を記載します。

| Item | Value |
| --- | --- |
| Handoff To |  |
| Continue From |  |
| Must Read Artifacts |  |
| Stop Conditions |  |
| Recommended Next Prompt / Skill |  |

## 14. Evidence

| Evidence ID | Type | Path / Link | Summary |
| --- | --- | --- | --- |
| EVD-001 | command-output / log / screenshot / code / test / review |  |  |

## 15. Quality Checklist

| Check | Status | Notes |
| --- | --- | --- |
| Input artifacts are listed | yes / no |  |
| Repository branch / commit are recorded | yes / no / not-applicable |  |
| Findings have evidence | yes / no / not-applicable |  |
| Decisions include reason | yes / no / not-applicable |  |
| Open QA is explicit | yes / no |  |
| Generated artifacts are indexed | yes / no / not-applicable |  |
| Safety blockers are not hidden | yes / no / not-applicable |  |
