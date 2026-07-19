---
language: ja-JP
---

# Workflow Feedback

Workflow Feedback は、各AI workflow実行中に見つかった摩擦、迷い、手戻り、欠落、重複確認、runtime観測不足、docs不足、encoding / branch / 保存先の曖昧さを、後で改善判断できる形に残すためのreportです。

## 基本方針

- 各AI workflowは、実行中に改善候補を見つけたら `work/feedback/` へFeedback reportを作成または更新します。
- `work/feedback/` は単一ディレクトリです。`inbox/`、`aggregated/`、`processed/`、`icebox/` は作りません。
- 通常workflow内では初期状態を `Proposed` として残します。
- 通常workflow内から `/self-improvement` を自動実行しません。
- Feedbackがたまった後、人間が `/self-improvement` を実行して採用 / 不採用 / 保留を判断します。
- 採用 / 不採用 / 保留はFeedback report内の `Review Status` と `Human Check` に追記します。

## 保存コマンド

新しいFeedback reportを作る場合は、既存helperを使います。

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "/docs-sync" `
  --reporter "AI workflow" `
  --situation "docs整備中" `
  --friction "参照すべきdocsが不明" `
  --impact "判断負荷が増えた" `
  --proposed-improvement "docs入口に参照順を追加する"
```

既存reportに追記する方が自然な場合は、同じ `work/feedback/*.md` を更新します。

## Review Flow

Feedbackがたまったら `/self-improvement` を実行します。

```text
通常AI workflow
  -> work/feedback/*.md に Proposed feedback を保存
  -> feedbackがたまる
  -> /self-improvement を実行
  -> Human Reviewで Accepted / Rejected / Deferred を追記
  -> AcceptedだけIssue bodyへ変換
  -> 個別Human Check後にIssue / branch / push / PRへ進む
```

## 判断基準

- Repeated: 複数workflowで再発しそうか。
- Actionable: docs、runtime、template、prompt、skillのどこを直すか説明できるか。
- Governed: Platform GovernanceとFit Checkに反しないか。
- Evidence-based: 実行中の具体的な迷い、手戻り、欠落に紐づいているか。

## 関連資料

- [Self-Improvement Workflow](../workflows/self-improvement.md)
- [Workflow Evolution Policy](../governance/workflow-evolution-policy.md)
- [Platform Fit Check](../governance/platform-fit-check.md)
