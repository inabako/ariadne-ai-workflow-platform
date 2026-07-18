---
name: vscode-environment
description: Build or maintain reproducible VSCode Workspace-as-Code environments for AI workflows. Use when the user selects /vscode-environment or asks to standardize .vscode/settings.json, tasks.json, launch.json, extensions.json, workspace.code-workspace, terminal profiles, AI extension setup, Docker/Git/Python/Node/Java tooling, or evidence-backed VSCode environment setup.
---

# VSCode Environment Workflow

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.github/shared/output-language-policy.md`.

## Purpose

Manage a VSCode development environment as Workspace as Code so AI agents and humans can reproduce the same terminal, task, debug, tool, Docker, Git, language runtime, and evidence workflow setup.

## 日本語運用要約

このworkflowの中心目的は、AIさんが迷わずAI workflow repositoryを実行できるVSCode環境を整えることです。したがって、記入済み草案は入口の必須条件ではありません。引数なしで `/vscode-environment` が選ばれた場合は、self-provision modeとしてcurrent repositoryを対象にし、既存の `.vscode`、`runtime/tools`、`runtime/workflow`、`runtime/registries`、docs、prompts、testsを読みます。そのうえで、repo-local command toolをVSCode統合ターミナルのPATHへ通し、`aiwfctl`、workspace validator、workflow doctor、pytestなどの実行経路を整えます。

target workspace pathが指定された場合は、target-workspace modeとして対象repoを読みます。この場合も、草案は任意です。AIは対象repoの既存設定、README、tooling、test、workflow entrypointを確認し、安全に推定できる既定値だけを使います。既存 `.vscode` filesは必ず読んでから変更し、無条件に置き換えてはいけません。

custom-design modeは、repo evidenceだけでは決められない特殊な設計要件がある場合に使います。たとえば、独自terminal role、Docker運用、extension policy、debug / launch構成、multi-root、personal path、local-only設定、特別なAI workflow taskなどです。この場合は `work/requirements/devlop-edit-draft/README.md` と `README_*.md` を任意の補助入力として扱います。未解決の選択、空欄、矛盾、TODOが残る場合は `open-questions.md` を作成して停止し、人間回答と承認を待ちます。

このworkflowでは、草案の有無よりも「repo evidenceで安全に判断できるか」を優先します。判断できるものは進め、判断できないものは質問する、という切り分けでAIと人間の認識負担を減らします。

実装時は、まず現在の設定を読むことを必須にします。`settings.json`、`tasks.json`、`launch.json`、`extensions.json` が存在する場合は、既存の役割を壊さないように差分追加を優先します。長いinline PowerShellや一時的な個人設定に寄せるのではなく、repositoryにcommitできるhelper script、process task、validator、docsを使って再現性を残します。

完了判断は「ファイルを置いたか」ではなく「AI workflowを呼び出せるか」で行います。少なくともVSCode JSONの妥当性、`aiwfctl help` の導線、repo-local tools PATH、必要なtask label、workflow doctor、pytestまたは該当validatorの結果を確認し、実行できない項目はhuman-check evidenceとして記録します。tool installや既存設定の置換など、環境へ影響する操作はHuman Gateを通します。

この方針により、要件草案がなくても標準整備は進められ、特殊な好みや機械依存の判断だけを人間に戻せます。AIは推測で止まりすぎず、危険な推測だけを止めます。

## Operating Modes

`/vscode-environment` supports three modes. A filled draft is optional and is used only when the requested environment cannot be derived safely from repository evidence.

### 1. self-provision mode

Use this mode when `/vscode-environment` has no argument.

- Target: the current repository / workspace root.
- Purpose: make this AI workflow repository executable by AI agents and humans.
- Filled draft: not required.
- Evidence source: existing repository assets such as `.vscode/`, `runtime/tools/`, `runtime/workflow/`, `runtime/registries/`, docs, prompts, and tests.
- Required behavior: inspect current files, preserve existing settings, add missing repo-local tooling and validation support, then run workspace validators.

### 2. target-workspace mode

Use this mode when `/vscode-environment <target-workspace-path>` is provided.

- Target: the specified repository / workspace path.
- Purpose: standardize that workspace as VSCode Workspace as Code.
- Filled draft: optional.
- Evidence source: target repository files and any supplied human notes.
- Required behavior: read the target `.vscode` files before editing, infer safe defaults from repository evidence, and ask only for information that cannot be determined safely.

Example:

```text
/vscode-environment C:\github\localty-system-gui
```

### 3. custom-design mode

Use this mode when the user wants special terminal roles, Docker behavior, extension policy, launch profiles, personal/local-only paths, multi-root layout, or non-standard workflow entry tasks.

- Target: current repository or specified target workspace.
- Filled draft: optional but useful.
- Human questions: allowed when design choices would materially change committed files or local machine behavior.
- Draft location: `work/requirements/devlop-edit-draft/`.

`work/requirements/devlop-edit-draft/README.md` is the human-editable scaffold. Treat it as a template, not as a filled requirement draft.

Filled drafts may be saved in the same directory as `README_*.md`, for example `README_20260614.md`. Legacy `.txt` drafts in that directory may also be inspected.

If custom-design information is missing, contradictory, blank, or still marked as `TODO`, create `open-questions.md` and stop before implementation.

## Required Inputs

All modes require:

- target workspace, resolved from current repository in self-provision mode or from the command argument in target-workspace mode
- intended AI workflow entry points that can be inferred from registry/docs or supplied by the user
- required tools and runtimes that can be inferred from repository evidence or supplied by the user
- required VSCode extensions, terminal profiles, and task labels when they are being created or changed

## Directory Model

Draft scaffold / intake:

```text
work/requirements/devlop-edit-draft/README.md
work/requirements/devlop-edit-draft/README_YYYYMMDD.md
```

Workflow artifacts stay in this repository:

```text
work/<work-id>/design-document/
work/<work-id>/context/
work/<work-id>/process-report/
work/<work-id>/test-evidence/
```

Workspace files are written only to the target workspace after requirements and validation pass:

```text
<target-workspace>/.vscode/settings.json
<target-workspace>/.vscode/tasks.json
<target-workspace>/.vscode/launch.json
<target-workspace>/.vscode/extensions.json
<target-workspace>/.vscode/<name>.code-workspace
```

## Runtime Helpers

Create or refresh the draft README scaffold:

```powershell
uv run --project runtime python runtime/workflow/vscode_environment.py draft-template
```

Create open questions for unresolved custom-design choices:

```powershell
uv run --project runtime python runtime/workflow/vscode_environment.py open-questions `
  --work-id "vscode-environment"
```

