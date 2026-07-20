# Runtime Entrypoint Policy

## Purpose

This policy prevents workflow agents from choosing different runtime entrypoints for the same operation.

## Official Entrypoint

Use `aiwfctl` / `runtime/common/ctl.py` as the official runtime entrypoint for normal workflow execution.

`runtime/workflow/*.py` files are internal implementation modules. Do not invoke them directly from SKILL instructions, agent prompts, workflow docs, or human-facing runbooks unless the task is explicitly runtime module development or unit testing for that exact module.

## Windows 11 PowerShell Runtime

When an AI workflow runs on Windows 11, start from the PowerShell-native runtime first:

```powershell
.\runtime\windows-ps1\aiwf.ps1 ctl <aiwfctl-command>
```

This PS1 runtime sets UTF-8 no BOM console encoding, resolves the repository-local runtime paths, avoids Windows Store `python` / `py` aliases, and delegates normal workflow execution to `aiwfctl`.

Do not add workflow-specific decision logic to `runtime/windows-ps1/*.ps1`. If an operation is missing, create a self-improvement Feedback report first. Only Accepted Feedback may later become a governed `runtime/common/ctl.py` change.

## POSIX Bash Runtime

When an AI workflow runs on Linux, WSL, or macOS, start from the bash-native runtime first:

```bash
./runtime/posix-bash/aiwf.sh ctl <aiwfctl-command>
```

This bash runtime sets Python UTF-8 environment variables, resolves the repository-local runtime paths, and delegates normal workflow execution to `aiwfctl`.

Do not add workflow-specific decision logic to `runtime/posix-bash/*.sh`. If an operation is missing, create a self-improvement Feedback report first. Only Accepted Feedback may later become a governed `runtime/common/ctl.py` change.

## Required Routes

| Area | Official route |
| --- | --- |
| Context First manifest and required context checks | `aiwfctl context ...` |
| Human Check registry inspection and approval guard checks | `aiwfctl human-gate ...` |
| GitHub knowledge maintenance analysis, sync, rebase package, replay, and RAG candidates | `aiwfctl github-knowledge ...` |
| close archive prepare / audit / prune | `aiwfctl close-archive ...` |
| self-improvement feedback, review, issue body, and evidence scaffold | `aiwfctl self-improvement ...` |
| DuckDB knowledge read model operations | `aiwfctl knowledge ...` |
| Environment selection and workflow environment checks | `aiwfctl env ...` |

## Missing Entrypoint Rule

If a workflow needs an operation that is not exposed through `aiwfctl`, stop the current operation and create a self-improvement Feedback report first.

Use the official Feedback route:

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "<workflow-or-skill>" `
  --reporter "AI workflow" `
  --situation "Needed runtime operation is not exposed through aiwfctl." `
  --friction "<missing operation and attempted workflow step>" `
  --impact "Agent may bypass the official runtime entrypoint or hide missing runtime capability." `
  --proposed-improvement "Add an official aiwfctl entrypoint in runtime/common/ctl.py after Human Review."
```

After Feedback is recorded, wait for Human Review / accepted self-improvement flow before adding the `runtime/common/ctl.py` command. Do not silently implement the missing entrypoint inside the active workflow.

Do not add a new `python runtime/workflow/*.py ...` direct invocation to SKILL files, agent prompts, workflow docs, or generated process reports as a workaround.

## Reporting Rule

When reporting runtime commands to a human or another agent, prefer the full repository-local form:

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . <command>
```


On Windows 11, prefer the PowerShell-native form:

```powershell
.\runtime\windows-ps1\aiwf.ps1 ctl <command>
```

On Linux, WSL, or macOS, prefer the bash-native form:

```bash
./runtime/posix-bash/aiwf.sh ctl <command>
```

Short `aiwfctl <command>` examples are acceptable only when the surrounding document already states that `runtime/windows-script` is on `PATH`.
