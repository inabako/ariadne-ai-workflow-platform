# Agent Inventory

このページは、既存Agentの責務、RAG利用、外部Web RAG利用、専門性の不足を棚卸しするための一覧です。

目的:

- 既存Agentで足りている領域を確認する。
- 新しい専門Agentを追加すべき領域を見極める。
- 外部Web RAGを読むべきAgentと、読んではいけない判断境界を明確にする。
- 専門Agentのreview結果を、次回以降の内部RAGとして再利用できる形にする。
- role overlap と depth gap を見つける。

## Inventory Columns

| Column | Meaning |
| --- | --- |
| Agent | `.github/agents/` 配下のprompt file |
| Type | `full-stack`, `reviewer`, `implementer`, `knowledge`, `external-web` |
| Workflow Phase | 主に使う工程 |
| Responsibility | 主な責務 |
| Internal RAG Usage | 内部RAGをどう使うか |
| External Web RAG Usage | 外部Web RAGをどう使うか |
| Decision Authority | そのAgentが決めてよいこと |
| Missing Depth / Escalation | 不足しやすい専門領域と移譲先 |
| Main Outputs | 代表的な成果物 |

## Agent Inventory

| Agent | Type | Workflow Phase | Responsibility | Internal RAG Usage | External Web RAG Usage | Decision Authority | Missing Depth / Escalation | Main Outputs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `requirement-discovery-agent.prompt.md` | full-stack | 要件定義 | 草案精査、質問、要件レビュー草案 | 過去finding、risk、test gapを補助参照 | 知見不足領域の質問品質向上に使う | 完成版保存前のreview draft作成まで。Critical item確定は人間 | Python / Go / Network / GStreamerなどは専門source reviewerへ | `*-inspection.md`, `*-knowledge-gaps.md`, `*-questions.md`, `*-requirements-review.md` |
| `docs-drift-analyzer-agent.prompt.md` | reviewer | docs-sync | 実装とdocsの差分分析 | 過去docs driftや運用知見を補助参照 | 公式docsとの一般論確認に限定 | docs drift itemの分析。実装変更は不可 | API / platform仕様は専門source reviewerへ | `docs-drift-analysis.json` |
| `repository-discovery-agent.prompt.md` | knowledge | github-knowledge-maintenance | repository識別、scan scope、clone可否、collection plan作成 | 過去workflow運用知見を補助参照 | 原則不要 | collection plan作成まで。GitHub mutationやclone承認は不可 | repository ownership不明時は人間へ確認 | `github-knowledge-analysis.json` |
| `github-metadata-collector-agent.prompt.md` | knowledge | github-knowledge-maintenance | GitHub CLI/APIでIssue、PR、comment、label、releaseなどを収集 | 過去収集ルールを補助参照 | 原則不要 | read-only collectionまで。mutation不可 | GitHub APIで取れない情報はclone承認へエスカレーション | `metadata_sources` |
| `knowledge-asset-discovery-agent.prompt.md` | knowledge | github-knowledge-maintenance | Intent、Scope、Design Decision、Maintenance Knowledge、RAG候補を抽出 | 過去CAR/RAGを補助参照 | 原則不要 | knowledge asset candidate作成まで。repair決定は不可 | 根拠不足時はlow confidence / open question | `knowledge_assets`, `knowledge_db_candidates`, `rag_candidates` |
| `narrative-analyzer-agent.prompt.md` | reviewer | github-knowledge-maintenance | Issue -> PR -> Review -> Comment -> Documentation の整合性検査 | 過去narrative gapやreview escapeを参照 | 原則不要 | narrative gap分類まで。歴史の書き換え不可 | 矛盾がある場合は人間へ確認 | `narrative_gaps` |
| `documentation-repair-agent.prompt.md` | knowledge | github-knowledge-maintenance | Issue/PR/CAR/README/docs/ADR補足案を生成 | 類似repair proposalを補助参照 | 原則不要 | proposal作成まで。GitHub mutation不可 | target不明時はopen question | `github-knowledge-repair-plan-*.md` |
| `github-documentation-sync-agent.prompt.md` | knowledge | github-knowledge-maintenance | 承認済みrepairをGitHub CLI/API sync planへ変換 | 過去GitHub sync運用を補助参照 | 原則不要 | approved actionだけ実行可。Git履歴変更不可 | command差異は再reviewへ戻す | `github-documentation-sync-plan-*.md` |
| `knowledge-db-registrar-agent.prompt.md` | knowledge | github-knowledge-maintenance | Knowledge DB候補とRAG候補を生成し、承認後にRAG publication | 既存RAG taxonomyを参照 | 原則不要 | candidate作成まで。publicationは人間承認後 | raw dump化しそうな内容は要約へ戻す | `github-knowledge-rag-candidate-*.md` |
| `gui-svg-analyzer-agent.prompt.md` | full-stack | GaC / UaC GUI Mode | SVG構造、要素、領域、GUI責務を解析 | 既存GUI findingを補助参照 | 原則不要 | SVGから観測できる構造の分析まで | 業務状態遷移は親workflowへ | `svg-analysis.md` |
| `gui-semantic-layout-agent.prompt.md` | full-stack | GaC / UaC GUI Mode | PyQt非依存のSemantic Layout Graphを生成 | 既存GUI構造を補助参照 | 原則不要 | areas/widgets/relationships候補作成 | controller API確定は親workflowへ | `semantic-layout-graph.yaml` |
| `gui-widget-mapping-agent.prompt.md` | full-stack | GaC / UaC GUI Mode | PyQt6 Widget、class、signal、test対象へ写像 | 既存Widget/test patternを参照 | PyQt公式情報の補助確認のみ | mapping候補作成 | 既存architecture変更は親workflowへ | `widget-mapping.md` |
| `gui-layout-spec-agent.prompt.md` | full-stack | GaC / UaC GUI Mode | SYS/FEAT/FIX別のLayout仕様を作成 | 過去GUI設計と回帰findingを参照 | 原則不要 | generated候補の仕様化まで | source統合判断は親workflowへ | `layout-spec.md` |
| `gui-pyqt6-generator-agent.prompt.md` | implementer | GaC / UaC GUI Mode | LayoutとobjectNameを持つI/O-free PyQt6候補生成 | 既存code patternを参照 | PyQt公式情報の補助確認のみ | `generated/`候補作成まで | sourceへの適用はreview必須 | `generated/pyqt6/` |
| `gui-qtest-generator-agent.prompt.md` | implementer | GaC / UaC GUI Mode | offscreen GUI smoke、findChild、signal確認候補生成 | 既存test fixtureを参照 | PyQt QTest公式情報の補助確認のみ | `generated/`候補作成まで | 実I/O試験は親workflowへ | `generated/tests/test_gui_smoke.py` |
| `web-svg-layout-mode.prompt.md` | full-stack | Web SVG Layout Mode | SVGをWeb route、section、component、responsive layout、React候補、Playwright候補へ変換 | 既存Webapp準備reportと実装規約を補助参照 | 対象framework公式情報の補助確認のみ | generated候補作成まで | API/auth/env/state確定は親workflowへ | `web-ui/` |
| `ariadne-architect-agent.prompt.md` | full-stack | 設計 | system structure、責務境界、architecture | 過去設計判断、incident、corrective reportを参照 | 技術選定の制約確認に使う | architecture draft作成。安全/実装確定はreview後 | Network / Go / Python / GStreamerの深掘りは専門Agentへ | `architecture.md` |
| `ariadne-runtime-agent.prompt.md` | full-stack | runtime設計 | process model、lifecycle、restart、watchdog | runtime incident、preflight、startup知見を参照 | OS/runtime公式docs確認に使う | runtime design案作成。platform挙動の確定はtest evidence後 | Python subprocess/threading、Go context/sync、systemd/MSYS2は専門Agentへ | `runtime-design.md` |
| `network-migration-planner-agent.prompt.md` | full-stack | network計画 | LAN -> VPN -> relay -> remote ops移行計画 | 過去network issue、field noteを参照 | RFC / VPN / NAT traversal情報を参照 | migration plan作成。protocol採用はreview後 | UDP/TCP/QUIC/STUN/TURN/ICEは `network-protocol-source-reviewer` 候補 | `network-migration-plan.md` |
| `remote-gateway-architect-agent.prompt.md` | full-stack | gateway設計 | remote gatewayのサービス境界、責務分離 | remote gateway関連findingを参照 | Go / network / observability / video情報を補助参照 | gateway architecture案作成。実装仕様確定はreview後 | Go runtime、network protocol、GStreamerは専門Agentへ | `remote-gateway-architecture.md` |
| `deployment-architect-agent.prompt.md` | full-stack | deployment設計 | deployment topology、migration plan | 過去deployment / startup / preflight知見を参照 | Docker / Kubernetes / platform docsを参照 | deployment案作成。installや運用変更は人間承認後 | container network、Windows/Linux/Raspberry Piは専門Agentへ | `deployment-architecture.md` |
| `safety-reviewer-agent.prompt.md` | reviewer | safety review | STOP、communication loss、safe state、安全finding | 過去safety finding、incident、review escapeを参照 | 標準/公式docsは補助。finding確定はrepo evidence必須 | safety findingとblock判断 | domain-specific safety standard深掘りは専門Agent候補 | `safety-review.md` |
| `security-reviewer-agent.prompt.md` | reviewer | security review | remote access、auth、command authority | 過去security findingを参照 | official security docs / vendor docsを補助参照 | security findingとrequired QA | WireGuard/Tailscale/AuthN/AuthZ深掘りは専門Agent候補 | `security-review.md` |
| `network-reviewer-agent.prompt.md` | reviewer | network review | network design、latency、loss、route、authority | 過去network finding、packet evidenceを参照 | RFC / IANA / Wireshark / tunnel docsを補助参照 | network findingとtest要求 | `network-protocol-source-reviewer` を優先候補 | `network-review.md` |
| `observability-reviewer-agent.prompt.md` | reviewer | observability review | logs、metrics、traces、incident traceability | 過去incident/evidence gapを参照 | Prometheus / OpenTelemetry docsを補助参照 | observability findingとevidence要求 | `observability-source-reviewer` を候補 | `observability-review.md` |
| `ariadne-tester-agent.prompt.md` | full-stack | test設計 | test strategy、test matrix、evidence plan | 過去test gap、regression、incidentを参照 | official docsからverification pointを補助参照 | test specification案作成 | pytest / Go test / tc-netem / packet evidenceは専門Agentへ | `test-specification.md` |
| `remote-gateway-implementer-agent.prompt.md` | implementer | 実装 | 承認済みarchitectureとboilerplate selectionに基づく実装 | Issue scopeとRAG contextを参照 | unknown implementation areaのsupporting referenceとして参照 | 承認済み範囲の実装。architecture/protocol/template責務境界変更は不可 | Go runtime / Python runtime / Network / GStreamer専門Agentへ | source, tests, `implementation-report.md` |
| `documentation-writer-agent.prompt.md` | knowledge | docs化 | decision record、troubleshooting、再利用可能な知識化 | 実施済みwork artifactをRAG候補化 | 外部Webはsupporting referenceとして引用/要約 | docs draft作成。仕様確定は不可 | docs taxonomyやRAG schema変更は人間/architect確認 | docs, troubleshooting, RAG notes |
| `knowledge-capture-agent.prompt.md` | knowledge | 完了後整理 | PR資料、証跡整理、RAG/docs候補抽出、archive準備 | process/test/evidenceから内部RAG候補を抽出 | 外部WebRAG利用箇所をsupporting referenceとして記録 | push/archive/RAG登録は人間承認後 | RAG登録自動化はruntime/skill側へ | PR docs, `knowledge-capture-report.md` |
| `workflow-help-curator-agent.prompt.md` | knowledge | help maintenance / self-improvement | aiwfctl help registry、schema、docs、testsを同期し、workflow入口不足やhelp driftをFeedback reportへ整理する | 過去のhelp drift、workflow変更、運用ルールを補助参照 | 原則不要。外部仕様名の説明補助に限定 | help contractの更新案、registry/docs/tests変更案、Feedback reportとIssue body候補の整理まで。採用判断とGitHub mutationは不可 | command追加やruntime仕様変更が必要な場合はworkflow ownerへ戻す | `workflow-help-curation-report.md`, `runtime/registries/workflow_help.json`, `work/feedback/*.md` |
| `external-web-source-reviewer-agent.prompt.md` | external-web | 知見不足調査 | 外部Web一次情報をclaims/metadataへ圧縮 | 内部RAGと矛盾しないか確認 | 主担当。公式docs/RFC/vendor docsを精査 | claims作成まで。project findingや設計決定は不可 | Python/Go/Networkなどは専門source reviewer候補へ分化 | `rag/external-web/<category>/*.md` |
| `external-web-rag-dispatcher-agent.prompt.md` | external-web | RAG dispatch | 蓄積済み外部WebRAGを検索・集約 | 内部RAGより弱い補助contextとして扱う | 主担当。カテゴリ別に集約 | aggregate作成まで。Critical itemやfinding確定は不可 | 大規模化時はcategory workerへ分割 | `rag/external-web/retrieval/*-aggregate.md` |
| `python-runtime-specialist-agent.prompt.md` | specialist reviewer | specialist review | Python runtime / PyQt / pytest / socket lifecycle / pyqt-template適用の専門review | Python関連の過去finding、test gap、review escapeを参照 | Python公式docs等をsupporting referenceとして参照 | review finding、required tests、trusted external knowledgeの提示まで | architecture変更や実装は担当Agentへ戻す | `specialist-review-python-runtime.md` |
| `go-realtime-gateway-specialist-agent.prompt.md` | specialist reviewer | specialist review | Go realtime gateway / goroutine / context / net / gateway-template適用の専門review | gateway/runtime/networkの過去findingを参照 | Go公式docs、標準library docsをsupporting referenceとして参照 | review finding、required tests、trusted external knowledgeの提示まで | protocol採用や実装はarchitect/implementerへ戻す | `specialist-review-go-realtime-gateway.md` |
| `network-realtime-protocol-specialist-agent.prompt.md` | specialist reviewer | specialist review | UDP/TCP/QUIC/NAT/packet evidence の専門review | network incident、packet evidence、prior riskを参照 | RFC、IANA、vendor docsをsupporting referenceとして参照 | review finding、required tests、trusted external knowledgeの提示まで | project finding確定にはrepo evidence必須 | `specialist-review-network-protocol.md` |
| `video-pipeline-specialist-agent.prompt.md` | specialist reviewer | specialist review | GStreamer / receiver / latency / video loss の専門review | video/runtime/GUI findingを参照 | GStreamer docs等をsupporting referenceとして参照 | review finding、required tests、trusted external knowledgeの提示まで | pipeline変更は設計/実装Agentへ戻す | `specialist-review-video-pipeline.md` |
| `observability-telemetry-specialist-agent.prompt.md` | specialist reviewer | specialist review | logs / metrics / telemetry / incident traceability の専門review | incident、evidence gap、observability findingを参照 | OpenTelemetry / Prometheus docsをsupporting referenceとして参照 | review finding、required tests、trusted external knowledgeの提示まで | instrumentation実装はimplementerへ戻す | `specialist-review-observability.md` |
| `platform-deployment-specialist-agent.prompt.md` | specialist reviewer | specialist review | Windows/Linux/Raspberry Pi/MSYS2/Docker/startup の専門review | startup/preflight/deployment findingを参照 | platform/vendor docsをsupporting referenceとして参照 | review finding、required tests、trusted external knowledgeの提示まで | installやdeployment変更はhuman gate後 | `specialist-review-platform-deployment.md` |
| `test-fault-injection-specialist-agent.prompt.md` | specialist reviewer | specialist review | pytest / Go test / fault injection / packet evidence の専門review | test gap、regression、review escapeを参照 | testing/tool docsをsupporting referenceとして参照 | review finding、required tests、trusted external knowledgeの提示まで | test実装はtester/implementerへ戻す | `specialist-review-testing.md` |
| `security-remote-access-specialist-agent.prompt.md` | specialist reviewer | specialist review | VPN / tunnel / auth / operator authority / secrets の専門review | security finding、remote access riskを参照 | vendor/security docsをsupporting referenceとして参照 | review finding、required tests、trusted external knowledgeの提示まで | auth model採用はhuman/architect確認後 | `specialist-review-remote-security.md` |
| `safety-control-specialist-agent.prompt.md` | specialist reviewer | specialist review | STOP / communication loss / safe state / watchdog の専門review | safety finding、incident、review escapeを参照 | 外部docsは補助のみ。project safety intentを優先 | safety finding、block QA、required testsの提示まで | safety-critical未解決時はfail/conditional-pass | `specialist-review-safety-control.md` |

