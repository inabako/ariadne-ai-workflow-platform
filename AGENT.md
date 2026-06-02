# Intent-Driven Robotics AI Workflow: Agent Guide

このリポジトリは、Localty の robotics system development を Intent、Safety、Operational Learning を中心に進めるための AI workflow repository です。

Agent は、単に成果物を作るだけではなく、次のAgentと人間が判断を継続できるように、context、decision、reason、evidence、risk、open QA を残してください。

## Core Principles

- 仕組みより Intent
- 便利さより安全
- 美しさより運用可能性
- 自信より証拠
- 実装前に責務境界
- 現場学習をRAG知識として残す

Robotics workflow では、実装できたかより先に、安全に試せるか、安全に止められるか、安全に戻せるかを確認します。

## Directory Roles

```text
.github/
  agents/      role-based Agent prompts
  prompts/     slash command style workflow prompts
  schemas/     JSON Schema contracts for Agent-to-Agent data sharing
  shared/      common rules, principles, handoff guidance

knowledge-inbox/
  investigations/
  improvement-reports/
  field-notes/

work/          project-specific artifact and source work area
work/requirements/
               completed requirement documents waiting for intake
rag/           future RAG-ready knowledge area
runtime/       workflow runtime functions
skills/        workflow skill assets
templates/     reusable artifact templates
```

Runtime functions:

```text
runtime/
  common/      shared runtime utilities
  intake/      move submitted requirements into work/<採番ID>/ and initialize context
  retrieval/   retrieve context/artifacts and support sequential or parallel task execution
  scm/         prepare repository, compare requirements, create issue branch, commit changes
  github/      create GitHub Issue draft or issue
  rag/         normalize reports, create chunks, and build file-based RAG indexes
```

Environment files:

```text
.env.example   shareable GitHub / SCM setting keys
.env           local secrets and machine-specific values, never commit
.gitignore     excludes .env and .env.*
```

Runtime は `runtime/common/env.py` を通じて `.env` を読み込みます。

GitHub token、account、repository、git user config などの実値を prompt、schema、source code に直接書かないでください。

案件ごとに変わる repository は、要件定義書の `Repository Control` に必ず記載します。repository が読み取れない要件定義書は intake で受領しません。

## Prompt Usage

Workflow prompts live in `.github/prompts/`.

Current prompt set:

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

Role-based Agent prompts live in `.github/agents/`.

Workflow Skill entrypoints live in `skills/`.

Current Skill entrypoints:

- `/robotics-new-system` -> `skills/robotics-new-system/SKILL.md` -> `/new-robotics-system-development`
- `/robotics-feature-maintenance` -> `skills/robotics-feature-maintenance/SKILL.md` -> `/robotics-maintenance-development`
- `/corrective-action-report` -> `skills/corrective-action-report/SKILL.md` -> `rag/corrective-action-report/`

`/corrective-action-report` を使う場合は、対象repositoryと対象branchを user に確認してから read-only review を開始してください。未指定の場合は必ず入力を求めます。

## Shared Data Contract

Agent間の情報連携フォーマットは `.github/schemas/*.schema.json` で定義します。

JSON Schema は実データそのものではなく、Agentやtoolが共有JSONを structured data として解釈・検証するための contract です。

Current schema set:

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

Agent は、次のAgentが必要とする情報を schema に沿って残してください。

特に以下を曖昧にしないでください。

- intent
- decision
- reason
- evidence
- open QA
- risk / severity
- required tests
- artifact path
- owner agent

## Shared Rules

共通判断ルールは `.github/shared/` を参照してください。

- `localty-principles.md`
- `risk-and-severity.md`
- `artifact-management.md`
- `agent-handoff.md`

## Artifact Handling

成果物のひな形は `templates/` 配下に置きます。

```text
templates/
  requirements/
  design-document/
  process-report/
  test-evidence/
  test-specifications/
```

`templates/requirements/` の要件定義書には `Repository Control` 欄を設けます。

新機能および保守開発では、target repository / target branch を要件定義書に記載し、案件ごとに可変にしてください。`.env` に repository fallback は置きません。

実案件の成果物は、採番IDごとに `work/<採番ID>/` 配下へ保存します。

