# Runtime pytest 単体試験仕様

作成日: 2026-07-07

この文書は、`runtime/tests` 配下で収集される pytest node を、単体試験仕様として source file ごとに整理した索引です。
上位のUT項目表は [Runtime pytest UTテスト項目表](test-items.md) を参照します。
coverage 推移と監査履歴は repository root の `Runtime pytest 分岐・CLI・coverage監査レポート.md` を参照します。

この仕様では、長い `pytest node id` でMarkdownプレビューが横に広がりすぎないよう、個別ケースを表ではなくブロック形式で記載します。

## サマリ

| 項目 | 値 |
| --- | ---: |
| pytest files | 39 |
| pytest test functions | 681 |
| pytest collected cases | 723 |
| pytest result | `726 passed` |
| statement coverage | 99.66% |
| total coverage | 99.48% |

## 共通前提

- 実行起点は `C:\github\ariadne-ai-workflow-platform\runtime` です。
- pytest / coverage は `runtime/pyproject.toml` の `dev` dependency group で管理します。
- 外部I/O、GitHub API、Git操作、Docker、MSYS2、Go、VSCode task runner は、原則としてmock、dry-run、または明示的なmissing検出として検証します。
- 期待結果は、pytest assertion がすべて成功し、対象runtimeが意図したJSON、Markdown、context、manifest、error boundaryを返すことです。

## 実行コマンド

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\windows-script\uv.cmd run --project . --group dev pytest tests -q
```

収集ケースを確認する場合:

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\windows-script\uv.cmd run --project . --group dev pytest --collect-only -q tests
```

## ケース一覧

ケース本文は source file ごとに `cases/` 配下へ分割しています。同期チェックでは、この索引ファイルと `cases/*.md` を結合してpytest収集結果と照合します。

| Source | Cases |
| --- | ---: |
| [test_close_archive.py](cases/test_close_archive.md) | 16 |
| [test_common_runtime.py](cases/test_common_runtime.md) | 11 |
| [test_context_first.py](cases/test_context_first.md) | 34 |
| [test_corrective_action_report.py](cases/test_corrective_action_report.md) | 7 |
| [test_coverage_audit.py](cases/test_coverage_audit.md) | 14 |
| [test_ctl_help.py](cases/test_ctl_help.md) | 52 |
| [test_dispatcher_context.py](cases/test_dispatcher_context.md) | 12 |
| [test_docs_sync_workflow.py](cases/test_docs_sync_workflow.md) | 11 |
| [test_flutter_multiplatform.py](cases/test_flutter_multiplatform.md) | 16 |
| [test_gate_restart.py](cases/test_gate_restart.md) | 4 |
| [test_github_knowledge_maintenance.py](cases/test_github_knowledge_maintenance.md) | 48 |
| [test_github_runtime.py](cases/test_github_runtime.md) | 36 |
| [test_iac_template.py](cases/test_iac_template.md) | 6 |
| [test_init_corrective_action_fix.py](cases/test_init_corrective_action_fix.md) | 10 |
| [test_intake_requirements.py](cases/test_intake_requirements.md) | 8 |
| [test_knowledge_capture.py](cases/test_knowledge_capture.md) | 7 |
| [test_mcp_boilerplate_templates.py](cases/test_mcp_boilerplate_templates.md) | 3 |
| [test_mcp_server_group_workflow.py](cases/test_mcp_server_group_workflow.md) | 12 |
| [test_observability_metrics.py](cases/test_observability_metrics.md) | 19 |
| [test_preflight.py](cases/test_preflight.md) | 36 |
| [test_pytest_ut_spec_sync.py](cases/test_pytest_ut_spec_sync.md) | 21 |
| [test_rag_artifact_migration.py](cases/test_rag_artifact_migration.md) | 19 |
| [test_rag_build.py](cases/test_rag_build.md) | 8 |
| [test_rag_dispatcher.py](cases/test_rag_dispatcher.md) | 10 |
| [test_rag_duckdb_store.py](cases/test_rag_duckdb_store.md) | 15 |
| [test_rag_ingestion_optimizer.py](cases/test_rag_ingestion_optimizer.md) | 9 |
| [test_rag_pipeline_units.py](cases/test_rag_pipeline_units.md) | 23 |
| [test_rag_retrieve_context.py](cases/test_rag_retrieve_context.md) | 17 |
| [test_remaining_policy_vscode_runtime.py](cases/test_remaining_policy_vscode_runtime.md) | 26 |
| [test_remaining_rag_scm_runtime.py](cases/test_remaining_rag_scm_runtime.md) | 11 |
| [test_retrieval_runtime.py](cases/test_retrieval_runtime.md) | 23 |
| [test_scm_runtime.py](cases/test_scm_runtime.md) | 53 |
| [test_sdk_analysis.py](cases/test_sdk_analysis.md) | 11 |
| [test_self_improvement_workflow.py](cases/test_self_improvement_workflow.md) | 15 |
| [test_svg_layout_modes.py](cases/test_svg_layout_modes.md) | 19 |
| [test_system_integration.py](cases/test_system_integration.md) | 15 |
| [test_vscode_environment_workflow.py](cases/test_vscode_environment_workflow.md) | 10 |
| [test_vscode_workspace.py](cases/test_vscode_workspace.md) | 2 |
| [test_workflow_doctor.py](cases/test_workflow_doctor.md) | 32 |
| [test_workflow_state_noise_validation.py](cases/test_workflow_state_noise_validation.md) | 21 |

## 更新ルール

- この文書は `pytest --collect-only -q tests` の収集結果を正として更新します。
- 同期確認は `cd runtime && .\windows-script\uv.cmd run --project . --group dev python tools\pytest_ut_spec_sync.py --spec ..\docs\reference\runtime-pytest-ut\case-specification.md --runtime-root . check` で実行します。
- 入力値欄の再生成は `cd runtime && .\windows-script\uv.cmd run --project . --group dev python tools\pytest_ut_spec_sync.py --spec ..\docs\reference\runtime-pytest-ut\case-specification.md --runtime-root . fix-inputs` で実行します。
- テスト関数を追加、削除、renameした場合は、この仕様と該当する `cases/*.md` を更新します。
- `pytest.mark.parametrize` によって1つのtest functionから複数caseが収集される場合は、pytest node idのparameter表記まで仕様として残します。
- 個別caseの詳細な入力値やfixtureは、該当pytest sourceを正とします。