## Current Coverage Summary

| Area | Current Coverage | Gap |
| --- | --- | --- |
| 要件定義 | `requirement-discovery-agent` で対応済み | 技術未知領域はexternal-web / specialistへ移譲 |
| Architecture | `ariadne-architect`, `remote-gateway-architect`, `deployment-architect` で対応済み | 技術仕様の深掘りは専門source reviewerが必要 |
| Runtime | `ariadne-runtime-agent` で対応済み | Python/Go runtimeの細部は専門化候補 |
| Safety / Security / Network / Observability review | reviewer群で対応済み | RFC、protocol、observability official docsの精査専門化余地あり |
| Testing | `ariadne-tester-agent` で対応済み | pytest、Go test、tc/netem、packet evidenceの専門化余地あり |
| External Web RAG | 汎用source reviewer / dispatcherで対応済み | よく使う領域は専門source reviewer化すると品質が上がる |
| Specialist Review | safety / security / network / observability reviewerで一部対応済み | Python、Go、GStreamer、platform、test techniqueなどの深掘りreviewは候補化が必要 |
| Knowledge Capture | `knowledge-capture-agent` で対応済み | 専門review結果と「信じた外部知識」の一覧化を強化可能 |

## Specialist Agent Candidates

初期セットとして、下記のspecialist reviewer promptを `.github/agents/` に追加済みです。今後は運用頻度とreview結果を見て、追加・統合・分割します。

