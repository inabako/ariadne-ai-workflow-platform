# Intent-Driven Robotics AI Workflow

Localty の robotics system development を、Intent、Safety、Operational Learning を中心に進めるための AI workflow repository です。

Web system の workflow をそのまま流用せず、robotics system に必要な hardware、field operation、runtime、network、operator responsibility、safety gate を含めて設計します。

この repository は、現場で学びながら、安全に試し、安全に止め、安全に戻し、学びを次の workflow / Agent / RAG に残すための foundation です。

## Quick Start

まず読む場所:

1. [docs/README.md](docs/README.md)
2. [docs/workflows/README.md](docs/workflows/README.md)
3. [docs/reference/repository-structure.md](docs/reference/repository-structure.md)

Workflow を選ぶ場合:

| やりたいこと | Entry point | Guide |
| --- | --- | --- |
| 箇条書き草案から要件定義書を作る | `/requirement-discovery` | [Requirement Discovery](docs/workflows/requirement-discovery.md) |
| 新しいrobotics systemを始める | `/robotics-new-system` | [Robotics New System](docs/workflows/robotics-new-system.md) |
| 新システム設計からShared Artifacts検証、IaC連携まで一気通貫で行う | `/robotics-new-system-iac` | [Robotics New System + IaC](docs/workflows/robotics-new-system-iac.md) |
| 既存systemの新機能追加、bug fix、保守開発を行う | `/robotics-feature-maintenance` | [Robotics Feature Maintenance](docs/workflows/robotics-feature-maintenance.md) |
| リアルタイムシステム向けIaCを設計、生成、検証、文書化する | `/realtime-iac` | [Realtime IaC](docs/workflows/realtime-iac.md) |
| repository / branchをread-onlyで調査し、改善reportを作る | `/corrective-action-report` | [Corrective Action Report](docs/workflows/corrective-action-report.md) |
| 改善reportからIssue、branch、修正、test、pushまで進める | `/corrective-action-fix` | [Corrective Action Fix](docs/workflows/corrective-action-fix.md) |
| 実装とdocsのズレを検出し、docsだけ修正する | `/docs-sync` | [Docs Sync](docs/workflows/docs-sync.md) |
| 完了IssueからPR材料、RAG候補、docs候補、archive準備を作る | `/knowledge-capture` | [Knowledge Capture](docs/workflows/knowledge-capture.md) |
| reportをRAG化する、または開発前にRAGを読む | `/rag-build`, `/rag-load` | [RAG Build / Load](docs/workflows/rag-build-load.md) |

## Core Principles

- Intent から始める。
- 実装前に責務境界を見える化する。
- 実機より前に safety gate を通す。
- simulation / bench / field を段階化する。
- STOP、rollback、observability を後回しにしない。
- 会話ログではなく artifact と evidence を残す。
- 学びを `rag/` と workflow docs に戻す。

Robotics workflow では、作れるかより先に、安全に試せるか、止められるか、戻せるか、観測できるかを確認します。

## Repository Map

```text
.github/    prompts, agents, schemas, shared rules
docs/       workflow guides and reference docs
rag/        corrective reports and file-based RAG artifacts
runtime/    workflow helper CLI
skills/     Codex Skill entrypoints
templates/  requirement, design, report, test templates
work/       per-workflow artifacts and cloned sources
```

詳しくは [Repository Structure](docs/reference/repository-structure.md) を参照してください。

## Documentation

| Area | Document |
| --- | --- |
| Docs index | [docs/README.md](docs/README.md) |
| Workflow index | [docs/workflows/README.md](docs/workflows/README.md) |
| Runtime CLI | [docs/reference/runtime.md](docs/reference/runtime.md) |
| Templates | [docs/reference/templates.md](docs/reference/templates.md) |
| Skill discovery | [docs/reference/skill-discovery.md](docs/reference/skill-discovery.md) |
| Data model | [docs/reference/data-model.md](docs/reference/data-model.md) |
| RAG | [docs/reference/rag.md](docs/reference/rag.md) |
| Operations | [docs/reference/operations.md](docs/reference/operations.md) |

## Runtime And Skills

Runtime helper CLI は `runtime/` にあります。詳細は [Runtime](docs/reference/runtime.md) と `runtime/**/README.md` を参照してください。

Skill entrypoint は `skills/` にあります。対応関係は `skills/skill-index.json` にまとめます。

`skills/` はこの repository の source of truth です。Codex候補として表示するには、必要に応じて `C:\Users\User\.codex\skills` からJunctionで接続します。詳しくは [Skill Discovery](docs/reference/skill-discovery.md) を参照してください。

## Environment

GitHub / SCM 連携で必要な値は repository root の環境ファイルで管理します。

```text
.env.example
.env
```

現行の基本キー:

```env
GITHUB_OWNER=
GITHUB_TOKEN=
```

案件ごとに変わる repository / branch は `.env` に置かず、要件定義書の `Repository Control` またはworkflow inputを source of truth にします。

## Status

この repository は、Localty の robotics workflow を試行錯誤しながら育てる foundation です。

現在は以下を整備済みです。

- 要件定義書 discovery / intake
- 新規system workflow
- 新規system + realtime IaC integrated workflow
- 新機能 / 保守開発 workflow
- リアルタイムシステム向けIaC workflow
- corrective action report / fix workflow
- docs-sync workflow
- knowledge capture workflow
- GitHub Issue / branch / commit / push補助runtime
- environment preflight
- Agent間共有JSON Schema
- artifact templates
- file-based RAG pipeline
- local context compression
- local embeddings / hybrid reranking

詳細な運用ルールは [Operations](docs/reference/operations.md) を参照してください。

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
