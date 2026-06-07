# Intent-Driven Robotics AI Workflow

Localty の robotics system development を、Intent、Safety、Operational Learning を中心に進めるための AI workflow repository です。

Web system の workflow をそのまま流用せず、robotics system に必要な hardware、field operation、runtime、network、operator responsibility、safety gate を含めて設計します。

この repository は、完成形を一度に固定するためのものではありません。現場で学びながら、安全に試し、安全に止め、安全に戻し、学びを次の workflow / Agent / RAG に残すための foundation です。

## Table of Contents

- [Core Concept](#core-concept)
- [Current Structure](#current-structure)
- [Primary Entry Points](#primary-entry-points)
- [VS Code Prompt Discovery](#vs-code-prompt-discovery)
- [Requirement Intake Gate](#requirement-intake-gate)
- [Development Workflow](#development-workflow)
  - [New Robotics System](#new-robotics-system)
  - [Feature / Maintenance Development](#feature--maintenance-development)
- [Corrective Action Report](#corrective-action-report)
- [Runtime](#runtime)
- [Work Directory Model](#work-directory-model)
- [Templates](#templates)
- [Environment Files](#environment-files)
- [Skills](#skills)
- [Workflow Prompts](#workflow-prompts)
- [Agent Prompts](#agent-prompts)
- [Shared JSON Schema](#shared-json-schema)
- [Shared Rules](#shared-rules)
- [Data Sharing Model](#data-sharing-model)
- [RAG / Knowledge Capture](#rag--knowledge-capture)
- [RAG Pipeline](#rag-pipeline)
- [Commit Rule](#commit-rule)
- [License](#license)
- [Status](#status)

## Core Concept

大切にすること:

- Intent から始める
- 実装前に責務境界を見える化する
- 実機より前に Safety Gate を通す
- simulation / bench / field を段階化する
- STOP、rollback、observability を後回しにしない
- 会話ログではなく artifact と evidence を残す
- 学びを `knowledge-inbox` / `rag` に戻す

Robotics workflow では、作れるかよりも先に、安全に試せるか、止められるか、戻せるか、観測できるかを確認します。

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

rag/
  corrective-action-report/
  normalized/
  chunks/
  indexes/
  embeddings/
  retrieval/

runtime/
  common/
  intake/
  retrieval/
  scm/
  github/

skills/
  corrective-action-report/
  robotics-feature-maintenance/
  robotics-new-system/

templates/
  requirements/
  design-document/
  process-report/
  test-evidence/
  test-specifications/

work/
  requirements/
```

## Primary Entry Points

この repository では、主に6つの slash command / Skill entrypoint を使います。

| Slash Command | Purpose | Skill | Main Output |
| --- | --- | --- | --- |
| `/robotics-new-system` | 新しい robotics system を立ち上げる | `skills/robotics-new-system/` | `work/<receipt-id>/` |
| `/robotics-feature-maintenance` | 既存 robotics system の新機能追加または保守開発を行う | `skills/robotics-feature-maintenance/` | `work/<receipt-id>/` |
| `/corrective-action-report` | 指定repository / branchの改善点をreport化する | `skills/corrective-action-report/` | `rag/corrective-action-report/` |
| `/rag-build` | Markdown report を file-based RAG artifact に変換する | `skills/rag-build/` | `rag/normalized/`, `rag/chunks/`, `rag/indexes/`, `rag/embeddings/` |
| `/rag-load` | 開発前に RAG を検索し、圧縮済みcontextを読み込む | `skills/rag-load/` | `rag/retrieval/<uuid>.json` |

`/robotics-new-system` と `/robotics-feature-maintenance` は、開発 workflow を開始するための入口です。

`/corrective-action-report` は、開発開始ではなく read-only review と改善点report作成の入口です。

`/rag-build` は RAG 作成、`/rag-load` は RAG 読み込みの入口です。開発本体へ入る前に `/rag-load` を実行します。`/rag-load` は `runtime/rag/rag_dispatcher.py` を使って複数クエリを並列検索し、既存の `retrieve_context.py` 圧縮結果を集約します。

RAG artifact のファイル名は UUID にします。検索はファイル名ではなく、JSON の `content` と metadata を対象にします。

Additional corrective implementation entrypoint:

| Command | Purpose | Skill | Main Output |
| --- | --- | --- | --- |
| `/corrective-action-fix` | GitHub repository / branchを取得し、report/RAG/Issue/branch/修正/test/確認/pushまで進める | `skills/corrective-action-fix/` | `work/<branch>/`, `work/issue-<issue-number>/`, `rag/corrective-action-report/` |

### Dispatcher 方針

`runtime/rag/rag_dispatcher.py` は、意図的に `/rag-load` 専用にしています。

RAG load には、複数の検索queryを計画し、必要に応じて並列検索し、開発前に圧縮済みcontext packを集約するという明確な dispatch / aggregate 責務があります。

一方で、`/corrective-action-fix` 全体は単一の workflow dispatcher で包まない方針です。このflowには GitHub Issue 作成、remote branch 作成、clone、commit、人間確認、push が含まれます。これらは副作用と人間の承認gateを伴うため、`skills/corrective-action-fix/SKILL.md` に工程を明示し、小さな runtime CLI を段階ごとに呼び出します。

同じ承認gateと副作用境界を明示できない限り、corrective action 用の all-in-one dispatcher は追加しません。

## VS Code Prompt Discovery

VS Code / GitHub Copilot Chat の `/` 候補に出すため、prompt files は `.github/prompts/*.prompt.md` に置いています。

現在の prompt entrypoint:

```text
.github/prompts/
  corrective-action-fix.prompt.md
  corrective-action-report.prompt.md
  rag-build.prompt.md
  rag-load.prompt.md
  robotics-new-system.prompt.md
  robotics-feature-maintenance.prompt.md
```

`/corrective-action-report` は候補表示を安定させるため、prompt file に frontmatter を持っています。

```yaml
---
name: corrective-action-report
description: 指定された repository / branch の現状を調査し、改善点を corrective action report として保存します。
argument-hint: "<target-repository> <target-branch>"
agent: agent
---
```

候補に出ない場合は、VS Code で `C:\github\intent-driven-robotics-ai-workflow` を workspace として開いてください。別 repository、たとえば `localty-system-gui` を開いている場合、兄弟ディレクトリの `.github/prompts` は候補に出ないことがあります。

必要に応じて、VS Code の `Reload Window`、`Chat: Open Customizations`、または `/prompts` で prompt file の読み込み状態を確認します。

## Requirement Intake Gate

新システム作成、新機能開発、保守開発では、開発本体へ入る前に `work/requirements/` へ完成版の要件定義書を配置します。

```text
work/
  requirements/
    <completed-requirements>.md
```

標準運用:

```text
1 requirement file = 1 receipt ID
```

`runtime/intake/intake_requirements.py` は、以下の場合に受領拒否します。

- `work/requirements/` に要件定義書が無い
- `work/requirements/` に要件定義書が2件以上ある
- 要件定義書から `Repository Control` が読み取れない

会話ログだけを根拠に intake 済みとして扱ってはいけません。

Repository は `.env` の fallback ではなく、要件定義書の `Repository Control` に必ず記載します。対象 repository が要件定義書に無い場合は受領しない方針です。

## Development Workflow

### New Robotics System

呼び出し:

```text
/robotics-new-system
```

内部の詳細flow:

```text
/pre-development-preparation
  -> /rag-load
  -> /new-robotics-system-development
```

基本工程:

```text
Intake
  -> Repository Sync
  -> Requirement Comparison
  -> GitHub Issue Draft / Create
  -> Working Branch Create
  -> RAG Load / Prior Findings
  -> Intent / Mission
  -> Operational Context
  -> Hazard Analysis / Safety Requirements
  -> System Architecture
  -> Runtime / Network / Deployment Design
  -> Test Strategy
  -> Implementation
  -> Integration / Bench Test
  -> Limited Field Test
  -> Release / Operation Handover
  -> Semantic Commit
```

重要 gate:

- STOP / emergency stop behavior が未定義なら進めない
- communication loss behavior が未定義なら進めない
- startup / shutdown safe state が未定義なら進めない
- critical / high safety finding が残っている場合は field test に進めない

### Feature / Maintenance Development

呼び出し:

```text
/robotics-feature-maintenance
```

内部の詳細flow:

```text
/pre-development-preparation
  -> /rag-load
  -> /robotics-maintenance-development
```

基本工程:

```text
Intake
  -> Repository Sync
  -> Requirement Comparison
  -> GitHub Issue Draft / Create
  -> Working Branch Create
  -> Change Intent
  -> Current State Capture
  -> Impact Analysis
  -> Risk Classification
  -> Change Design
  -> Test Plan
  -> Implementation
  -> Verification
  -> Deployment Plan
  -> Post-change Observation
  -> Semantic Commit
```

保守開発では、変更量よりも影響範囲と安全性を優先します。

Safety behavior、network authority、runtime process ownership、operator workflow に影響する変更は、実装前に review 対象として扱います。

## Corrective Action Report

呼び出し:

```text
/corrective-action-report
```

この Skill は、指定された repository / branch の現状を調査し、改善点、risk、test gap、documentation gap、architecture concern、workflow opportunity を report として残します。

開始前に必ず確認する入力:

- target repository: local path、GitHub URL、または owner/repo
- target branch: 調査対象 branch

どちらかが未指定の場合は、作業前に user へ入力を求めます。

current branch を勝手に採用しません。user が current branch 利用を明示的に承認した場合のみ使います。

出力先:

```text
rag/corrective-action-report/
```

推奨ファイル名:

```text
YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md
```

この Skill は read-only review を基本とします。GitHub Issue 作成、branch 作成、commit、source 修正は行いません。user が明示的に実装修正へ進めた場合のみ、別 workflow へ移行します。

## Runtime

`runtime/` には、workflow を実行・補助するための処理機能を置きます。

```text
runtime/
  common/      shared runtime utilities
  intake/      requirement intake and work directory initialization
  retrieval/   sequential / parallel task runner and context retrieval
  scm/         repository sync, requirement comparison, branch, commit
  github/      GitHub Issue draft / create
  rag/         report normalization, chunking, and file-based RAG indexes
```

Implemented runtime CLI:

| Script | Responsibility |
| --- | --- |
| `runtime/workflow/init_corrective_action_fix.py` | corrective-action-fix 用の `work/<branch>/` または `work/issue-<issue-number>/` と初期contextを作成する |
| `runtime/scm/push_branch.py` | human check承認後に `feature/issue-<issue-number>` branch をpushし、push recordを残す |
| `runtime/intake/intake_requirements.py` | `work/requirements/` の要件定義書を受付ID単位で `work/<receipt-id>/` へ移動し、初期contextを作成する |
| `runtime/retrieval/task_runner.py` | task plan を sequential / parallel に処理し、task result を出力する |
| `runtime/scm/prepare_repository.py` | target repository / branch を取得し、`work/<receipt-id>/source/` と `scm-state.json` を整える |
| `runtime/scm/compare_requirements.py` | 要件定義書と repository state の比較reportを作る |
| `runtime/github/issue_manager.py` | GitHub Issue draft / create を行う |
| `runtime/scm/create_issue_branch.py` | Issue番号からGitHub上に `feature/issue-<issue-number>` branchを作成し、work配下へclone / checkoutする |
| `runtime/scm/commit_changes.py` | 成果物とsource差分を semantic commit で commit する |
| `runtime/rag/standardize_corrective_report_names.py` | corrective action report Markdown を `YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md` に統一する |
| `runtime/rag/normalize_documents.py` | Markdown report を metadata 付きの RAG document JSON に変換する |
| `runtime/rag/chunk_documents.py` | normalized document を retrieval しやすい chunk JSON に分割する |
| `runtime/rag/build_index.py` | document / chunk を JSONL index として `rag/indexes/` に集約する |
| `runtime/rag/embed_chunks.py` | chunk index から local sparse embedding を生成する |
| `runtime/rag/retrieve_context.py` | JSONL index と local embeddings から候補chunkを選び、圧縮済みcontext packを生成する |
| `runtime/rag/rag_dispatcher.py` | 開発前RAG読み込み用に複数queryを計画・並列検索し、圧縮済みcontext packを集約する |
| `runtime/rag/jsonize_rag_tree.py` | `rag/` 配下の非UUID JSON、JSONL、Markdown、text artifact を UUID名の JSON wrapper に変換する |

Intake example:

```powershell
python runtime/intake/intake_requirements.py --workflow new-robotics-system-development
```

Maintenance intake example:

```powershell
python runtime/intake/intake_requirements.py --workflow robotics-maintenance-development
```

## Work Directory Model

受付後は、採番IDごとに `work/<receipt-id>/` を作成します。

```text
work/
  <receipt-id>/
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
      scm-state.json
```

成果物の基本格納先:

| Directory | Purpose |
| --- | --- |
| `design-document/` | 設計書、要件定義書、architecture documents |
| `process-report/` | 比較結果、Issue draft、review report、工程ごとの report |
| `test-evidence/` | テスト証跡、実行ログ、スクリーンショット、観測結果 |
| `test-specifications/` | テスト仕様書、テストケース表 |
| `source/` | clone、差分、実装対象 source |
| `context/` | Agent間共有JSON、handoff、artifact index |

## Templates

各フローの成果物ひな形は `templates/` に置きます。

```text
templates/
  requirements/
    new-system/
    feature-maintenance/
  design-document/
  process-report/
  test-evidence/
  test-specifications/
```

`templates/requirements/` には、ロボティクス版の新システム用、および新機能/保守開発用の要件定義書テンプレートを置きます。

要件定義書には `Repository Control` 欄を必ず設け、target repository / target branch を案件ごとに指定します。

Current artifact templates:

| Directory | Template | Purpose |
| --- | --- | --- |
| `templates/design-document/` | `robotics-design-document-template.md` | 設計方針、責務境界、安全設計、test strategy を固定形式で残す |
| `templates/process-report/` | `robotics-process-report-template.md` | 各工程の入力、実行内容、判断、finding、handoff を残す |
| `templates/test-evidence/` | `robotics-test-evidence-template.md` | テスト実行条件、結果、証跡、pass / fail 判断を残す |
| `templates/test-specifications/` | `robotics-test-specification-template.md` | test strategy、test case table、entry / exit criteria を残す |

共通品質ルール:

- front matter に project、receipt_id、repository、branch、commit、workflow、phase、status を残す
- Intent、Decision、Reason、Evidence、Open QA を明示する
- safety-critical な内容では STOP、communication loss、startup safe state、shutdown safe state を確認する
- 出力先は `work/<receipt-id>/` 配下の対応ディレクトリにする
- 生成後は `work/<receipt-id>/context/artifact-index.json` に登録する

## Environment Files

GitHub / SCM 連携で必要な値は、repository root の環境ファイルで管理します。

```text
.env.example   共有可能なキー一覧
.env           ローカル実値、commit禁止
.gitignore     .env と .env.* を除外し、.env.example は追跡対象
```

`.env.example` の現行キー:

```env
GITHUB_OWNER=
GITHUB_TOKEN=
```

`.env` には token やローカル実値を書きますが、commit しません。

`GITHUB_OWNER` を設定すると、`localty-system-gui` のようなrepository名だけの指定を `<GITHUB_OWNER>/localty-system-gui` として解決できます。

案件ごとに変わる repository は `.env` に置きません。要件定義書の `Repository Control` を source of truth とします。

## Skills

`skills/` には、workflow を選択するための Skill entrypoint を置きます。

```text
skills/
  robotics-new-system/
    SKILL.md
    agents/openai.yaml
  robotics-feature-maintenance/
    SKILL.md
    agents/openai.yaml
  corrective-action-report/
    SKILL.md
    agents/openai.yaml
  skill-index.json
```

`skills/skill-index.json` は、slash command、Skill、delegated prompt、output path を対応づける index です。

### Codex Skill Discovery

`C:\github\intent-driven-robotics-ai-workflow\skills` は、この repository における Skill の source of truth です。

Codex の Skill 候補として表示するには、Codex が探索する local skill directory からも見える必要があります。

現在は以下の junction で接続します。

```text
C:\Users\User\.codex\skills\robotics-new-system
  -> C:\github\intent-driven-robotics-ai-workflow\skills\robotics-new-system

C:\Users\User\.codex\skills\robotics-feature-maintenance
  -> C:\github\intent-driven-robotics-ai-workflow\skills\robotics-feature-maintenance

C:\Users\User\.codex\skills\corrective-action-report
  -> C:\github\intent-driven-robotics-ai-workflow\skills\corrective-action-report
```

これにより、Skill 本体は workflow repository 側で管理しながら、Codex の候補にも出せます。

注意:

- repository 内の `skills/` に置くだけでは、Codex の Skill 候補に自動表示されない場合があります
- 新しい Codex session で候補に出ない場合は、Codex / VS Code の reload が必要な場合があります
- VS Code Copilot Chat の `/` 候補は `.github/prompts/*.prompt.md`、Codex Skill 候補は `C:\Users\User\.codex\skills` が主な探索対象です

## Workflow Prompts

`.github/prompts/` には、`/xxxxx` 形式で呼び出すことを想定した workflow prompt を置きます。

Current prompts:

- `/robotics-workflow`
- `/robotics-new-system`
- `/robotics-feature-maintenance`
- `/corrective-action-report`
- `/corrective-action-fix`
- `/pre-development-preparation`
- `/new-robotics-system-development`
- `/robotics-maintenance-development`
- `/robotics-safety-gates`
- `/robotics-test-strategy`
- `/robotics-release-and-field-operation`

`/robotics-new-system` と `/robotics-feature-maintenance` は薄い entrypoint で、詳細はそれぞれ `/new-robotics-system-development` と `/robotics-maintenance-development` へ委譲します。

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

Agent は、単に成果物を作るだけではなく、次のAgentと人間が判断を継続できるように、context、decision、reason、evidence、risk、open QA を残します。

## Shared JSON Schema

`.github/schemas/` には、Agent間で情報連携するための JSON Schema を置きます。

JSON Schema は、実データそのものではなく、共有JSONの構造を定義する contract です。

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
- `rag-document.schema.json`
- `rag-chunk.schema.json`
- `rag-embedding.schema.json`
- `rag-retrieval-result.schema.json`
- `rag-context-pack.schema.json`

これにより、Agentやtoolが以下を structured data として扱いやすくなります。

- project / workflow / safety context
- artifact index
- decision record
- review finding
- QA
- test evidence
- handoff package
- task plan / task result
- SCM state
- GitHub Issue
- commit record

## Shared Rules

`.github/shared/` には、すべてのAgentが共通で参照する判断ルールを置きます。

- `localty-principles.md`
- `risk-and-severity.md`
- `artifact-management.md`
- `agent-handoff.md`

## Data Sharing Model

現時点では、JSON DB ではなく file-based shared memory として扱います。

Schema は `.github/schemas/` に置き、実データは project ごとの作業領域に保存します。

```text
work/<receipt-id>/context/*.json
```

将来的には、SQLite、DuckDB、PostgreSQL、vector DB、workflow engine の state store へ移行できます。

## RAG / Knowledge Capture

現場で得た発見、incident、review escape、design decision は、未来のAgentに役立つ可能性があります。

一時知識:

```text
knowledge-inbox/
  investigations/
  improvement-reports/
  field-notes/
```

改善点レポート:

```text
rag/
  corrective-action-report/
  normalized/
  chunks/
  indexes/
  embeddings/
  retrieval/
```

`rag/corrective-action-report/` は、`/corrective-action-report` によって作成された repository / branch 改善レポートの保存先です。

RAG化する前提で、可能な限り front matter、project、repository、branch、commit、type、status、created_at、source、tags、evidence、open questions を残します。

## RAG Pipeline

RAG は「作成」と「読み込み」を分けます。

- `/rag-build`: レビューや改善レポートを file-based RAG の中間形式へ変換する
- `/rag-load`: 開発前に RAG を検索し、圧縮済み context pack を読み込む

いきなり vector DB に投入せず、まず file-based RAG の中間形式へ変換します。

```text
source markdown
  -> normalized JSON document
  -> chunk JSON
  -> JSONL indexes
  -> local embeddings
  -> compressed JSON context pack
```

### RAG Build

標準コマンド:

```powershell
python runtime/rag/normalize_documents.py `
  --source-dir rag/corrective-action-report `
  --output-dir rag/normalized `
  --document-type corrective-action-report `
  --clean-output

python runtime/rag/chunk_documents.py `
  --input-dir rag/normalized `
  --output-dir rag/chunks `
  --clean-output

python runtime/rag/build_index.py `
  --normalized-dir rag/normalized `
  --chunks-dir rag/chunks `
  --output-dir rag/indexes

python runtime/rag/embed_chunks.py `
  --chunks-index rag/indexes/chunks.jsonl `
  --output rag/embeddings/chunks-embeddings.jsonl

python runtime/rag/jsonize_rag_tree.py `
  --rag-dir rag `
  --output-dir rag/jsonized `
  --clean-output
```

### RAG Load

開発前に、task context から 3〜5 個の検索クエリを作り、可能なら並列に retrieval します。

標準では `runtime/rag/rag_dispatcher.py` を使います。RAG 圧縮は `runtime/rag/retrieve_context.py` の既存 context pack 生成を使います。

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "MainWindow 分割 Qt smoke test" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

主な出力:

| Path | Purpose |
| --- | --- |
| `rag/normalized/*.json` | Markdown report を metadata 付き document に変換したもの |
| `rag/chunks/*.json` | retrieval / embeddings 用の chunk |
| `rag/indexes/documents.jsonl` | document-level index |
| `rag/indexes/chunks.jsonl` | chunk-level index |
| `rag/embeddings/chunks-embeddings.jsonl` | local sparse embedding index |
| `rag/jsonized/*.json` | 既存の非UUID JSON、JSONL、Markdown、text RAG artifact を UUID名 JSON wrapper 化したもの |
| `rag/retrieval/<uuid>.json` (`artifact_type: rag-load-dispatch`) | 複数query retrieval の集約結果 |
| `rag/retrieval/<uuid>.json` (`artifact_type: rag-retrieval-result`) | query、selected chunks、dropped chunks、filter条件 |
| `rag/retrieval/<uuid>.json` (`artifact_type: rag-context-pack`) | Agent投入用の圧縮済みcontext pack |

Markdown出力はデバッグ用途です。必要な場合だけ `--write-markdown` を指定します。

この段階では JSONL index として扱い、将来的に OpenAI embeddings、SQLite、DuckDB、PostgreSQL + pgvector、FAISS、Chroma へ移行できます。

この repository の local workflow では、deterministic な keyword retrieval、local embedding cosine similarity、hybrid reranking、extractive compression までを扱います。

Vector DB、provider-based embeddings、高度な semantic search、reranking model は、将来の MCP repository 側で担当します。

## Commit Rule

成果物とsource差分は作業branchに commit します。

Branch naming:

```text
feature/issue-<issue-number>
```

Semantic commit examples:

```text
feat: add remote gateway skeleton
fix: correct telemetry timeout handling
docs: update robotics safety gate
test: add communication loss regression
chore: update workflow skill index
```

許可するtype:

- feat
- fix
- docs
- style
- refactor
- test
- chore
- build
- ci
- perf
- revert

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Status

この repository は、Localty の robotics workflow を試行錯誤しながら育てる foundation です。

現在は以下が整備済みです。

- 新システム作成 Skill
- 新機能開発・保守開発 Skill
- 改善点レポート Skill
- 要件定義書 intake harness
- 1要件定義書 = 1受付ID の受領ルール
- repository fallback を使わない Repository Control 方針
- runtime/scm の GitHub Issue / branch / commit 補助
- sequential / parallel task runner
- Agent間共有用 JSON Schema
- corrective action report の RAG 保存先
- file-based RAG pipeline
- local context compression
- local embeddings / hybrid reranking

より詳細な命名規則、採番ルール、承認済みartifactの保管ポリシーは、今後の運用に合わせて定義します。
