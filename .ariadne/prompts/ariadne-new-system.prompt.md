# Ariadne New System Skill Entrypoint

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.ariadne/shared/output-language-policy.md` に従って日本語で作成してください。

## Purpose

`/ariadne-new-system` は、新しい対象システムを立ち上げるための Skill entrypoint です。

Use:

```text
.agents/skills/ariadne-new-system/SKILL.md
```

Then delegate the detailed workflow to:

```text
/ariadne-new-system-development
```

## Required Intake Gate

Before implementation or design work, run or require:

```powershell
.\runtime\windows-script\aiwf.cmd ctl intake run --workflow ariadne-new-system-development
```

Reject the order when:

- `work/requirements/` has no completed requirement document
- `work/requirements/` has two or more requirement documents
- the requirement document does not contain readable `Repository Control`

Do not proceed from chat history alone.

## Next Step

After intake succeeds, run `/pre-development-preparation`, then run `/rag-load`, then continue with `/ariadne-new-system-development`.

`/rag-load` must search prior corrective action reports in parallel where possible and use `aiwfctl rag retrieve` through the RAG dispatcher to generate compressed context packs before development design starts.

Before implementation starts, run the Boilerplate Template Selection Gate from `/ariadne-new-system-development`.

- If a matching template exists under `templates/boilerplates/`, copy it and implement only in the copied destination.
- If the system includes realtime gateway IaC / infrastructure, consider `templates/boilerplates/infrastructure/microservice-infra-template/` and preserve the IaC gates for shared artifacts, software inventory, exposure, secrets, firewall policy, rollback, and Terraform validation.
- If no matching template exists, record the fallback reason and continue with traditional coding.
- Record the result in `work/<receipt-id>/process-report/boilerplate-template-selection.md`.
