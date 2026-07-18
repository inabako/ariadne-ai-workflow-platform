# DuckDB RAG Read Model

この文書は、RAGデータ管理にDuckDBを導入するPhase 1の責務境界をまとめます。

## 基本方針

DuckDBファイルはsource of truthではありません。

AriadneのRAG source of truthは、引き続きMarkdown、JSON、JSONLなどのfile-based artifactです。DuckDBはそれらを検索・集計・監査しやすくするための生成read modelとして扱います。

そのため、標準のDuckDBファイルは `db/rag/ariadne-knowledge.duckdb` に生成しますが、`db/rag/**` は `.gitignore` でGit管理外です。再生成できる生成物として扱います。

## Phase 1の対象

Phase 1では、既存のRAG pipelineを置き換えません。

```text
file-based RAG artifacts
  -> ingestion_optimizer.py による品質評価
  -> DuckDB generated read model
```

既存の `runtime/rag/ingestion_optimizer.py` を再利用し、DuckDB登録時にも以下の評価値を保存します。

- source reliability
- retrieval usefulness
- freshness
- duplication
- total score
- optimization score
- optimization decision

## Runtime

実装は `runtime/rag/duckdb_store.py` です。

### init

```powershell
uv run --project runtime python runtime/rag/duckdb_store.py init
```

作成される主なtableは以下です。

| Table | 目的 |
| --- | --- |
| `knowledge_documents` | knowledge本体、metadata、source traceability |
| `knowledge_tags` | knowledgeとtagの多対多検索補助 |
| `knowledge_scores` | ingestion optimizer由来の評価値 |

### ingest

```powershell
uv run --project runtime python runtime/rag/duckdb_store.py ingest --file work/db/ariadne-knowledge-platform/rag/optimized-chunks/<id>.json
```

1つのJSON recordをDuckDBへ登録します。

- 同じ `knowledge_id` かつ同じ `content_hash` はskip
- 同じ `knowledge_id` で内容が変わった場合はupdate
- 別IDでも同じ `content_hash` の場合はduplicateとしてskip

### migrate

```powershell
uv run --project runtime python runtime/rag/duckdb_store.py migrate --source work/db/ariadne-knowledge-platform/rag/optimized-chunks
```

指定ディレクトリ配下のJSONを再帰的に登録します。

壊れたJSONや `content` 欠損recordがあっても、移行処理全体は止めません。エラーは `db/rag/migration-errors.jsonl` に出力し、summaryの `failed_count` と `errors` に残します。

### search

```powershell
uv run --project runtime python runtime/rag/duckdb_store.py search `
  --query "PyQt GUI smoke test" `
  --tag gui `
  --environment windows-msys2-gui `
  --limit 10
```

検索は、指定された条件だけを利用します。

- keyword query
- semantic hint
- category
- tag
- source
- document type
- environment
- workflow
- reliability score
- freshness score

結果は、keyword一致、semantic hint一致、relevance、reliability、freshnessを合成した `final_score` 順に並べます。検索結果が0件でも異常終了せず、0件の正常結果として返します。

### export-context

```powershell
uv run --project runtime python runtime/rag/duckdb_store.py export-context `
  --query "PyQt GUI smoke test" `
  --output work/issue-123/context/knowledge.json
```

検索結果をAgentへ渡すContext JSONとして出力します。このJSONも一時生成物であり、RAGの正本ではありません。

## aiwfctl

Phase 2では、`aiwfctl knowledge` からも呼び出せます。

```powershell
aiwfctl knowledge init
aiwfctl knowledge migrate --source work/db/ariadne-knowledge-platform/rag/optimized-chunks
aiwfctl knowledge ingest --file work/db/ariadne-knowledge-platform/rag/optimized-chunks/<id>.json
aiwfctl knowledge search --query "PyQt GUI smoke test" --limit 10
aiwfctl knowledge export-context --query "PyQt GUI smoke test" --output work/issue-123/context/knowledge.json
```