専門Agentは2種類に分けます。

| Type | Role | Primary Output |
| --- | --- | --- |
| source reviewer | 外部Webの一次情報をclaims / metadata / verification notesへ圧縮する | `rag/external-web/<category>/*.md` |
| specialist reviewer | 内部RAG、外部Web RAG、current evidenceを読んで、成果物の妥当性を専門観点でreviewする | `work/<receipt-id>/process-report/specialist-review-<domain>.md` |

| Candidate | Type | Trigger | Review Output | RAG Save Category | Why |
| --- | --- | --- | --- | --- | --- |
| `python-runtime-specialist-agent.prompt.md` | specialist reviewer | Python socket/threading/asyncio/subprocess/logging/venv/pytest/PyQtが成果物のriskに関わる | `specialist-review-python-runtime.md` | `rag/specialist-review/python-runtime/`, `rag/external-web/python-runtime/` | localty-system-gui系でPython runtime差分が多い |
| `go-realtime-gateway-specialist-agent.prompt.md` | specialist reviewer | Go realtime gateway、net/context/sync/time/pprof/raceが設計/実装に関わる | `specialist-review-go-realtime-gateway.md` | `rag/specialist-review/go-runtime/`, `rag/external-web/go-runtime/` | realtime gateway実装で重要 |
| `network-realtime-protocol-specialist-agent.prompt.md` | specialist reviewer | UDP/TCP/QUIC/NAT/STUN/TURN/ICE/RFCが通信仕様に関わる | `specialist-review-network-protocol.md` | `rag/specialist-review/network/`, `rag/external-web/network/` | remote gatewayとrobot通信で重要 |
| `video-pipeline-specialist-agent.prompt.md` | specialist reviewer | GStreamer pipeline、receiver、latency、codecが設計/検証に関わる | `specialist-review-video-pipeline.md` | `rag/specialist-review/video/`, `rag/external-web/video/` | GUI/video経路で重要 |
| `observability-telemetry-specialist-agent.prompt.md` | specialist reviewer | Prometheus/OpenTelemetry/log/trace/metric設計が証跡性に関わる | `specialist-review-observability.md` | `rag/specialist-review/observability/`, `rag/external-web/observability/` | evidenceとincident traceabilityで重要 |
| `platform-deployment-specialist-agent.prompt.md` | specialist reviewer | Windows/Linux/Raspberry Pi/MSYS2/Docker差分がstartup/integrationに関わる | `specialist-review-platform-deployment.md` | `rag/specialist-review/platform/`, `rag/external-web/platform/` | platform差分がstartup/integrationに影響する |
| `test-fault-injection-specialist-agent.prompt.md` | specialist reviewer | pytest/Go test/fault injection/tc-netem/packet captureが検証計画に関わる | `specialist-review-testing.md` | `rag/specialist-review/testing/`, `rag/external-web/testing/` | verification designの深みを増やす |
| `security-remote-access-specialist-agent.prompt.md` | specialist reviewer | VPN、tunnel、auth、operator authority、secret handlingがremote operationに関わる | `specialist-review-remote-security.md` | `rag/specialist-review/security/`, `rag/external-web/security/` | remote gatewayの権限境界で重要 |
| `safety-control-specialist-agent.prompt.md` | specialist reviewer | STOP、communication loss、safe state、drive zero、watchdogが成果物に関わる | `specialist-review-safety-control.md` | `rag/specialist-review/safety/` | robot固有の安全意図をreview結果として残す |

