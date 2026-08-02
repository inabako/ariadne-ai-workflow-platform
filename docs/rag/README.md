# RAG Documents

このディレクトリは、Ariadne の RAG 運用のうち、read model、吸収品質、検証に関わる文書を置きます。

RAG全体の概念と配置責務は [RAG](../reference/rag.md)、build / load の実行手順は [RAG Build / Load](../workflows/rag-build-load.md) を先に参照してください。

## Documents

| Document | 役割 |
| --- | --- |
| [DuckDB RAG Read Model](duckdb-read-model.md) | DuckDB read model の生成、検索、再構築、Git管理境界 |
| [RAG Knowledge Quality Metrics](knowledge-quality-metrics.md) | ingestion optimization の評価項目、判定、evidence |

## 責務境界

`docs/rag/` は、RAGの内部運用設計を説明する場所です。

- RAG source of truthとcleanup分類は `docs/reference/rag.md` に置く。
- `/rag-build` / `/rag-load` の実行手順は `docs/workflows/rag-build-load.md` に置く。
- DuckDB read model、migration、reference check、quality metrics はこのディレクトリに置く。
- 実際のRAG生成物やknowledge sourceは、このdocsディレクトリには置かない。
