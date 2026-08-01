# Runtime Registry Templates

このディレクトリは、`db/registries/registry.duckdb` をfresh checkoutで再生成するためのbootstrap seedです。

`registry.duckdb` は生成物として `.gitignore` 対象にします。一方で、ARIADNE自身の `aiwfctl help`、`aiwfctl env`、Context First Tool Dispatcher、Human Gate Policy、Workflow Doctor が初期起動に必要とするsource JSONは、templateとしてrepositoryに保持します。

## 責任範囲

- workflow、intake、doctor、将来のruntime補助CLIから共通参照される承認ゲート、分類表、許可リストなどのseedを置きます。
- JSON Schemaは置きません。schema定義は `.ariadne/schemas/` に置きます。
- RAG蓄積物は置きません。RAGは `rag/` 配下で扱います。
- 作業中/close済み成果物は置きません。作業成果物は `work/` 配下で扱います。
- 運用時のknowledge workspace mirrorは `work/db/ariadne-knowledge-platform/registries/` に置きます。

## 現在のregistry

| File | 用途 |
| --- | --- |
| `human_gates.json` | 人間承認が必要なruntime操作のregistry |
| `workflow_help.json` | `aiwfctl help` で表示するAI workflow prompt command / extensionのregistry |
| `search_terms.json` | 検索語registry。各検索語の `id` はUUID、`owner_id` は `workflow_help.json` のsnake_case機能ID |
| `tool_candidates.json` | Context First Tool Dispatcher が参照するtool候補、mode、Human Check条件のregistry |
| `workflow_environment_profiles.json` | `aiwfctl env` で参照する利用者向けEnvironmentと内部Backend profileのregistry |

## 再生成

```powershell
uv run --project runtime python runtime/common/registry_store.py --repo-root . ensure
```

sourceを明示する場合:

```powershell
uv run --project runtime python runtime/common/registry_store.py --repo-root . build --source-dir templates/registries
```
