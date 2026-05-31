# Robotics Workflow

このディレクトリは、Localty の Intent-Driven Robotics Workflow を定義します。

Web system の workflow をそのまま流用せず、robotics system に必要な safety、hardware、field operation、runtime、network、operator responsibility を中心に置きます。

## Core Principle

ロボット開発では、実装できたかより先に、安全に試せるか、安全に止められるか、安全に戻せるかを確認します。

Localty の workflow は、完成形を一度に作るためではなく、現場で学びながら安全に成長するためのものです。

## Workflow Set

| File | Purpose |
| --- | --- |
| `robotics-new-system.prompt.md` | `/robotics-new-system` Skill entrypoint |
| `robotics-feature-maintenance.prompt.md` | `/robotics-feature-maintenance` Skill entrypoint |
| `pre-development-preparation.prompt.md` | 開発前準備、repository sync、Issue、branch 作成 |
| `new-robotics-system-development.prompt.md` | 新システム開発の標準フロー |
| `robotics-maintenance-development.prompt.md` | 既存システムの新機能追加・保守変更フロー |
| `robotics-safety-gates.prompt.md` | 各段階で通す Safety Gate |
| `robotics-test-strategy.prompt.md` | simulation、bench、field を含む test strategy |
| `robotics-release-and-field-operation.prompt.md` | release、rollback、現場運用、incident capture |

## Skill Entrypoints

| Slash Command | Skill | Delegated Flow |
| --- | --- | --- |
| `/robotics-new-system` | `skills/robotics-new-system/SKILL.md` | `/new-robotics-system-development` |
| `/robotics-feature-maintenance` | `skills/robotics-feature-maintenance/SKILL.md` | `/robotics-maintenance-development` |

## Two Primary Flows

### 新システム開発

まだ構造が固まっていない system を対象にします。

主な関心:

- mission / operational context の定義
- architecture と responsibility boundary
- safety requirement と hazard analysis
- simulation / bench / field の段階検証
- operator handover と運用手順

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
  -> safety / security / network / observability reviews
  -> robotics tester
  -> implementer
  -> documentation writer
  -> knowledge-inbox / RAG
```

review で critical / high risk や unanswered safety QA が出た場合は、implementation へ進まず requirements または architecture へ戻します。
