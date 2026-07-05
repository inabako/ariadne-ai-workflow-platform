---
name: vscode-environment
description: Build or maintain a reproducible VSCode Workspace-as-Code setup with settings, tasks, launch configs, extensions, terminal profiles, AI workflow entry tasks, tests, evidence, and documentation.
argument-hint: "[target-workspace-path | --custom-design]"
agent: agent
---

# VSCode Environment AI Workflow

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

Use:

```text
skills/vscode-environment/SKILL.md
```

## Goal

Build a VSCode environment as Workspace as Code so AI agents and humans can reproduce the same setup without relying on personal user settings.

## 日本語実行方針

このworkflowは、AIさんがAI workflow repositoryを実行しやすくするためのVSCode環境整備を目的にします。記入済み草案は必須ではありません。引数なしの場合はself-provision modeとしてcurrent repositoryを対象にし、既存の `.vscode`、`runtime/tools`、workflow registry、docs、testsを読んで、不足しているrepo-local tooling、task、validator、evidence導線を整えます。

target workspace pathが指定された場合は、target-workspace modeとして対象repoを読みます。この場合も草案は任意です。対象repoの既存設定と実装証跡から安全に推定できるものは推定し、既存 `.vscode` filesは読んでから保全的に変更します。

custom-design modeは、特殊なterminal構成、Docker、extension policy、launch、multi-root、personal path、local-only設定など、repo evidenceだけでは判断できない要件がある場合に使います。このときだけ、任意draftまたはHuman質問で補足します。未解決事項がある場合は `open-questions.md` を作成して停止します。

## Modes And Inputs

Use one of these modes:

1. self-provision mode
   - Trigger: `/vscode-environment` with no argument.
   - Target: current repository / workspace root.
   - Filled draft: not required.
   - Goal: make this AI workflow repository executable by AI agents and humans.

2. target-workspace mode
   - Trigger: `/vscode-environment <target-workspace-path>`.
   - Target: the specified repository / workspace.
   - Filled draft: optional.
   - Goal: inspect the target repository and standardize its VSCode Workspace-as-Code environment.

3. custom-design mode
   - Trigger: explicit custom request, special terminal/Docker/extension/launch/multi-root/local-path requirements, or `--custom-design`.
   - Target: current repository or specified target workspace.
   - Filled draft: optional but useful.
   - Goal: collect choices that cannot be safely inferred from repository evidence.

Required information may come from repository evidence, command arguments, optional drafts, or human answers. Do not require a filled draft for self-provision mode or ordinary target-workspace mode.

Use `work/requirements/devlop-edit-draft/README.md` and `README_*.md` only as optional custom-design intake. If custom requirements are missing, blank, contradictory, or still marked `TODO`, create `open-questions.md` and stop before implementation.

## Flow

1. Select mode: self-provision, target-workspace, or custom-design.
2. Resolve the target workspace from the current repository or the provided path.
3. Read existing `.vscode` files and repository evidence before proposing changes.
4. For custom-design mode only, read optional draft files under `work/requirements/devlop-edit-draft/`; create `open-questions.md` when design choices cannot be safely inferred.
5. Initialize a work area with `runtime/workflow/vscode_environment.py init`.
6. Create or update `workspace-requirements.md`.
7. Validate shared artifacts with the Workspace Shared Artifact Validator.
8. Run `runtime/environment/preflight.py --profile vscode-environment` when applicable.
9. Create `vscode-design.md`.
10. Create `terminal-design.md`.
11. Implement `.vscode/settings.json`, `tasks.json`, `launch.json`, `extensions.json`, and optional `workspace.code-workspace`.
    - If the workspace has repo-local command tools such as `runtime/tools/*.cmd`, add that tools directory to `terminal.integrated.env.windows.Path`.
    - For this workflow repository, include `${workspaceFolder}\\runtime\\tools` so `aiwfctl help` works in VSCode integrated terminals.
    - Add a provisioning/support task for `runtime/tools/register-aiwfctl-path.cmd --shell` when `aiwfctl` should also work from normal PowerShell or Windows Terminal.
    - The same registration and refreshed shell can be invoked through `runtime/tools/aiwfctl.cmd path shell`.
12. Run workspace tests and record evidence.
13. Update setup / troubleshooting docs.
14. If the environment pattern is reusable, capture it under `rag/workspace-environment/` as `YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md`.

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
- Prefer workspace-local Path extension for repo-local tools over requiring personal Windows Path edits.
- When global User Path registration is required, use an explicit helper task such as `workflow:aiwfctl-path-shell`; do not hide User Path changes inside unrelated tasks.
- Record all skipped tests and human-check items.

## RAG Capture

For Localty workspace environment knowledge, use:

```powershell
uv run --project runtime python runtime/workflow/vscode_environment.py rag-template `
  --work-id "vscode-environment" `
  --topic "localty-vscode-environment" `
  --repository "localty"
```

Build approved notes with `runtime/rag/normalize_documents.py --source-dir rag/workspace-environment --document-type workspace-environment-pattern`.
