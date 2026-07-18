# Runtime Entrypoint Policy

## Purpose

This policy prevents workflow agents from choosing different runtime entrypoints for the same operation.

## Official Entrypoint

Use `aiwfctl` / `runtime/ctl.py` as the official runtime entrypoint for normal workflow execution.

`runtime/workflow/*.py` files are internal implementation modules. Do not invoke them directly from SKILL instructions, agent prompts, workflow docs, or human-facing runbooks unless the task is explicitly runtime module development or unit testing for that exact module.

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
uv run --project runtime python runtime/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "<workflow-or-skill>" `
  --reporter "AI workflow" `
  --situation "Needed runtime operation is not exposed through aiwfctl." `
  --friction "<missing operation and attempted workflow step>" `
  --impact "Agent may bypass the official runtime entrypoint or hide missing runtime capability." `
  --proposed-improvement "Add an official aiwfctl entrypoint in runtime/ctl.py after Human Review."
```

After Feedback is recorded, wait for Human Review / accepted self-improvement flow before adding the `runtime/ctl.py` command. Do not silently implement the missing entrypoint inside the active workflow.

Do not add a new `python runtime/workflow/*.py ...` direct invocation to SKILL files, agent prompts, workflow docs, or generated process reports as a workaround.

## Reporting Rule

When reporting runtime commands to a human or another agent, prefer the full repository-local form:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . <command>
```

Short `aiwfctl <command>` examples are acceptable only when the surrounding document already states that `runtime/tools` is on `PATH`.
