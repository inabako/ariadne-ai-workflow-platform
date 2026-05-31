# Intent-Driven Robotics AI Workflow

Localty の robotics system development を、Intent、Safety、Operational Learning を中心に進めるための AI workflow repository です。

Web system の workflow をそのまま流用せず、robotics system に必要な hardware、field operation、runtime、network、operator responsibility、safety gate を含めて設計します。

## Concept

この workflow は、完成形を一度に作るためではなく、現場で学びながら安全に育てるためのものです。

大切にすること:

- Intent から始める
- 実装前に責務境界を見える化する
- 実機より前に Safety Gate を通す
- simulation / bench / field を段階化する
- STOP、rollback、observability を後回しにしない
- 学びを `knowledge-inbox` / RAG に戻す

## Current Structure

```text
.github/
  agents/      role-based Agent prompt definitions
  prompts/     slash command style workflow prompts
  schemas/     JSON Schema contracts for shared Agent data
  shared/      common principles and operational rules

knowledge-inbox/
  investigations/
  improvement-reports/
  field-notes/

work/
  requirements/
rag/
  corrective-action-report/
runtime/
skills/
templates/
```

## Runtime

`runtime/` には、workflow を実行・補助するための処理機能を置きます。

```text
runtime/
  common/
  intake/      投入された要件定義書を受付ID単位の work/<採番ID>/ へ移動する機能
  retrieval/   task を順次または並列で処理し、必要なcontextやartifactを取り出す機能
  scm/         target repository取得、要件比較、Issue branch作成、semantic commit
  github/      GitHub Issue draft / create
```

`runtime/intake/` は、`work/requirements/` に配置された完成版要件定義書を受け付け、受付IDの採番、`work/<採番ID>/` の初期化、要件定義書の移動、初期 `context/*.json` の作成を担当します。

`work/requirements/` に要件定義書が無い場合、Skill や workflow prompt から作業をオーダーされても intake harness は受領拒否します。

`work/requirements/` に要件定義書が2件以上ある場合も受領拒否します。標準運用は `1 requirement file = 1 receipt ID` です。

`runtime/retrieval/` は、task queue / task graph、前工程artifact、`context/*.json` を読み取り、Agentに渡すhandoff packageの組み立てや sequential / parallel task execution を補助します。

Implemented runtime CLI:

```text
runtime/intake/intake_requirements.py
runtime/retrieval/task_runner.py
runtime/scm/prepare_repository.py
runtime/scm/compare_requirements.py
runtime/github/issue_manager.py
runtime/scm/create_issue_branch.py
runtime/scm/commit_changes.py
```

## Environment Files

GitHub / SCM 連携で必要な値は、repository root の環境ファイルで管理します。

```text
.env.example   共有可能なキー一覧
.env           ローカル実値、commit禁止
.gitignore     .env と .env.* を除外し、.env.example は追跡対象
```

`.env` では、GitHub authentication、git user config、default branch / remote、default labels / assignees を管理します。

案件ごとに変わる repository は、要件定義書の `Repository Control` に必ず記載します。repository が読み取れない要件定義書は intake で受領しません。

実値やtokenは `.env.example`、prompt、schema、source code に書きません。

## Artifact Templates

各フローの成果物ひな形は `templates/` に置きます。

```text
templates/
  requirements/          要件定義書
  design-document/       設計書
  process-report/        プロセス毎のレポート
  test-evidence/         テスト証跡
  test-specifications/   テスト仕様書、テストケース表
```

`templates/requirements/` には、ロボティクス版の新システム用、および新機能/保守開発用の要件定義書テンプレートを置きます。

完成版の要件定義書は `work/requirements/` に配置します。新システム立ち上げ、新機能追加、保守開発のいずれでも、この投入口を共通で使います。

新機能および保守開発の要件定義書には `Repository Control` 欄があり、target repository / target branch を案件ごとに指定できます。`runtime/intake/intake_requirements.py` は repository が読み取れない要件定義書を受領しません。

## Workflow Prompts

`.github/prompts/` には、`/xxxxx` 形式で呼び出すことを想定した workflow prompt を置きます。

Current prompts:

- `/robotics-workflow`
- `/robotics-new-system`
- `/robotics-feature-maintenance`
- `/corrective-action-report`
- `/pre-development-preparation`
- `/new-robotics-system-development`
- `/robotics-maintenance-development`
- `/robotics-safety-gates`
- `/robotics-test-strategy`
- `/robotics-release-and-field-operation`

## Agent Prompts

`.github/agents/` には、役割ごとの Agent prompt を置きます。

Current agents:

