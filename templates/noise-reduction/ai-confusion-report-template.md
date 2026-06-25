---
project:
draft:
workflow: requirement-discovery
phase: noise-reduction
artifact: ai-confusion-report
status: draft
language: ja-JP
created_at:
---

# AI Confusion Report

## Intent

AIが推測しそうになった箇所、意味を取り違えそうな箇所、補完禁止の箇所を明示する。

## Confusion Points

| ID | Text / Term | Possible Wrong Guess | Why Guessing Is Dangerous | Required Human Answer | Priority | Human Interview ID |
| --- | --- | --- | --- | --- | --- | --- |
| AC-001 |  |  |  |  | High / Medium / Low | HI-001 |

## Rule

- 推測した内容を要件定義書へ入れない。
- 不明なままなら `Open Questions` に残す。
