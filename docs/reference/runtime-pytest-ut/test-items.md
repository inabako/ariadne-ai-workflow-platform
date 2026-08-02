# Runtime pytest UTテスト項目表

作成日: 2026-07-07

この文書は、Ariadne AI Workflow Platform の `runtime/tests` 配下にある pytest UT を、人間が確認しやすいテスト項目表として整理したものです。

pytest node id 単位の詳細な単体試験仕様は [Runtime pytest 単体試験仕様](case-specification.md) を参照します。ケース本文は source file ごとに `cases/*.md` へ分割しています。

詳細な coverage 推移と監査結果は、repository root の `Runtime pytest 分岐・CLI・coverage監査レポート.md` を参照します。

## 現在の到達点

| 項目 | 値 |
| --- | ---: |
| pytest対象ディレクトリ | `runtime/tests` |
| pytest files | 54 |
| pytest test functions | 832 |
| pytest collected tests | 847 |
| pytest result | `847 passed` |
| statement coverage | 96% |
| total coverage | 96% |
| missing lines | 397 |
| missing branches | 189 |

## 実行コマンド

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\windows-script\uv.cmd run --project . --group dev pytest tests -q
```

coverageを更新する場合:

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
Remove-Item -LiteralPath .coverage.json -ErrorAction SilentlyContinue
Remove-Item -LiteralPath .coverage -ErrorAction SilentlyContinue
.\windows-script\uv.cmd run --project . --group dev coverage run --data-file .coverage -m pytest tests -q
.\windows-script\uv.cmd run --project . --group dev coverage json --data-file .coverage -o .coverage.json
```

