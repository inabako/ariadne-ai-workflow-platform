# Ariadne Feature Maintenance Skill Entrypoint

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.ariadne/shared/output-language-policy.md` に従って日本語で作成してください。

## Purpose

`/ariadne-feature-maintenance` は、既存対象システムの新機能追加または保守開発を開始するための Skill entrypoint です。

Use:

```text
skills/ariadne-feature-maintenance/SKILL.md
```

Then delegate the detailed workflow to:

```text
/ariadne-feature-maintenance-development
```

## Required Intake Gate

Before implementation or design work, run or require:

```powershell
.\runtime\windows-script\aiwf.cmd ctl intake run --workflow ariadne-feature-maintenance-development
```

Reject the order when:

- `work/requirements/` has no completed requirement document
- `work/requirements/` has two or more requirement documents
- the requirement document does not contain readable `Repository Control`

Do not proceed from chat history alone.

## Next Step

After intake succeeds, run `/pre-development-preparation`, then run `/rag-load`, then continue with `/ariadne-feature-maintenance-development`.

`/rag-load` must search prior corrective action reports in parallel where possible and use `aiwfctl rag retrieve` through the RAG dispatcher to generate compressed context packs before maintenance design starts.