## Specialist Review Loop

専門Agentは、内部RAGと外部Web RAGを読んだあと、成果物をreviewします。review結果は作業artifactとして保存し、RAG登録承認後に内部RAGへ吸収します。

```text
internal RAG load
  -> external-web RAG dispatch when needed
  -> draft artifact
  -> specialist review
  -> artifact update / QA / tests
  -> human gate
  -> specialist review result becomes internal RAG candidate
```

保存先:

```text
work/<receipt-id>/process-report/specialist-review-<domain>.md
rag/specialist-review/<domain>/*.md
```

`work/<receipt-id>/process-report/` は作業中の一次保存先です。`rag/specialist-review/<domain>/` への登録、または `/rag-build` による吸収は人間承認後に行います。

## Trusted External Knowledge Record

専門Agentが外部Web RAGを使った場合、どの外部知識を信じたか、どの範囲では信じなかったかをreviewに残します。

```markdown
## Trusted External Knowledge

| Claim | Source RAG Path | Source URL | Trust Level | Used For | Verified By | Limits / Rejected Scope |
| --- | --- | --- | --- | --- | --- | --- |
```

記録する観点:

- accepted claim: 採用した外部知識
- rejected or limited claim: 採用しなかった、または条件付きにした外部知識
- used for: requirement、architecture、implementation plan、test specification、findingなど
- verified by: current source、unit test、integration evidence、human check、未確認なら `not-yet-verified`
- conflict: 内部RAG、current code、人間回答と矛盾した点

