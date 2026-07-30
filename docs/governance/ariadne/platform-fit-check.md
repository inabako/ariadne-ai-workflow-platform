---
language: ja-JP
---

# Platform Fit Check

Platform Fit Check は、Ariadne AI Workflow Platform の改善案を採用してよいか判断するためのchecklistです。

このcheckは、改善を止めるためではなく、改善がplatformの思想と噛み合っているかを確認するために使います。

## 使い方

改善案、Issue、Pull Request、workflow変更、runtime変更、docs構造変更を扱う前に、このcheckを確認します。

判断は単純なyes/noだけで終わらせません。迷う項目がある場合は、採用条件、保留理由、必要なEvidence、Human Check内容を記録します。

## AIが迷わないか

判断方法: Agentが入力、目的、制約、成果物、停止条件を推論せずに読めるか確認します。

採用例: `work/<id>/context/` に必要Contextを追加し、workflowが最初に読むようにする。

非採用例: READMEのどこかに曖昧な説明だけを追加し、Agentが実行時に読み解く前提にする。

## 認知負荷を下げるか

判断方法: 人間とAI Agentの探索、判断、手戻りが減るか確認します。

採用例: 複数docsに散らばった入口を索引化し、slash command、入力、出力、gateを表で整理する。

非採用例: 手順を増やすだけで、どの判断が楽になるか説明できない変更。

## 品質を支える仕組みか

判断方法: 変更が品質を個人の注意力ではなく、Context、Evidence、test、schema、Human Checkで支えるか確認します。

採用例: docs drift分析をJSONに保存し、Issue bodyをそのJSONから生成する。

非採用例: 「気をつける」とだけ書き、検証やartifactを残さない。

## 維持しやすいか

判断方法: 後から別の人間やAI Agentが読んで、変更理由、責務、検証方法を理解できるか確認します。

採用例: runtime helperに対応するdocs、schema、test、README linkを揃える。

非採用例: 一つのscriptに例外処理を増やし続け、外部から挙動が分からなくなる。

## 改善しやすいか

判断方法: 実行結果、friction、error、Evidenceが次の改善候補へ接続できるか確認します。

採用例: process report、runtime metrics、artifact indexを残し、次のworkflowが参照できるようにする。

非採用例: 成功時も失敗時も会話ログ以外に何も残らない変更。

## 責務を曖昧にしないか

判断方法: Human、AI Agent、Dispatcher、Workflow、Runtime、Repositoryのどこが何を担当するか明確か確認します。

採用例: Dispatcherがtool選択を記録し、workflowはそのContextを読む。

非採用例: workflowが環境選択、GitHub mutation、実装、承認、archiveを一つの暗黙手順で処理する。

## Human Responsibilityを壊さないか

判断方法: 人間が判断すべき操作や設計方針がAI Agentへ暗黙に移譲されていないか確認します。

採用例: pushやRAG登録の前に、変更範囲、Evidence、残リスクを提示してHuman Checkを待つ。

非採用例: 「効率化」のために承認が必要な操作を自動実行する。

## Platform思想と矛盾しないか

判断方法: 変更がMission、Philosophy、Core Principles、Non Goalsと矛盾しないか確認します。

採用例: Agentの推論負荷を下げ、Context FirstとEvidence Firstを強める改善。

非採用例: 短期的に便利でも、責任境界を曖昧にし、後続workflowが読めるEvidenceを残さない改善。

## 判定結果の残し方

Platform Fit Checkの結果は、必要に応じてIssue、process report、review、docs drift analysisへ残します。

記録する項目:

- check対象。
- 採用、非採用、保留の判断。
- 判断理由。
- Human Check要否。
- 必要なEvidence。
- 関連するGovernance文書。

## Self-Improvement Workflow との関係

Self-Improvement Workflow は、改善候補をIssue化する前にこのcheckを使います。

Repository Curation Workflow は、repository整理やdocs再配置がplatform思想に合うか確認するために使います。

Runtime Maintenance Workflow は、runtime改善が便利さだけでなく、Context First、Evidence First、Human Responsibilityを強めるか確認するために使います。

## Summary

- Platform Fit Checkは、改善案がAriadneの思想に適合するか判断するためのchecklistである。
- 迷う項目は推測で通さず、理由、条件、Evidence、Human Checkを記録する。
- 採用判断では、AIの迷い、認知負荷、品質、維持性、改善性、責務境界、人間の責任を確認する。
- Self-Improvement、Repository Curation、Runtime Maintenanceの前提checkとして使う。
