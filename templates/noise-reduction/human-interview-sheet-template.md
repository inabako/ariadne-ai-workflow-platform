---
project:
draft:
workflow: requirement-discovery
phase: noise-reduction
artifact: human-interview-sheet
status: draft
language: ja-JP
created_at:
---

# Human Interview Sheet

## Intent

Noise Reductionで検出した不明点、衝突、矛盾、曖昧表現、推測禁止箇所を人間へ確認する。

## Questions

| ID | Question | Reason | Impact Area | Priority | Related Reports | Blocks Readiness | Owner | Answer |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HI-001 |  |  |  | High / Medium / Low |  | yes / no |  |  |

## Interview Rule

- High優先度かつ`Blocks Readiness: yes`の質問が未回答なら、Readinessは`BLOCK`にする。
- 回答はProject Glossaryまたは該当reportへ反映する。