## Workflow Insertion Points

| Workflow | Specialist Review Trigger | Required Handling |
| --- | --- | --- |
| `/requirement-discovery` | 要件の質問品質に専門知識が必要、または未知の安全/通信/runtime領域がある | requirement review draftへRAG path、未確認事項、専門QAを残す |
| `/requirement-discovery` | 要件草案に未知用語、表記揺れ、資料矛盾、曖昧表現、AIが推測しそうな箇所がある | Noise Reduction Phaseを実行し、Readinessが`BLOCK`ならreview draftや完成版要件へ進まない |
| `/ariadne-new-system` | architecture、runtime、network、deployment、safety、test strategyの専門前提が成果物を左右する | implementation前にspecialist reviewを実行し、high/critical findingはdesignへ戻す |
| `/ariadne-new-system` | Go gateway / Next.js webapp / PyQt GUI / realtime gateway IaCなど、`templates/boilerplates/` に一致するboilerplateがある | implementation前にboilerplate selectionを記録し、templateがある場合はコピー先だけを編集する |
| `/ariadne-new-system`, `/ariadne-feature-maintenance`, `/corrective-action-fix` | Next.js dashboard / admin / monitoring / business webapp画面を実装する | implementation前にNext.js Webapp Implementation Prepを作成し、画面契約、API契約、auth、env、test evidenceを明示する |
| `/ariadne-new-system`, `/ariadne-feature-maintenance`, `/corrective-action-fix` | Web画面向けSVG layout案がある | Web SVG Layout Modeを実行し、`web-ui/`のReact / Playwright候補をreview後に採用する |
| `/ariadne-new-system-iac` | 新システム設計成果物をIaCへ渡す前に、要件、通信仕様、port、network boundary、ADR、software inventoryの整合性が成果物を左右する | Shared Artifact Validatorを実行し、`pass` または human-approved `conditional-pass` 以外ではIaCへ進めない |
| `/ariadne-feature-maintenance` | 既存挙動、STOP、network authority、runtime ownership、operator workflowへ影響する | impact analysis、change design、test planの前後でspecialist reviewを実行する |
| `/corrective-action-report` | finding品質が専門知識に依存する | external-webだけでfinding化せず、repo evidenceとspecialist reviewをsupporting referenceとして記録する |
| `/corrective-action-fix` | 実装方針、Issue scope、test specificationが専門知識に依存する | Issue作成前または実装前にspecialist reviewを実行し、採用知識と検証方法をtest evidenceへつなぐ |
| `/realtime-iac` | port / network boundary / runtime / firewall / systemd / Docker / observability / security / evidence strategyが成果物を左右する | 共有成果物gate後にIaC設計Agent群へ渡し、実装前と検証前にspecialist reviewを実行する |
| `/realtime-iac` | realtime gateway infrastructure が対象で `realtime-gateway-infra-template/` が利用可能 | IaC implementation前にboilerplate selectionを記録し、template採用時もshared artifacts、software inventory、public exposure、secret source、firewall policy、rollback、Terraform validationを省略しない |
| `/github-knowledge-maintenance` | GitHub Issue / PR / comment / docs / CAR の説明不足が未来のAI workflowやRAG再利用性に影響する | GitHub CLI/API evidenceをJSONへ集約し、repair proposal、approved sync action、RAG candidateを分離する |
| `/knowledge-capture` | 完了Issueに専門review、採用外部知識、review escapeが含まれる | RAG candidatesとして抽出し、人間承認後に内部RAGへ吸収する |

