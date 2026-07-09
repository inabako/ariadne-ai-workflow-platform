---
name: self-improvement
description: Collect Ariadne workflow feedback, append human review decisions, generate issue bodies for accepted feedback, and hand off to existing GitHub/SCM helpers.
argument-hint: "[feedback-report]"
agent: agent
---

# /self-improvement

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

## Purpose

Ariadne AI Workflow Platform のworkflow実行中に発生した摩擦、ノイズ、やりづらさ、改善候補をFeedback reportとして保存し、人間レビューで採用 / 不採用 / 保留を追記し、採用されたものだけIssue化へ進めます。

## Workflow

1. `work/feedback/` にFeedback reportを作成する。
2. Feedback reportにEvidence、Priority、Categoryを記録する。
3. `docs/governance/` のPlatform Fit Checkを確認する。
4. Human Review結果を同じFeedback reportへ追記する。
5. Acceptedの場合だけIssue bodyを生成する。
6. GitHub Issue作成、branch作成、push、PR作成は個別Human Check後に既存runtime helperで行う。

## Runtime Helpers

```powershell
python runtime/workflow/self_improvement.py init-feedback
python runtime/workflow/self_improvement.py create-feedback --target-workflow "/docs-sync" --situation "<situation>" --friction "<friction>"
python runtime/workflow/self_improvement.py review-feedback --feedback work/feedback/<feedback>.md --decision accepted --reviewer "Human" --reason "<reason>"
python runtime/workflow/self_improvement.py issue-body --feedback work/feedback/<feedback>.md
python runtime/workflow/self_improvement.py branch-name --issue-number 42
python runtime/workflow/self_improvement.py evidence-scaffold --work-id issue-42
```

## Guardrails

- `work/feedback/` 配下に `inbox/`、`aggregated/`、`processed/`、`icebox/` を作らない。
- Rejected / DeferredのFeedbackはIssue化しない。
- GitHub / SCM mutationは既存helperへ委譲する。
- branchは `feature/issue-<issue-number>`、work folderは `work/issue-<issue-number>` を使う。
