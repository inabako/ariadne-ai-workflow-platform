# External Web RAG

要件定義、設計工程、改善レポート、改善実装で知見が足りない領域が出た場合に、外部Webの一次情報を精査し、外部Web RAGとして蓄積・dispatchする補助workflowです。

## Purpose

```text
要件を聞く
  -> 知らない領域が出る
  -> 調べる
  -> 外部Web RAGに蓄積する
  -> 要件定義 / 設計 / 改善flowで補助contextとして使う
```

このworkflowは、外部Web情報を要件の最終判断として使うためではありません。

目的は、より良い質問、より安全な制約整理、より明確な設計論点、より広いreview/test観点を作ることです。

## Source Index

URL候補は次に置きます。

```text
rag/external-web/knowledge-sources.md
```

## Directory Layout

```text
rag/
  external-web/
    knowledge-sources.md
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

## Agents

| Agent | Purpose | Output |
| --- | --- | --- |
| `external-web-source-reviewer-agent.prompt.md` | 外部Webを精査し、claims / metadata / verification notesへ圧縮する | `rag/external-web/<category>/*.md` |
| `external-web-rag-dispatcher-agent.prompt.md` | 蓄積済み外部Web RAGを検索・集約して要件/設計/改善flowへ渡す | `rag/external-web/retrieval/*-aggregate.md` |

## Flow

1. Requirement Discoveryで知見不足の領域を見つける。
2. `work/requirements/draft/<draft-stem>-knowledge-gaps.md` にknowledge gapを書く。
3. `rag/external-web/knowledge-sources.md` から関連sourceを選ぶ。
4. External Web Source Reviewerが外部Webを精査する。
5. 外部ページ本文ではなく、claim、metadata、verification notesを保存する。
6. External Web RAG Dispatcherが必要なcategoryを検索・集約する。
7. Requirement review draftに、参照したRAG pathと未確認事項を反映する。
8. Critical itemは人間確認で確定する。

## Corrective Action Integration

改善フローでは、外部Web RAGを次の目的で使います。

- finding候補を広げる
- risk観点を補う
- test観点を補う
- 公式docs / RFC / vendor docsとの照合ポイントを作る
- 実装時のunknown areaを補助する

ただし、外部WebRAGだけでfindingを確定しません。

```text
external-web RAG
  -> supporting_reference
  -> current repo evidenceへ結び直す
  -> finding / issue scope / test specification
```

最終findingには、対象repositoryのfile、behavior、log、docs gap、test gapなどのevidenceが必要です。

## JSON Pipeline

外部Web RAGの吸収内容は、内部RAGと同じ `rag/normalized/*.json` 形式へ変換します。

```text
rag/external-web/<category>/*.md
  -> rag/normalized/*.json
  -> rag/chunks/*.json
  -> rag/indexes/*.jsonl
  -> rag/embeddings/*.jsonl
  -> rag/retrieval/*.json
```

Normalize example:

```powershell
python runtime/rag/normalize_documents.py `
  --source-dir rag/external-web/network `
  --output-dir rag/normalized `
  --document-type external-web-knowledge
```

The normalized JSON keeps external-web provenance under `metadata`:

```json
{
  "document_type": "external-web-knowledge",
  "metadata": {
    "source_type": "external-web",
    "category": "network",
    "topic": "udp-usage-guidelines",
    "trust_level": "official-standard",
    "retrieved_at": "2026-06-09T00:00:00+09:00",
    "verify_before_use": true,
    "sources": ["https://www.rfc-editor.org/rfc/rfc8085"]
  }
}
```

External-web only retrieval:

```powershell
python runtime/rag/retrieve_context.py `
  "Go realtime gateway UDP NAT traversal" `
  --source-type external-web `
  --category network `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000
```

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
claims:
  - UDP applications should include congestion and loss considerations.
verification_notes:
  - Confirm against current gateway design and local packet-loss tests.
---
```

```markdown
# UDP Usage Guidelines

## Claims

- 

## Requirement Impact

- 

## Design Impact

- 

## Verification Notes

- 

## Open Questions

- 
```

## Trust Boundary

外部Web RAGは補助contextです。

優先順位:

1. Current source code
2. Test evidence
3. Human-approved operational findings
4. Internal work RAG
5. External official docs / standards
6. External community sources

外部Web RAGが current code、test evidence、人間回答と矛盾する場合は、人間に確認します。

改善フローでは、外部WebRAGを `supporting_reference` として記録します。

## Requirement Discovery Integration

Requirement Discoveryでは、以下をCritical itemとして扱い、外部Web RAGだけでは確定しません。

- Repository
- Target Branch
- Safety requirements
- STOP / emergency stop behavior
- Communication loss behavior

外部Web RAGは、これらを確定するのではなく、質問の質と設計論点を上げるために使います。
