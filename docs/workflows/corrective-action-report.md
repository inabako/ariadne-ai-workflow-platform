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

## External Web RAG Support

外部Web RAGは、finding候補、risk観点、test観点、公式仕様との照合ポイントを補強するために使います。

```text
repository / branch read-only inspection
  -> internal RAG load
  -> knowledge gap detection
  -> external-web RAG dispatch when needed
  -> findings tied back to repository evidence
  -> corrective action report
```

外部Web RAGだけでfindingを確定しません。

最終findingには、必ず対象repositoryのevidenceを紐づけます。

- file / line / component
- behavior
- docs gap
- log / runtime evidence
- test gap
- reproducible inspection result

外部Web由来の根拠は `supporting_reference` として記録します。

外部Web RAGの詳細は [External Web RAG](external-web-rag.md) を参照してください。

## Report Must Include

- prioritized findings
- recommended actions
- affected files / components
- expected unit tests
- startup / integration check expectations
- human-check items
- RAG capture candidates
- supporting references
- evidence

推奨追加セクション:

```markdown
## Supporting References

| Finding ID | Reference Type | Source | How It Was Used | Verification Required |
| --- | --- | --- | --- | --- |
```

## Guardrails

- target repository と target branch が未指定なら作業前に確認します。
- current branch を勝手に採用しません。
- reportはRAG化しやすいmetadataとstable section orderを保ちます。
- 外部WebRAGは current source code、test evidence、人間承認済み運用知見を上書きしません。

## Source Skill

```text
skills/corrective-action-report/SKILL.md
```
