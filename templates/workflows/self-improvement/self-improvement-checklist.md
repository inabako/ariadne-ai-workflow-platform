---
language: ja-JP
workflow: self-improvement
artifact_type: checklist
---

# Self-Improvement Checklist

## Feedback Review

- [ ] `work/feedback/` にFeedback reportがある。
- [ ] Feedback reportにSituation、Friction、Impact、Evidenceが記載されている。
- [ ] Human ReviewでAccepted、Rejected、Deferredのいずれかが追記されている。
- [ ] RejectedまたはDeferredの場合、理由とNext Actionが記載されている。

## Issue化

- [ ] AcceptedのFeedbackだけをIssue化している。
- [ ] Issue本文にAriadne Fit Checkが含まれている。
- [ ] Issue titleは `[改善フロー]` prefixを使う。
- [ ] GitHub Issue作成前にHuman Checkを行う。

## Branch / Push

- [ ] branch名は `feature/issue-<issue-number>` である。
- [ ] work folderは `work/issue-<issue-number>/` である。
- [ ] branch作成前にHuman Checkを行う。
- [ ] push前にHuman Checkを行う。
- [ ] RAG登録やclose archive準備は別途Human Checkを行う。

## Evidence

- [ ] `work/<work-id>/process-report/self-improvement/` に判断記録がある。
- [ ] `work/<work-id>/test-evidence/self-improvement/` に検証結果がある。
- [ ] `work/<work-id>/context/artifact-index.json` に成果物が登録されている。
