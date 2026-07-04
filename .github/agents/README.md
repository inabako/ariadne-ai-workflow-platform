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
| `requirement-discovery-agent.prompt.md` | 箇条書き草案の精査、Noise Reduction、深掘り質問、要件定義書レビュー草案 | `work/requirements/draft/*-noise-reduction/`, `*-questions.md`, `*-requirements-review.md` |
| `external-web-source-reviewer-agent.prompt.md` | 不足知識に対して外部Web一次情報を精査し、外部Web RAG候補へ要約する | `rag/external-web/<category>/*.md` |
| `external-web-rag-dispatcher-agent.prompt.md` | 蓄積済み外部Web RAGをカテゴリ別に検索・集約し、要件定義/設計/改善flowへ渡す | `rag/external-web/retrieval/*-aggregate.md` |
| `docs-drift-analyzer-agent.prompt.md` | 実装とdocsの差分検出、JSON化、Issue材料作成 | `work/<branch>/context/docs-drift-analysis.json` |
| `repository-discovery-agent.prompt.md` | GitHub repository識別、scan scope、collection plan作成 | `work/<work-id>/context/github-knowledge-analysis.json` |
| `github-metadata-collector-agent.prompt.md` | GitHub CLI/APIによるIssue、PR、comment、label、release収集 | `metadata_sources` |
| `knowledge-asset-discovery-agent.prompt.md` | Intent、Scope、Design Decision、Maintenance Knowledge、RAG候補抽出 | `knowledge_assets`, `rag_candidates` |
| `narrative-analyzer-agent.prompt.md` | Issue -> PR -> Review -> Comment -> Documentation の整合性検査 | `narrative_gaps` |
| `documentation-repair-agent.prompt.md` | Issue/PR/CAR/README/docs/ADR補足案作成 | `github-knowledge-repair-plan-*.md` |
| `github-documentation-sync-agent.prompt.md` | 承認済みrepairのGitHub CLI/API sync plan作成 | `github-documentation-sync-plan-*.md` |
| `knowledge-db-registrar-agent.prompt.md` | Knowledge DB候補とRAG候補生成 | `github-knowledge-rag-candidate-*.md` |
| `workspace-requirements-analyst-agent.prompt.md` | VSCode workspace要件、tool、extension、terminal、task整理 | `workspace-requirements.md` |
| `workspace-shared-artifact-validator-agent.prompt.md` | VSCode環境構築前の必須artifact検証 | `workspace-shared-artifact-validation.json`, `workspace-shared-artifact-validation.md` |
| `vscode-architect-agent.prompt.md` | settings/tasks/launch/extensions/workspace設計 | `vscode-design.md` |
| `terminal-architect-agent.prompt.md` | terminal profileとAI workflow terminal role設計 | `terminal-design.md` |
| `workspace-implementer-agent.prompt.md` | 承認済み設計に基づく.vscode/workspace実装 | `.vscode/*`, `workspace-implementation.md` |
| `workspace-test-agent.prompt.md` | task、terminal、launch、Docker/runtime、AI workflow起動検証 | `workspace-test.md`, `test-evidence/evidence/` |
| `workspace-documentation-writer-agent.prompt.md` | VSCode setup/troubleshooting/evidence docs整理 | README/setup docs, `workspace-documentation.md` |
| `gui-svg-analyzer-agent.prompt.md` | SVG構造、要素、領域、GUI責務の解析 | `gac-uac/svg-analysis.md` |
| `gui-semantic-layout-agent.prompt.md` | SVG解析からPyQt非依存のSemantic Layout Graph生成 | `gac-uac/semantic-layout-graph.yaml` |
| `gui-widget-mapping-agent.prompt.md` | Semantic LayoutをPyQt6 Widget、class、signal、test対象へ写像 | `gac-uac/widget-mapping.md` |
| `gui-layout-spec-agent.prompt.md` | SYS / FEAT / FIX別の実装可能Layout仕様作成 | `gac-uac/layout-spec.md` |
| `gui-pyqt6-generator-agent.prompt.md` | 外部I/OなしのPyQt6候補生成 | `gac-uac/generated/pyqt6/` |
| `gui-qtest-generator-agent.prompt.md` | offscreen実行可能なQTest smoke候補生成 | `gac-uac/generated/tests/test_gui_smoke.py` |
| `web-svg-layout-mode.prompt.md` | SVGからWeb route、component、responsive layout、React候補、Playwright候補を生成 | `web-ui/` |
| `robotics-architect-agent.prompt.md` | システム構造と責務境界 | `architecture.md` |
| `shared-artifact-validator-agent.prompt.md` | 新システム設計成果物をIaC投入可能なShared Artifactsとして検証 | `shared-artifact-validation.md`, `shared-artifact-validation.json` |
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
| `workflow-help-curator-agent.prompt.md` | aiwfctl help registry、schema、docs、testsの同期確認と検索性改善 | `workflow-help-curation-report.md`, `runtime/registries/workflow_help.json` |
| `python-runtime-specialist-agent.prompt.md` | Python runtime / PyQt / pytest / socket lifecycle の専門review | `specialist-review-python-runtime.md` |
| `go-realtime-gateway-specialist-agent.prompt.md` | Go realtime gateway / goroutine / context / net の専門review | `specialist-review-go-realtime-gateway.md` |
| `network-realtime-protocol-specialist-agent.prompt.md` | UDP/TCP/QUIC/NAT/packet evidence の専門review | `specialist-review-network-protocol.md` |
| `video-pipeline-specialist-agent.prompt.md` | GStreamer / video receiver / latency / video loss の専門review | `specialist-review-video-pipeline.md` |
| `observability-telemetry-specialist-agent.prompt.md` | logs / metrics / telemetry / incident traceability の専門review | `specialist-review-observability.md` |
| `platform-deployment-specialist-agent.prompt.md` | Windows/Linux/Raspberry Pi/MSYS2/Docker/startup の専門review | `specialist-review-platform-deployment.md` |
| `test-fault-injection-specialist-agent.prompt.md` | pytest / Go test / fault injection / packet evidence の専門review | `specialist-review-testing.md` |
| `security-remote-access-specialist-agent.prompt.md` | VPN / tunnel / auth / operator authority / secrets の専門review | `specialist-review-remote-security.md` |
| `safety-control-specialist-agent.prompt.md` | STOP / communication loss / safe state / watchdog の専門review | `specialist-review-safety-control.md` |
| `iac-requirements-agent.prompt.md` | IaC共有成果物とインフラ要件の整理、open questions抽出 | `requirements.md`, `open-questions.md` |
| `iac-network-security-design-agent.prompt.md` | realtime IaCのnetwork/security/firewall設計 | `network-design.md`, `security-design.md`, `firewall-policy.md` |
| `iac-runtime-design-agent.prompt.md` | Docker Compose、systemd、startup、restart、health check設計 | `runtime-design.md`, `docker-compose-design.md` |
| `iac-observability-design-agent.prompt.md` | logs、metrics、monitoring、logrotate、evidence設計 | `observability-design.md`, `monitoring-policy.md` |
| `iac-implementer-agent.prompt.md` | 承認済み設計からIaC artifactsを生成 | IaC artifacts, `iac-implementation.md` |
| `iac-security-review-agent.prompt.md` | generated IaCのsecret/exposure/privilege/firewall review | `security-review.md` |
| `iac-docker-desktop-test-agent.prompt.md` | Docker Desktop上のcompose/config/startup/health/port/log検証 | `docker-test-plan.md`, `docker-test-result.md` |
| `iac-linux-runtime-test-agent.prompt.md` | Linux上のsystemd/firewall/logrotate/service検証 | `runtime-validation.md` |
| `iac-integration-test-agent.prompt.md` | control/video/telemetry/gateway疎通と復旧確認 | `integration-test.md` |
| `iac-documentation-agent.prompt.md` | IaC運用docs、setup、troubleshooting、network overview整理 | README, setup/operation docs |

