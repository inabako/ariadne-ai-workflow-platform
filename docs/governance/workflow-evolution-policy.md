---
language: ja-JP
---

# Workflow Evolution Policy

この文書は、Ariadne AI Workflow Platform のworkflowをどのように改善するかを定義します。

Workflow改善は、思いつきで手順を変える作業ではありません。運用中に見えた摩擦をfeedbackとして捕捉し、Issue化し、Human Reviewを通し、Evidenceを残して次のworkflowへ戻す循環です。

## 基本方針

Workflowは、固定された手順書ではなく、継続的に改善されるplatform資産です。

ただし、改善は自由変更ではありません。次を満たす場合にのみ進めます。

- Platform Governanceと矛盾しない。
- Context Firstを弱めない。
- Human Responsibilityを曖昧にしない。
- Evidenceが残る。
- 後続workflowが参照できる形でdocs、schema、runtime、RAG候補へ反映できる。

## Feedback Capture

Feedback Capture は、workflow実行中に発生した摩擦、迷い、手戻り、欠落、誤解を捕捉することです。

捕捉対象は、失敗だけではありません。人間が何度も同じ説明をした箇所、AI Agentが推論で補った箇所、docsと実装がずれた箇所もfeedbackです。

## Workflow Feedback

Workflow Feedback は、捕捉したfeedbackをworkflow改善に使える形へ整理したものです。

例:

- 入力artifactが不足していた。
- Human Checkの条件が曖昧だった。
- `work/<id>/context/` のContextが後続workflowに渡らなかった。
- docsにある手順とruntime helperの挙動が違った。
- 出力EvidenceがRAG候補として使いにくかった。

## Friction

Friction は、workflowを進めるうえで発生した抵抗です。

Frictionは悪いものではありません。Ariadneでは、frictionを改善候補の発生源として扱います。

ただし、frictionをその場の会話で解消して終わらせると、platformは学習しません。再発するfrictionはartifact化します。

## Improvement Candidate

Improvement Candidate は、対応する価値があると判断された改善候補です。

候補化するときは、次を記録します。

- 何が起きたか。
- どのworkflow、runtime、docs、schemaに関係するか。
- Platform Fit Check上の判断。
- 期待する改善効果。
- Human Checkが必要か。
- Evidenceとして何を残すか。

## Icebox

Icebox は、今すぐ実装しない改善候補の置き場です。

重要度が低いもの、情報が不足しているもの、複数案を比較したいものは、無理に進めずIceboxへ置きます。

Iceboxに置く場合も、理由を残します。忘れるためではなく、判断を保留した理由を後から読めるようにするためです。

## GitHub Issue

改善を実行する場合は、GitHub Issueとして範囲、目的、完了条件、Human Check条件を明確にします。

Issueは会話の要約ではありません。改善対象、判断理由、変更範囲、検証方法を後続作業者が読める入口です。

## Human Check

Human Check は、改善の採用、責任境界、副作用、push、RAG登録、archiveなどの判断を人間が確認するgateです。

AI Agentは、Human Checkに必要な材料を準備します。判断そのものを隠したり、自動化で通過したりしません。

## Improvement Workflow

Improvement Workflow は、Issue化された改善を実装、検証、docs更新、Evidence保存、必要に応じたRAG候補化へ進める流れです。

改善中も、対象外の変更を混ぜません。workflow改善、docs同期、runtime修正、repository整理は、それぞれの責務境界を守って進めます。

## 改善サイクル

```text
Workflow

↓

Feedback

↓

Issue

↓

Human Review

↓

Improvement

↓

Evidence

↓

Next Workflow
```

このサイクルは、Ariadneが自己改善するための基本形です。

Workflowから得たfeedbackをIssueへ変換し、人間が採用判断を行い、改善を実施し、Evidenceとして残します。そのEvidenceは、docs、RAG、runtime、template、schemaへ戻り、次のworkflowのContextになります。

## Self-Improvement Workflow との関係

Self-Improvement Workflow は、この改善サイクルを扱う中心workflowです。

Repository Curation Workflow は、feedbackやEvidenceがrepository内で見つけやすいか、古いdocsが残っていないか、RAG候補が適切に整理されているかを確認します。

Runtime Maintenance Workflow は、runtime実行中に発生したfrictionをmetrics、logs、process reportから見つけ、改善候補へ変換します。

## Summary

- Workflow改善は、feedbackからIssue、Human Review、Evidence、Next Workflowへ戻す循環で行う。
- Frictionは失敗ではなく、改善候補の源泉として扱う。
- 改善はPlatform Governance、Context First、Human Responsibilityと矛盾してはならない。
- Human Checkを通す判断と、AI Agentが準備するEvidenceを分離する。
