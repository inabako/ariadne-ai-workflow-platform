---
language: ja-JP
---

# Self-Improvement Workflow

`/self-improvement` は、Ariadne AI Workflow Platform のworkflow実行中に見つかった摩擦、ノイズ、やりづらさ、改善候補を収集し、人間レビューで採用判断し、採用されたものをIssue化へ進めるworkflowです。

目的は、自動修正そのものではありません。Workflow自体の品質、使いやすさ、保守性を継続的に改善できるようにすることです。

## 位置づけ

通常のAI workflowは、実行中に見つけた改善候補を `work/feedback/` へ `Proposed` として保存します。
`/self-improvement` は、Feedbackがたまった後に実行し、人間が採用 / 不採用 / 保留を判断して、AcceptedのFeedbackだけをIssue化へ進めるためのworkflowです。

つまり、Feedback保存は各AI workflow実行時の標準動作であり、`/self-improvement` は蓄積後に実行するreview / improvement入口です。

## 使う場面

- 指示が曖昧でAI Agentが迷った。
- 前提条件、Context、参照docsが不足していた。
- Human Checkのタイミングが重い、または重複していた。
- runtimeの観測情報、metrics、Evidenceが不足していた。
- 文字コード、改行コード、保存先、branch規約が曖昧だった。
- 同じ確認や修正が複数workflowで繰り返された。

## 保存先

```text
work/feedback/
```

`work/feedback/` は単一ディレクトリです。`inbox/`、`aggregated/`、`processed/`、`icebox/` は作りません。

採用 / 不採用 / 保留は、Feedback report内の `Review Status` と `Human Check` に追記します。

永続テンプレートは次に置きます。

```text
templates/workflows/self-improvement/
```

## Flow

```text
AI workflow実行
  ↓
work/feedback/ に Proposed feedback 作成
  ↓
Feedback蓄積後に /self-improvement 実行
  ↓
Platform Governance / Fit Check確認
  ↓
Human Review結果をFeedback reportへ追記
  ↓
AcceptedのみIssue body生成
  ↓
GitHub Issue作成前Human Check
  ↓
Issue作成
  ↓
branch作成前Human Check
  ↓
feature/issue-<issue-number> 作成
  ↓
改善実装
  ↓
test / validation / evidence保存
  ↓
push前Human Check
  ↓
push / knowledge capture
```

## Runtime Helper

Feedback置き場を初期化します。

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . self-improvement init-feedback
```

Feedback reportを作成します。

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "/docs-sync" `
  --reporter "Human" `
  --situation "docs整備中" `
  --friction "参照すべきdocsが不明" `
  --impact "判断負荷が増えた" `
  --proposed-improvement "docs入口に参照順を追加する"
```

Human Review結果を同じFeedback reportへ追記します。

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . self-improvement review-feedback `
  --feedback work/feedback/<feedback>.md `
  --decision accepted `
  --reviewer "Human" `
  --reason "繰り返し発生する摩擦で改善価値がある" `
  --next-action "Issue化する"
```

AcceptedのFeedbackからIssue bodyを生成します。

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . self-improvement issue-body `
  --feedback work/feedback/<feedback>.md
```

Issue番号から既存規約のbranch名を確認します。

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . self-improvement branch-name --issue-number 42
```

Evidence保存先を作成し、`artifact-index.json` に登録します。

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . self-improvement evidence-scaffold --work-id issue-42
```

## GitHub / SCM連携

GitHub Issue作成、branch作成、commit、push、Pull Request作成は、既存runtime helperを使います。

```powershell
python runtime/github/issue_manager.py `
  --work-id "<work-id>" `
  --title "[改善フロー] <issue-title>" `
  --flow-label improvement `
  --body-file "<issue-body.md>" `
  --create

python runtime/scm/create_issue_branch.py `
  --work-id "issue-<issue-number>" `
  --issue-number "<issue-number>" `
  --repository "<target-repository>" `
  --base-branch "<target-branch>" `
  --link-to-issue

python runtime/scm/commit_changes.py `
  --work-id "issue-<issue-number>" `
  --message "fix: improve workflow feedback handling" `
  --all

python runtime/scm/push_branch.py `
  --work-id "issue-<issue-number>" `
  --human-check approved `
  --set-upstream
```

## Human Check

Feedback report内のHuman Reviewは、採用 / 不採用 / 保留を判断します。

次のoperationは、採用判断とは別に個別Human Checkを必要とします。

- GitHub Issue作成。
- GitHub branch作成。
- push。
- Pull Request作成。
- RAG登録 / rebuild。
- close archive準備 / prune。
- missing tool / package install。

## Branch Policy

branch名は既存規約に統一します。

```text
feature/issue-<issue-number>
```

work folderはWindows pathでslashが問題にならないよう、次を使います。

```text
work/issue-<issue-number>/
```

## Platform Governance

Issue化前に [Platform Fit Check](../governance/ariadne/platform-fit-check.md) を確認します。

通過できない改善案はIssue化せず、Feedback report上でRejectedまたはDeferredにします。

## 成功条件

- `work/feedback/` にFeedback reportが保存される。
- Feedback reportへHuman Review結果が追記される。
- AcceptedのFeedbackからIssue bodyを生成できる。
- branch名が `feature/issue-<issue-number>` になる。
- evidence scaffoldが `work/<work-id>/process-report/self-improvement/` と `work/<work-id>/test-evidence/self-improvement/` に作られる。
- `artifact-index.json` にSelf-Improvement成果物が登録される。

## Summary

- `/self-improvement` は、workflowの摩擦を改善flowへつなぐための入口である。
- `work/feedback/` は単一ディレクトリで、状態はFeedback report内に追記する。
- Issue化するのはAcceptedのFeedbackだけである。
- GitHub / SCM mutationは既存helperへ委譲し、Human Checkを個別に通す。