pytest node単位の完全一覧を確認する場合:

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\windows-script\uv.cmd run --project . --group dev pytest --collect-only -q tests
```

## テスト項目表

| ID | pytest file | test functions | collected tests | 主対象 | 主なUT観点 | runtimeを支える意味 |
| --- | --- | ---: | ---: | --- | --- | --- |
| RT-UT-001 | `runtime/tests/test_close_archive.py` | 16 | 16 | `runtime/workflow/close_archive.py` | close archive prepare、audit、prune、RAG参照、削除承認、archive path安全性 | 完了作業の知識保存とworkspace cleanupを安全に分離する |
| RT-UT-002 | `runtime/tests/test_common_runtime.py` | 11 | 11 | `runtime/common/*`, `runtime/constants/paths.py` | slug、repo root、artifact index、JSON/Markdown、env、repository設定抽出、knowledge source repository ENV | 全workflowが共有する基礎関数を安定させる |
| RT-UT-003 | `runtime/tests/test_context_first.py` | 34 | 34 | `runtime/workflow/context_first.py`、関連workflow | context manifest、environment selection、test-evidence読取、dispatcher context、IaC handoff、各workflowのContext First登録 | workflow実行前に必要contextを固定し、AIの推測実行を減らす |
| RT-UT-004 | `runtime/tests/test_corrective_action_report.py` | 6 | 6 | `runtime/workflow/corrective_action_report.py` | corrective action report context登録、front matter解析、section count、show/register CLI | 改善レポートを後続fix workflowへ渡せる構造にする |
| RT-UT-005 | `runtime/tests/test_coverage_audit.py` | 14 | 14 | `runtime/tools/coverage_audit.py`, `runtime/tools/text_encoding_convert.py`, `runtime/tools/text_encoding_guard.py`, `runtime/tools/utf8_bom.py` | runtime module集計、CLI検査、coverage実行、JSON/Markdown出力、script path load、encoding候補検査・hex preview・SJIS/CP932からUTF-8への安全変換、decode error・不可逆欠落検出、UTF-8 BOM検出・除去 | runtime品質を継続監査する自己診断を支える |
| RT-UT-006 | `runtime/tests/test_ctl_help.py` | 57 | 57 | `runtime/ctl/ctl.py`, `runtime/ctl/ctl_help.py`, `runtime/ctl/ctl_doctor_adapter.py`, `runtime/workflow/work_cleanup.py`, `runtime/windows-script/aiwf.cmd`, `runtime/windows-script/aiwf.ps1`, `runtime/posix-bash/aiwf.sh` | `aiwfctl help`、`help runtime`、Windows 11 PowerShell入口、Linux/WSL/macOS bash入口、runtime-local pytest config/cache、`aiwfctl doctor --repair-encoding --dry-run`、`aiwfctl knowledge`、`aiwfctl work cleanup-check/apply`、GitHub knowledge sync/rebase apply、human-gate、close-archive、env選択、検索、警告表示、Context First初期化、registry参照、分離search_terms registry、DuckDB `search_terms` table、templates registry seed、全prompt commandの検索語coverage | 肥大化したworkflowをCLI索引から迷わず呼べるようにし、一時work作業場をKnowledge吸収確認後に安全cleanupできるようにする |
| RT-UT-007 | `runtime/tests/test_dispatcher_context.py` | 12 | 12 | `runtime/workflow/dispatcher_context.py` | workflow/tool candidate scoring、Human Check、registry fallback、context生成 | Intentからworkflow/tool選定へ進むdispatcherの判断根拠を固定する |
| RT-UT-008 | `runtime/tests/test_docs_sync_workflow.py` | 11 | 11 | `runtime/workflow/docs_sync.py` | docs-sync init、SCM context gate、analysis template、Issue body、CLI dispatch | 実装とdocs差分をdocs-only workflowとして安全に切り出す |
| RT-UT-008A | `runtime/tests/test_expectation_design_runtime.py` | 7 | 7 | `runtime/design/expectation/*`, `runtime/ctl/ctl.py` | Expectation-Driven Design init、compare、candidate scaffold、feasibility、extraction、review、Human Gate、refinement、contracts、verification、feedback、Review Council dispatch | Expectation-Driven Design Flow のruntime contractとartifact generationをpytest仕様に紐付ける |
| RT-UT-008B | `runtime/tests/test_e2e_runtime.py` | 18 | 18 | `runtime/testing/e2e_runtime.py`, `runtime/ctl/ctl.py` | E2E/結合試験plan、verification contract、contract scaffold、contract/plan整合性確認、readiness、Stub不足検出、Human Check前実行停止、dry-run、run/observe/verify/explain証跡、Review Council bridge、coverage確認、Human final gate、final gate監査情報、evidence package、output copy、trace/log参照、未解決loop検出、fix loop、Review Council / SCM / trace連携導線、CLI route | 成果物に対する結合試験とE2Eテストをruntime artifactとして残し、検証契約を固定してから、Review Council確認、coverage確認、Human最終判断、handoff package、問題発見、修正指示、再テストへつなげる |
| RT-UT-009 | `runtime/tests/test_flutter_multiplatform.py` | 16 | 16 | `runtime/workflow/flutter_multiplatform.py`、`runtime/ctl/ctl.py` | target未指定Human Check、yaml/CLI target読込、host OS別build可否、boilerplate展開、verify/build evidence、WebDriver不足判断、finalize完了判定、aiwfctl入口 | Flutter multi-platform開発でtarget/platform/build環境を推測せず、実試験証跡と完了判定をContext Firstで後続workflowへ渡す |
| RT-UT-009A | `runtime/tests/test_gate_restart.py` | 4 | 4 | `runtime/common/gate_restart.py`, `.ariadne/shared/gate-restart-policy.md`, `.ariadne/schemas/gate-restart.schema.json` | gate failure後の同一gate再開、repair command必須化、pass/fail後の固定遷移 | gate異常を下流工程へ飛ばさず、修復後も同じgateから本線復帰させる |
| RT-UT-010 | `runtime/tests/test_github_knowledge_maintenance.py` | 50 | 50 | `runtime/workflow/github_knowledge_maintenance.py` | GitHub knowledge init、operation gate、tool selection、artifact integrity、repair/rebase detect/plan/review-intake/package/apply/sync plan/apply/RAG candidate、resume encoding gate | GitHub情報を長期知識資産化する前のhuman gateと出力を守る |
| RT-UT-011 | `runtime/tests/test_github_runtime.py` | 34 | 38 | `runtime/github/*`, `runtime/ctl/ctl.py` | REST/GraphQL API、Issue作成、PR作成、linked branch、title/body生成、error response、`aiwfctl github issue/pr` | GitHub mutationをmockで安全に検証し、実API依存を局所化する |
| RT-UT-012 | `runtime/tests/test_iac_template.py` | 6 | 6 | `runtime/workflow/iac_template.py`、`runtime/ctl/ctl.py` | IaC template catalog、OpenTelemetry Collector template copy、overwrite guard、health evidence、Terraform ENV path、aiwfctl route | Infrastructure boilerplateをtemplate原本からwork配下へ安全に展開し、非破壊healthとContext First evidenceを残す |
| RT-UT-013 | `runtime/tests/test_init_corrective_action_fix.py` | 9 | 9 | `runtime/workflow/init_corrective_action_fix.py` | corrective report解析、manifest優先、work初期化、report context登録、CLI | 改善レポートから修正workflowへ入る入口を安定させる |
| RT-UT-014 | `runtime/tests/test_intake_requirements.py` | 10 | 10 | `runtime/intake/intake_requirements.py`, `runtime/ctl/ctl.py` | requirement document発見、repository control、receipt、context初期化、copy/move、`aiwfctl intake run` | 要件受付時点でrepository、branch、contextを固定する |
| RT-UT-015 | `runtime/tests/test_knowledge_capture.py` | 7 | 7 | `runtime/workflow/knowledge_capture.py` | PR材料、docs/RAG候補、context fallback、close archive fallback、report生成 | 完了Issueから知識・PR・archive材料を取りこぼさない |
| RT-UT-016 | `runtime/tests/test_mcp_boilerplate_templates.py` | 3 | 3 | `templates/boilerplates/*` | MCP layered template contract、boilerplate index、OpenTelemetry Collector template contract | repo-local boilerplateが索引と必須ファイル契約を満たしていることを確認する |
| RT-UT-017 | `runtime/tests/test_mcp_server_group_workflow.py` | 12 | 12 | `runtime/workflow/mcp_server_group.py`、`runtime/ctl/ctl.py` | MCP server/client/agent template展開、境界分離、Context First evidence、CLI route | MCP関連boilerplateを用途別に分け、安全にwork配下へ展開する |
| RT-UT-018 | `runtime/tests/test_observability_metrics.py` | 17 | 17 | `runtime/observability/*` | monthly rotation、JSONL append、token/context/cost、evidence、Context First registration、non-fatal warning | Runtime metricsをbridge instrumentationとして観測可能にする |
| RT-UT-018A | `runtime/tests/test_oss_release_foundation.py` | 12 | 12 | `runtime/release/*`, `.github/workflows/*`, `docs/legal/*`, `docs/security/*` | OSS release files、AGPL/REUSE metadata、ScanCode、REUSE lint、VS Code act rehearsal、release validation、release manifest | OSS公開前のrelease foundationをruntime test evidenceとして固定する |
| RT-UT-019 | `runtime/tests/test_preflight.py` | 37 | 37 | `runtime/environment/preflight.py` | Docker、Python、MSYS2、Terraform ENV path、GitHub CLI auth、install approval、Markdown report、act CLI、Docker daemon、ScanCode audit profile | 実行環境不足を作業前に検出し、人間承認なしのinstallやcredential設定を防ぐ |
| RT-UT-019A | `runtime/tests/test_preflight_ctl_runtime.py` | 2 | 2 | `runtime/ctl/ctl.py`, `runtime/ctl/ctl_preflight_adapter.py` | `aiwfctl preflight` route, JSON output preservation, process report path, runtime log command path | environment preflightを公式CTL入口へ統一し、wrapperやVSCode taskからも同じ観測経路で実行できるようにする |
| RT-UT-020 | `runtime/tests/test_pytest_ut_spec_sync.py` | 21 | 22 | `runtime/tools/pytest_ut_spec_sync.py` | pytest収集結果とUT仕様書の同期確認、入力値抽出、差分検知、missing case scaffold、Markdown report、Context First manifest登録 | UT仕様書がpytest実体からずれたときに検出し、必要なcase scaffoldを作成してコンテキストの可観測性を保つ |
| RT-UT-021 | `runtime/tests/test_rag_artifact_migration.py` | 19 | 19 | `runtime/rag/migrate_retrieval_artifacts.py`、`standardize_corrective_report_names.py` | retrieval artifact移行、UUID化、Markdown jsonize、report名標準化、参照更新 | RAG資産の肥大化に耐える命名・参照・移行を守る |
| RT-UT-022 | `runtime/tests/test_rag_build.py` | 8 | 8 | `runtime/rag/rag_build.py` | normalize/chunk/index/embed pipeline統合、standardize制御、DuckDB migration evidence、context登録、CLI | RAG buildを一貫したpipeline artifactとして残す |
| RT-UT-022A | `runtime/tests/test_rag_ctl_runtime.py` | 6 | 6 | `runtime/ctl/ctl.py`, `runtime/ctl/ctl_rag_adapter.py`, `runtime/ctl/ctl_knowledge_adapter.py` | `aiwfctl rag retrieve/jsonize/migrate-legacy-root` route、runtime log command path、context pack generation、RAG/DuckDB/semantic-hints dry-run plan | RAG生成・検索系の通常入口をCTLに統一し、agentが個別moduleを直接呼ぶ必要を減らす |
| RT-UT-023 | `runtime/tests/test_rag_dispatcher.py` | 10 | 10 | `runtime/rag/rag_dispatcher.py` | query planning、dispatch plan、context pack、execution-plan参照、DuckDB backend、run command | RAG検索からworkflow/agentへ渡す文脈を安定させる |
| RT-UT-024 | `runtime/tests/test_rag_duckdb_store.py` | 15 | 15 | `runtime/rag/duckdb_store.py` | DuckDB schema生成、JSON ingest、duplicate skip、same ID update、migration error継続、標準source rebuild、migration履歴、検索、参照確認evidence、context JSON出力、CLI境界 | file-based RAG artifactをsource of truthにしたまま生成read modelへ安全に投影する |
| RT-UT-025 | `runtime/tests/test_rag_ingestion_optimizer.py` | 9 | 9 | `runtime/rag/ingestion_optimizer.py` | chunk候補評価、ACCEPT/REWRITE/HUMAN_CHECK/REJECT、evidence出力、policy fallback、CLI境界 | RAG吸収前にKnowledge品質を濾過し、index/embeddingへ流す根拠を残す |
| RT-UT-026 | `runtime/tests/test_rag_pipeline_units.py` | 23 | 23 | `runtime/rag/normalize_documents.py`、`chunk_documents.py`、`build_index.py`、`embed_chunks.py` | normalize、chunk、index、embedding、defensive fallback、script path load | RAG pipelineの最小単位を守り、本文を失わない生命線を確認する |
| RT-UT-027 | `runtime/tests/test_rag_retrieve_context.py` | 17 | 17 | `runtime/rag/retrieve_context.py` | JSONL読込、tokenize、keyword/semantic/hybrid search、DuckDB backend、budget圧縮、context pack出力 | 開発前RAG loadで必要なcontextを安全に圧縮して渡す |
| RT-UT-028 | `runtime/tests/test_remaining_policy_vscode_runtime.py` | 26 | 26 | `runtime/workflow/human_gate_policy.py`、`vscode_task_runner.py` | human gate registry、承認判定、VSCode task runner、PATH更新、Docker/Go/MSYS2 helper | 人間承認とVSCode実行補助をRuntimeから呼べる形にする |
| RT-UT-028I | `runtime/tests/test_iac_deployment_runtime.py` | 3 | 3 | `runtime/workflow/iac_deployment_runtime.py`, `runtime/workflow/kubernetes_runtime.py`, `runtime/ctl/ctl.py` | app runtime assessment、deployment contract、IaC deployment gap report、Kubernetes contract参照、CTL route | IaC生成前に最終アプリ状態を確認し、provider-specific IaC がDeployment Contractを入力にできるようにする |
| RT-UT-028J | `runtime/tests/test_iac_prepare_runtime.py` | 3 | 3 | `runtime/workflow/iac_prepare_runtime.py`, `runtime/workflow/iac_deployment_runtime.py`, `runtime/workflow/kubernetes_runtime.py`, `runtime/ctl/ctl.py` | `aiwfctl iac prepare` route、Deployment Contract先行、provider自動検出、Kubernetes/k3s準備、dry-run、E2E plan | IaC開始時に正しい順番をruntimeが案内し、要件/設計からE2E直前まで迷わず進める入口を守る |
| RT-UT-028K | `runtime/tests/test_kubernetes_runtime.py` | 5 | 5 | `runtime/workflow/kubernetes_runtime.py`, `runtime/ctl/ctl.py` | Kubernetes/k3s compatibility assessment、gap report、manifest scaffold、dry-run evidence、integration E2E plan、CTL route | 要件定義に Kubernetes/k3s が指定された場合に、実クラスタへ apply する前の成立性、gap、dry-run、E2E 接続 evidence を runtime artifact として残せるようにする |
| RT-UT-029 | `runtime/tests/test_remaining_rag_scm_runtime.py` | 10 | 10 | `runtime/rag/jsonize_rag_tree.py`、`runtime/scm/compare_requirements.py` | RAG tree jsonize、source削除、requirements比較、git diff、artifact出力 | RAG/SCMの残存横断moduleを横断的に守る |
| RT-UT-029A | `runtime/tests/test_retrieval_ctl_runtime.py` | 2 | 2 | `runtime/ctl/ctl.py`, `runtime/ctl/ctl_retrieval_adapter.py` | `aiwfctl retrieval run` route, task report generation, runtime log command path | agent task実行計画を公式CTL入口へ統一し、task runnerを直接呼ぶ必要を減らす |
| RT-UT-030 | `runtime/tests/test_retrieval_runtime.py` | 16 | 23 | `runtime/retrieval/task_runner.py` | task plan検証、dependency、dry-run、parallel/sequential、logs、reports、CLI | agent task実行計画を依存関係付きで安全に動かす |
| RT-UT-030L | `runtime/tests/test_runtime_log.py` | 8 | 8 | `runtime/workflow/runtime_log.py`, `runtime/ctl/ctl.py` | `aiwfctl log summary`、log tail、log grep、log export、log archive/prune dry-run、承認制archive/prune、runtime event log集計 | runtime logの肥大化を見える化し、Human Check付きで安全に退避・縮小できるようにする |
| RT-UT-030A | `runtime/tests/test_runtime_status.py` | 9 | 9 | `runtime/workflow/runtime_status.py`, `runtime/ctl/ctl.py`, `runtime/workflow/workflow_doctor.py`, `runtime/environment/preflight.py` | `aiwfctl status`、`status --summary/--verbose/--problems --json`、active trace、runtime event log、work state、work-id関連trace、knowledge source、DuckDB read model、doctor warning count、dependency readiness、doctor guidance由来のnext action表示、runtime log肥大化時のlog maintenance next action、status/helpノイズ除外後のlast relevant/problem event | workflow実行前後に現在地と次の確認コマンドを一目で把握し、work-id・doctor warning・dependency readinessから関連traceや復旧導線を辿れるようにする |
| RT-UT-030B | `runtime/tests/test_runtime_trace.py` | 6 | 6 | `runtime/workflow/runtime_trace.py`, `runtime/ctl/ctl.py` | `aiwfctl trace show`、`trace show --problems`、trace id検索、latest trace選択、command集約、blocked/failed event抽出、resume hint、last successful command、missing trace終了コード、trace begin work-id記録、active trace異常復旧preview/approval | workflowが最後まで通らない原因をtrace単位で読み解き、active trace異常時も安全に復旧できるようにする |
| RT-UT-031 | `runtime/tests/test_scm_runtime.py` | 55 | 55 | `runtime/scm/*`, `runtime/ctl/ctl.py` | prepare repository、issue branch、push、commit、bootstrap、token askpass、dry-run/non-dry-run、`aiwfctl scm prepare/branch` | Git操作をremote mutation前提でも安全にmock・dry-run検証する |
| RT-UT-032 | `runtime/tests/test_sdk_analysis.py` | 11 | 11 | `runtime/workflow/sdk_analysis.py`、`runtime/ctl/ctl.py` | SDK入力skip、metadata抽出、AWS/GCP cloud metadata抽出、Stripe payment metadata抽出、Context First登録、knowledge JSON候補、secret値非コピー、外部discovery候補生成、aiwfctl入口 | 要件定義工程でSDKプログラムを安全に前処理し、外部関連資料の確認観点と人間確認が必要な採用判断を見える形にする |
| RT-UT-033 | `runtime/tests/test_self_improvement_workflow.py` | 15 | 15 | `runtime/workflow/self_improvement.py`、`skills/*/SKILL.md`、`db/registries/registry.duckdb` | feedback report作成、Runtime log分析、Human Review追記、Issue body生成、evidence scaffold、feedback出力妥当化、help registry妥当化 | Ariadne自身のworkflow改善候補を安全に保存し、運用判断から改善Issueへつなぐ |
| RT-UT-034 | `runtime/tests/test_svg_layout_modes.py` | 19 | 19 | `runtime/workflow/gui_mode.py`、`web_svg_layout_mode.py` | SVG解析、input claim、PyQt/QTest候補、React/Playwright候補、validation、self-test | GUI/Web SVG入力から画面候補生成までをworkflow拡張として守る |
| RT-UT-035 | `runtime/tests/test_system_integration.py` | 15 | 15 | `runtime/workflow/system_integration.py`、`runtime/ctl/ctl.py` | system integration context生成、SDK cloud/payment metadata読取、emulator候補分類、emulator template展開、emulator health/preflight、Integration Test runbook生成、Integration Test evidence/finalize確認、Context First登録、aiwfctl入口 | 生成・修正コードを対象システムへ自然に統合し、emulatorと本番差分や起動前提の欠落、Integration Test手順の曖昧さ、完了判定漏れを見える形にする |
| RT-UT-035A | `runtime/tests/test_tools_ctl_runtime.py` | 3 | 3 | `runtime/ctl/ctl.py`, `runtime/ctl/ctl_tools_adapter.py` | `aiwfctl tools coverage-audit/bom-scan/encoding-guard` route, JSON output preservation, runtime log command path | runtime maintenance toolsを公式CTL入口へ統一し、wrapperやagent promptから直接tool moduleを呼ぶ必要を減らす |
| RT-UT-035B | `runtime/tests/test_visual_ctl_runtime.py` | 3 | 3 | `runtime/ctl/ctl.py`, `runtime/ctl/ctl_gui_adapter.py` | `aiwfctl gui init-input/self-test` route, `aiwfctl web-svg run` route, runtime log command path | GUI/Web SVG generation and validation are unified under the official CTL entrypoint so agents do not need to call workflow modules directly |
| RT-UT-036 | `runtime/tests/test_vscode_environment_workflow.py` | 10 | 10 | `runtime/workflow/vscode_environment.py`, `runtime/constants/paths.py` | self-provision、local RAG backup directory provisioning、draft/open questions、RAG template、requirements、validation、CLI | AI workflow実行環境をVSCode workspace as codeとして整え、ローカルKnowledgeバックアップ階層をGit pushなしで準備する |
| RT-UT-037 | `runtime/tests/test_vscode_workspace.py` | 2 | 2 | `.vscode/*`、`runtime/windows-script/aiwfctl.cmd` | aiwfctl PATH task、cmd usage | VSCodeから`aiwfctl`を迷わず呼べる導線を守る |
| RT-UT-038 | `runtime/tests/test_workflow_doctor.py` | 38 | 38 | `runtime/workflow/workflow_doctor.py`, `runtime/common/text_boundary.py`, `runtime/common/gate_restart.py` | tracked policy、required files、pytest runtime boundary、human gate registry、registry bootstrap seed、close archive completeness、git line ending policy、uv startup route、doctor warning guidance、text-boundary repair preview、spec index repair preview、text-boundary repair、spec index repair、gate restart、UT仕様書同期チェック、fail-on-warning | workflow repository自身の健康診断と本線復帰を自動化する |
| RT-UT-038A | `runtime/tests/test_workflow_ctl_runtime.py` | 4 | 4 | `runtime/ctl/ctl.py`, `runtime/ctl/ctl_workflow_adapter.py` | `aiwfctl workflow state/docs-sync/iac-handoff/validate-vscode-workspace` route、runtime log command path | workflow補助系を公式CTL入口へ統一し、agentが個別workflow moduleを直接呼ぶ必要を減らす |
| RT-UT-039 | `runtime/tests/test_workflow_state_noise_validation.py` | 22 | 22 | `runtime/workflow/workflow_state.py`、`noise_reduction.py`、`validate_output_language.py`、`validate_vscode_workspace.py` | workflow state、noise reduction、Japanese output guard、VSCode workspace JSON検証 | 要件定義前処理・状態管理・出力言語品質を守る |

## 観点別の対応範囲

| 観点 | 主なpytest file |
| --- | --- |
| Context First / dispatcher | `test_context_first.py`, `test_dispatcher_context.py`, `test_ctl_help.py` |
| Workflow lifecycle | `test_intake_requirements.py`, `test_corrective_action_report.py`, `test_init_corrective_action_fix.py`, `test_knowledge_capture.py`, `test_docs_sync_workflow.py`, `test_self_improvement_workflow.py` |
| RAG pipeline / retrieval | `test_rag_pipeline_units.py`, `test_rag_build.py`, `test_rag_ctl_runtime.py`, `test_rag_ingestion_optimizer.py`, `test_rag_duckdb_store.py`, `test_rag_retrieve_context.py`, `test_rag_dispatcher.py`, `test_rag_artifact_migration.py`, `test_remaining_rag_scm_runtime.py`, `test_retrieval_ctl_runtime.py` |
| SCM / GitHub mutation boundary | `test_scm_runtime.py`, `test_github_runtime.py`, `test_github_knowledge_maintenance.py` |
| Environment / VSCode / preflight | `test_preflight.py`, `test_preflight_ctl_runtime.py`, `test_remaining_policy_vscode_runtime.py`, `test_vscode_environment_workflow.py`, `test_vscode_workspace.py` |
| GUI / Web SVG workflow extension | `test_svg_layout_modes.py`, `test_visual_ctl_runtime.py` |
| E2E / integration evidence | `test_e2e_runtime.py`, `test_iac_deployment_runtime.py`, `test_iac_prepare_runtime.py`, `test_kubernetes_runtime.py`, `test_system_integration.py` |
| Flutter multi-platform workflow | `test_flutter_multiplatform.py` |
| Runtime quality guard | `test_coverage_audit.py`, `test_pytest_ut_spec_sync.py`, `test_self_improvement_workflow.py`, `test_tools_ctl_runtime.py`, `test_workflow_ctl_runtime.py`, `test_workflow_doctor.py`, `test_workflow_state_noise_validation.py` |

## 運用ルール

- この表は `runtime/tests` のUT項目を人間が把握するための台帳です。
- pytest node単位の完全な実行一覧は `pytest --collect-only -q tests` を正とします。
- test function数とcollected tests数が異なる場合は、`pytest.mark.parametrize` などにより、1つの関数から複数caseが収集されています。
- runtimeの重要CLI、Context First gate、SCM/GitHub mutation境界、RAG pipeline、GUI/SVG workflowを変更した場合は、該当行のUT観点を更新します。
- coverageの数値履歴は、root直下の `Runtime pytest 分岐・CLI・coverage監査レポート.md` に追記します。
