# VSCode Environment

`/vscode-environment` builds a reproducible VSCode Workspace-as-Code setup for a target repository or workspace.

## Command

```text
/vscode-environment <target-workspace-path>
```

When the command has no argument, the workflow starts from the draft README in:

```text
work/requirements/devlop-edit-draft/README.md
```

Example:

```text
/vscode-environment C:\github\localty-system-gui
```

## Outputs

Workflow artifacts:

```text
work/<work-id>/design-document/workspace-requirements.md
work/<work-id>/design-document/open-questions.md
work/<work-id>/design-document/vscode-design.md
work/<work-id>/design-document/terminal-design.md
work/<work-id>/context/workspace-shared-artifact-validation.json
work/<work-id>/process-report/
work/<work-id>/test-evidence/
```

Target workspace artifacts:

```text
.vscode/settings.json
.vscode/tasks.json
.vscode/launch.json
.vscode/extensions.json
workspace.code-workspace
```

## Flow

1. Place or create a draft README under `work/requirements/devlop-edit-draft/`.
2. Create `open-questions.md` from the draft when required details are missing.
3. Wait for human review and approval.
4. Initialize `work/<work-id>` with the confirmed target workspace.
5. Analyze workspace requirements.
6. Validate shared artifacts.
7. Run environment preflight.
8. Design VSCode settings, tasks, launch configs, extensions, and workspace file.
9. Design terminal profiles and terminal roles.
10. Implement `.vscode` files after validation.
11. Test tasks, terminal startup, Docker/runtime integration, and AI workflow entry tasks.
12. Record evidence.
13. Update setup and troubleshooting docs.
14. Capture reusable workspace knowledge under `rag/workspace-environment/` when it should feed future RAG.

## Stop Rules

Stop and create `open-questions.md` when the command has no target argument, no draft README exists, or required tools, extensions, terminal profiles, AI workflow entry tasks, or evidence requirements are missing or contradictory.

Stop for human approval before installing tools/extensions, replacing existing `.vscode` files, changing default terminal behavior, or accepting `conditional-pass`.

## RAG Capture

Reusable Localty VSCode environment knowledge is stored as source Markdown under:

```text
rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

Create a correctly named note with:

```powershell
uv run python runtime/workflow/vscode_environment.py rag-template `
  --work-id "vscode-environment" `
  --topic "localty-vscode-environment" `
  --repository "localty"
```

After human approval, normalize it as `workspace-environment-pattern` through the file-based RAG pipeline.

## Source Skill

```text
skills/vscode-environment/SKILL.md
```
