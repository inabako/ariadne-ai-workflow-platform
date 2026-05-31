---
name: corrective-action-report
description: 指定された repository / branch の現状を調査し、改善点を corrective action report として保存します。
argument-hint: "<target-repository> <target-branch>"
agent: agent
---

# Corrective Action Report Skill Entrypoint

## Purpose

`/corrective-action-report` は、指定された repository / branch の現状を調査し、改善点、risk、test gap、documentation gap、architecture concern、workflow opportunity を RAG 用の corrective action report として保存するための Skill entrypoint です。

Use:

```text
skills/corrective-action-report/SKILL.md
```

## Required Inputs

開始前に、必ず以下を確認する。

- target repository: local path、GitHub URL、または owner/repo
- target branch: 調査対象branch

どちらかが未指定の場合は、作業前に user へ入力を求める。

current branch を勝手に採用しない。user が current branch 利用を明示的に承認した場合のみ使う。

## Output

Report output directory:

```text
C:\github\intent-driven-robotics-ai-workflow\rag\corrective-action-report
```

Recommended filename:

```text
yyyyMMdd_HHmmss_<repository-name>_<branch-name>_corrective-action-report.md
```

## Guardrail

この Skill は read-only review を基本とする。

GitHub Issue 作成、branch 作成、commit、source 修正は行わない。user が明示的に実装修正へ進めた場合のみ、別 workflow へ移行する。
