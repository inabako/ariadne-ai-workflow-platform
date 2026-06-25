# Robotics Workflow

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

このディレクトリは、Localty の Intent-Driven Robotics Workflow を定義します。

Web system の workflow をそのまま流用せず、robotics system に必要な safety、hardware、field operation、runtime、network、operator responsibility を中心に置きます。

## Core Principle

ロボット開発では、実装できたかより先に、安全に試せるか、安全に止められるか、安全に戻せるかを確認します。

Localty の workflow は、完成形を一度に作るためではなく、現場で学びながら安全に成長するためのものです。

## Workflow Set

| File | Purpose |
| --- | --- |
| `requirement-discovery.prompt.md` | `/requirement-discovery` Skill entrypoint |
| `noise-reduction-phase.prompt.md` | `/requirement-discovery` 内で要件review draft前に実行するノイズ除去フェーズ |
| `docs-sync.prompt.md` | `/docs-sync` Skill entrypoint |
| `robotics-new-system.prompt.md` | `/robotics-new-system` Skill entrypoint |
| `robotics-new-system-iac.prompt.md` | `/robotics-new-system-iac` Skill entrypoint |
| `robotics-feature-maintenance.prompt.md` | `/robotics-feature-maintenance` Skill entrypoint |
| `gac-uac-gui-mode.prompt.md` | SVGがある場合に3つの実装workflowへ差し込む共通GUI拡張 |
| `nextjs-webapp-implementation-prep.prompt.md` | Next.js画面機能がある場合に3つの実装workflowへ差し込む実装前準備 |
| `realtime-iac.prompt.md` | `/realtime-iac` Skill entrypoint |
| `corrective-action-report.prompt.md` | `/corrective-action-report` Skill entrypoint |
| `pre-development-preparation.prompt.md` | 開発前準備、repository sync、Issue、branch 作成 |
| `new-robotics-system-development.prompt.md` | 新システム開発の標準フロー |
| `robotics-maintenance-development.prompt.md` | 既存システムの新機能追加・保守変更フロー |
| `robotics-safety-gates.prompt.md` | 各段階で通す Safety Gate |
| `robotics-test-strategy.prompt.md` | simulation、bench、field を含む test strategy |
| `robotics-release-and-field-operation.prompt.md` | release、rollback、現場運用、incident capture |
| `knowledge-capture.prompt.md` | PR資料、テスト証跡、RAG/docs候補、archive準備 |

## Skill Entrypoints

| Slash Command | Skill | Delegated Flow |
| --- | --- | --- |
| `/requirement-discovery` | `skills/requirement-discovery/SKILL.md` | requirement discovery and human review |
| `/docs-sync` | `skills/docs-sync/SKILL.md` | implementation/docs drift analysis and docs-only issue branch |
| `/robotics-new-system` | `skills/robotics-new-system/SKILL.md` | `/new-robotics-system-development` |
| `/robotics-new-system-iac` | `skills/robotics-new-system-iac/SKILL.md` | Shared Artifacts validation then `/realtime-iac` |
| `/robotics-feature-maintenance` | `skills/robotics-feature-maintenance/SKILL.md` | `/robotics-maintenance-development` |
| `/realtime-iac` | `skills/realtime-iac/SKILL.md` | realtime IaC design, generation, validation, and docs |
| `/corrective-action-report` | `skills/corrective-action-report/SKILL.md` | read-only improvement report |
| `/knowledge-capture` | `skills/knowledge-capture/SKILL.md` | finalization and knowledge recovery |

## Two Primary Flows

### Requirement Discovery

人間が `work/requirements/draft/` に置いた箇条書き草案を、完成版要件定義書へ育てる前段 workflow です。

Critical items が不足している場合は、設計や実装方針を勝手に決めず、人間へ質問します。

Completion は、人間レビューで OK が出た後に `work/requirements/` へ完成版を1件だけ保存した状態です。

### Documentation Sync

実装と `docs/` の差分を検出し、差分結果を `docs-drift-analysis.json` に保存してから Issue 化する workflow です。

`work/<target-branch>` は read-only 分析用、`work/issue-<issue-number>` は docs 修正用に分けます。

この flow では実装コードを変更しません。

### 新システム開発

まだ構造が固まっていない system を対象にします。

主な関心:

- mission / operational context の定義
- architecture と responsibility boundary
- safety requirement と hazard analysis
- simulation / bench / field の段階検証
- operator handover と運用手順

### 新システム + IaC 統合

新しい system を設計した後、その設計成果物を Shared Artifacts として固定し、validator を通してから realtime IaC workflow へ渡します。

主な関心:

- 要件定義、通信仕様、port定義、境界定義、ADRの整合
- software inventory と infrastructure ownership
- IaCが推測で port、route、public exposure、secret、runtime unit を決めないこと
- validator の `pass` または human-approved `conditional-pass`

### 保守開発

既に動いている system への変更を対象にします。

主な関心:

- change intent の明確化
- impact analysis
- risk classification
- regression / safety check
- deployment plan
- post-change observation

## Shared Rule

どちらの flow でも、次の問いを先に確認します。

- 人や設備に危険がないか
- STOP / emergency stop が最高優先か
- 通信断、video loss、sensor failure で安全側へ倒れるか
- 実機前に simulation / mock / bench で確認できるか
- rollback できるか
- operator が degraded state を認識できるか
- logs / telemetry から原因追跡できるか

## Relation To Agents

この workflow は `.github/agents` の prompt と組み合わせて使います。

標準的な流れ:

```text
intent / requirements
  -> robotics architect
  -> robotics runtime agent
  -> network migration planner
  -> remote gateway architect
  -> deployment architect
  -> shared artifact validator when IaC is in scope
  -> safety / security / network / observability reviews
  -> robotics tester
  -> implementer
  -> documentation writer
  -> knowledge capture
  -> knowledge-inbox / RAG
```

review で critical / high risk や unanswered safety QA が出た場合は、implementation へ進まず requirements または architecture へ戻します。