Initialize a workflow work area:

```powershell
uv run --project runtime python runtime/workflow/vscode_environment.py init `
  --work-id "vscode-environment" `
  --target-dir "<target-workspace>"
```

The init command creates both workflow state and Context First runtime context:

```text
work/vscode-environment/context/vscode-environment-state.json
work/vscode-environment/context/runtime-context.json
work/vscode-environment/context/context-manifest.json
```

`runtime-context.json` records the intended terminal scope, repo-local tool paths, verification commands, and Human Check conditions. Read it before changing `.vscode` files or terminal/PATH behavior.

Create a requirements scaffold:

```powershell
uv run --project runtime python runtime/workflow/vscode_environment.py requirements-template `
  --work-id "vscode-environment"
```

Create a shared artifact validation scaffold:

```powershell
uv run --project runtime python runtime/workflow/vscode_environment.py validation-template `
  --work-id "vscode-environment"
```

Create a reusable VSCode environment RAG source note:

```powershell
uv run --project runtime python runtime/workflow/vscode_environment.py rag-template `
  --work-id "vscode-environment" `
  --topic "localty-vscode-environment" `
  --repository "localty"
```

Run environment preflight:

```powershell
uv run --project runtime python runtime/environment/preflight.py `
  --profile vscode-environment `
  --work-id "vscode-environment" `
  --source-dir "<target-workspace>"
```

For VSCode tasks, prefer `type: "process"` plus a repo-local helper script over long inline PowerShell command strings. Do not put `ExecutionPolicy Bypass`, nested PowerShell launchers, or complex `python -c` snippets in `.vscode/tasks.json`.

If the target workspace has repository-local command tools under `runtime/tools/` or another approved tools directory, add that directory to the VSCode integrated terminal PATH in `.vscode/settings.json`.

Example for this workflow repository:

```json
{
  "terminal.integrated.env.windows": {
    "Path": "${workspaceFolder}\\runtime\\tools;${env:Path}",
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
    "AIWF_TEXT_ENCODING": "utf-8"
  }
}
```

This allows commands such as `aiwfctl help list` to work in VSCode terminals without relying on personal user settings.

### UTF-8 First Policy

When provisioning a Windows VSCode workspace that contains Japanese Markdown, prompts, JSON, or workflow docs, declare UTF-8 at the start of the workspace environment instead of relying on auto-detection.

`runtime/workflow/vscode_environment.py init` writes `encoding_contract` into `work/<work-id>/context/runtime-context.json`. Read that contract before implementing `.vscode` files, and treat it as the provisioning baseline unless the target repository has a documented mixed-encoding exception.

