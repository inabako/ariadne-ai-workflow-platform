---
project:
draft:
workflow: requirement-discovery
phase: noise-reduction
artifact: readiness-report
status: draft
language: ja-JP
created_at:
---

# Readiness Report

## Intent

Noise Reduction Phaseの結果から、要件review draftへ進めるかを判定する。

## Readiness

| Field | Value |
| --- | --- |
| Status | PASS / WARNING / BLOCK |
| Reason |  |
| Human Interview Open High Count |  |
| Human Interview Open Medium Count |  |
| Human Interview Open Low Count |  |
| Requirement Review Draft May Start | yes / no |
| Design / Implementation May Start | no |

## Checklist

| Check | Status | Evidence |
| --- | --- | --- |
| Unknown Words整理済み | pass / warning / block |  |
| 用語衝突整理済み | pass / warning / block |  |
| 表記揺れ整理済み | pass / warning / block |  |
| 資料矛盾整理済み | pass / warning / block |  |
| 曖昧表現整理済み | pass / warning / block |  |
| AI推測禁止箇所整理済み | pass / warning / block |  |
| 不足定義整理済み | pass / warning / block |  |
| Human Interview票作成済み | pass / warning / block |  |
| Project Glossary作成済み | pass / warning / block |  |

## Decision Rule

- `PASS`: 設計開始可能な理解度。ただしこのphase自体は設計を開始しない。
- `WARNING`: 軽微な確認あり。Open Questionsへ残して要件review draftへ進める。
- `BLOCK`: Human Interview完了まで設計、実装、完成版要件化を禁止する。
