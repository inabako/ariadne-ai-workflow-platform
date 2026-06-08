# Shared Schemas

このディレクトリは、Agent 間で情報を受け渡すための共通 schema を定義します。

目的は、各Agentが別々の表現で判断、QA、finding、test evidence、artifact を書いてしまうことを防ぎ、次のAgentが迷わず読み取れる状態を作ることです。

## Schema List

| File | Purpose |
| --- | --- |
| `agent-context.schema.json` | Agent 実行時に共有する project / workflow / safety context |
| `artifact-index.schema.json` | 生成物の場所、状態、所有Agent、依存関係 |
| `decision-record.schema.json` | 設計判断と理由、代替案、影響範囲 |
| `finding-record.schema.json` | review finding、risk、severity、required action |
| `qa-record.schema.json` | 未解決QA、回答、blocking status |
| `test-evidence.schema.json` | test 実行結果、環境、証跡、残リスク |
| `handoff-package.schema.json` | Agent から次Agentへ渡す要約パッケージ |
| `task-plan.schema.json` | sequential / parallel に処理する task 定義 |
| `task-result.schema.json` | runtime/retrieval による task 実行結果 |
| `scm-state.schema.json` | target repository / branch / issue branch の状態 |
| `support-repositories.schema.json` | RAGやpreflightで判明したsupport repositoryの準備状態 |
| `github-issue.schema.json` | GitHub Issue draft / created record |
| `commit-record.schema.json` | semantic commit の記録 |
| `knowledge-capture.schema.json` | PR資料、docs証跡、RAG/docs候補、archive準備の記録 |
| `docs-drift-analysis.schema.json` | 実装とdocsの差分、根拠、Issue化材料、受け入れ条件 |
| `rag-document.schema.json` | RAG投入用に正規化した document |
| `rag-chunk.schema.json` | retrieval / embeddings 用の chunk |
| `rag-embedding.schema.json` | local embedding index のchunk vector |
| `rag-retrieval-result.schema.json` | query、selected chunks、dropped chunks、filter条件 |
| `rag-context-pack.schema.json` | 圧縮済みcontext、source、token見積もり |

## Usage Rule

Agent は、長い文書だけでなく、次のAgentが使う判断材料を schema に沿って残します。

特に以下は省略しません。

- intent
- decision
- reason
- evidence
- unresolved QA
- risk / severity
- required tests
- artifact path
- owner agent

## Storage Rule

各種 report の最終格納先は、workflow ごとの storage policy で定義します。

この schema では、固定ディレクトリを決めず、`artifact-index.schema.json` の `path` に実際の保存先を記録します。
