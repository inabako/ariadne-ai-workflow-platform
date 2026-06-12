---
name: vscode-environment
description: Build or maintain a reproducible VSCode Workspace-as-Code setup with settings, tasks, launch configs, extensions, terminal profiles, AI workflow entry tasks, tests, evidence, and documentation.
argument-hint: "<target-workspace-path>"
agent: agent
---

# VSCode Environment AI Workflow

Use:

```text
skills/vscode-environment/SKILL.md
```

## Goal

Build a VSCode environment as Workspace as Code so AI agents and humans can reproduce the same setup without relying on personal user settings.

## Required Inputs

- draft README under `work/requirements/devlop-edit-draft/`
- target workspace path, either in the draft or human answers
- required tools
- required extensions
- required terminal profiles
- required AI workflow entry tasks

If `/vscode-environment` has no argument, do not use the current directory as the target. Read the draft README from `work/requirements/devlop-edit-draft/`, create `open-questions.md`, and stop.

If any required input is missing from the draft, stop and create `open-questions.md`.

## Flow

1. Read or create the draft README under `work/requirements/devlop-edit-draft/`.
2. Create `open-questions.md` when arguments or draft details are missing.
3. Wait for human review and approval.
4. Initialize a work area with `runtime/workflow/vscode_environment.py init`.
5. Create or update `workspace-requirements.md`.
6. Validate shared artifacts with the Workspace Shared Artifact Validator.
7. Run `runtime/environment/preflight.py --profile vscode-environment`.
8. Create `vscode-design.md`.
9. Create `terminal-design.md`.
10. Implement `.vscode/settings.json`, `tasks.json`, `launch.json`, `extensions.json`, and optional `workspace.code-workspace`.
11. Run workspace tests and record evidence.
12. Update setup / troubleshooting docs.
13. If the environment pattern is reusable, capture it under `rag/workspace-environment/` as `YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md`.

## Agents

- `.github/agents/workspace-requirements-analyst-agent.prompt.md`
- `.github/agents/workspace-shared-artifact-validator-agent.prompt.md`
- `.github/agents/vscode-architect-agent.prompt.md`
- `.github/agents/terminal-architect-agent.prompt.md`
- `.github/agents/workspace-implementer-agent.prompt.md`
- `.github/agents/workspace-test-agent.prompt.md`
- `.github/agents/workspace-documentation-writer-agent.prompt.md`

## Guardrails

- Do not overwrite existing `.vscode` files until they have been read.
- Do not store secrets or personal tokens.
- Do not install tools or extensions without human approval.
- Do not use personal absolute paths in committed workspace files unless the user explicitly asks for local-only setup.
- Use placeholders for machine-specific paths.
- Record all skipped tests and human-check items.

## RAG Capture

For Localty workspace environment knowledge, use:

```powershell
uv run python runtime/workflow/vscode_environment.py rag-template `
  --work-id "vscode-environment" `
  --topic "localty-vscode-environment" `
  --repository "localty"
```

Build approved notes with `runtime/rag/normalize_documents.py --source-dir rag/workspace-environment --document-type workspace-environment-pattern`.
