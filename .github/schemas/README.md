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
| `pytest-ut-spec-sync-report.schema.json` | pytest実体とUT仕様書の同期チェック結果、Context異音検知の証跡 |
| `handoff-package.schema.json` | Agent から次Agentへ渡す要約パッケージ |
| `task-plan.schema.json` | sequential / parallel に処理する task 定義 |
| `task-result.schema.json` | runtime/retrieval による task 実行結果 |
| `scm-state.schema.json` | target repository / branch / issue branch の状態 |
| `support-repositories.schema.json` | RAGやpreflightで判明したsupport repositoryの準備状態 |
| `github-issue.schema.json` | GitHub Issue draft / created record |
| `commit-record.schema.json` | semantic commit の記録 |
| `corrective-action-report.schema.json` | read-only改善レポートの保存先、対象repository/branch、RAG候補、後続fix入力Context |
| `knowledge-capture.schema.json` | PR資料、docs証跡、RAG/docs候補、archive準備の記録 |
| `docs-drift-analysis.schema.json` | 実装とdocsの差分、根拠、Issue化材料、受け入れ条件 |
| `github-knowledge-analysis.schema.json` | GitHub Issue / PR / docs / CARの知識資産、narrative gap、repair proposal、sync action、RAG候補 |
| `github-operation-gate.schema.json` | GitHub read-only収集、mutation、clone、RAG publicationのHuman Check条件 |
| `human-gates.schema.json` | 人間承認が必要なworkflow操作registryの構造定義 |
| `workflow-help.schema.json` | `aiwfctl help` 用workflow prompt command registryの構造定義 |
| `tool-candidates.schema.json` | Context First Tool Dispatcher が参照するtool候補registryの構造定義 |
| `context-manifest.schema.json` | Context First Architectureで `work/<work-id>/context/context-manifest.json` を標準化する構造定義 |
| `environment-selection.schema.json` | `work/<work-id>/context/environment-selection.json` の標準Context構造定義 |
| `workflow-selection.schema.json` | Dispatcherが選択したworkflow command、intent、confidence、Human Check要否 |
| `tool-selection.schema.json` | Dispatcherが選択したtool、read-only / mutation / local mode、Human Check要否 |
| `runtime-context.schema.json` | Context Firstでworkflow実行時のterminal、tool path、検証コマンド、Human Check条件を共有する構造定義 |
| `runtime-metrics.schema.json` | Runtime Observabilityのworkflow / agent / token / context / cost / errorメトリクス |
| `execution-plan.schema.json` | workflow間handoff前に、必要Context、停止条件、次commandを共有する実行計画 |
| `realtime-iac-handoff.schema.json` | Robotics New System + IaCからRealtime IaCへ渡すShared Artifacts、validator結果、残リスク、次command |
| `workflow-environment-profiles.schema.json` | `aiwfctl env` 用Environment Dispatcher registryの構造定義 |
| `workspace-shared-artifact-validation.schema.json` | VSCode Environment workflowの必須artifact検証、条件、未解決QA |
| `vscode-environment-state.schema.json` | VSCode Environment workflowのmode、対象workspace、必須artifact、初期化状態 |
| `gui-mode-state.schema.json` | SVG検出、SYS/FEAT/FIX mode、生成成果物、親workflow返却状態 |
| `web-svg-layout-state.schema.json` | Web画面向けSVG検出、WEB_* mode、生成成果物、親workflow返却状態 |
| `rag-document.schema.json` | RAG投入用に正規化した document |
| `rag-chunk.schema.json` | retrieval / embeddings 用の chunk |
| `rag-ingestion-evidence.schema.json` | RAG吸収前のchunk候補評価、ACCEPT / REWRITE / HUMAN_CHECK / REJECT、Evidence summary |
| `rag-embedding.schema.json` | local embedding index のchunk vector |
| `rag-build-run.schema.json` | RAG build pipelineの入力、stage結果、index、embedding出力、Context登録記録 |
| `rag-duckdb-migration.schema.json` | rag-buildからDuckDB read modelを再生成したmigration evidence |
| `rag-duckdb-reference-check.schema.json` | DuckDB read model構築後に代表queryで参照できることを検証するevidence |
| `sdk-analysis-context.schema.json` | 要件定義工程のSDK事前解析context |
| `sdk-external-discovery.schema.json` | SDKプログラムから外部関連資料の確認候補を作るdiscovery context |
| `system-integration-context.schema.json` | システム統合品質向上workflowの統合ポイント、エミュレータ候補、Human Check context |
| `emulator-setup-context.schema.json` | cloud emulator templateをwork配下へ展開した結果を記録するcontext |
| `emulator-health-context.schema.json` | cloud emulator template展開後のhealth/preflight/evidence context |
| `integration-test-plan-context.schema.json` | Integration Testの実行順序、Human Check、証跡期待値を記録するrunbook context |
| `integration-finalization-context.schema.json` | Integration Test後のEvidence、違和感、完了条件、Knowledge化対象を記録する最終context |
| `rag-dispatch-plan.schema.json` | RAG検索前のintent、metadata、semantic hint、query計画 |
| `rag-retrieval-result.schema.json` | query、selected chunks、dropped chunks、filter条件 |
| `rag-context-pack.schema.json` | 圧縮済みcontext、source、token見積もり |
| `rag-load-dispatch.schema.json` | 複数queryのRAG取得結果、context pack、execution-plan参照、集約context |

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
