# Runtime Registries

`registry.duckdb` is the runtime registry source used by `aiwfctl`, Context First Tool Dispatcher, Human Gate Policy, and Workflow Doctor.

The legacy JSON registry files were migrated to DuckDB and removed from the runtime source tree. A source backup copy is kept in the knowledge workspace:

```text
work/db/ariadne-knowledge-platform/registries/
```

## Tables

| Table | Purpose |
| --- | --- |
| `workflow_help_commands` | AI workflow prompt commands shown and searched by `aiwfctl help` |
| `workflow_help_extensions` | Workflow extension help shown by `aiwfctl help` |
| `workflow_help_search_terms` | Natural-language intent and synonym terms linked to help commands/extensions |
| `tool_candidates` | Tool candidate records used by Context First Tool Dispatcher |
| `human_gates` | Runtime operations that require Human Check |
| `workflow_environments` | Public environment names shown by `aiwfctl env` |
| `environment_profiles` | Internal backend profiles for environment selection |
| `environment_mappings` | Workflow/target mappings for environment selection |

## Maintenance

Build or refresh the DuckDB registry from the backup JSON source:

```powershell
uv run --project runtime python runtime/registry_store.py --repo-root . build
```

Inspect row counts:

```powershell
uv run --project runtime python runtime/registry_store.py --repo-root . summary
```

Schema definitions remain under `.github/schemas/`; generated work artifacts remain under `work/`.