Do not treat Codex `~/.codex/config.toml` or project `.codex/config.toml` as a UTF-8 enforcement layer by inventing an `[encoding]` table. Codex config should contain documented Codex settings only. Use `AGENTS.md` or workflow docs for agent-facing UTF-8 policy text, and use `.vscode/settings.json`, `.editorconfig`, PowerShell startup commands, and `aiwfctl doctor` for machine enforcement.

Add or preserve these settings in `.vscode/settings.json` unless the target repository has an explicit, documented encoding exception:

```json
{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": false,
  "files.eol": "\n",
  "terminal.integrated.env.windows": {
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
    "AIWF_TEXT_ENCODING": "utf-8"
  }
}
```

For PowerShell terminal profiles, initialize UTF-8 before the user or agent starts editing or validating text:

```powershell
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
chcp 65001 > $null
```

Keep `.bat` and `.cmd` encoding boundaries intact. If a repository intentionally keeps Windows batch files in Shift_JIS / CP932, preserve that exception with `.editorconfig` rather than forcing all files to UTF-8.

For this workflow repository, include an explicit provisioning task or step that runs:

```powershell
.\runtime\tools\register-aiwfctl-path.cmd --shell
```

This registers `runtime\tools` in User Path and opens a refreshed PowerShell session where `aiwfctl help list` is immediately available.

The same behavior can be invoked through the aiwfctl wrapper:

```powershell
.\runtime\tools\aiwfctl.cmd path shell
```

## Workflow

### 1. Mode Selection And Intake

Select one of the supported modes:

- self-provision mode: no argument; use the current repository as target and do not require a filled draft.
- target-workspace mode: target path argument is provided; read the target repository and use any draft only as supplemental information.
- custom-design mode: special terminal, Docker, extension, launch, local path, multi-root, or workflow task requirements are requested; use draft and/or human questions as supplemental input.

For custom-design mode, the optional draft model is:

```text
work/requirements/devlop-edit-draft/README.md           # scaffold
work/requirements/devlop-edit-draft/README_YYYYMMDD.md  # optional filled draft
```

If custom design requirements are missing, blank, contradictory, or still marked `TODO`, create:

```text
work/<work-id>/design-document/open-questions.md
```

Stop until the human answers and approves.

### 2. Requirements Analysis

Use `.github/agents/workspace-requirements-analyst-agent.prompt.md`.

Create:

```text
work/<work-id>/design-document/workspace-requirements.md
```

The requirements must list the selected mode, target workspace, required tools, extensions, terminal profiles, default shell, tasks, debug targets, AI workflow entry tasks, Docker usage, Git expectations, language runtimes, evidence outputs, and placeholders for personal paths or secrets.

In self-provision mode, derive these from the current repository. For this workflow repository, include `runtime/tools`, `aiwfctl`, `workflow:aiwfctl-path-shell`, `validate_vscode_workspace.py`, and `workflow_doctor.py` when applicable.

### 3. Shared Artifact Validation

Use `.github/agents/workspace-shared-artifact-validator-agent.prompt.md`.

Validate that the requirements include:

- required tools
- required extensions
- required terminal profile structure
- required AI workflow entry points

If missing or contradictory, stop and write:

```text
work/<work-id>/design-document/open-questions.md
work/<work-id>/context/workspace-shared-artifact-validation.json
```

Do not implement `.vscode` files until validation is `pass` or human-approved `conditional-pass`.

### 4. VSCode Design

Use `.github/agents/vscode-architect-agent.prompt.md`.

Create:

```text
work/<work-id>/design-document/vscode-design.md
```

Design `settings.json`, `tasks.json`, `launch.json`, `extensions.json`, and `workspace.code-workspace`.

### 5. Terminal Design

Use `.github/agents/terminal-architect-agent.prompt.md`.

Create:

```text
work/<work-id>/design-document/terminal-design.md
```

Define terminal roles such as Dispatcher, Software Workflow, IaC Workflow, Docker Test, and Evidence. Keep personal paths as placeholders unless the user approves concrete local paths.

### 6. Implementation

Use `.github/agents/workspace-implementer-agent.prompt.md`.

Implement only after requirements, validation, and design artifacts exist. Preserve existing user settings unless the workflow explicitly replaces them. Prefer additive `.vscode` changes and document any migration.

### 7. Test And Evidence

Use `.github/agents/workspace-test-agent.prompt.md`.

Create:

```text
work/<work-id>/test-evidence/workspace-test.md
work/<work-id>/test-evidence/evidence/
```

Test JSON validity, task labels, terminal profile names, debug configs, Docker integration, language runtime commands, and AI workflow startup tasks. If a command needs human observation or external UI state, record it as human-check evidence.

### 8. Documentation

