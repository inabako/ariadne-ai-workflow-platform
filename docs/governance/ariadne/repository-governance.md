---
language: ja-JP
---

# Repository Governance

この文書は、Ariadne AI Workflow Platform のrepository運用方針を定義します。

Repositoryは、platformを置く単なる入れ物ではありません。Workflow、Runtime、Docs、RAG、Evidence、Skill、Template、Schemaを接続するplatformの一部です。

## Repository Curation

Repository Curation は、repositoryを後続の人間とAI Agentが読みやすい状態に保つ活動です。

対象:

- docsの入口とリンク。
- runtime helperとdocsの対応。
- skill entrypointとworkflow docsの対応。
- template、schema、agent promptの対応。
- work、rag、archiveの保存方針。
- 古い情報、重複情報、mojibakeの検出。

Repository Curationは、見た目の整理ではなく、AI Agentが迷わないContextを維持するためのgovernanceです。

## Branch Policy

通常の改善作業は、target branchからissue branchを作って進めます。

基本形:

```text
feature/issue-<issue-number>
```

branchは、変更範囲とIssueを追跡可能にするための単位です。複数の責務を一つのbranchへ混ぜると、reviewとrollbackが難しくなります。

## GitHub Flow

GitHub Issue、branch、commit、push、Pull Requestは、Human Checkを伴う操作として扱います。

AI Agentは、Issue body、変更範囲、検証結果、PR材料を準備できます。ただし、GitHub mutationやpushは人間承認なしに進めません。

## Issue運用

Issueは、改善や実装のsource of truthです。

Issueには次を含めます。

- 目的。
- 対象範囲。
- 対象外。
- 完了条件。
- Human Check条件。
- 検証方法。
- 関連Evidence。

会話の流れだけに依存せず、後続workflowが読める形で判断を残します。

## Evidence保存

Evidenceは、判断と検証の根拠です。

保存対象:

- process report。
- test report。
- docs drift analysis。
- runtime metrics。
- artifact index。
- Human Check記録。
- RAG candidate。

Evidenceは、作業完了後に消える一時出力ではありません。後続workflow、review、RAG化、archiveの入力になります。

## Docs更新

実装、runtime、workflow、schema、templateが変わる場合、docsの更新要否を確認します。

docs更新では、単に手順を増やすのではなく、なぜその手順が必要かを説明します。思想、設計、運用、改善の流れが読めることを重視します。

Docs Syncでは、current implementationとcurrent docsを主証拠として扱い、古いRAGや記憶で現在の実装を上書きしません。

## UTF-8前提

Ariadneは、日本語Markdown、prompt、schema、reportを多く扱います。

Markdown、JSON、YAML、prompt、docsはUTF-8を前提にします。mojibakeが見える場合は、軽微な表示問題ではなくworkflow concernとして扱います。

`.bat` / `.cmd` など、Shift_JIS / CP932を意図する例外は境界を明示し、無理に一括変換しません。

## RAG Knowledge管理

RAGは、過去の判断、改善report、docs候補、運用知識を再利用するための補助知識です。

ただし、RAGは現在のrepository evidenceより優先しません。

運用方針:

- RAG登録はHuman Check後に行う。
- RAG sourceは日本語主体で、検索しやすい構造にする。
- 外部記事や外部docsの本文を無断で蓄積しない。
- 現在のコード、docs、schema、runtimeと矛盾する場合は、current repositoryを優先する。

## DuckDB運用方針

DuckDBは、RAGやruntime metricsなどの構造化分析を将来的に扱う候補です。

運用上は、DuckDBを唯一のsource of truthにしません。Markdown、JSON、schema、process reportなどのfile-based artifactを基本とし、DuckDBは検索、集計、分析を助ける派生層として扱います。

DuckDBを導入または更新する場合は、次を明確にします。

- 元になるfile-based artifact。
- 生成手順。
- 再生成方法。
- Human Check要否。
- archiveやRAGとの関係。

## Repository自身もPlatformの一部である

Ariadneでは、repository構造、docs、runtime、RAG、archive、Issue運用がすべてplatformの一部です。

そのため、repositoryの整理は単なる保守ではありません。AI Agentが迷わず、Humanが責任ある判断を行い、workflowが継続改善できる状態を保つためのgovernanceです。

## Self-Improvement Workflow との関係

Self-Improvement Workflow は、repository内のfrictionや改善候補をIssue化し、Evidenceとして残します。

Repository Curation Workflow は、この文書を直接の判断基準として、docs、RAG、archive、skill、runtimeの整理を行います。

Runtime Maintenance Workflow は、runtime変更がrepository内のdocs、schema、test、Evidence保存先と一致しているか確認します。

## Summary

- Repositoryはplatformの入れ物ではなく、Ariadneそのものを構成する一部である。
- Issue、branch、Evidence、docs、RAG、archiveは後続workflowが読める形で管理する。
- UTF-8を前提にし、mojibakeはworkflow concernとして扱う。
- DuckDBは分析用の派生層であり、file-based artifactを基本のsource of truthにする。
