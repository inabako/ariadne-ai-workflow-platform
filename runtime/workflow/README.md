# Runtime Workflow

`runtime/workflow/` contains workflow-level helper commands.

## Commands

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
```

This command does not edit the target workspace, install tools, or change VSCode files by itself.

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