```text
work/
  <採番ID>/
    design-document/
    process-report/
    test-evidence/
    test-specifications/
    source/
```

Agent は成果物を作成したら、`artifact-index.schema.json` に `path`、`type`、`status`、`owner_agent` を記録してください。

採番IDまたは保存先が未確定の場合は、以下のどちらかにしてください。

- user に保存先を確認する
- 一時保存した上で `artifact-index.schema.json` に `path` と `status: draft` を記録する

## Runtime Handling

`runtime/intake/` は、`work/requirements/` に配置された完成版要件定義書を受付ID単位の `work/<採番ID>/` へ移動し、初期contextを作成する機能に使います。

Skill や workflow prompt から作業をオーダーされても、`work/requirements/` に要件定義書が無い場合は harness で受領拒否してください。会話ログだけを根拠に intake 済みとして扱ってはいけません。

`work/requirements/` に要件定義書が複数ある場合も、どれを受け付けるべきか曖昧なため受領拒否してください。標準運用は `1 requirement file = 1 receipt ID` です。

`runtime/retrieval/` は、task を順次または並列で処理するときに、必要なcontext、artifact、handoff packageを取り出してAgentへ渡す機能に使います。

Implemented runtime CLI:

```text
runtime/intake/intake_requirements.py
runtime/retrieval/task_runner.py
runtime/scm/prepare_repository.py
runtime/scm/compare_requirements.py
runtime/github/issue_manager.py
runtime/scm/create_issue_branch.py
runtime/scm/commit_changes.py
runtime/rag/normalize_documents.py
runtime/rag/chunk_documents.py
runtime/rag/build_index.py
runtime/rag/embed_chunks.py
runtime/rag/retrieve_context.py
```

新規機能および保守開発では、開発本体へ入る前に `/pre-development-preparation` を通してください。

標準準備工程:

```text
1. GitHubからtarget branchを取得
2. 要件定義書とrepository stateを比較
3. 修正内容をGitHub Issueへ記載
4. Issue番号から feature/issue-<issue-number> branchを作成
5. 開発工程
6. 成果物とsource差分をsemantic commitでcommit
```

重いtaskや独立したreview taskは、`task-plan.schema.json` に沿ってtask planを作成し、`runtime/retrieval/task_runner.py` で sequential / parallel に処理してください。

review report や corrective action report を RAG 化する場合は、以下を順に実行してください。

```text
runtime/rag/normalize_documents.py
  -> runtime/rag/chunk_documents.py
  -> runtime/rag/build_index.py
  -> runtime/rag/embed_chunks.py
  -> runtime/rag/retrieve_context.py
```

RAG source は `rag/corrective-action-report/`、変換後のJSONは `rag/normalized/`、chunkは `rag/chunks/`、indexは `rag/indexes/`、local embeddingは `rag/embeddings/`、圧縮済みcontext packは `rag/retrieval/` に保存します。

この local workflow では keyword retrieval、local embedding cosine similarity、hybrid reranking、extractive compression までを扱います。Vector DB、provider-based embeddings、高度な semantic search、reranking model は将来の MCP repository 側で担当します。

## Safety Rules

以下が未定義または未回答の場合、実装・field trial・releaseへ進めないでください。

- STOP / emergency stop behavior
- communication loss behavior
- startup safe state
- shutdown safe state
- safety-critical QA
- rollback plan for high / critical risk changes
- field trial stop condition

## Handoff Rule

Agent間のhandoffでは、`handoff-package.schema.json` に沿って、最低限以下を残してください。

- from agent / to agent
- workflow / phase
- intent
- summary
- decisions
- artifacts
- open questions
- risks
- required next actions
- stop conditions

Handoff は単なる要約ではありません。次のAgentが同じ文脈を再探索せず、判断の続きから始めるための context package です。

## RAG Capture

現場で得た発見、incident、review escape、design decision は、未来のAgentに役立つ可能性があります。

一時知識は以下へ保存します。

```text
knowledge-inbox/
  investigations/
  improvement-reports/
  field-notes/
```

RAG化する前提で、可能な限り front matter、project、type、status、created_at、source、tags を残してください。

RAG pipeline の標準出力:

```text
rag/
  corrective-action-report/
  normalized/
  chunks/
  indexes/
  embeddings/
  retrieval/
```
