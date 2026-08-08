---
name: vscode-environment
description: Build or maintain reproducible VSCode Workspace-as-Code environments for AI workflows. Use when the user selects /vscode-environment or asks to standardize .vscode/settings.json, tasks.json, launch.json, extensions.json, workspace.code-workspace, terminal profiles, AI extension setup, Docker/Git/Python/Node/Java tooling, or evidence-backed VSCode environment setup.
---

# Vscode Environment

この Skill は、Codex が `/vscode-environment` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/vscode-environment.prompt.md`
- `docs/workflows/vscode-environment.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
