---
language: ja-JP
---

# Platform Governance

Platform Governance は、Ariadne AI Workflow Platform が長期にわたり同じ設計思想を保ちながら改善されるための入口です。

これは開発ルール集ではありません。新しいworkflow、runtime改善、Agent追加、RAG改善、repository改善を行うときに、「何を作るか」より先に「何を改善してよいか」を判断するための設計憲章です。

## Ariadne における位置付け

Ariadne は、AI Agent が複雑なworkflowやrepository状態に迷わず、本質的な課題へ集中するためのContext First型platformです。

そのため、改善の判断基準も個別の実装都合ではなく、platform全体の思想から始めます。

- AIが迷わない環境を設計する。
- 認知負荷を下げる。
- Context、Evidence、Human Checkを第一級の成果物として扱う。
- 責任境界を曖昧にしない。
- 学びを次のworkflow、Agent、RAGへ戻す。

Platform Governance は、この判断基準を人間、AI Agent、Workflowが共有するための知識層です。

## ドキュメント一覧

| Document | 目的 |
| --- | --- |
| [platform-governance.md](platform-governance.md) | Ariadne全体のMission、Philosophy、Core Principles、Non Goalsを定義する |
| [architecture-principles.md](architecture-principles.md) | Ariadneで守る設計原則と、採用理由、運用上の注意を整理する |
| [workflow-evolution-policy.md](workflow-evolution-policy.md) | Workflow改善をfeedback、Issue、Human Review、Evidenceへ接続する方針を定義する |
| [human-responsibility.md](human-responsibility.md) | HumanとAI Agentの責任境界を明文化する |
| [platform-fit-check.md](platform-fit-check.md) | 改善案がAriadneの思想に適合するか確認するchecklistを提供する |
| [repository-governance.md](repository-governance.md) | Repository自体をplatformの一部として運用する方針を定義する |

## AI Agent が参照する理由

AI Agent は、目の前のtaskを局所最適で解くことがあります。

Platform Governance は、Agentが次を判断するための基準です。

- その変更はAriadneの思想と合うか。
- その変更はContext Firstを強めるか、弱めるか。
- その変更はHuman Responsibilityを守るか。
- その変更はEvidenceとして後続workflowが読める形で残るか。
- その変更は将来の自己改善を助けるか。

Agentは、実装前、docs更新前、Issue化前、改善提案前にこのdirectoryを参照します。

## Self-Improvement Workflow との関係

Self-Improvement Workflow、Repository Curation Workflow、Runtime Maintenance Workflow は、Ariadne自身を改善します。

自己改善は強力ですが、基準がなければplatformの思想を壊す方向にも進みます。これらのworkflowは、改善候補を扱う前にPlatform Governanceを読み、改善案が採用可能かを判断します。

- Self-Improvement Workflow は、改善候補がplatform思想と矛盾しないか確認する。
- Repository Curation Workflow は、repository構造、docs、RAG、archiveが長期運用に耐えるか確認する。
- Runtime Maintenance Workflow は、runtime改善がContext First、Evidence First、Human Checkを弱めないか確認する。

## Summary

- Platform Governance はAriadneの設計憲章であり、単なるルール集ではない。
- 改善判断は「何を作るか」ではなく「何を改善してよいか」から始める。
- AI Agent、Workflow、人間が同じ基準を参照するための入口である。
- Self-Improvement Workflow、Repository Curation Workflow、Runtime Maintenance Workflow は、この文書群を改善判断の前提として扱う。
