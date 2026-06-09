# Specialist Review RAG

このディレクトリは、Specialist Agentのreview結果を内部RAG候補として保存する場所です。

作業中のreview結果は、まず次へ保存します。

```text
work/<id>/process-report/specialist-review-<domain>.md
```

人間がRAG登録を承認した後、durableな知識だけをこのディレクトリへ保存します。

```text
rag/specialist-review/<domain>/
```

## Boundary

Specialist reviewはproject-specificな判断です。

- 外部Web由来のclaim自体は `rag/external-web/<category>/` に保存します。
- Specialist reviewには、どのclaimを信じたか、どのclaimを採用しなかったか、何で検証したかを保存します。
- current source code、test evidence、人間承認済みfindingを外部Web RAGだけで上書きしません。

## Recommended Front Matter

```yaml
---
artifact_type: specialist-review
source_type: internal-work
domain: network
workflow: corrective-action-fix
status: draft
created_at: 2026-06-09T00:00:00+09:00
review_agent: network-realtime-protocol-specialist-agent
reviewed_artifacts:
  - work/issue-123/design-document/network-design.md
internal_rag_used:
  - rag/retrieval/<context-pack>.json
external_web_rag_used:
  - rag/external-web/network/<knowledge>.md
tags:
  - specialist-review
  - network
---
```

## Recommended Sections

```markdown
# Specialist Review: <Domain>

## Review Target

## Findings

## Trusted External Knowledge

| Claim | Source RAG Path | Source URL | Trust Level | Used For | Verified By | Limits / Rejected Scope |
| --- | --- | --- | --- | --- | --- | --- |

## Required Tests

## Open Questions

## RAG Capture Candidate
```
