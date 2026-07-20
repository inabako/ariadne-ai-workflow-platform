---
language: ja-JP
---

# Human Responsibility

この文書は、Ariadne AI Workflow Platform におけるHumanとAI Agentの責任境界を定義します。

Ariadneは、AI Agentに多くの作業を任せます。しかし、責任を曖昧にしません。AI Agentが迷わない環境を設計し、最終判断を行い、platformの方向性を守る責任は人間にあります。

## Human の責任

### 設計思想

人間は、Ariadneが何を目指すplatformかを定義し、維持します。

AI Agentは与えられたContextから提案できますが、platformの価値、採用基準、守るべき思想を最終的に定めるのは人間です。

### 最終判断

採用、非採用、延期、scope変更、外部公開、副作用を伴う操作の判断は人間が行います。

AI Agentは判断材料を整理し、リスクや選択肢を提示します。人間の承認が必要な操作を、AI Agentが暗黙に進めてはいけません。

### Platform Governance

人間は、Platform Governanceを更新し、解釈の揺れを減らします。

Governanceが曖昧な場合、AI Agentの出力が揺れます。その揺れはAIの失敗ではなく、設計環境の不足として扱います。

### Human Check

Human Checkは、人間が責任を持つ判断点です。

対象例:

- GitHub Issue / Pull Request 作成。
- push。
- RAG登録 / rebuild。
- close archive準備 / prune。
- installや環境変更。
- 実機、外部I/O、network公開を伴う操作。
- 責任境界や設計思想に影響する採用判断。

## AI Agent の責任

### 提案

AI Agentは、Context、docs、runtime evidence、RAG補助情報を読み、改善案や実装案を提案します。

提案には、理由、影響範囲、検証方法、Human Check要否を含めます。

### 実装

AI Agentは、承認された範囲内で実装、docs更新、test追加、artifact生成を行います。

対象外の変更や責務境界をまたぐ変更は、独断で混ぜません。

### 改善案

AI Agentは、workflow実行中に見えたfrictionやdocs driftを改善候補として整理できます。

ただし、候補を採用するかは人間が判断します。

### Runtime分析

AI Agentは、runtime logs、metrics、process report、test結果を読み、問題点や改善余地を分析します。

分析結果は、後続workflowが読めるEvidenceとして残します。

### Evidence生成

AI Agentは、判断と検証の根拠をartifactとして残します。

Evidenceは、人間がレビューし、次のworkflowが参照するための共有資産です。

## 責任境界を曖昧にしない

Ariadneでは、次の状態を避けます。

- AI Agentが人間の承認を代替する。
- 人間が判断材料を残さず口頭または会話だけで決める。
- Workflowが副作用をHuman Checkなしに実行する。
- docs、runtime、Issueのどれがsource of truthか分からない。
- 失敗の原因がAI、Context、tool、runtime、人間判断のどこにあるか追跡できない。

責任境界が曖昧な場合は、作業を進める前にContext、Issue、docs、Governanceのいずれかへ明文化します。

## Self-Improvement Workflow との関係

Self-Improvement Workflow は、AI Agentが改善案を作り、人間が採用判断を行う責任分離を前提にします。

Repository Curation Workflow は、責任境界がdocs、Issue、branch、archive、RAGに明示されているか確認します。

Runtime Maintenance Workflow は、runtimeがHuman Checkを迂回していないか、必要な判断材料を生成しているか確認します。

## Summary

- 人間は設計思想、最終判断、Platform Governance、Human Checkに責任を持つ。
- AI Agentは提案、実装、改善案、runtime分析、Evidence生成を担う。
- AI Agentは人間の責任を代替しない。
- 責任境界が曖昧な場合は、作業前にContext、Issue、docs、Governanceへ明文化する。
