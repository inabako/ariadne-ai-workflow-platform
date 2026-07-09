# Workflow Feedback

`work/feedback/` は、Self-Improvement Workflowの実行時Feedback report置き場です。

細かい `inbox/`、`aggregated/`、`processed/`、`icebox/` は作りません。各Feedback reportに `Review Status` と `Human Check` を追記し、採用 / 不採用 / 保留を同じファイルで管理します。

永続テンプレートは `templates/self-improvement/` に置きます。

```powershell
python runtime/workflow/self_improvement.py create-feedback `
  --target-workflow "/docs-sync" `
  --reporter "Human" `
  --situation "docs整備中" `
  --friction "参照すべきdocsが不明" `
  --impact "判断負荷が増えた"
```
