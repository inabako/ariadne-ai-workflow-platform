# Runtime Workflow

`runtime/workflow/` contains workflow-level helper commands.

## Commands

### `gui_mode.py`

Checks `work/requirements/svg-input/<PREFIX>_*.svg`, claims matching files into the Issue work area, and dispatches the shared GaC / UaC GUI Mode extension.

Examples:

```powershell
python runtime/workflow/gui_mode.py init-input
python runtime/workflow/gui_mode.py run --issue-id SYS-0001
python runtime/workflow/gui_mode.py validate --issue-id SYS-0001
```

Corrective Action compatibility:

```powershell
python runtime/workflow/gui_mode.py run `
  --issue-id FIX-123 `
  --work-dir work/issue-123 `
  --mode corrective-improvement
```

`SYS_`, `FEAT_`, and `FIX_` filename prefixes select the parent flow. Matching files are moved into `work/<issue-id>/input/gui/` after the Issue work area exists. No SVG returns `status: skipped`. Generated PyQt6 and QTest files remain candidates under `gac-uac/generated/` and are never copied into target source automatically.

### `docs_sync.py`

Initializes documentation sync work folders, creates a docs drift analysis JSON scaffold, and creates a GitHub Issue body from that JSON.

Examples:

```powershell
python runtime/workflow/docs_sync.py init `
  --repository localty-system-gui `
  --target-branch develop

python runtime/workflow/docs_sync.py analysis-template `
  --work-id develop

python runtime/workflow/docs_sync.py issue-body `
  --work-id develop
```

Primary artifacts:

```text
work/<target-branch>/context/docs-drift-analysis.json
work/<target-branch>/process-report/docs-sync-issue-body-*.md
```

This command does not create GitHub Issues, change docs, push branches, run RAG registration, or move archives by itself.

### `github_knowledge_maintenance.py`

Initializes GitHub Repository Knowledge Maintenance work folders, creates an analysis JSON scaffold, and generates human review plans for repair, GitHub sync, and RAG candidates.

Examples:

```powershell
python runtime/workflow/github_knowledge_maintenance.py init `
  --repository localty-system-gui `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output

python runtime/workflow/github_knowledge_maintenance.py analysis-template `
  --work-id github-knowledge-localty-system-gui-recent

python runtime/workflow/github_knowledge_maintenance.py repair-plan `
  --work-id github-knowledge-localty-system-gui-recent

python runtime/workflow/github_knowledge_maintenance.py github-sync-plan `
  --work-id github-knowledge-localty-system-gui-recent

python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
  --work-id github-knowledge-localty-system-gui-recent
```

Primary artifacts:

```text
work/<work-id>/context/github-knowledge-analysis.json
work/<work-id>/process-report/github-knowledge-repair-plan-*.md
work/<work-id>/process-report/github-documentation-sync-plan-*.md
work/<work-id>/process-report/github-knowledge-rag-candidate-*.md
```

This command does not mutate GitHub, clone repositories, change source code, rewrite Git history, or publish RAG unless the approved subcommand options are provided.

### `init_corrective_action_fix.py`

Initializes base and issue work folders for the corrective action fix workflow.

### `vscode_environment.py`

Initializes VSCode Environment workflow work folders and creates requirements / validation scaffolds.

Examples:

```powershell
python runtime/workflow/vscode_environment.py init `
  --work-id vscode-environment `
  --target-dir C:\github\localty-system-gui

python runtime/workflow/vscode_environment.py draft-template

python runtime/workflow/vscode_environment.py open-questions `
  --work-id vscode-environment

python runtime/workflow/vscode_environment.py requirements-template `
  --work-id vscode-environment

python runtime/workflow/vscode_environment.py validation-template `
  --work-id vscode-environment

python runtime/workflow/vscode_environment.py rag-template `
  --work-id vscode-environment `
  --topic localty-vscode-environment `
  --repository localty
```

Primary artifacts:

```text
work/<work-id>/design-document/workspace-requirements.md
work/<work-id>/design-document/open-questions.md
work/<work-id>/context/workspace-shared-artifact-validation.json
work/<work-id>/process-report/workspace-shared-artifact-validation.md
rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
rag/normalized/<uuid>.json
```

The workspace-environment Markdown is the human-reviewable source note. After human approval, the final reusable knowledge must be normalized into UUID-named JSON under `rag/normalized/`.

This command does not edit the target workspace, install tools, change VSCode files, or run the RAG normalization pipeline by itself.

### `knowledge_capture.py`

Generates the final knowledge-capture package for a completed issue workflow.

Example:

```powershell
python runtime/workflow/knowledge_capture.py `
  --issue issue-11 `
  --repository localty-system-gui `
  --branch feature/issue-11 `
  --base-work-id develop
```

Outputs:

```text
work/<issue-id>/process-report/pull-request-title.md
work/<issue-id>/process-report/pull-request-description.md
work/<issue-id>/process-report/merge-comment.md
work/<issue-id>/process-report/knowledge-capture-report.md
work/<issue-id>/process-report/knowledge-capture-*.json
```

This command does not push, run RAG registration, or move archives. It prepares reports and readiness checks for human approval.

When `--base-work-id` is provided, the report also records the required base work reset:

```text
work/<base-work-id>/process-report
  -> work/close/<issue-id>/process-report/base-work-<base-work-id>
```

Delete `work/<base-work-id>` only after that copy is verified and the user approves deletion.
