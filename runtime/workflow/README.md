# Runtime Workflow

`runtime/workflow/` contains workflow-level helper commands.

## Commands

### `init_corrective_action_fix.py`

Initializes base and issue work folders for the corrective action fix workflow.

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
