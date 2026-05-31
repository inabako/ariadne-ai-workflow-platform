# Corrective Action Reports

このディレクトリは、repository / branch の現状改善点を整理した corrective action report を蓄積する場所です。

`/corrective-action-report` Skill は、対象repositoryと対象branchを確認した上で、改善点、risk、test gap、documentation gap、architecture concern、workflow opportunity をここへ保存します。

推奨ファイル名:

```text
yyyyMMdd_HHmmss_<repository-name>_<branch-name>_corrective-action-report.md
```

この場所のreportは、将来の RAG knowledge として再利用する前提で、front matter、根拠、open question、recommended action を残してください。