Use `.github/agents/workspace-documentation-writer-agent.prompt.md`.

Update the target workspace README or setup docs with setup steps, recommended extensions, tasks, troubleshooting, and evidence capture instructions.

### 9. RAG Capture And UUID JSON Finalization

When the VSCode environment pattern is reusable for Localty or another target workspace, save a Markdown source note under:

```text
work/db/ariadne-knowledge-platform/rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

Use the runtime helper to create a correctly named draft:

```powershell
uv run --project runtime python runtime/workflow/vscode_environment.py rag-template `
  --work-id "<work-id>" `
  --topic "localty-vscode-environment" `
  --repository "localty"
```

The Markdown file is the human-reviewable source note. It is not the final machine-readable knowledge artifact.

After human approval, normalize the approved source through the file-based RAG pipeline with `--source-dir work/db/ariadne-knowledge-platform/rag/workspace-environment` and `--document-type workspace-environment-pattern`.

```powershell
uv run --project runtime python runtime/rag/normalize_documents.py `
  --source-dir work/db/ariadne-knowledge-platform/rag/workspace-environment `
  --output-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --document-type workspace-environment-pattern
```

The final durable knowledge record is the generated UUID-named JSON document:

```text
work/db/ariadne-knowledge-platform/rag/normalized/<uuid>.json
```

Chunk JSON, indexes, embeddings, and retrieval context packs are derived artifacts from that UUID-named normalized JSON. Use `work/db/ariadne-knowledge-platform/rag/jsonized/<uuid>.json` only as a wrapper for existing non-UUID artifacts; it does not replace the normalized RAG document.

## Human Gates

Stop for human approval before:

- installing missing tools or extensions
- replacing existing `.vscode` files
- changing default terminal or shell behavior
- writing personal absolute paths
- running Docker Desktop or long-running tasks
- accepting `conditional-pass`

## Workflow Feedback Output

During every AI workflow run, capture actionable workflow friction or improvement candidates in `work/feedback/`.
Create or update a Feedback report when you observe ambiguity, repeated checks, missing context/docs, runtime observation gaps, noisy handoffs, encoding issues, or a reusable workflow improvement.

Use the existing helper when creating a new report:

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "<slash-command>" `
  --reporter "AI workflow" `
  --situation "<what was happening>" `
  --friction "<observed friction>" `
  --impact "<impact on quality, speed, or safety>" `
  --proposed-improvement "<candidate improvement>"
```

Keep the initial `Review Status` as `Proposed`. Do not run `/self-improvement` automatically inside this workflow; `/self-improvement` is executed later when feedback has accumulated and a human is ready to review Accepted / Rejected / Deferred decisions.

## Guardrails

- Do not depend on personal VSCode user settings.
- Do not store secrets in `.vscode`, `.code-workspace`, or committed docs.
- Do not infer missing terminal profile names, extension IDs, ports, runtime versions, or workflow task labels.
- Do not overwrite existing workspace files without reading and preserving useful content.
- Keep machine-specific values as placeholders when the workflow output is meant for a repository.
- If repo-local `.cmd`, `.bat`, or executable helper tools are part of the workflow entrypoint, expose their directory through `terminal.integrated.env.windows.Path` instead of requiring each user to edit their personal Windows Path.
- If the workflow needs a command available outside VSCode integrated terminals, include a provisioning task that runs the repo-local PATH registration helper, such as `runtime/tools/register-aiwfctl-path.cmd --shell`.
- Declare UTF-8 early for VSCode files, Python process I/O, and PowerShell terminal I/O when the workspace contains Japanese docs or prompts.
- Do not enable encoding auto-guessing for AI workflow repositories unless the repository explicitly documents mixed encodings.
- Keep generated evidence under `work/<work-id>/test-evidence/`; put durable target-repository docs in the target workspace only when approved.
- Avoid long inline PowerShell / `python -c` in VSCode tasks. Use process tasks that call committed helper scripts such as `runtime/workflow/vscode_task_runner.py`.
- Do not recommend or generate `ExecutionPolicy Bypass` in workspace tasks or install-plan evidence.

## Completion

The workflow is complete when:

- requirements and validation artifacts exist
- `.vscode` and optional `.code-workspace` files are valid JSON / JSONC
- required task and launch entries are testable or have recorded human-check evidence
- Docker / Git / runtime checks are recorded
- setup and troubleshooting docs are updated
- reusable VSCode environment knowledge is captured under `work/db/ariadne-knowledge-platform/rag/workspace-environment/` when it should feed future RAG
- approved reusable knowledge is normalized into UUID-named JSON under `work/db/ariadne-knowledge-platform/rag/normalized/` as the final RAG knowledge artifact