## Shared Artifact Validator

`/ariadne-new-system-iac` は、新システムworkflowの設計成果物を realtime IaC workflow へ渡す前に、専用validator promptを使います。

| Agent | Type | Workflow Phase | Responsibility | Main Outputs |
| --- | --- | --- | --- | --- |
| `shared-artifact-validator-agent.prompt.md` | reviewer | shared artifact validation | requirements、communication specification、port definition、network boundary、ADR、software inventory、safety traceability、IaC readinessを検証し、不足・矛盾・human approval項目を明示する | `shared-artifact-validation.md`, `shared-artifact-validation.json` |

## Realtime IaC Agent Set

`/realtime-iac` は、既存の Ariadne architecture / runtime / security / observability Agent と連携しつつ、IaC固有の成果物名と検証順序を固定するために専用Agent promptを使います。

| Agent | Type | Workflow Phase | Responsibility | Main Outputs |
| --- | --- | --- | --- | --- |
| `iac-requirements-agent.prompt.md` | full-stack | shared artifact gate / requirements | communication specification、port definition list、network boundary definitionを確認し、不足時は停止する | `requirements.md`, `open-questions.md` |
| `iac-network-security-design-agent.prompt.md` | full-stack | network / security design | firewall、TLS、auth、secret、reverse proxy、TURN/STUN、public exposureを設計する | `network-design.md`, `security-design.md`, `firewall-policy.md` |
| `iac-runtime-design-agent.prompt.md` | full-stack | runtime design | Docker Compose、systemd、startup、restart、health check、rollback unitを設計する | `runtime-design.md`, `docker-compose-design.md` |
| `iac-observability-design-agent.prompt.md` | full-stack | observability design | logs、logrotate、metrics、health signal、incident evidenceを設計する | `observability-design.md`, `monitoring-policy.md` |
| `iac-implementer-agent.prompt.md` | implementer | implementation | 承認済み設計とboilerplate selectionからIaC artifactsを生成する。`.env`とsecretは生成せず、template採用時はコピー先だけを編集する | IaC artifacts, `iac-implementation.md` |
| `iac-security-review-agent.prompt.md` | reviewer | security review | public ports、secret leakage、privilege、TLS/auth/firewall整合性をreviewする | `security-review.md` |
| `iac-docker-desktop-test-agent.prompt.md` | tester | Docker Desktop validation | `docker compose config`、startup、health、env、ports、logs、restart、networkを検証する | `docker-test-plan.md`, `docker-test-result.md` |
| `iac-linux-runtime-test-agent.prompt.md` | tester | Linux runtime validation | systemd、firewall、logrotate、service restart、health checkを検証する | `runtime-validation.md` |
| `iac-integration-test-agent.prompt.md` | tester | integration validation | control、video、telemetry、gateway、recoveryの疎通を確認する | `integration-test.md` |
| `iac-documentation-agent.prompt.md` | knowledge | documentation | setup、operation、troubleshooting、architecture/network overviewを整える | README, docs, `iac-documentation.md` |