## Git管理

DuckDBファイル、migration error log、RAG蓄積物は生成物です。

Gitへ上げるのはworkflow本体、runtime、docs、schema、prompt、testなどの再現手順です。Ariadne本体側の root `rag/**` は使用せず、生成物は `db/rag/**`、知識sourceは `work/db/ariadne-knowledge-platform/rag/**` に分離します。

RAG source of truthは、標準では `work/db/ariadne-knowledge-platform` にcloneした `ariadne-knowledge-platform` repository側へ置きます。

## RAG吸収標準フロー

RAG吸収は、Ariadne本体の `rag/` に知識を溜める作業ではありません。

標準運用では、作業中の知識候補をHuman承認後に `ariadne-knowledge-platform` へ登録し、Ariadne側ではDuckDB read modelへ再投影します。

```mermaid
flowchart TD
    A[Workflowで知識候補が発生] --> B[work/{workflow-id}/process-report/*.md]
    B --> C{Human承認}
    C -- No --> D[作業証跡として保持<br/>RAGには吸収しない]
    C -- Yes --> E[work/db/ariadne-knowledge-platformへ登録]
    E --> F[normalize / chunk / optimize<br/>JSON source materialを作成]
    F --> G[ariadne-knowledge-platformへcommit / push]
    G --> H[aiwfctl knowledge rebuild]
    H --> I[db/rag/ariadne-knowledge.duckdb]
    I --> J[aiwfctl knowledge verify]
    J --> K[db/rag/evidence/reference-check.json]
    J --> L[db/rag/evidence/context/context-manifest.json]
    K --> M[後続workflow / Agentが参照]
    L --> M
```

### 1. 知識候補を作業領域に残す

各workflowの作業中に発生した知識候補は、まず個別workの `process-report` に保存します。

```text
work/<workflow-id>/process-report/*.md
```

この段階のMarkdownは、まだRAG正本ではありません。作業証跡、候補、Human確認対象として扱います。

### 2. Human承認後にknowledge sourceへ登録する

Human承認された知識だけを、knowledge source repository cloneへ移します。

```text
work/db/ariadne-knowledge-platform
```

このディレクトリはAriadne本体の一時フォルダではなく、`ariadne-knowledge-platform` repositoryのcloneです。

登録対象は、最終的にDuckDB rebuildが読めるJSON source materialへ変換します。

```text
work/db/ariadne-knowledge-platform/rag/normalized/
work/db/ariadne-knowledge-platform/rag/chunks/
work/db/ariadne-knowledge-platform/rag/optimized-chunks/
work/db/ariadne-knowledge-platform/rag/jsonized/
```

Markdownを置くだけではDuckDBには入りません。Markdown sourceを使う場合は、normalize / chunk / optimizeを通して、上記のJSON source materialへ変換します。

### 3. knowledge source repositoryをcommit / pushする

knowledge source clone側で内容を確認し、`ariadne-knowledge-platform` へcommit / pushします。

```powershell
cd work/db/ariadne-knowledge-platform
git status
git add .
git commit -m "docs: add approved RAG knowledge"
git push
```

### 4. Ariadne側でDuckDB read modelを再構築する

Ariadne本体側へ戻り、knowledge source cloneからDuckDB read modelを再構築します。

```powershell
aiwfctl knowledge rebuild `
  --source-repo work/db/ariadne-knowledge-platform `
  --reset
```

生成されるDuckDBは検索用のread modelです。

```text
db/rag/ariadne-knowledge.duckdb
```

このファイルはsource of truthではありません。削除されてもknowledge sourceから再生成できます。

### 5. 参照確認evidenceを残す

rebuild後は、代表queryで検索できることを確認します。

```powershell
aiwfctl knowledge verify `
  --query workflow `
  --query runtime `
  --query RAG `
  --source-repo work/db/ariadne-knowledge-platform
```

