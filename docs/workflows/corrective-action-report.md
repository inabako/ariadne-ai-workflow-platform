# Corrective Action Report

指定された repository / branch の現状を read-only で調査し、改善点、risk、test gap、documentation gap、architecture concern、workflow opportunity をreportとして残すworkflowです。

## Command

```text
/corrective-action-report <target-repository> <target-branch>
```

例:

```text
/corrective-action-report localty-system-gui develop
```

## Output

```text
rag/corrective-action-report/YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md
```

## Scope

このworkflowは調査とreport作成だけを行います。

- GitHub Issueを作成しません。
- branchを作成しません。
- sourceを修正しません。
- commitしません。

修正まで進める場合は [Corrective Action Fix](corrective-action-fix.md) に移行します。

## Report Must Include

- prioritized findings
- recommended actions
- affected files / components
- expected unit tests
- startup / integration check expectations
- human-check items
- RAG capture candidates
- evidence

## Guardrails

- target repository と target branch が未指定なら作業前に確認します。
- current branch を勝手に採用しません。
- reportはRAG化しやすいmetadataとstable section orderを保ちます。

## Source Skill

```text
skills/corrective-action-report/SKILL.md
```
