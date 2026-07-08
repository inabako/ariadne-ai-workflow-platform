# Runtime pytest UTテスト項目表

作成日: 2026-07-07

この文書は、Ariadne AI Workflow Platform の `runtime/tests` 配下にある全pytestを、UTのテスト項目表として整理したものです。

512ケースをpytest node id単位で列挙した単体試験仕様書は [Runtime pytest 単体試験仕様書（512ケース）](runtime-pytest-ut-case-specification.md) を参照します。

詳細なcoverage推移と監査結果は、repository root の `Runtime pytest 分岐・CLI・coverage監査レポート.md` を参照します。

## 現在の到達点

| 項目 | 値 |
| --- | ---: |
| pytest対象ディレクトリ | `runtime/tests` |
| pytest files | 30 |
| pytest test functions | 499 |
| pytest collected tests | 523 |
| pytest result | `523 passed` |
| statement coverage | 100.00% |
| total coverage | 99.73% |
| missing lines | 0 |
| missing branches | 26 |

## 実行コマンド

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\tools\uv.cmd run --project . --group dev pytest tests -q
```

coverageを更新する場合:

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
Remove-Item -LiteralPath .coverage.json -ErrorAction SilentlyContinue
Remove-Item -LiteralPath .coverage -ErrorAction SilentlyContinue
.\tools\uv.cmd run --project . --group dev coverage run --data-file .coverage -m pytest tests -q
.\tools\uv.cmd run --project . --group dev coverage json --data-file .coverage -o .coverage.json
```

