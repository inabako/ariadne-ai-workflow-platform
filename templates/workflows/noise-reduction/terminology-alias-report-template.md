---
project:
draft:
workflow: requirement-discovery
phase: noise-reduction
artifact: terminology-alias-report
status: draft
language: ja-JP
created_at:
---

# Terminology Alias Report

## Intent

表記揺れ、略称、同義語候補を抽出し、用語統一の判断材料にする。

## Alias Candidates

| ID | Canonical Candidate | Alias / Variant | Source Documents | Same Meaning? | Risk | Priority | Human Interview ID |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TA-001 |  |  |  | yes / no / unknown |  | High / Medium / Low | HI-001 |

## Notes

- 同義語かどうか不明な場合は `unknown` とする。
- DB field、API field、event name、state nameは特に慎重に扱う。