`--work-id` / `--work-dir` を省略した場合、汎用のDuckDB reference checkとして次へ集約します。

```text
db/rag/evidence/reference-check.json
db/rag/evidence/context/context-manifest.json
```

後続workflow / Agentは、このmanifestからDuckDB参照可否を確認できます。

### 6. 後続workflowがDuckDBを読む

検索だけ行う場合:

```powershell
aiwfctl knowledge search --query "調べたい内容"
```

Agent投入用Contextを作る場合:

```powershell
aiwfctl knowledge export-context `
  --query "調べたい内容" `
  --output work/<work-id>/context/knowledge.json
```

## 配置責務

| Path | 役割 | Git上の扱い |
| --- | --- | --- |
| `work/<workflow-id>/process-report/*.md` | 作業中の知識候補、Human確認対象 | Ariadne本体では追跡しない |
| `work/db/ariadne-knowledge-platform` | knowledge source repository clone | Ariadne本体では追跡しない。clone側でcommit / pushする |
| `work/db/ariadne-knowledge-platform/rag/normalized` | DuckDB rebuild対象の正規化済みknowledge record | knowledge source側で管理 |
| `work/db/ariadne-knowledge-platform/rag/chunks` | DuckDB rebuild対象のchunk record | knowledge source側で管理 |
| `work/db/ariadne-knowledge-platform/rag/optimized-chunks` | ingestion optimizationでACCEPTされたchunk | knowledge source側で管理 |
| `db/rag/ariadne-knowledge.duckdb` | 生成DuckDB read model | Ariadne本体では追跡しない |
| `db/rag/evidence/` | rebuild / verifyの実行証跡 | Ariadne本体では追跡しない |

## 後続Phase候補

Phase 1では、既存file-based indexとretrievalを壊さないことを優先しました。

Phase 2では、DuckDB read modelに対する検索とAgent向けContext JSON生成を追加しました。

Phase 3では、既存file-based retrievalを維持したまま、`retrieve_context.py` と `rag_dispatcher.py` からDuckDB read modelを任意backendとして利用できるようにしました。

```powershell
uv run --project runtime python runtime/rag/retrieve_context.py `
  "PyQt GUI smoke test" `
  --backend duckdb `
  --duckdb-path db/rag/ariadne-knowledge.duckdb `
  --tag gui `
  --max-chars 4000
```

Dispatcherから利用する場合:

```powershell
uv run --project runtime python runtime/rag/rag_dispatcher.py `
  --task "PyQt GUI smoke test" `
  --retrieval-backend duckdb `
  --duckdb-path db/rag/ariadne-knowledge.duckdb `
  --tag gui