pytest node単位の完全一覧を確認する場合:

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\tools\uv.cmd run --project . --group dev pytest --collect-only -q tests
```

## テスト項目表

| ID | pytest file | test functions | collected tests | 主対象 | 主なUT観点 | runtimeを支える意味 |
| --- | --- | ---: | ---: | --- | --- | --- |
| RT-UT-001 | `runtime/tests/test_close_archive.py` | 14 | 14 | `runtime/workflow/close_archive.py` | close archive prepare / audit / prune、RAG参照、削除承認、archive path安全性 | 完了作業の知識吸収とworkspace cleanupを安全に分離する |
| RT-UT-002 | `runtime/tests/test_common_runtime.py` | 9 | 9 | `runtime/common/*` | slug、repo root、artifact index、JSON/Markdown、env、repository設定抽出 | 全workflowが共有する基礎関数を安定させる |
| RT-UT-003 | `runtime/tests/test_context_first.py` | 34 | 34 | `runtime/workflow/context_first.py`、関連workflow | context manifest、environment selection、test-evidence読取、dispatcher context、IaC handoff、各workflowのContext First登録 | workflow実行前に必要contextを固定し、AIの推測実行を減らす |
| RT-UT-004 | `runtime/tests/test_corrective_action_report.py` | 6 | 6 | `runtime/workflow/corrective_action_report.py` | corrective action report context登録、front matter解析、section count、show/register CLI | 改善レポートを後続fix workflowへ渡せる構造にする |
| RT-UT-005 | `runtime/tests/test_coverage_audit.py` | 6 | 6 | `runtime/tools/coverage_audit.py` | runtime module集計、CLI検出、coverage実行、JSON/Markdown出力、script path load | runtime品質を継続監査する自己診断を支える |
| RT-UT-006 | `runtime/tests/test_ctl_help.py` | 33 | 33 | `runtime/ctl.py` | `aiwfctl help`、`aiwfctl doctor`、env選択、検索、警告色、Context First初期化、registry参照 | 巨大化したworkflowをCLI索引から迷わず呼べるようにする |
| RT-UT-007 | `runtime/tests/test_dispatcher_context.py` | 12 | 12 | `runtime/workflow/dispatcher_context.py` | workflow/tool candidate scoring、human check、registry fallback、context生成 | Intentからworkflow/tool選定へ進むdispatcherの判断根拠を固定する |
| RT-UT-008 | `runtime/tests/test_docs_sync_workflow.py` | 11 | 11 | `runtime/workflow/docs_sync.py` | docs-sync init、SCM context gate、analysis template、Issue body、CLI dispatch | 実装とdocs差分をdocs-only workflowとして安全に切り出す |
| RT-UT-009 | `runtime/tests/test_github_knowledge_maintenance.py` | 18 | 18 | `runtime/workflow/github_knowledge_maintenance.py` | GitHub knowledge init、operation gate、tool selection、repair/sync/RAG candidate | GitHub情報を長期知識資産化する際のhuman gateと出力を守る |
| RT-UT-010 | `runtime/tests/test_github_runtime.py` | 31 | 35 | `runtime/github/*` | REST/GraphQL API、Issue作成、PR作成、linked branch、title/body生成、エラー応答 | GitHub mutationをmockで安全に検証し、実API依存を局所化する |
| RT-UT-011 | `runtime/tests/test_init_corrective_action_fix.py` | 7 | 7 | `runtime/workflow/init_corrective_action_fix.py` | corrective report解決、manifest優先、work初期化、report context登録、CLI | 改善レポートから修正workflowへ入る入口を安定させる |
| RT-UT-012 | `runtime/tests/test_intake_requirements.py` | 8 | 8 | `runtime/intake/intake_requirements.py` | requirement document発見、repository control、receipt、context初期化、copy/move | 要件受け入れ時点でrepository/branch/contextを固定する |
| RT-UT-013 | `runtime/tests/test_knowledge_capture.py` | 7 | 7 | `runtime/workflow/knowledge_capture.py` | PR材料、docs/RAG候補、context fallback、close archive fallback、report生成 | 完了Issueから知識・PR・archive材料を取りこぼさない |
| RT-UT-014 | `runtime/tests/test_observability_metrics.py` | 17 | 17 | `runtime/observability/*` | monthly rotation, JSONL append, token/context/cost, evidence, Context First registration, non-fatal warning | Runtime metrics as bridge instrumentation: cost, context weight, and workflow health remain observable |
| RT-UT-015 | `runtime/tests/test_preflight.py` | 25 | 27 | `runtime/environment/preflight.py` | Docker、Python、MSYS2、Localty protocol、install approval、Markdown report | 実行環境不足を作業前に検出し、人間承認なしのinstallを防ぐ |
| RT-UT-016 | `runtime/tests/test_pytest_ut_spec_sync.py` | 17 | 17 | `runtime/tools/pytest_ut_spec_sync.py` | pytest収集結果とUT仕様書の同期確認、入力値欄再生成、node id正規化、差分検知、Markdown report、Context First manifest登録 | UT仕様書がpytest実体からズレたときに検出し、コンテキストの可観測性を保つ |
| RT-UT-017 | `runtime/tests/test_rag_artifact_migration.py` | 18 | 18 | `runtime/rag/migrate_retrieval_artifacts.py`、`standardize_corrective_report_names.py` | retrieval artifact移行、UUID化、Markdown jsonize、report名標準化、参照更新 | RAG資産の肥大化に耐える命名・参照・移行を守る |
| RT-UT-018 | `runtime/tests/test_rag_build.py` | 6 | 6 | `runtime/rag/rag_build.py` | normalize/chunk/index/embed pipeline統合、standardize制御、context登録、CLI | RAG buildを一貫したpipeline artifactとして残す |
| RT-UT-019 | `runtime/tests/test_rag_dispatcher.py` | 9 | 9 | `runtime/rag/rag_dispatcher.py` | query planning、dispatch plan、context pack、execution-plan参照、run command | RAG検索からworkflow/agentへ渡す文脈を安定させる |
| RT-UT-020 | `runtime/tests/test_rag_pipeline_units.py` | 23 | 23 | `runtime/rag/normalize_documents.py`、`chunk_documents.py`、`build_index.py`、`embed_chunks.py` | normalize、chunk、index、embedding、defensive fallback、script path load | RAG pipelineの最小単位を守り、本文を失わない救命糸を確認する |
| RT-UT-021 | `runtime/tests/test_rag_retrieve_context.py` | 16 | 16 | `runtime/rag/retrieve_context.py` | JSONL読込、tokenize、keyword/semantic/hybrid search、budget圧縮、context pack出力 | 開発前RAG loadで必要なcontextを安全に圧縮して渡す |
| RT-UT-022 | `runtime/tests/test_remaining_policy_vscode_runtime.py` | 26 | 26 | `runtime/workflow/human_gate_policy.py`、`vscode_task_runner.py` | human gate registry、承認判定、VSCode task runner、PATH更新、Docker/Go/MSYS2 helper | 人間承認とVSCode実行補助をruntimeから呼べる形にする |
| RT-UT-023 | `runtime/tests/test_remaining_rag_scm_runtime.py` | 10 | 10 | `runtime/rag/jsonize_rag_tree.py`、`runtime/scm/compare_requirements.py` | RAG tree jsonize、source削除、requirements比較、git diff、artifact出力 | RAG/SCMの残存重要moduleを横断的に守る |
| RT-UT-024 | `runtime/tests/test_retrieval_runtime.py` | 16 | 23 | `runtime/retrieval/task_runner.py` | task plan検証、dependency、dry-run、parallel/sequential、logs、reports、CLI | agent task実行計画を依存関係つきで安全に動かす |
| RT-UT-025 | `runtime/tests/test_scm_runtime.py` | 52 | 52 | `runtime/scm/*` | prepare repository、issue branch、push、commit、bootstrap、token askpass、dry-run/non-dry-run | Git操作をremote mutation前提でも安全にmock・dry-run検証する |
| RT-UT-026 | `runtime/tests/test_svg_layout_modes.py` | 19 | 19 | `runtime/workflow/gui_mode.py`、`web_svg_layout_mode.py` | SVG解析、input claim、PyQt/QTest候補、React/Playwright候補、validation、self-test | GUI/Web SVG入力から画面候補生成までをworkflow拡張として守る |
| RT-UT-027 | `runtime/tests/test_vscode_environment_workflow.py` | 10 | 10 | `runtime/workflow/vscode_environment.py` | self-provision、draft/open questions、RAG template、requirements、validation、CLI | AI workflow実行環境をVSCode workspace as codeとして整える |
| RT-UT-028 | `runtime/tests/test_vscode_workspace.py` | 2 | 2 | `.vscode/*`、`runtime/tools/aiwfctl.cmd` | aiwfctl PATH task、cmd usage | VSCodeから`aiwfctl`を迷わず呼べる導線を守る |
| RT-UT-029 | `runtime/tests/test_workflow_doctor.py` | 17 | 17 | `runtime/workflow/workflow_doctor.py` | tracked policy、required files、human gate registry、close archive completeness、UT仕様書同期チェック、fail-on-warning | workflow repository自身の健康診断を自動化する |
| RT-UT-030 | `runtime/tests/test_workflow_state_noise_validation.py` | 20 | 20 | `runtime/workflow/workflow_state.py`、`noise_reduction.py`、`validate_output_language.py`、`validate_vscode_workspace.py` | workflow state、noise reduction、Japanese output guard、VSCode workspace JSON検証 | 要件定義前処理・状態管理・出力言語品質を守る |

## 観点別の対応範囲

| 観点 | 主なpytest file |
| --- | --- |
| Context First / dispatcher | `test_context_first.py`, `test_dispatcher_context.py`, `test_ctl_help.py` |
| Workflow lifecycle | `test_intake_requirements.py`, `test_corrective_action_report.py`, `test_init_corrective_action_fix.py`, `test_knowledge_capture.py`, `test_docs_sync_workflow.py` |
| RAG pipeline / retrieval | `test_rag_pipeline_units.py`, `test_rag_build.py`, `test_rag_retrieve_context.py`, `test_rag_dispatcher.py`, `test_rag_artifact_migration.py`, `test_remaining_rag_scm_runtime.py` |
| SCM / GitHub mutation boundary | `test_scm_runtime.py`, `test_github_runtime.py`, `test_github_knowledge_maintenance.py` |
| Environment / VSCode / preflight | `test_preflight.py`, `test_remaining_policy_vscode_runtime.py`, `test_vscode_environment_workflow.py`, `test_vscode_workspace.py` |
| GUI / Web SVG workflow extension | `test_svg_layout_modes.py` |
| Runtime quality guard | `test_coverage_audit.py`, `test_pytest_ut_spec_sync.py`, `test_workflow_doctor.py`, `test_workflow_state_noise_validation.py` |

## 運用ルール

- この表は `runtime/tests` のUT項目を人間が把握するための台帳です。
- pytest node単位の完全な実行一覧は `pytest --collect-only -q tests` を正とします。
- test function数とcollected tests数が異なる場合は、`pytest.mark.parametrize` によって1つの関数から複数caseが収集されています。
- runtimeの重要CLI、Context First gate、SCM/GitHub mutation境界、RAG pipeline、GUI/SVG workflowを変更した場合は、該当行のUT観点を更新します。
- coverageの数値履歴は、root直下の `Runtime pytest 分岐・CLI・coverage監査レポート.md` に追記します。
