# Mermaid Diagrams

このディレクトリは、Ariadne AI Workflow の視覚理解を速くするためのMermaid図を置きます。

## Documents

| Document | Purpose |
| --- | --- |
| [Workflow Flowcharts](workflow-flowcharts.md) | 各AI workflow、RAG Build / Load、Review Council Runtime、Expectation-Driven Design、Runtime TraceのMermaid式flowchart |
| [Workflow Flowchart Process Tables](workflow-flowchart-process-tables.md) | flowchartを業務工程、入力、出力、Gateへ読み替える横断資料 |
| [Dispatcher / Workflow Map](dispatcher-workflow-map.md) | Dispatcher群と各Workflowの関係、Context First gate、RAG dispatch、Review Council接続、Runtime Observability、`.ariadne` / registry境界の位置づけ |
| [Artifact Lifecycle Map](artifact-lifecycle-map.md) | work、context、evidence、logs、RAG、registry、DuckDB read modelのartifact lifecycle |
| [aiwfctl Runtime Command Map](aiwfctl-runtime-command-map.md) | `aiwfctl` command、runtime module、入出力artifactの対応関係 |
| [Human Gate / Side Effect Map](human-gate-side-effect-map.md) | 人間承認が必要な副作用操作、停止、再開、証跡の流れ |
| [Knowledge / RAG Lifecycle Deep Map](knowledge-rag-lifecycle-deep-map.md) | Knowledge候補、RAG source、build、DuckDB read model、retrieval、cleanupの詳細関係 |
| [OSS Release Audit Map](oss-release-audit-map.md) | REUSE、ScanCode、Dependency Review、release evidence、GitHub Security Advisoriesの監査関係 |

## Rule

- Mermaid図は、詳細手順そのものではなく、動作イメージを掴むための入口として使います。
- 表ベースの解説は、flowchartを業務工程、入力、出力、gateへ読み替えるために使います。
- 詳細な実行手順は `docs/workflows/` と `.agents/skills/<skill-name>/SKILL.md` をsource of truthにします。
- RAG、Review Council、Expectation-Driven Design、Runtime Observabilityなどの主要workflowを変更した場合は、実行手順docsだけでなく、このディレクトリのflowchartと工程表も同期します。
