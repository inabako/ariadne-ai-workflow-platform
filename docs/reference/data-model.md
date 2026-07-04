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
docs-drift-analysis.schema.json
workflow-help.schema.json
rag-document.schema.json
rag-chunk.schema.json
rag-embedding.schema.json
rag-dispatch-plan.schema.json
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

よく使うcontext:

| File | Purpose |
| --- | --- |
| `agent-context.json` | project / workflow / safety context |
| `artifact-index.json` | 成果物のpath、status、owner、依存関係 |
| `scm-state.json` | repository、branch、commit、source_dir |
| `docs-drift-analysis.json` | docs-syncの差分分析 |
| `support-repositories.json` | support repositoryや必要component |

## File-Based Policy

現時点では、JSON DBではなくfile-based shared memoryとして扱います。

理由:

- 人間が読める。
- Git差分で追跡できる。
- workflow途中のhandoffが簡単。
- 将来のDB / workflow engine移行前にdata shapeを固定できる。

将来的には、SQLite、DuckDB、PostgreSQL、vector DB、workflow engine state storeへ移行できます。
