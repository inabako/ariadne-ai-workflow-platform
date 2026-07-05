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

## Context First

report作成後は、成果物をContext Firstへ登録します。

```powershell
python runtime/workflow/corrective_action_report.py register `
  --repository "<target-repository>" `
  --target-branch "<target-branch>" `
  --report-path "rag/corrective-action-report/<report>.md"
```

生成されるContext:

```text
work/<target-branch>/context/corrective-action-report.json
work/<target-branch>/context/context-manifest.json
```

`corrective-action-report.json` には、report保存先、対象repository / branch、commit、RAG候補、finding件数の概要を記録します。

後続の `/corrective-action-fix` は、明示的なreport引数が無い場合、このmanifest上のreportを優先して読みます。

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
  -> specialist review when findings need domain depth
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

## Specialist Review Support

finding品質が専門知識に依存する場合は、report確定前にSpecialist Agentのreviewを挟みます。

使う例:

- Python / Go runtimeの挙動がfindingに影響する。
- network protocol、NAT、latency、packet evidenceの解釈が必要。
- GStreamer / video pipelineの仕様確認が必要。
- platform差分やdeployment制約がriskに影響する。
- test designにfault injection、packet capture、race検出が必要。

review結果は次へ保存します。

```text
work/<target-branch>/process-report/specialist-review-<domain>.md
```

Specialist Agentのreviewは、final findingの代替ではありません。final findingには必ず対象repositoryのevidenceを紐づけます。

reportには、専門reviewで採用した外部知識を `Supporting References` と `RAG Capture Candidates` に反映します。

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

専門reviewを使った場合は、次の表も追加します。

```markdown
## Specialist Review References

| Domain | Review Path | Trusted External Knowledge | Repository Evidence | Result |
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
