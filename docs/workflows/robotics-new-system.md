# Robotics New System

新しい robotics system、robot runtime、remote operation system、device integration、architecture-level launch を始めるworkflowです。

## Command

```text
/robotics-new-system
```

## Required Input

完成版の要件定義書が必要です。

```text
work/requirements/<completed-requirements>.md
```

要件定義書には `Repository Control` を含めます。

## Flow

```text
Intake
  -> Repository Sync
  -> Requirement Comparison
  -> GitHub Issue Draft / Create
  -> Working Branch Create
  -> RAG Load / Prior Findings
  -> Intent / Mission
  -> Operational Context
  -> Hazard Analysis / Safety Requirements
  -> System Architecture
  -> Runtime / Network / Deployment Design
  -> Test Strategy
  -> Implementation
  -> Integration / Bench Test
  -> Limited Field Test
  -> Release / Operation Handover
  -> Semantic Commit
```

## Stop Rules

次が未定義なら先へ進めません。

- STOP / emergency stop behavior
- communication loss behavior
- startup safe state
- shutdown safe state
- rollback path
- observability

Critical / high safety finding が残っている場合、field testへ進めません。

## Main Artifacts

```text
work/<receipt-id>/design-document/
work/<receipt-id>/process-report/
work/<receipt-id>/test-specifications/
work/<receipt-id>/test-evidence/
work/<receipt-id>/context/
```

## Source Skill

```text
skills/robotics-new-system/SKILL.md
```
