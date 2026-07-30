---
language: ja-JP
---

# Platform Governance

この文書は、Ariadne AI Workflow Platform 全体の憲章です。

Ariadne は、workflowを増やすためのrepositoryではありません。AI Agentが本質的な課題へ集中し、人間が責任ある判断を行い、成果と学びを次の改善へ戻すためのplatformです。

## Mission

AIが迷わず本質的な課題へ集中できる世界を作る。

Ariadne のMissionは、AIを万能化することではありません。AIが能力を発揮できる環境を、人間が設計し、維持し、改善し続けることです。

## Philosophy

品質を支える確かな仕組みを提供する。

品質は、個人の注意力や一回限りのレビューだけでは維持できません。Ariadne は、Context、Workflow、Dispatcher、RAG、Evidence、Human Checkを組み合わせ、品質が再現可能に生まれる状態を目指します。

## Core Principles

### AIが迷わない環境を設計する

Agentに曖昧な前提を推論させません。必要なContext、入力、制約、停止条件をartifactとして渡します。

### 認知負荷を下げる

人間とAI Agentのどちらにも、不要な探索や判断を押し付けません。索引、template、schema、Context Firstのhandoffで作業の見通しをよくします。

### 維持しやすい

Workflowやruntimeは、一度動けばよいものではありません。後から読み直せる構造、責務境界、検証方法、archive方針を持ちます。

### 改善しやすい

改善は例外作業ではなく、platformの通常運用です。Feedback、Issue、Evidence、RAG候補を残し、次の改善へ接続します。

### Human Responsibilityを守る

最終判断、責任境界、承認が必要な操作は人間が持ちます。AI Agentは提案、実装、分析、Evidence生成を担いますが、人間の責任を置き換えません。

### Context First

Workflowは、先にContextを読みます。環境、tool、runtime、branch、repository、入力artifactを毎回推論する状態を避けます。

### Evidence First

判断や改善は、会話ログだけに残しません。検証結果、process report、docs、schema、RAG sourceなど、後続workflowが参照できるEvidenceとして残します。

### Workflowは継続的に改善する

Workflowは固定された手順ではなく、運用から学び、明示的なHuman Reviewを経て改善される対象です。

## Non Goals

次は Ariadne では採用しません。

- Ariadneの思想と矛盾する機能。
- AI任せの責任境界。
- 責務が曖昧になる構造。
- 認知負荷を増加させるWorkflow。
- Evidenceを残さない改善。
- Human Checkが必要な操作を自動化で隠す設計。

## Self-Improvement Workflow との関係

Self-Improvement Workflow は、この憲章を改善判断の基準として使います。

Repository Curation Workflow は、repository構造とdocsがこの憲章を読みやすく支えているか確認します。

Runtime Maintenance Workflow は、runtime改善がContext First、Evidence First、Human Responsibilityを壊さないか確認します。

## Summary

- AriadneのMissionは、AIが迷わず本質的な課題へ集中できる環境を作ること。
- 品質は個人の頑張りではなく、Context、Workflow、Evidence、Human Checkの仕組みで支える。
- Human Responsibility、Context First、Evidence Firstはplatform改善の中核である。
- 思想と矛盾する機能、責務が曖昧になる構造、認知負荷を増やすworkflowは採用しない。
