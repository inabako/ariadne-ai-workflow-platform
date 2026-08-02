# Knowledge / RAG Lifecycle Deep Map

この文書は、作業中の発見が長期Knowledgeになり、RAG build / load / DuckDB read modelを通じて後続workflowへ戻る流れを図で示します。

詳細は `docs/reference/rag.md`、`docs/workflows/rag-build-load.md`、`docs/workflows/knowledge-capture.md`、`docs/rag/duckdb-read-model.md`、`docs/rag/knowledge-quality-metrics.md` を優先します。

## 全体像

```mermaid
flowchart TD
  subgraph Discovery[Knowledge discovery]
    WorkReport[work process reports]
    TestEvidence[test evidence]
    ReviewCouncil[Review Council artifacts]
    GitHubKnowledge[GitHub knowledge maintenance]
    ExternalWeb[External Web RAG notes]
    WorkspaceEnv[Workspace environment notes]
  end

  subgraph Approval[Adoption decision]
    Candidate[Knowledge / RAG candidate]
    HumanGate{Human approval / workflow verification}
  end

  subgraph SourceRepo[Knowledge source workspace]
    SourceMarkdown[work/db/ariadne-knowledge-platform/rag source Markdown]
    Normalized[normalized UUID JSON]
  end

  subgraph BuildPipeline[File-based RAG build]
    RawChunks[raw chunk JSON]
    Optimization[ingestion optimization]
    Optimized[accepted optimized chunks]
    Indexes[JSONL indexes]
    Embeddings[local embeddings]
    BuildRun[rag-build-run-latest.json]
  end

  subgraph ReadModels[Generated read models]
    DuckDB[db/rag/ariadne-knowledge.duckdb]
    DuckEvidence[db/rag/evidence]
  end

  subgraph Retrieval[Context retrieval]
    DispatchPlan[rag-dispatch-plan.json]
    ContextPack[rag-context-pack.json]
    LoadDispatch[rag-load-dispatch.json]
  end

  WorkReport --> Candidate
  TestEvidence --> Candidate
  ReviewCouncil --> Candidate
  GitHubKnowledge --> Candidate
  ExternalWeb --> Candidate
  WorkspaceEnv --> Candidate

  Candidate --> HumanGate
  HumanGate -- no --> ReviewPending[review pending / rejected note]
  HumanGate -- yes --> SourceMarkdown

  SourceMarkdown --> Normalized
  Normalized --> RawChunks
  RawChunks --> Optimization
  Optimization --> Optimized
  Optimization --> QualityEvidence[db/rag/evidence/ingestion]
  Optimized --> Indexes
  Optimized --> Embeddings
  Indexes --> BuildRun
  Embeddings --> BuildRun

  Optimized --> DuckDB
  QualityEvidence --> DuckEvidence
  DuckEvidence --> DuckDB

  BuildRun --> DispatchPlan
  Indexes --> ContextPack
  Embeddings --> ContextPack
  DuckDB --> ContextPack
  DispatchPlan --> ContextPack
  ContextPack --> LoadDispatch
  LoadDispatch --> Workflow[Development / review workflow]
```

## Knowledge source種類

| Source | 保存先 | 採用時の注意 |
| --- | --- | --- |
| Corrective Action Report | `work/db/ariadne-knowledge-platform/rag/corrective-action-report/` | finding、risk、missing test、修正判断を抽出する |
| GitHub Knowledge | `work/db/ariadne-knowledge-platform/rag/github-knowledge/` | Issue / PR / review / releaseの説明資産として扱う |
| Workspace Environment | `work/db/ariadne-knowledge-platform/rag/workspace-environment/` | VSCode / terminal / tool環境の再現知識として扱う |
| External Web | `work/db/ariadne-knowledge-platform/rag/external-web/<category>/` | URL、retrieved_at、claims、verification_notesを残し、repo evidenceを上書きしない |
| Specialist Review | `work/db/ariadne-knowledge-platform/rag/specialist-review/<domain>/` | reviewed artifact、使ったRAG、採用/不採用claim、未解決QAを残す |
| Review Council | `work/db/ariadne-knowledge-platform/rag/review-council/<work-id>/<review-id>/` | verdict、finding、evidence gate、challenge、human gateを残す |

## Absorption Quality

```mermaid
flowchart TD
  Chunk[raw chunk candidate] --> Score[quality scoring]
  Score --> Decision{ACCEPT / REWRITE / HUMAN_CHECK / REJECT}
  Decision -- ACCEPT --> Accept[optimized-chunks]
  Decision -- REWRITE --> Rewrite[rewritten chunk]
  Rewrite --> Score
  Decision -- HUMAN_CHECK --> HumanReview[human-check-required evidence]
  Decision -- REJECT --> Reject[rejected evidence]

  Accept --> Index[index / embedding]
  HumanReview --> SourceFix[fix source or approve explicitly]
  SourceFix --> Chunk
```

RAG buildは、Markdownをそのまま検索indexへ流しません。
`ingestion optimization` で意味のまとまり、traceability、metadata、重複、曖昧さを評価し、`ACCEPT` 済みchunkだけを通常のindex / embedding対象にします。

## Load / Dispatch

```mermaid
flowchart TD
  ExecutionPlan[execution-plan.json] --> QueryPlan[RAG query planning]
  Task[task / repository / branch] --> QueryPlan
  QueryPlan --> DispatchPlan[rag-dispatch-plan.json]
  DispatchPlan --> Backend{Retrieval backend}
  Backend -- file --> FileIndex[indexes / embeddings]
  Backend -- duckdb --> DuckDB[db/rag/ariadne-knowledge.duckdb]
  FileIndex --> Retrieve[retrieve context]
  DuckDB --> Retrieve
  Retrieve --> ContextPack[rag-context-pack.json]
  ContextPack --> LoadDispatch[rag-load-dispatch.json]
  LoadDispatch --> Manifest[context-manifest.json]
```

`rag-load` は検索結果だけでなく、「なぜそのqueryで検索したか」を `rag-dispatch-plan` に残します。
後続workflowは、context packの内容だけでなく検索意図も確認します。

## Cleanupとの関係

```mermaid
flowchart TD
  WorkScope[temporary work scope] --> Candidate[Knowledge candidate]
  Candidate --> Approved{approved and normalized?}
  Approved -- no --> NoCleanup[cleanup not ready]
  Approved -- yes --> ArtifactIndex[artifact-index cleanup evidence]
  ArtifactIndex --> CleanupCheck[work cleanup-check]
  CleanupCheck --> CleanupGate{work-delete approved?}
  CleanupGate -- no --> Keep[keep work]
  CleanupGate -- yes --> CleanupApply[cleanup-apply]
```

`chunks`、`optimized-chunks`、`indexes`、`embeddings`、`retrieval` は再生成可能な派生成果物です。
cleanup可否の根拠にする場合は、承認済みsourceまたは normalized JSON が `artifact-index.json` に記録されている必要があります。
