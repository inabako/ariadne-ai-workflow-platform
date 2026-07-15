# Runtime pytest 蜊倅ｽ楢ｩｦ鬨謎ｻ墓ｧ俶嶌・・06繧ｱ繝ｼ繧ｹ・・

菴懈・譌･: 2026-07-07

縺薙・譁・嶌縺ｯ縲～runtime/tests` 驟堺ｸ九〒蜿朱寔縺輔ｌ繧却ytest node繧偵∝腰菴楢ｩｦ鬨謎ｻ墓ｧ倥→縺励※1繧ｱ繝ｼ繧ｹ縺壹▽蛻玲嫌縺励◆繧ゅ・縺ｧ縺吶・
荳贋ｽ阪・UT鬆・岼陦ｨ縺ｯ [Runtime pytest UT Test Items](test-items.md) 繧貞盾辣ｧ縺励∪縺吶・
coverage謗ｨ遘ｻ縺ｨ逶｣譟ｻ螻･豁ｴ縺ｯ repository root 縺ｮ `Runtime pytest 蛻・ｲ舌・CLI繝ｻcoverage逶｣譟ｻ繝ｬ繝昴・繝・md` 繧貞盾辣ｧ縺励∪縺吶・

縺薙・莉墓ｧ俶嶌縺ｧ縺ｯ縲・聞縺・`pytest node id` 縺ｧMarkdown繝励Ξ繝薙Η繝ｼ縺梧ｨｪ縺ｫ蠎・′繧峨↑縺・ｈ縺・√こ繝ｼ繧ｹ荳隕ｧ繧定｡ｨ縺ｧ縺ｯ縺ｪ縺上ヶ繝ｭ繝・け蠖｢蠑上〒險倩ｼ峨＠縺ｾ縺吶・

## 繧ｵ繝槭Μ

| 鬆・岼 | 蛟､ |
| --- | ---: |
| pytest files | 38 |
| pytest test functions | 619 |
| pytest collected cases | 632 |
| pytest result | `632 passed` |
| statement coverage | 99.66% |
| total coverage | 99.48% |

## 蜈ｱ騾壼燕謠・

- 螳溯｡瑚ｵｷ轤ｹ縺ｯ `C:\github\ariadne-ai-workflow-platform\runtime` 縺ｧ縺吶・
- pytest / coverage 縺ｯ `runtime/pyproject.toml` 縺ｮ `dev` dependency group縺ｧ邂｡逅・＠縺ｾ縺吶・
- 螟夜ΚI/O縲；itHub API縲；it謫堺ｽ懊．ocker縲｀SYS2縲；o縲〃SCode task runner縺ｯ縲∝次蜑㍊ock縲‥ry-run縲√∪縺溘・譏守､ｺ逧・↑missing讀懷・縺ｨ縺励※讀懆ｨｼ縺励∪縺吶・
- 譛溷ｾ・ｵ先棡縺ｯ縲｝ytest assertion縺後☆縺ｹ縺ｦ謌仙粥縺励∝ｯｾ雎｡runtime縺梧э蝗ｳ縺励◆JSON縲｀arkdown縲…ontext縲［anifest縲‘rror boundary繧定ｿ斐☆縺薙→縺ｧ縺吶・

## 螳溯｡後さ繝槭Φ繝・

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\tools\uv.cmd run --project . --group dev pytest tests -q
```

