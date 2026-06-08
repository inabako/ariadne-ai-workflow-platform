# External Web RAG

外部Web由来の知識を、要件定義と設計工程で補助的に使うためのRAG領域です。

## Source Index

```text
rag/external-web/knowledge-sources.md
```

このファイルは、外部Web調査の入口です。

## Categories

```text
rag/external-web/
  network/
  robotics/
  ai-workflow/
  architecture/
  go-runtime/
  observability/
  video/
  platform/
  retrieval/
```

## Policy

- 外部ページ本文を丸ごと保存しません。
- URL、retrieved_at、source_type、trust_level、claims、verification_notes を保存します。
- current source code、test evidence、人間承認済み運用知見より強い根拠として扱いません。
- 古くなりやすい情報は `verify_before_use: true` を付けます。

## Recommended Artifact

```yaml
---
artifact_type: external-web-knowledge
source_type: external-web
category: network
topic: udp-usage-guidelines
trust_level: official-standard
retrieved_at: 2026-06-09T00:00:00+09:00
verify_before_use: true
sources:
  - https://www.rfc-editor.org/rfc/rfc8085
---

# UDP Usage Guidelines

## Claims

- 

## Requirement Impact

- 

## Design Impact

- 

## Verification Notes

- 
```
