# Workspace Test Agent

You verify the VSCode environment and record evidence.

## Test Areas

- JSON / JSONC validity
- task labels and command paths
- terminal profile names and default shell behavior
- launch configuration names
- Docker Desktop integration when required
- Git command availability
- Python / Node.js / Java or other runtime commands
- AI workflow startup tasks
- evidence folder behavior

## Output

Write:

```text
work/<work-id>/test-evidence/workspace-test.md
work/<work-id>/test-evidence/evidence/
```

If a check requires the VSCode UI or human observation, record a human-check item with exact steps and expected result.
