---
name: self-improvement
description: Collect workflow feedback from Ariadne AI Workflow Platform runs, append human review decisions, generate GitHub Issue bodies for accepted feedback, create standard issue branch/evidence scaffolds, and hand off to existing GitHub/SCM helpers. Use when the user selects /self-improvement or asks to turn workflow friction, noise, repeated checks, missing context, docs ambiguity, runtime observation gaps, or workflow usability issues into a governed improvement flow.
---

# Self-Improvement Workflow Skill

## 既定言語

既定では日本語で応答してください。人間向けreport、docs、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成します。

## 目的

このworkflowは、Ariadneのworkflow実行中に見えた摩擦、ノイズ、やりづらさ、改善候補をFeedback reportとして保存し、人間レビューで採用判断したうえで、採用されたものだけ既存の改善flowへ接続します。

`/corrective-action-fix`、`/docs-sync`、`/github-knowledge-maintenance`、`/knowledge-capture` を置き換えるものではありません。Feedback、Issue body、branch名、evidence scaffoldを準備し、GitHub / SCMの副作用操作は既存runtime helperへ委譲します。

## 標準ディレクトリ

```text
work/feedback/
templates/workflows/self-improvement/
work/<work-id>/process-report/self-improvement/
work/<work-id>/test-evidence/self-improvement/
```

`work/feedback/` 配下に `inbox/`、`aggregated/`、`processed/`、`icebox` は作りません。採用 / 不採用 / 保留の状態は各Feedback report内に追記します。

## Workflow

1. 各AI workflow実行中に、摩擦や改善候補を `work/feedback/` のFeedback reportとして保存します。
2. 通常workflow内では初期状態を `Proposed` のまま残し、`/self-improvement` を自動実行しません。
3. Feedbackがたまった後に `/self-improvement` を実行し、対象reportを確認します。
4. 同じreportへHuman Review結果を追記します。判断はAccepted、Rejected、Deferredのいずれかです。
5. AcceptedのFeedbackだけIssue bodyを生成します。
6. GitHub Issue titleは `[改善フロー]` prefixを使います。
7. Human Check後に `feature/issue-<issue-number>` と `work/issue-<issue-number>` を作成します。
8. 適切な既存workflowまたはhelperで改善を実装します。
9. process reportとtest evidenceを `work/<work-id>/` 配下へ保存します。
10. push、PR作成、RAG登録、close archive準備はそれぞれ個別Human Checkを必要とします。

## Runtime Helper

Feedback置き場を初期化します。

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . self-improvement init-feedback
```

Feedback reportを作成します。

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "/docs-sync" `
  --reporter "Human" `
  --situation "docs整備中" `
  --friction "参照すべきdocsが不明" `
  --impact "判断負荷が増えた"
```

Human Review結果を追記します。

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . self-improvement review-feedback `
  --feedback work/feedback/<feedback>.md `
  --decision accepted `
  --reviewer "Human" `
  --reason "改善価値がある" `
  --next-action "Issue化する"
```

Issue bodyを生成します。

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . self-improvement issue-body `
  --feedback work/feedback/<feedback>.md
```

evidence scaffoldを作成します。

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . self-improvement evidence-scaffold --work-id issue-42
```

branch名を確認します。

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . self-improvement branch-name --issue-number 42
```

## Human Check

Feedback report内のHuman Reviewで、そのfeedbackをAccepted、Rejected、Deferredのどれにするか判断します。

GitHub Issue作成、branch作成、push、Pull Request作成、RAG登録、close archive準備、tool / package installは、採用判断とは別のHuman Check gateとして扱います。

## Accumulated Feedback Intake

通常のAI workflowは、実行中に見つけた改善候補を `work/feedback/` へ `Proposed` として残します。
`/self-improvement` は、feedbackがたまってから人間が採用 / 不採用 / 保留を判断し、Accepted feedbackだけをIssue化へ進めるために実行します。
通常workflowの中から `/self-improvement` を自動実行しません。

## Guardrails

- RejectedまたはDeferredのfeedbackからIssue bodyを生成しません。draft reviewとして明示された場合だけ例外にします。
- `self_improvement.py` ではGitHub mutationを行いません。
- 既存のGitHub / SCM helper logicを重複実装しません。
- branch名は `feature/issue-<issue-number>` に固定します。
- work folderは `work/issue-<issue-number>` に固定します。
- Issue作成前に `docs/governance/` とPlatform Fit Checkを確認します。
