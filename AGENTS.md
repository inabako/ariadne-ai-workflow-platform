# Ariadne AI Workflow: Agent Guide

このリポジトリは、Localty の対象システム開発を Intent、Safety、Operational Learning を中心に進めるための AI workflow repository です。

Agent は、単に成果物を作るだけではなく、次のAgentと人間が判断を継続できるように、context、decision、reason、evidence、risk、open QA を残してください。

## Core Principles

- 仕組みより Intent
- 便利さより安全
- 美しさより運用可能性
- 自信より証拠
- 実装前に責務境界
- 現場学習をRAG知識として残す

Ariadne workflow では、実装できたかより先に、安全に試せるか、安全に止められるか、安全に戻せるかを確認します。

## Ariadne Responsibility

Ariadne は、AI Agent が迷わず作業を進めるために、workflow の入口、context、decision、evidence、Human Check、handoff を管理します。

- 会話ログではなく、後続Agentと人間が読める artifact を残す。
- 対象システムの責務境界、risk、test evidence を先に見える化する。
- GitHub Issue、branch、push、install、RAG公開などの副作用は Human Check で分離する。
- workflow 中に摩擦や不足を見つけた場合は、Ariadne 自身の改善候補として保存する。

## Directory Roles

```text
.ariadne/
  agents/      role-based Agent prompts
  prompts/     slash command style workflow prompts
  schemas/     JSON Schema contracts for Agent-to-Agent data sharing
  shared/      common rules, principles, handoff guidance

.github/
  workflows/   GitHub Actions workflows
  ISSUE_TEMPLATE/
  PULL_REQUEST_TEMPLATE/
  copilot-instructions.md
               thin VS Code Copilot bridge into AGENTS.md and .ariadne/
  instructions/
               thin VS Code Copilot custom instruction bridge
  prompts/     thin VS Code Copilot prompt stubs only

knowledge-inbox/
  investigations/
  improvement-reports/
  field-notes/

work/          project-specific artifact and source work area
work/requirements/
               completed requirement documents waiting for intake
work/requirements/draft/
               human bullet-list drafts for requirement discovery
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
  workflow/    initialize workflow contexts and create workflow-level handoff artifacts
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

Workflow prompts live in `.ariadne/prompts/`.

Current prompt set:

- `/ariadne-workflow`
- `/requirement-discovery`
- `/docs-sync`
- `/github-knowledge-maintenance`
- `/vscode-environment`
- `/ariadne-new-system`
- `/ariadne-feature-maintenance`
- `gac-uac-gui-mode` (parent workflow extension; not a standalone Skill)
- `/corrective-action-report`
- `/corrective-action-fix`
- `/pre-development-preparation`
- `/rag-build`
- `/rag-load`
- `/ariadne-new-system-development`
- `/ariadne-feature-maintenance-development`
- `/ariadne-safety-gates`
- `/ariadne-test-strategy`
- `/ariadne-release-and-field-operation`

Role-based Agent prompts live in `.ariadne/agents/`.

Workflow Skill entrypoints live in `skills/`.

Current Skill entrypoints:

- `/requirement-discovery` -> `skills/requirement-discovery/SKILL.md` -> `work/requirements/draft/`, then `work/requirements/` after human OK
- `/docs-sync` -> `skills/docs-sync/SKILL.md` -> `work/<target-branch>/context/docs-drift-analysis.json`, then docs-only `feature/issue-<number>`
- `/github-knowledge-maintenance` -> `skills/github-knowledge-maintenance/SKILL.md` -> `work/github-knowledge-<repository>-<mode>/context/github-knowledge-analysis.json`, then approval-gated GitHub documentation sync and RAG candidates
- `/vscode-environment` -> `skills/vscode-environment/SKILL.md` -> `work/<work-id>/`, `.vscode/*`, optional `workspace.code-workspace`
- `/ariadne-new-system` -> `skills/ariadne-new-system/SKILL.md` -> `/ariadne-new-system-development`
- `/ariadne-feature-maintenance` -> `skills/ariadne-feature-maintenance/SKILL.md` -> `/ariadne-feature-maintenance-development`
- `/corrective-action-report` -> `skills/corrective-action-report/SKILL.md` -> `rag/corrective-action-report/`
- `/corrective-action-fix` -> `skills/corrective-action-fix/SKILL.md` -> `work/<branch>/`, `work/issue-<issue-number>/`, `feature/issue-<issue-number>`
- `/rag-build` -> `skills/rag-build/SKILL.md` -> `rag/normalized/`, `rag/chunks/`, `rag/indexes/`, `rag/embeddings/`
- `/rag-load` -> `skills/rag-load/SKILL.md` -> `rag/retrieval/<uuid>.json`

GaC / UaC GUI Mode is not a standalone Skill entrypoint. Before Issue creation, SVG files are placed under `work/requirements/svg-input/` with `SYS_`, `FEAT_`, or `FIX_` prefixes. After the Issue work area exists, the three implementation workflows claim matching files and dispatch `.ariadne/prompts/gac-uac-gui-mode.prompt.md`.

`/corrective-action-report` を使う場合は、対象repositoryと対象branchを user に確認してから read-only review を開始してください。未指定の場合は必ず入力を求めます。

## Shared Data Contract

Agent間の情報連携フォーマットは `.ariadne/schemas/*.schema.json` で定義します。

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
- `docs-drift-analysis.schema.json`
- `github-knowledge-analysis.schema.json`
- `gui-mode-state.schema.json`
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

共通判断ルールは `.ariadne/shared/` を参照してください。

- `localty-principles.md`
- `risk-and-severity.md`
- `artifact-management.md`
- `agent-handoff.md`
- `output-language-policy.md`

## Output Language

人間向けのreport、document、review、evidence、RAG source Markdownは、既定で日本語で出力します。

source code、identifier、command、file path、URL、API名、GitHub / VSCode / Docker などの固有名詞は英語のままでかまいません。見出し、要約、判断理由、Human Review、Next Action は日本語で書きます。

Markdown source artifact の front matter には、可能な限り `language: ja-JP` を入れてください。

生成後は、必要に応じて次を実行して英語主体の成果物を検出します。

```powershell
uv run --project runtime python runtime/workflow/validate_output_language.py `
  --paths work rag docs `
  --fail-on-violation
```

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

`templates/artifacts/requirements/` の要件定義書には `Repository Control` 欄を設けます。

`work/requirements/draft/` は未完成の箇条書き草案置き場です。`/requirement-discovery` では、Critical items が未確定の場合に設計や実装案を推測せず、人間へ質問してください。完成版は人間レビュー OK 後にのみ `work/requirements/` へ保存します。

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
runtime/workflow/init_corrective_action_fix.py
runtime/retrieval/task_runner.py
runtime/scm/prepare_repository.py
runtime/scm/compare_requirements.py
runtime/github/issue_manager.py
runtime/scm/create_issue_branch.py
runtime/scm/commit_changes.py
runtime/scm/push_branch.py
runtime/rag/normalize_documents.py
runtime/rag/chunk_documents.py
runtime/rag/build_index.py
runtime/rag/embed_chunks.py
runtime/rag/retrieve_context.py
```

新規機能および保守開発では、開発本体へ入る前に `/pre-development-preparation` と `/rag-load` を通してください。

`/docs-sync` では、`work/<target-branch>` を read-only の分析用 checkout とし、実装と `docs/` の差分を `work/<target-branch>/context/docs-drift-analysis.json` に保存してから Issue 化してください。docs 修正は `work/issue-<issue-number>/source/repository/docs` のみで行い、実装コードは変更しません。

標準準備工程:

```text
1. GitHubからtarget branchを取得
2. 要件定義書とrepository stateを比較
3. 修正内容をGitHub Issueへ記載
4. Issue番号からGitHub上に feature/issue-<issue-number> branchを作成し、work配下へclone / checkout
5. `/rag-load` で過去の corrective action report を並列検索し、圧縮済みcontext packを読み込む
6. 開発工程
7. 成果物とsource差分をsemantic commitでcommit
```

Corrective action fix flow:

```text
1. /corrective-action-fix <repository> <branch>
2. prepare base checkout under work/<branch>/source/repository
3. corrective-action-report
4. /rag-build
5. /rag-load
6. GitHub Issue draft/create
7. create feature/issue-<issue-number> on GitHub, then clone / checkout it under work/issue-<issue-number>/source/repository
8. implement corrective changes in work/issue-<issue-number>
9. create/run unit tests
10. startup/integration check
11. human check
12. push feature/issue-<issue-number>
```

この flow では、startup/integration check の人間確認が `approved` になるまで push しないでください。
`work/issue-<issue-number>` は作業フォルダ名、`feature/issue-<issue-number>` は Git branch 名として扱ってください。
`ariadne-ai-workflow-platform` は workflow/RAG/report の管理repositoryであり、この flow の push 対象にしないでください。push するのは、user が step 1 で指定した repository の `work/issue-<issue-number>/source/repository` にある `feature/issue-<issue-number>` branch だけです。
`work/<branch>` または `work/issue-<issue-number>` が既に存在する場合は、既存の原本または作業フォルダがあるため停止し、user に確認してください。確認済みで再利用する場合のみ `--reuse-existing` を使ってください。

重いtaskや独立したreview taskは、`task-plan.schema.json` に沿ってtask planを作成し、`runtime/retrieval/task_runner.py` で sequential / parallel に処理してください。

review report や corrective action report を RAG 作成する場合は `/rag-build` を使い、以下を順に実行してください。

```text
runtime/rag/normalize_documents.py
  -> runtime/rag/chunk_documents.py
  -> runtime/rag/build_index.py
  -> runtime/rag/embed_chunks.py
```

RAG source は `rag/corrective-action-report/`、変換後のJSONは `rag/normalized/`、chunkは `rag/chunks/`、indexは `rag/indexes/`、local embeddingは `rag/embeddings/`、圧縮済みcontext packは `rag/retrieval/` に保存します。

開発前の RAG 読み込みは `/rag-load` を使います。`/rag-load` は `runtime/rag/rag_dispatcher.py` を実行します。dispatcher は 3〜5 個の検索クエリを作り、可能なら `runtime/rag/retrieve_context.py` を並列実行します。圧縮は `retrieve_context.py` が生成する `artifact_type: rag-context-pack` の `rag/retrieval/<uuid>.json` を利用し、集約結果を `artifact_type: rag-load-dispatch` の `rag/retrieval/<uuid>.json` に保存します。

RAG artifact のファイル名は UUID とし、検索はファイル名ではなく JSON の `content` と metadata を対象にしてください。Markdown出力はデバッグ用で、必要な場合だけ `--write-markdown` を使います。

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