蜿朱寔繧ｱ繝ｼ繧ｹ繧堤｢ｺ隱阪☆繧句ｴ蜷・

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\tools\uv.cmd run --project . --group dev pytest --collect-only -q tests
```

## 繧ｱ繝ｼ繧ｹ荳隕ｧ

繧ｱ繝ｼ繧ｹ譛ｬ譁・・source file縺斐→縺ｫ cases/ 驟堺ｸ九∈蛻・屬縺励※縺・∪縺吶ょ酔譛溘メ繧ｧ繝・け縺ｧ縺ｯ縲√％縺ｮ邏｢蠑輔ヵ繧｡繧､繝ｫ縺ｨ cases/*.md 繧堤ｵ仙粋縺励※pytest蜿朱寔邨先棡縺ｨ辣ｧ蜷医＠縺ｾ縺吶・

| Source | Cases |
| --- | ---: |
| [test_close_archive.py](cases/test_close_archive.md) | 16 |
| [test_common_runtime.py](cases/test_common_runtime.md) | 10 |
| [test_context_first.py](cases/test_context_first.md) | 34 |
| [test_corrective_action_report.py](cases/test_corrective_action_report.md) | 6 |
| [test_coverage_audit.py](cases/test_coverage_audit.md) | 6 |
| [test_ctl_help.py](cases/test_ctl_help.md) | 36 |
| [test_dispatcher_context.py](cases/test_dispatcher_context.md) | 12 |
| [test_docs_sync_workflow.py](cases/test_docs_sync_workflow.md) | 11 |
| [test_flutter_multiplatform.py](cases/test_flutter_multiplatform.md) | 16 |
| [test_github_knowledge_maintenance.py](cases/test_github_knowledge_maintenance.md) | 18 |
| [test_github_runtime.py](cases/test_github_runtime.md) | 36 |
| [test_init_corrective_action_fix.py](cases/test_init_corrective_action_fix.md) | 9 |
| [test_intake_requirements.py](cases/test_intake_requirements.md) | 8 |
| [test_knowledge_capture.py](cases/test_knowledge_capture.md) | 7 |
| [test_mcp_boilerplate_templates.py](cases/test_mcp_boilerplate_templates.md) | 2 |
| [test_mcp_server_group_workflow.py](cases/test_mcp_server_group_workflow.md) | 12 |
| [test_observability_metrics.py](cases/test_observability_metrics.md) | 17 |
| [test_preflight.py](cases/test_preflight.md) | 27 |
| [test_pytest_ut_spec_sync.py](cases/test_pytest_ut_spec_sync.md) | 20 |
| [test_rag_artifact_migration.py](cases/test_rag_artifact_migration.md) | 19 |
| [test_rag_build.py](cases/test_rag_build.md) | 8 |
| [test_rag_dispatcher.py](cases/test_rag_dispatcher.md) | 10 |
| [test_rag_duckdb_store.py](cases/test_rag_duckdb_store.md) | 15 |
| [test_rag_ingestion_optimizer.py](cases/test_rag_ingestion_optimizer.md) | 9 |
| [test_rag_pipeline_units.py](cases/test_rag_pipeline_units.md) | 23 |
| [test_rag_retrieve_context.py](cases/test_rag_retrieve_context.md) | 17 |
| [test_remaining_policy_vscode_runtime.py](cases/test_remaining_policy_vscode_runtime.md) | 26 |
| [test_remaining_rag_scm_runtime.py](cases/test_remaining_rag_scm_runtime.md) | 10 |
| [test_retrieval_runtime.py](cases/test_retrieval_runtime.md) | 23 |
| [test_scm_runtime.py](cases/test_scm_runtime.md) | 53 |
| [test_sdk_analysis.py](cases/test_sdk_analysis.md) | 11 |
| [test_self_improvement_workflow.py](cases/test_self_improvement_workflow.md) | 14 |
| [test_svg_layout_modes.py](cases/test_svg_layout_modes.md) | 19 |
| [test_system_integration.py](cases/test_system_integration.md) | 15 |
| [test_vscode_environment_workflow.py](cases/test_vscode_environment_workflow.md) | 10 |
| [test_vscode_workspace.py](cases/test_vscode_workspace.md) | 2 |
| [test_workflow_doctor.py](cases/test_workflow_doctor.md) | 25 |
| [test_workflow_state_noise_validation.py](cases/test_workflow_state_noise_validation.md) | 21 |

## 譖ｴ譁ｰ繝ｫ繝ｼ繝ｫ

- 縺薙・譁・嶌縺ｯ `pytest --collect-only -q tests` 縺ｮ蜿朱寔邨先棡繧呈ｭ｣縺ｨ縺励※譖ｴ譁ｰ縺励∪縺吶・
- 蜷梧悄遒ｺ隱阪・ `cd runtime && .\tools\uv.cmd run --project . --group dev python tools\pytest_ut_spec_sync.py --spec ..\docs\reference\runtime-pytest-ut\case-specification.md --runtime-root . check` 縺ｧ螳溯｡後＠縺ｾ縺吶・
- 蜈･蜉帛､谺・・蜀咲函謌舌・ `cd runtime && .\tools\uv.cmd run --project . --group dev python tools\pytest_ut_spec_sync.py --spec ..\docs\reference\runtime-pytest-ut\case-specification.md --runtime-root . fix-inputs` 縺ｧ螳溯｡後＠縺ｾ縺吶・
- 繝・せ繝磯未謨ｰ繧定ｿｽ蜉縲∝炎髯､縲〉ename縺励◆蝣ｴ蜷医・縲√％縺ｮ606繧ｱ繝ｼ繧ｹ莉墓ｧ俶嶌繧よ峩譁ｰ縺励∪縺吶・
- `pytest.mark.parametrize` 縺ｫ繧医▲縺ｦ1縺､縺ｮtest function縺九ｉ隍・焚case縺悟庶髮・＆繧後ｋ蝣ｴ蜷医・縲｝ytest node id縺ｮparameter陦ｨ險倥∪縺ｧ莉墓ｧ倥→縺励※谿九＠縺ｾ縺吶・
- 蛟句挨case縺ｮ隧ｳ邏ｰ縺ｪ蜈･蜉帛､繧・ixture縺ｯ縲∬ｩｲ蠖菟ytest source繧呈ｭ｣縺ｨ縺励∪縺吶・
