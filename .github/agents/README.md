# Localty Agent Prompts

このディレクトリには、Intent-Driven Robotics Workflow で利用する Agent prompt を格納します。

各Agentは、Localtyの成長文化を守るために設計されています。

- 仕組みより Intent
- 便利さより安全
- 美しさより運用可能性
- 自信より証拠
- 実装前に責務境界
- 現場学習をRAG知識として残す

## Agent Map

| Agent | 主な役割 | 代表的な出力 |
| --- | --- | --- |
| `requirement-discovery-agent.prompt.md` | 箇条書き草案の精査、深掘り質問、要件定義書レビュー草案 | `work/requirements/draft/*-questions.md`, `*-requirements-review.md` |
| `external-web-source-reviewer-agent.prompt.md` | 不足知識に対して外部Web一次情報を精査し、外部Web RAG候補へ要約する | `rag/external-web/<category>/*.md` |
| `external-web-rag-dispatcher-agent.prompt.md` | 蓄積済み外部Web RAGをカテゴリ別に検索・集約し、要件定義/設計へ渡す | `rag/external-web/retrieval/*-aggregate.md` |
| `docs-drift-analyzer-agent.prompt.md` | 実装とdocsの差分検出、JSON化、Issue材料作成 | `work/<branch>/context/docs-drift-analysis.json` |
| `robotics-architect-agent.prompt.md` | システム構造と責務境界 | `architecture.md` |
| `robotics-runtime-agent.prompt.md` | process model、lifecycle、restart、watchdog | `runtime-design.md` |
| `network-migration-planner-agent.prompt.md` | LAN -> VPN -> Relay -> Remote Ops の移行計画 | `network-migration-plan.md` |
| `remote-gateway-architect-agent.prompt.md` | remote gateway のサービス境界 | `remote-gateway-architecture.md` |
| `deployment-architect-agent.prompt.md` | deployment topology と migration plan | `deployment-architecture.md` |
| `remote-gateway-implementer-agent.prompt.md` | 承認済みarchitectureに基づく実装 | source, tests, `implementation-report.md` |
| `safety-reviewer-agent.prompt.md` | ロボティクス安全レビュー | `safety-review.md` |
| `security-reviewer-agent.prompt.md` | remote access と command security のレビュー | `security-review.md` |
| `network-reviewer-agent.prompt.md` | network design review | `network-review.md` |
| `observability-reviewer-agent.prompt.md` | logs, metrics, telemetry, incident traceability | `observability-review.md` |
| `robotics-tester-agent.prompt.md` | test strategy と test matrix | `test-specification.md` |
| `documentation-writer-agent.prompt.md` | decision record と再利用可能な知識化 | docs, troubleshooting, RAG notes |
| `knowledge-capture-agent.prompt.md` | PR資料、証跡整理、RAG/docs候補抽出、archive準備 | PR docs, `knowledge-capture-report.md` |

## 推奨フロー

詳細な開発フローは `.github/prompts/` を参照してください。
Agent間の共通schemaは `.github/schemas/`、共通判断ルールは `.github/shared/` を参照してください。

```text
draft bullets
  -> requirement discovery
  -> external web knowledge review when knowledge is insufficient
  -> external web RAG dispatch when saved external knowledge is relevant
  -> reviewed requirements
  -> docs drift analysis when docs sync is requested
  -> robotics architect
  -> robotics runtime agent
  -> network migration planner
  -> remote gateway architect
  -> deployment architect
  -> safety / security / network / observability reviews
  -> robotics tester
  -> implementer
  -> documentation writer
  -> knowledge capture
  -> knowledge-inbox / RAG
```

reviewで未解決QAが出た場合は、architecture または requirements へ戻します。

## 共通レビュー原則

Reviewer は設計を黙って修正しません。以下を明示します。

- finding
- risk
- severity
- recommendation
- required QA
- required tests
- final judgment

## 共通実装原則

Implementer は以下を黙って変更しません。

- architecture
- protocol
- ports
- safety timeout
- authentication model
- operator authority model

実装中に曖昧さが見つかった場合は、QAとして返します。

## RAG Capture Rule

現場で得た発見、incident、review escape、design decision は、未来のAgentに役立つ可能性があります。Markdownで残す場合は front matter を付けます。

```yaml
---
project: localty-system-gui
type: improvement-report
status: draft
created_at: 2026-05-31T00:00:00+09:00
source: agent
tags:
  - robotics
  - safety
  - network
---
```

一時知識は以下へ保存することを推奨します。

```text
knowledge-inbox/
  investigations/
  improvement-reports/
  field-notes/
```

## Core Principle

このworkflowは、使うたびにLocaltyをより安全に、より理解しやすくするためにあります。
