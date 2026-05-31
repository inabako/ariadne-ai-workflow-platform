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

After intake succeeds, run `/pre-development-preparation`, then continue with `/new-robotics-system-development`.
