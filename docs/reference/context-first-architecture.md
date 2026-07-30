# Context First Architecture

Context First Architecture は、Workflow / Agent が毎回 Environment、Tool、Runtime を推論する状態を避けるための設計方針です。

先に Dispatcher が標準Contextを生成し、後続WorkflowはそのContextを第一入力として担当処理に集中します。

Dispatcher群と各Workflowの関係図は [Dispatcher / Workflow Map](../diagrams/dispatcher-workflow-map.md) を参照してください。

## 基本原則

1. Workflow は Context を最初に読む。
2. Workflow は Environment / Tool / Runtime を独自推論しない。
3. Dispatcher Context が不足する場合、重要Workflowでは Human Check または Context生成へ戻す。
4. Workflow は実行状態、成果物index、検証結果などの実行Contextを生成・更新できる。
5. Agent は Context を必須の第一入力とし、追加参照は Context に記録された source / artifact / repository に基づく。

## Dispatcher Context と Workflow Context

Context First では、Contextを2種類に分けます。

| 種別 | 生成者 | 例 | 変更ルール |
| --- | --- | --- | --- |
| Dispatcher Context | Dispatcher | `environment-selection.json`, `workflow-selection.json`, `tool-selection.json`, `runtime-context.json`, `execution-plan.json` | Workflowが独自生成・推論しない |
| Workflow Execution Context | Workflow / Agent | `workflow-state.json`, `artifact-index.json`, `scm-state.json`, workflow固有state | 担当処理の結果として更新できる |

これにより、Workflowは「判断」を増やさず、「実行」と「成果物作成」に集中できます。

## Context Directory

各 work directory は `context/` を持ちます。

```text
work/<work-id>/context/
```

初期導入では次を標準Contextとします。

```text
work/<work-id>/context/
  context-manifest.json
  environment-selection.json
```

将来的には次を追加できます。

```text
work/<work-id>/context/
  workflow-selection.json
  tool-selection.json
  runtime-context.json
  execution-plan.json
```

## context-manifest.json

`context-manifest.json` は、その work に存在するContext一覧を示す索引です。

後続Workflow / Agent は、context directoryを探索する前に manifest を確認します。

例:

```json
{
  "schema_version": "1.0",
  "artifact_type": "context-manifest",
  "architecture": "context-first",
  "adoption_phase": "phase-1",
  "work_id": "issue-123",
  "contexts": [
    {
      "type": "environment-selection",
      "path": "work/issue-123/context/environment-selection.json",
      "required": true,
      "generated_by": "environment-dispatcher",
      "owner": "dispatcher",
      "schema": ".ariadne/schemas/environment-selection.schema.json",
      "status": "available"
    }
  ]
}
```

schema:

```text
.ariadne/schemas/context-manifest.schema.json
```

## Environment Dispatcher

現時点で実装済みのDispatcherは Environment Dispatcher です。

```powershell
aiwfctl env select gui-mode --work-id issue-123
```

このコマンドは次を生成します。

```text
work/issue-123/context/environment-selection.json
work/issue-123/context/context-manifest.json
```

## Phase 3 Dispatcher Context

Phase 3では、Environmentだけでなく、workflow、tool、runtime、execution planもDispatcher Contextとして標準化します。

```powershell
aiwfctl context init `
  --work-id issue-123 `
  --workflow /docs-sync `
  --tool gh:read-only:GitHub metadata collection `
  --required-context workflow-selection `
  --required-context tool-selection `
  --next-command "/docs-sync localty-system-gui develop"
```

生成物:

```text
work/issue-123/context/workflow-selection.json
work/issue-123/context/tool-selection.json
work/issue-123/context/runtime-context.json
work/issue-123/context/execution-plan.json
work/issue-123/context/context-manifest.json
```

Workflow / Agent は、これらを独自に推論せず、`context-manifest.json` から参照します。
既存Contextがある場合、`--force` がない限り上書きせず、manifest登録だけを整えます。

### Medium Workflow Adoption

High対象Workflowに続き、Medium対象Workflowもmanifest接続を標準化します。

| Workflow | Context First の役割 |
| --- | --- |
| `/docs-sync` | `scm-state` と `docs-drift-analysis` をmanifestへ登録し、docs差分調査を後続処理へ渡す |
| `/corrective-action-report` | read-only改善レポートの保存先とRAG候補を `corrective-action-report` としてmanifestへ登録する |
| `/github-knowledge-maintenance` | `tool-selection` と `github-operation-gate` を先に確定し、GitHub read-only / mutation判断を明示する |
| `/knowledge-capture` | `scm-state` をmanifest優先で読み、古いworkではfallbackを記録する |
| `/rag-build` | RAG生成pipelineのstage結果を `rag-build-run` としてmanifestへ登録する |
| `/rag-load` | `execution-plan` を検索計画へ接続し、`rag-dispatch-plan` / `rag-load-dispatch` をmanifestへ登録する |

この段階では、既存workを壊さないためにfallbackを許可します。ただし、新規workでは `context-manifest.json` を第一入力として扱います。

### Medium Conditional Gates

Medium対象Workflowは、全面停止ではなく条件付きでContextを必須化します。

| Workflow | 必須化条件 | fallback |
| --- | --- | --- |
| `/docs-sync` | 新規workの `analysis-template` は `scm-state` 必須 | 旧運用だけ `--allow-missing-scm-state` |
| `/github-knowledge-maintenance` | mutation path / RAG publish path は `github-operation-gate` とHuman Check条件を確認 | read-only proposalは軽量に継続 |
| `/knowledge-capture` | active workはmanifest上の `scm-state` 必須 | `work/close/...` archiveと明示旧workはfallback可 |
| `/rag-load` | `--work-id` 指定時は `execution-plan` を確認 | missing時は停止せずHuman Check警告を記録 |

### Tool Candidate Scoring

Tool Dispatcher は `db/registries/registry.duckdb` を参照し、Workflow / Intent / 明示tool入力からtool候補をscore化します。

`tool-selection.json` には次を記録します。

- selected tools
- candidate score
- 選定理由
- read-only / local / mutation / generated mode
- install_required
- mutation_capable
- Human Check理由

mutation、install、Dockerなどhost影響があるtoolは、auto selectionしてもHuman Check対象として残します。

## Human Check

Dispatcher Contextを生成できない場合は Human Check に戻します。

例:

- Environmentが特定できない。
- Tool候補が複数ある。
- Runtimeが未定義である。
- 既存Contextと新しい選択結果が矛盾する。

Human Check後は Dispatcher がContextを更新します。

## 段階導入

一気に全WorkflowへContext必須を強制しません。

| Phase | 方針 |
| --- | --- |
| phase-1 | Contextがあれば必ず読む。`environment-selection.json` と `context-manifest.json` を標準化する |
| phase-2 | 重要Workflowで Dispatcher Context を必須化する |
| phase-3 | 全Workflowで Context First を標準入口にする |

## Workflow側の禁止事項

Workflowは次を行いません。

- Environmentを推測する。
- Toolを推測する。
- Runtimeを推測する。
- Dispatcher Contextを独自生成して判断を上書きする。

ただし、Workflowは次を行えます。

- `workflow-state.json` を更新する。
- `artifact-index.json` を更新する。
- workflow固有stateを更新する。
- test evidence / process reportを出力する。

## 検証

Context First の基本確認:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . context require `
  --work-dir work/issue-123 `
  --context environment-selection
```

戻り値が `human-check-required` の場合、先に Environment Dispatcher を実行します。
