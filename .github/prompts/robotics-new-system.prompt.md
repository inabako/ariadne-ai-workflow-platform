# Robotics New System Skill Entrypoint

## Purpose

`/robotics-new-system` は、新しい robotics system を立ち上げるための Skill entrypoint です。

Use:

```text
skills/robotics-new-system/SKILL.md
```

Then delegate the detailed workflow to:

```text
/new-robotics-system-development
```

## Required Intake Gate

Before implementation or design work, run or require:

```powershell
python runtime/intake/intake_requirements.py --workflow new-robotics-system-development
```

Reject the order when:

- `work/requirements/` has no completed requirement document
- `work/requirements/` has two or more requirement documents
- the requirement document does not contain readable `Repository Control`

Do not proceed from chat history alone.

## Next Step

After intake succeeds, run `/pre-development-preparation`, then run `/rag-load`, then continue with `/new-robotics-system-development`.

`/rag-load` must search prior corrective action reports in parallel where possible and use `runtime/rag/retrieve_context.py` to generate compressed context packs before development design starts.

Before implementation starts, run the Boilerplate Template Selection Gate from `/new-robotics-system-development`.

- If a matching template exists under `templates/boilerplate-templates/`, copy it and implement only in the copied destination.
- If no matching template exists, record the fallback reason and continue with traditional coding.
- Record the result in `work/<receipt-id>/process-report/boilerplate-template-selection.md`.
