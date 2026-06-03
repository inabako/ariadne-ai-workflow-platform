# Corrective Action Reports

このディレクトリは、repository / branch の現状改善点を整理した corrective action report を蓄積する場所です。

`/corrective-action-report` Skill は、対象 repository と対象 branch を確認した上で、改善点、risk、test gap、documentation gap、architecture concern、workflow opportunity をここへ保存します。

推奨ファイル名:

```text
YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md
```

branch、language、report type はファイル名ではなく front matter / tags に残します。

この場所の report は、将来の RAG knowledge として再利用する前提で、front matter、根拠、open question、recommended action を残してください。
