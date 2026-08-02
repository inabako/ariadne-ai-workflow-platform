# Artifact Lifecycle Map

この文書は、Ariadne の artifact がどこで作られ、何を source of truth とし、どこまでが生成物または evidence なのかを図で示します。

詳細な保存ルールは `docs/reference/repository-structure.md`、`docs/reference/test-artifact-storage.md`、`docs/reference/rag.md`、`docs/rag/duckdb-read-model.md` を優先します。

## 全体像

```mermaid
flowchart TD
  subgraph WorkflowAssets[AI workflow source assets]
    Ariadne[.ariadne prompts / agents / schemas / shared]
    Skills[skills/*/SKILL.md]
    Templates[templates/*]
    RegistrySeeds[templates/registries/*.json]
  end

  subgraph RegistryReadModel[Generated registry read model]
    RegistryDB[db/registries/registry.duckdb]
  end

  subgraph Intake[Requirement intake]
    Draft[work/requirements/draft]
    Completed[work/requirements]
  end

  subgraph WorkScope[work/work-id]
    Context[context/*.json]
    Design[design-document]
    Reports[process-report]
    Specs[test-specifications]
    Evidence[test-evidence]
    Source[source/repository]
    Expectation[design/expectation]
  end

  subgraph RuntimeLocal[Local runtime generated logs]
    RuntimeLog[logs/runtime/runtime-events.log]
    ActiveTrace[logs/runtime/active-trace.json]
    TestLog[logs/test]
    Metrics[logs/runtime-metrics-YYYYMM.jsonl]
  end

  subgraph TargetEvidence[Target repository evidence]
    TargetDocs[source/repository/docs/evidence/issue-number]
  end

  subgraph KnowledgeSource[Knowledge source workspace]
    KnowledgeMarkdown[work/db/ariadne-knowledge-platform/rag source markdown]
    Normalized[work/db/ariadne-knowledge-platform/rag/normalized]
    Chunks[work/db/ariadne-knowledge-platform/rag/chunks]
    Optimized[work/db/ariadne-knowledge-platform/rag/optimized-chunks]
    Indexes[work/db/ariadne-knowledge-platform/rag/indexes]
    Embeddings[work/db/ariadne-knowledge-platform/rag/embeddings]
    Retrieval[work/db/ariadne-knowledge-platform/rag/retrieval]
  end

  subgraph RagReadModel[Generated RAG read model and evidence]
    RagDB[db/rag/ariadne-knowledge.duckdb]
    RagEvidence[db/rag/evidence]
  end

  Ariadne --> Context
  Skills --> WorkScope
  Templates --> WorkScope
  RegistrySeeds --> RegistryDB
  RegistryDB --> Context

  Draft --> Completed
  Completed --> Context
  Completed --> Design

  Context --> Reports
  Context --> Specs
  Context --> Expectation
  Design --> Reports
  Specs --> Evidence
  Source --> TargetDocs
  Evidence --> TargetDocs

  ActiveTrace --> RuntimeLog
  RuntimeLog --> Reports
  RuntimeLog --> Evidence
  TestLog --> Evidence
  Metrics --> Context

  Reports --> KnowledgeMarkdown
  TargetDocs --> KnowledgeMarkdown
  KnowledgeMarkdown --> Normalized
  Normalized --> Chunks
  Chunks --> Optimized
  Optimized --> Indexes
  Optimized --> Embeddings
  Optimized --> RagDB
  RagEvidence --> RagDB
  Indexes --> Retrieval
  Embeddings --> Retrieval
  RagDB --> Retrieval
  Retrieval --> Context
```

## Artifact分類

| 分類 | 主な場所 | 役割 | Git管理 |
| --- | --- | --- | --- |
| AI workflow source | `.ariadne/`, `skills/`, `templates/` | Agent prompt、schema、Skill、artifact templateのsource | 管理対象 |
| Registry bootstrap source | `templates/registries/*.json` | fresh checkoutでregistry read modelを再生成するsource | 管理対象 |
| Registry read model | `db/registries/registry.duckdb` | `aiwfctl help`、Dispatcher、Human Gate、Doctorが読むruntime read model | 生成物 |
| Requirement source | `work/requirements/` | intake前の正式入力 | 運用により管理 |
| Work context | `work/<work-id>/context/*.json` | Agent / workflow 間で共有する実行context | 作業artifact |
| Process report | `work/<work-id>/process-report/` | 判断、比較、Issue draft、review、handoffの記録 | 作業artifact |
| Test specification | `work/<work-id>/test-specifications/` | UT、integration、human checkの計画 | 作業artifact |
| Test evidence | `work/<work-id>/test-evidence/` | 実行結果、ログ、スクリーンショット、人間確認 | evidence |
| Target evidence | `source/repository/docs/evidence/issue-<number>/` | target repositoryへpushする永続証跡 | target repository側で管理 |
| Runtime log | `logs/runtime/`, `logs/test/` | workflow失敗原因やtrace確認用のlocal observation source | 原則Git管理外 |
| RAG source | `work/db/ariadne-knowledge-platform/rag/...` | Knowledgeとして再利用するMarkdown / JSON source | source repository側で管理 |
| RAG generated artifacts | `normalized/`, `chunks/`, `optimized-chunks/`, `indexes/`, `embeddings/`, `retrieval/` | file-based RAG pipelineの中間・検索artifact | 再生成可能 |
| RAG read model | `db/rag/ariadne-knowledge.duckdb` | RAG sourceを検索・監査しやすくする生成read model | Git管理外 |
| RAG evidence | `db/rag/evidence/` | ingestion optimization、DuckDB migration、reference checkの証跡 | evidence |

## Source Of Truthの考え方

```mermaid
flowchart LR
  Source[Source artifact] --> Generated[Generated artifact]
  Generated --> Evidence[Evidence]
  Evidence --> Decision[Human / Runtime decision]
  Decision --> Feedback[Feedback / Knowledge candidate]

  Generated -.rebuildable.-> Source
  Feedback --> Source
```

生成物は、判断材料として使えても source of truth ではありません。
重要な判断は、source artifact、evidence、Human Gate、Review Council verdict、Feedback report のどれに基づいたかを残します。

## Cleanup Boundary

```mermaid
flowchart TD
  WorkDone[Issue work completed] --> CheckEvidence{Evidence promoted?}
  CheckEvidence -- no --> KeepWork[Keep work directory]
  CheckEvidence -- yes --> CheckKnowledge{Knowledge candidate captured?}
  CheckKnowledge -- no --> KeepWork
  CheckKnowledge -- yes --> Archive[close-archive / cleanup-check]
  Archive --> HumanGate{Human Check approved?}
  HumanGate -- no --> KeepWork
  HumanGate -- yes --> Prune[cleanup-apply]
```

`work/` 配下の一時artifactを削除する前に、target evidence、RAG候補、Review Council / Feedback の判断材料が必要な場所へ昇格していることを確認します。
