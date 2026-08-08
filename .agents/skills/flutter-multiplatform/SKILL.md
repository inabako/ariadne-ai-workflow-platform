---
name: flutter-multiplatform
description: Use when a workflow must create, modify, analyze, test, or build a Flutter application for Android, iOS, Web, Windows, macOS, or Linux while preserving target-platform selection, environment dispatch, evidence, and Context First handoff.
---

# Flutter Multiplatform

この Skill は、Codex が `/flutter-multiplatform` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/flutter-multiplatform.prompt.md`
- `docs/workflows/flutter-multiplatform.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