```

`--retrieval-backend duckdb` を指定した場合、dispatcherはfile-based `work/db/ariadne-knowledge-platform/rag/indexes/*.jsonl` の存在確認を要求しません。DuckDB read modelが存在しない場合は、先に `aiwfctl knowledge migrate --source work/db/ariadne-knowledge-platform/rag/optimized-chunks` で再生成します。

Phase 4では、`rag-build` の成果物としてDuckDB migration evidenceを残せるようにしました。

```powershell
uv run --project runtime python runtime/rag/rag_build.py `
  --duckdb-migrate `
  --duckdb-path db/rag/ariadne-knowledge.duckdb
```

`--duckdb-migrate` を指定した場合だけ、RAG build完了後にDuckDB read modelを再生成します。標準では以下を出力します。

| Artifact | Path |
| --- | --- |
| DuckDB read model | `db/rag/ariadne-knowledge.duckdb` |
| Migration evidence | `db/rag/evidence/migration-summary.json` |
| Error log | `db/rag/migration-errors.jsonl` |

`work-id` または `work-dir` が指定されている場合、Context First manifestへ以下を登録します。

- `rag-build-run`
- `rag-duckdb-migration`

これにより、後続workflowは `context-manifest.json` から、RAG build結果とDuckDB migration結果の両方を読めます。

## Phase 5 / Phase 6: 本格運用 rebuild と reference check

DuckDBを本格運用する場合は、RAG材料の正本を `ariadne-knowledge-platform` に置き、Ariadne側ではclone済みsource repoから生成read modelを作ります。

```powershell
aiwfctl knowledge source clone
aiwfctl knowledge source status
```

標準clone先は次の通りです。

```text
work/db/ariadne-knowledge-platform
```

標準運用では、RAG JSON / JSONLは最初から `work/db/ariadne-knowledge-platform/rag/` 配下へ生成します。旧配置や別cloneから取り込む必要がある場合だけ、次を実行します。

```powershell
aiwfctl knowledge source import-local --clean
```

この操作はlocal cloneへJSON材料をコピーするだけです。`ariadne-knowledge-platform` へ反映するには、clone側で内容を確認し、commit / pushします。

DuckDB再構築は、source repoを指定して実行します。

```powershell
aiwfctl knowledge rebuild `
  --source-repo work/db/ariadne-knowledge-platform `
  --reset
```

source repo内では、次の標準RAG JSONソースを探索します。

- `work/db/ariadne-knowledge-platform/rag/optimized-chunks`
- `work/db/ariadne-knowledge-platform/rag/chunks`
- `work/db/ariadne-knowledge-platform/rag/jsonized`
- `work/db/ariadne-knowledge-platform/rag/normalized`

`--reset` を指定した場合、既存の生成DuckDBファイルを削除してから再投入します。DuckDBファイルは生成物なので、Git管理対象にはしません。

`db/rag/` cleanupを行う場合でも、`db/rag/ariadne-knowledge.duckdb` は運用上のread model実体です。削除された場合は正本source repoから再生成できますが、workflow実行前には `workflow_doctor` / `aiwfctl doctor` が欠落を警告します。

```powershell
aiwfctl doctor --fail-on-warning
aiwfctl knowledge rebuild `
  --source-repo work/db/ariadne-knowledge-platform `
  --reset
```

投入後は、代表queryで参照できることを確認します。

```powershell
aiwfctl knowledge verify `
  --query workflow `
  --query runtime `
  --query RAG `
  --source-repo work/db/ariadne-knowledge-platform `
  --work-dir db/rag/evidence `
  --work-id duckdb-reference-check
```

標準では、以下へ参照確認evidenceを書きます。

| Artifact | Path |
| --- | --- |
| DuckDB read model | `db/rag/ariadne-knowledge.duckdb` |
| Migration error log | `db/rag/migration-errors.jsonl` |
| Reference check evidence | `db/rag/evidence/reference-check.json` |

reference checkは、各queryについて検索件数、上位結果、score、source pathを保存します。1つでも `min-results` を満たさないqueryがある場合、statusは `human-check-required` になります。

`--work-id` または `--work-dir` を指定した場合、指定先の `context/context-manifest.json` に `rag-duckdb-reference-check` contextを登録します。

汎用のDuckDB smoke / reference checkは、特定workflowの作業ではなくRAG read modelの実行証跡なので、標準では次へ倒します。

```text
db/rag/evidence/context/context-manifest.json
```

一方、特定Issueや後続workflowに紐づく確認では、従来通り `--work-id <work-id>` を指定し、`work/<work-id>/context/context-manifest.json` に登録します。

```powershell
aiwfctl knowledge verify `
  --query "PyQt GUI" `
  --min-results 1 `
  --output db/rag/evidence/reference-check.json `
  --source-repo work/db/ariadne-knowledge-platform `
  --work-dir db/rag/evidence `
  --work-id duckdb-reference-check
```

Phase 5 / Phase 6の狙いは、DuckDBが「作れる」だけでなく、既存RAGデータを投入した後に実際に参照できることを機械的に残すことです。

後続Phaseでは以下を検討します。

- score集計をRuntime Observability Metricsへ接続する
