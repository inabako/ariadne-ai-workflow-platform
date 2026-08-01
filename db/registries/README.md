# Runtime Registries

`registry.duckdb` は、`aiwfctl`、Context First Tool Dispatcher、Human Gate Policy、Workflow Doctor が参照するruntime registry read modelです。

`registry.duckdb` は生成物のためrepositoryにはcommitしません。fresh checkout時のbootstrap sourceは次に置きます。

```text
templates/registries/
```

運用中にknowledge workspace側へmirror / backupする場合は、次のpathを使います。

```text
work/db/ariadne-knowledge-platform/registries/
```

`workflow_help.json` はhelp command / extension payloadを保持します。各項目の `id` は `ariadne_new_system` のようなsnake_case機能IDです。検索語は `search_terms.json` に分離し、各検索語はUUID `id` と `owner_id` で対象機能IDへ接続します。

## Tables

| Table | Purpose |
| --- | --- |
| `workflow_help_commands` | `aiwfctl help` で表示・検索するAI workflow prompt command |
| `workflow_help_extensions` | `aiwfctl help` で表示・検索するworkflow extension |
| `search_terms` | registry itemへ接続する自然文intentや同義語 |
| `tool_candidates` | Context First Tool Dispatcher が参照するtool candidate |
| `human_gates` | Human Checkが必要なruntime operation |
| `workflow_environments` | `aiwfctl env` に表示する利用者向けEnvironment |
| `environment_profiles` | 内部backend profile |
| `environment_mappings` | workflow / target とenvironment profileの対応 |

## Maintenance

DuckDB registryをbootstrap sourceからbuild / refreshします。

```powershell
uv run --project runtime python runtime/common/registry_store.py --repo-root . build
```

DuckDB registryが存在することを確認し、欠落時だけbootstrap sourceから再生成します。

```powershell
uv run --project runtime python runtime/common/registry_store.py --repo-root . ensure
```

Runtime registry readersも、`db/registries/registry.duckdb` が欠落し、source JSONが揃っている場合は自動でensureを実行します。sourceの優先順は次です。

1. `templates/registries/`
2. `work/db/ariadne-knowledge-platform/registries/`

row countを確認します。

```powershell
uv run --project runtime python runtime/common/registry_store.py --repo-root . summary
```

Schema definitionsは `.ariadne/schemas/`、生成されたwork artifactは `work/` に置きます。