## 推奨フロー

詳細な開発フローは `.github/prompts/` を参照してください。
Agent間の共通schemaは `.github/schemas/`、共通判断ルールは `.github/shared/` を参照してください。

```text
draft bullets
  -> requirement discovery
  -> noise reduction phase before requirement review draft
  -> external web knowledge review when knowledge is insufficient
  -> external web RAG dispatch when saved external knowledge is relevant
  -> specialist review when artifact quality depends on domain depth
  -> reviewed requirements
  -> corrective action report / fix with external web as supporting reference when needed
  -> docs drift analysis when docs sync is requested
  -> GitHub knowledge maintenance when Issue / PR / docs / CAR explanation assets need repair
  -> robotics architect
  -> robotics runtime agent
  -> network migration planner
  -> remote gateway architect
  -> deployment architect
  -> shared artifact validator when new-system output feeds IaC
  -> claim prefixed SVG from work/requirements/svg-input and run GaC / UaC GUI agents
  -> run Web SVG Layout Mode when WEB_* SVG exists
  -> safety / security / network / observability reviews
  -> robotics tester
  -> realtime IaC agents when IaC is in scope
  -> boilerplate template selection before implementation
  -> implementer
  -> documentation writer
  -> knowledge capture
  -> knowledge-inbox / RAG
```

reviewで未解決QAが出た場合は、architecture または requirements へ戻します。

Specialist Agent一覧と採用条件は `docs/reference/agent-inventory.md` を参照してください。

Specialist reviewを使った場合は、採用した外部Web RAG、採用しなかったclaim、current evidence、必要なtest evidenceをreview結果に残します。

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
- boilerplate template responsibility boundaries
- IaC boilerplate gates for shared artifacts, software inventory, exposure, secrets, firewall policy, rollback, and Terraform validation

実装中に曖昧さが見つかった場合は、QAとして返します。

新システム実装で `templates/boilerplates/` に対象templateが存在する場合、Implementer はtemplateをコピーしてコピー先だけを編集します。対象templateが存在しない組み合わせでは、選定reportに理由を残して従来どおりcodingします。

IaC実装で realtime gateway infrastructure が対象に含まれる場合、Implementer は `realtime-gateway-infra-template/` を候補にし、採用時はコピー先だけを編集します。template採用時も、Shared Artifacts、software inventory、public exposure、secret source、firewall policy、rollback、Terraform validationを省略しません。

## RAG Capture Rule

現場で得た発見、incident、review escape、design decision は、未来のAgentに役立つ可能性があります。Markdownで残す場合は front matter を付けます。

専門Agentのreview結果もRAG候補です。作業中は次に保存します。

```text
work/<id>/process-report/specialist-review-<domain>.md
```

RAG登録承認後、必要に応じて次へ吸収します。

```text
rag/specialist-review/<domain>/
```

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