## VSCode Environment Agent Set

`/vscode-environment` uses a dedicated set of agents to build VSCode Workspace-as-Code artifacts before touching `.vscode` files.

| Agent | Type | Workflow Phase | Responsibility | Main Outputs |
| --- | --- | --- | --- | --- |
| `workspace-requirements-analyst-agent.prompt.md` | full-stack | requirements | tools, extensions, terminal profiles, tasks, launch targets, AI workflow entrypoints, evidence requirements | `workspace-requirements.md`, `open-questions.md` |
| `workspace-shared-artifact-validator-agent.prompt.md` | reviewer | validation | check required workspace artifacts and stop on missing or contradictory items | `workspace-shared-artifact-validation.json`, `workspace-shared-artifact-validation.md` |
| `vscode-architect-agent.prompt.md` | full-stack | design | design settings, tasks, launch configs, extensions, and workspace file | `vscode-design.md` |
| `terminal-architect-agent.prompt.md` | full-stack | design | design terminal profiles, default shell policy, and terminal roles | `terminal-design.md` |
| `workspace-implementer-agent.prompt.md` | implementer | implementation | implement approved `.vscode` and workspace files without overwriting user settings blindly | `.vscode/*`, `workspace-implementation.md` |
| `workspace-test-agent.prompt.md` | reviewer | test | verify JSON, tasks, terminal profiles, launch configs, Docker/runtime checks, and evidence | `workspace-test.md`, `test-evidence/evidence/` |
| `workspace-documentation-writer-agent.prompt.md` | knowledge | documentation | document setup, extensions, tasks, terminal usage, troubleshooting, and evidence capture | README/setup docs, `workspace-documentation.md` |

## Escalation Rules

- Full-stack Agentは、知らない技術領域を無理に決めません。
- Reviewer Agentは、外部WebRAGだけでfindingを確定しません。
- Implementer Agentは、外部WebRAGで見つけた方針を採用する前にtest evidenceで確認します。
- External Web Source Reviewerは、外部ページ本文を丸ごと保存しません。
- Specialist Agentを追加する前に、既存Agentでのrole overlapを確認します。

## Review Questions Before Adding A New Agent

- 既存Agentにチェック項目を足せば足りるか。
- 外部Web汎用Agentで十分か。
- その領域は3回以上繰り返し登場しているか。
- 公式docs/RFC/vendor docsを読む専門観点が必要か。
- 出力先categoryとmetadataが決まっているか。
- downstream Agentがその出力をどう使うか決まっているか。
