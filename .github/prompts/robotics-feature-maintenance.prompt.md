# Robotics Feature Maintenance Skill Entrypoint

## Purpose

`/robotics-feature-maintenance` は、既存 robotics system の新機能追加または保守開発を開始するための Skill entrypoint です。

Use:

```text
skills/robotics-feature-maintenance/SKILL.md
```

Then delegate the detailed workflow to:

```text
/robotics-maintenance-development
```

## Required Intake Gate

Before implementation or design work, run or require:

```powershell
python runtime/intake/intake_requirements.py --workflow robotics-maintenance-development
```

Reject the order when:

- `work/requirements/` has no completed requirement document
- `work/requirements/` has two or more requirement documents
- the requirement document does not contain readable `Repository Control`

Do not proceed from chat history alone.

## Next Step

After intake succeeds, run `/pre-development-preparation`, then run `/rag-load`, then continue with `/robotics-maintenance-development`.

`/rag-load` must search prior corrective action reports in parallel where possible and use `runtime/rag/retrieve_context.py` to generate compressed context packs before maintenance design starts.
