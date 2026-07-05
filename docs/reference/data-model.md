# Data Model

このworkflow repoでは、Agent間共有dataをJSON Schemaとfile-based contextで扱います。

## Schema Location

```text
.github/schemas/
```

代表的なschema:

```text
agent-context.schema.json
artifact-index.schema.json
decision-record.schema.json
finding-record.schema.json
qa-record.schema.json
test-evidence.schema.json
handoff-package.schema.json
task-plan.schema.json
task-result.schema.json
scm-state.schema.json
github-issue.schema.json
commit-record.schema.json
corrective-action-report.schema.json
docs-drift-analysis.schema.json
github-knowledge-analysis.schema.json
github-operation-gate.schema.json
workflow-help.schema.json
tool-candidates.schema.json
context-manifest.schema.json
environment-selection.schema.json
workflow-selection.schema.json
tool-selection.schema.json
runtime-context.schema.json
execution-plan.schema.json
rag-document.schema.json
rag-chunk.schema.json
rag-embedding.schema.json
rag-build-run.schema.json
rag-dispatch-plan.schema.json
rag-load-dispatch.schema.json
rag-retrieval-result.schema.json
rag-context-pack.schema.json
support-repositories.schema.json
knowledge-capture.schema.json
```

## Context Location

実データはprojectごとのwork folderに保存します。

```text
work/<work-id>/context/*.json
```

Context First Architectureでは、`context-manifest.json` を先に読みます。manifestは、そのworkに存在するDispatcher Context / Workflow Execution Contextの索引です。

よく使うcontext:

| File | Purpose |
| --- | --- |
| `context-manifest.json` | Context Firstの索引。存在するContext、生成者、schema、必須扱いを示す |
| `environment-selection.json` | Environment Dispatcherが生成する実行環境Context |
| `workflow-selection.json` | Workflow Dispatcherが生成するworkflow command / intent / confidence Context |
| `tool-selection.json` | Tool Dispatcherが生成するtool / mode / Human Check Context |
| `runtime-context.json` | Runtime Dispatcherが生成するterminal / tool path / verification command Context |
| `execution-plan.json` | Execution Plannerが生成する実行順序、必須Context、停止条件、次command Context |
| `agent-context.json` | project / workflow / safety context |
| `artifact-index.json` | 成果物のpath、status、owner、依存関係 |
| `scm-state.json` | repository、branch、commit、source_dir |
| `docs-drift-analysis.json` | docs-syncの差分分析 |
| `support-repositories.json` | support repositoryや必要component |

Dispatcher ContextはDispatcherが生成し、Workflowは独自推論で上書きしません。Workflowは `workflow-state.json`、`artifact-index.json`、workflow固有stateなど、実行結果としてのContextを更新できます。

### Additional Workflow Contexts

Medium対象Workflowでは、次のContextもmanifestへ登録します。

| File | Purpose |
| --- | --- |
| `github-operation-gate.json` | GitHub read-only / mutation / clone / Human Check 要否を示すContext |
| `github-knowledge-analysis.json` | GitHub Issue / PR / docs / CAR / commit情報の知識保守分析Context |
| `rag-build-run.json` | RAG build pipelineの入力、stage結果、index、embedding出力Context |
| `rag-dispatch-plan.json` | RAG検索前のquery plan / metadata filter / semantic hint Context |
| `rag-load-dispatch.json` | RAG検索結果と圧縮済みContext packのdispatch Context |

### Corrective Action Report Context

`corrective-action-report.json` は、read-only改善レポートの保存先、対象repository / branch、RAG候補、後続fix入力を記録します。

## File-Based Policy

現時点では、JSON DBではなくfile-based shared memoryとして扱います。

理由:

- 人間が読める。
- Git差分で追跡できる。
- workflow途中のhandoffが簡単。
- 将来のDB / workflow engine移行前にdata shapeを固定できる。

将来的には、SQLite、DuckDB、PostgreSQL、vector DB、workflow engine state storeへ移行できます。