- Robotics Architect Agent
- Robotics Runtime Agent
- Network Migration Planner Agent
- Remote Gateway Architect Agent
- Deployment Architect Agent
- Remote Gateway Implementer Agent
- Safety Reviewer Agent
- Security Reviewer Agent
- Network Reviewer Agent
- Observability Reviewer Agent
- Robotics Tester Agent
- Documentation Writer Agent

## Workflow Skills

`skills/` には、workflow を選択するための Skill entrypoint を置きます。

Current skills:

| Slash Command | Skill | Delegated Prompt |
| --- | --- | --- |
| `/robotics-new-system` | `skills/robotics-new-system/` | `/new-robotics-system-development` |
| `/robotics-feature-maintenance` | `skills/robotics-feature-maintenance/` | `/robotics-maintenance-development` |
| `/corrective-action-report` | `skills/corrective-action-report/` | `/corrective-action-report` |

`/robotics-new-system` と `/robotics-feature-maintenance` は、`work/requirements/` に完成版の要件定義書が1件だけある状態を前提にします。要件定義書が無い、2件以上ある、または `Repository Control` が読めない場合は intake harness で受領拒否します。

`/corrective-action-report` は開発開始ではなく read-only review と改善点report作成の Skill です。対象repositoryと対象branchを user に確認し、report を `rag/corrective-action-report/` へ保存します。

## Shared JSON Schema

`.github/schemas/` には、Agent間で情報連携するための JSON Schema を置きます。

JSON Schema は、実データそのものではなく、共有JSONの構造を定義する contract です。

これにより、Agentやtoolが以下を structured data として扱いやすくなります。

- project / workflow / safety context
- artifact index
- decision record
- review finding
- QA
- test evidence
- handoff package

Current schemas:

- `agent-context.schema.json`
- `artifact-index.schema.json`
- `decision-record.schema.json`
- `finding-record.schema.json`
- `qa-record.schema.json`
- `test-evidence.schema.json`
- `handoff-package.schema.json`
- `task-plan.schema.json`
- `task-result.schema.json`
- `scm-state.schema.json`
- `github-issue.schema.json`
- `commit-record.schema.json`

## Shared Rules

`.github/shared/` には、すべてのAgentが共通で参照する判断ルールを置きます。

- `localty-principles.md`
- `risk-and-severity.md`
- `artifact-management.md`
- `agent-handoff.md`

## Data Sharing Model

現時点では、JSON DB ではなく file-based shared memory として扱います。

Schema は `.github/schemas/` に置き、実データは project ごとの作業領域に保存する想定です。

Example:

```text
work/
  <採番ID>/
    design-document/
    process-report/
    test-evidence/
    test-specifications/
    source/
    context/
      agent-context.json
      artifact-index.json
      qa-records.json
      finding-records.json
      decision-records.json
      test-evidence.json
      handoff-package.json
```

成果物は `work/<採番ID>/design-document/`、`work/<採番ID>/process-report/`、`work/<採番ID>/test-evidence/`、`work/<採番ID>/test-specifications/` に保存します。

実装対象のsource、clone、差分、生成物は `work/<採番ID>/source/` に保存します。

将来的には、SQLite、DuckDB、PostgreSQL、vector DB、workflow engine の state store へ移行できます。

## New System Development Flow

新規機能および保守開発では、開発本体へ入る前に `/pre-development-preparation` を通します。

```text
Intake
  -> Repository Sync
  -> Requirement Comparison
  -> GitHub Issue Draft / Create
  -> Working Branch Create
  -> Development Workflow
  -> Semantic Commit
```

新システム立ち上げでは、以下の流れを基本とします。

```text
Intent / Mission
  -> Operational Context
  -> Hazard Analysis / Safety Requirements
  -> System Architecture
  -> Runtime / Network / Deployment Design
  -> Test Strategy
  -> Implementation
  -> Integration / Bench Test
  -> Limited Field Test
  -> Release / Operation Handover
```

重要なのは、作れるかではなく、安全に試せるか、止められるか、戻せるか、学びを残せるかです。

## Knowledge Inbox

現場で得た発見、incident、review escape、design decision は、未来のAgentに役立つ可能性があります。

一時知識は以下に保存します。

```text
knowledge-inbox/
  investigations/
  improvement-reports/
  field-notes/
rag/
  corrective-action-report/
```

## Status

この repository は試行錯誤しながら育てる workflow foundation です。

各種 report と成果物の基本格納先は `templates/` と `work/<採番ID>/` で定義済みです。

より詳細な命名規則、採番ルール、承認済みartifactの保管ポリシーは、今後の運用に合わせて定義します。
