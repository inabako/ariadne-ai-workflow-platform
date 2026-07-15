# Runtime pytest UT繝・せ繝磯・岼陦ｨ

菴懈・譌･: 2026-07-07

縺薙・譁・嶌縺ｯ縲、riadne AI Workflow Platform 縺ｮ `runtime/tests` 驟堺ｸ九↓縺ゅｋ蜈ｨpytest繧偵ゞT縺ｮ繝・せ繝磯・岼陦ｨ縺ｨ縺励※謨ｴ逅・＠縺溘ｂ縺ｮ縺ｧ縺吶・

606繧ｱ繝ｼ繧ｹ繧恥ytest node id蜊倅ｽ阪〒蛻玲嫌縺励◆蜊倅ｽ楢ｩｦ鬨謎ｻ墓ｧ俶嶌縺ｯ [Runtime pytest 蜊倅ｽ楢ｩｦ鬨謎ｻ墓ｧ俶嶌・・06繧ｱ繝ｼ繧ｹ・云(case-specification.md) 繧貞盾辣ｧ縺励∪縺吶ゅこ繝ｼ繧ｹ譛ｬ譁・・source file縺斐→縺ｫ `cases/*.md` 縺ｸ蛻・屬縺励※縺・∪縺吶・

隧ｳ邏ｰ縺ｪcoverage謗ｨ遘ｻ縺ｨ逶｣譟ｻ邨先棡縺ｯ縲〉epository root 縺ｮ `Runtime pytest 蛻・ｲ舌・CLI繝ｻcoverage逶｣譟ｻ繝ｬ繝昴・繝・md` 繧貞盾辣ｧ縺励∪縺吶・

## 迴ｾ蝨ｨ縺ｮ蛻ｰ驕皮せ

| 鬆・岼 | 蛟､ |
| --- | ---: |
| pytest蟇ｾ雎｡繝・ぅ繝ｬ繧ｯ繝医Μ | `runtime/tests` |
| pytest files | 38 |
| pytest test functions | 619 |
| pytest collected tests | 632 |
| pytest result | `632 passed` |
| statement coverage | 96% |
| total coverage | 96% |
| missing lines | 397 |
| missing branches | 189 |

## 螳溯｡後さ繝槭Φ繝・

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\tools\uv.cmd run --project . --group dev pytest tests -q
```

coverage繧呈峩譁ｰ縺吶ｋ蝣ｴ蜷・

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
Remove-Item -LiteralPath .coverage.json -ErrorAction SilentlyContinue
Remove-Item -LiteralPath .coverage -ErrorAction SilentlyContinue
.\tools\uv.cmd run --project . --group dev coverage run --data-file .coverage -m pytest tests -q
.\tools\uv.cmd run --project . --group dev coverage json --data-file .coverage -o .coverage.json
```

pytest node蜊倅ｽ阪・螳悟・荳隕ｧ繧堤｢ｺ隱阪☆繧句ｴ蜷・

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\tools\uv.cmd run --project . --group dev pytest --collect-only -q tests
```

## 繝・せ繝磯・岼陦ｨ

| ID | pytest file | test functions | collected tests | 荳ｻ蟇ｾ雎｡ | 荳ｻ縺ｪUT隕ｳ轤ｹ | runtime繧呈髪縺医ｋ諢丞袖 |
| --- | --- | ---: | ---: | --- | --- | --- |
| RT-UT-001 | `runtime/tests/test_close_archive.py` | 14 | 14 | `runtime/workflow/close_archive.py` | close archive prepare / audit / prune縲ヽAG蜿ら・縲∝炎髯､謇ｿ隱阪∥rchive path螳牙・諤ｧ | 螳御ｺ・ｽ懈･ｭ縺ｮ遏･隴伜精蜿弱→workspace cleanup繧貞ｮ牙・縺ｫ蛻・屬縺吶ｋ |
| RT-UT-002 | `runtime/tests/test_common_runtime.py` | 9 | 9 | `runtime/common/*` | slug縲〉epo root縲∥rtifact index縲゛SON/Markdown縲‘nv縲〉epository險ｭ螳壽歓蜃ｺ | 蜈ｨworkflow縺悟・譛峨☆繧句渕遉朱未謨ｰ繧貞ｮ牙ｮ壹＆縺帙ｋ |
| RT-UT-003 | `runtime/tests/test_context_first.py` | 34 | 34 | `runtime/workflow/context_first.py`縲・未騾｣workflow | context manifest縲‘nvironment selection縲》est-evidence隱ｭ蜿悶‥ispatcher context縲！aC handoff縲∝推workflow縺ｮContext First逋ｻ骭ｲ | workflow螳溯｡悟燕縺ｫ蠢・ｦ…ontext繧貞崋螳壹＠縲、I縺ｮ謗ｨ貂ｬ螳溯｡後ｒ貂帙ｉ縺・|
| RT-UT-004 | `runtime/tests/test_corrective_action_report.py` | 6 | 6 | `runtime/workflow/corrective_action_report.py` | corrective action report context逋ｻ骭ｲ縲’ront matter隗｣譫舌《ection count縲《how/register CLI | 謾ｹ蝟・Ξ繝昴・繝医ｒ蠕檎ｶ喃ix workflow縺ｸ貂｡縺帙ｋ讒矩縺ｫ縺吶ｋ |
| RT-UT-005 | `runtime/tests/test_coverage_audit.py` | 6 | 6 | `runtime/tools/coverage_audit.py` | runtime module髮・ｨ医，LI讀懷・縲…overage螳溯｡後゛SON/Markdown蜃ｺ蜉帙《cript path load | runtime蜩∬ｳｪ繧堤ｶ咏ｶ夂屮譟ｻ縺吶ｋ閾ｪ蟾ｱ險ｺ譁ｭ繧呈髪縺医ｋ |
| RT-UT-006 | `runtime/tests/test_ctl_help.py` | 36 | 36 | `runtime/ctl.py` | `aiwfctl help`縲～aiwfctl doctor`縲～aiwfctl knowledge`縲‘nv驕ｸ謚槭∵､懃ｴ｢縲∬ｭｦ蜻願牡縲，ontext First蛻晄悄蛹悶〉egistry蜿ら・ | 蟾ｨ螟ｧ蛹悶＠縺毆orkflow繧辰LI邏｢蠑輔°繧芽ｿｷ繧上★蜻ｼ縺ｹ繧九ｈ縺・↓縺吶ｋ |
| RT-UT-007 | `runtime/tests/test_dispatcher_context.py` | 12 | 12 | `runtime/workflow/dispatcher_context.py` | workflow/tool candidate scoring縲”uman check縲〉egistry fallback縲…ontext逕滓・ | Intent縺九ｉworkflow/tool驕ｸ螳壹∈騾ｲ繧dispatcher縺ｮ蛻､譁ｭ譬ｹ諡繧貞崋螳壹☆繧・|
| RT-UT-008 | `runtime/tests/test_docs_sync_workflow.py` | 11 | 11 | `runtime/workflow/docs_sync.py` | docs-sync init縲ヾCM context gate縲∥nalysis template縲！ssue body縲，LI dispatch | 螳溯｣・→docs蟾ｮ蛻・ｒdocs-only workflow縺ｨ縺励※螳牙・縺ｫ蛻・ｊ蜃ｺ縺・|
| RT-UT-036 | `runtime/tests/test_flutter_multiplatform.py` | 16 | 16 | `runtime/workflow/flutter_multiplatform.py`縲～runtime/ctl.py` | target譛ｪ謖・ｮ唏uman Check縲【aml/CLI target隱ｭ霎ｼ縲”ost OS蛻･build蜿ｯ蜷ｦ縲｜oilerplate螻暮幕縲」erify/build螳溯｡後‘vidence蝗槫庶縲仝ebDriver荳崎ｶｳ蛻・｡槭’inalize螳御ｺ・愛螳壹∥iwfctl蜈･蜿｣ | Flutter multi-platform髢狗匱縺ｧtarget/platform/build迺ｰ蠅・ｒ謗ｨ貂ｬ縺帙★縲∝ｮ溯ｩｦ鬨楢ｨｼ霍｡縺ｨ螳御ｺ・愛螳壹ｒContext First縺ｧ蠕檎ｶ嗹orkflow縺ｸ貂｡縺・|
| RT-UT-009 | `runtime/tests/test_github_knowledge_maintenance.py` | 18 | 18 | `runtime/workflow/github_knowledge_maintenance.py` | GitHub knowledge init縲｛peration gate縲》ool selection縲〉epair/sync/RAG candidate | GitHub諠・ｱ繧帝聞譛溽衍隴倩ｳ・肇蛹悶☆繧矩圀縺ｮhuman gate縺ｨ蜃ｺ蜉帙ｒ螳医ｋ |
| RT-UT-010 | `runtime/tests/test_github_runtime.py` | 31 | 35 | `runtime/github/*` | REST/GraphQL API縲！ssue菴懈・縲￣R菴懈・縲〕inked branch縲》itle/body逕滓・縲√お繝ｩ繝ｼ蠢懃ｭ・| GitHub mutation繧知ock縺ｧ螳牙・縺ｫ讀懆ｨｼ縺励∝ｮ蘗PI萓晏ｭ倥ｒ螻謇蛹悶☆繧・|
| RT-UT-011 | `runtime/tests/test_init_corrective_action_fix.py` | 7 | 7 | `runtime/workflow/init_corrective_action_fix.py` | corrective report隗｣豎ｺ縲［anifest蜆ｪ蜈医『ork蛻晄悄蛹悶〉eport context逋ｻ骭ｲ縲，LI | 謾ｹ蝟・Ξ繝昴・繝医°繧我ｿｮ豁｣workflow縺ｸ蜈･繧句・蜿｣繧貞ｮ牙ｮ壹＆縺帙ｋ |
| RT-UT-012 | `runtime/tests/test_intake_requirements.py` | 8 | 8 | `runtime/intake/intake_requirements.py` | requirement document逋ｺ隕九〉epository control縲〉eceipt縲…ontext蛻晄悄蛹悶…opy/move | 隕∽ｻｶ蜿励￠蜈･繧梧凾轤ｹ縺ｧrepository/branch/context繧貞崋螳壹☆繧・|
| RT-UT-013 | `runtime/tests/test_knowledge_capture.py` | 7 | 7 | `runtime/workflow/knowledge_capture.py` | PR譚先侭縲‥ocs/RAG蛟呵｣懊…ontext fallback縲…lose archive fallback縲〉eport逕滓・ | 螳御ｺ・ssue縺九ｉ遏･隴倥・PR繝ｻarchive譚先侭繧貞叙繧翫％縺ｼ縺輔↑縺・|
| RT-UT-014 | `runtime/tests/test_observability_metrics.py` | 17 | 17 | `runtime/observability/*` | monthly rotation, JSONL append, token/context/cost, evidence, Context First registration, non-fatal warning | Runtime metrics as bridge instrumentation: cost, context weight, and workflow health remain observable |
| RT-UT-015 | `runtime/tests/test_preflight.py` | 25 | 27 | `runtime/environment/preflight.py` | Docker縲￣ython縲｀SYS2縲´ocalty protocol縲（nstall approval縲｀arkdown report | 螳溯｡檎腸蠅・ｸ崎ｶｳ繧剃ｽ懈･ｭ蜑阪↓讀懷・縺励∽ｺｺ髢捺価隱阪↑縺励・install繧帝亟縺・|
| RT-UT-016 | `runtime/tests/test_pytest_ut_spec_sync.py` | 17 | 17 | `runtime/tools/pytest_ut_spec_sync.py` | pytest蜿朱寔邨先棡縺ｨUT莉墓ｧ俶嶌縺ｮ蜷梧悄遒ｺ隱阪∝・蜉帛､谺・・逕滓・縲］ode id豁｣隕丞喧縲∝ｷｮ蛻・､懃衍縲｀arkdown report縲，ontext First manifest逋ｻ骭ｲ | UT莉墓ｧ俶嶌縺継ytest螳滉ｽ薙°繧峨ぜ繝ｬ縺溘→縺阪↓讀懷・縺励√さ繝ｳ繝・く繧ｹ繝医・蜿ｯ隕ｳ貂ｬ諤ｧ繧剃ｿ昴▽ |
| RT-UT-017 | `runtime/tests/test_rag_artifact_migration.py` | 18 | 18 | `runtime/rag/migrate_retrieval_artifacts.py`縲～standardize_corrective_report_names.py` | retrieval artifact遘ｻ陦後ゞUID蛹悶｀arkdown jsonize縲〉eport蜷肴ｨ呎ｺ門喧縲∝盾辣ｧ譖ｴ譁ｰ | RAG雉・肇縺ｮ閧･螟ｧ蛹悶↓閠舌∴繧句多蜷阪・蜿ら・繝ｻ遘ｻ陦後ｒ螳医ｋ |
| RT-UT-018 | `runtime/tests/test_rag_build.py` | 8 | 8 | `runtime/rag/rag_build.py` | normalize/chunk/index/embed pipeline邨ｱ蜷医《tandardize蛻ｶ蠕｡縲．uckDB migration evidence縲…ontext逋ｻ骭ｲ縲，LI | RAG build繧剃ｸ雋ｫ縺励◆pipeline artifact縺ｨ縺励※谿九☆ |
| RT-UT-019 | `runtime/tests/test_rag_dispatcher.py` | 10 | 10 | `runtime/rag/rag_dispatcher.py` | query planning縲‥ispatch plan縲…ontext pack縲‘xecution-plan蜿ら・縲．uckDB backend縲〉un command | RAG讀懃ｴ｢縺九ｉworkflow/agent縺ｸ貂｡縺呎枚閼医ｒ螳牙ｮ壹＆縺帙ｋ |
| RT-UT-020 | `runtime/tests/test_rag_duckdb_store.py` | 15 | 15 | `runtime/rag/duckdb_store.py` | DuckDB schema逕滓・縲゛SON ingest縲‥uplicate skip縲《ame ID update縲［igration error邯咏ｶ壹∵ｨ呎ｺ穆ource rebuild縲［igration螻･豁ｴ縲∵､懃ｴ｢縲∝盾辣ｧ遒ｺ隱稿vidence縲，ontext JSON蜃ｺ蜉帙，LI蠅・阜 | file-based RAG artifact繧痴ource of truth縺ｫ縺励◆縺ｾ縺ｾ逕滓・read model縺ｸ螳牙・縺ｫ謚募ｽｱ縺吶ｋ |
| RT-UT-021 | `runtime/tests/test_rag_ingestion_optimizer.py` | 9 | 9 | `runtime/rag/ingestion_optimizer.py` | chunk蛟呵｣懆ｩ穂ｾ｡縲、CCEPT/REWRITE/HUMAN_CHECK/REJECT縲・vidence蜃ｺ蜉帙｝olicy fallback縲，LI蠅・阜 | RAG蜷ｸ蜿主燕縺ｫKnowledge蜩∬ｳｪ繧呈ｿｾ驕弱＠縲（ndex/embedding縺ｸ豬√☆譬ｹ諡繧呈ｮ九☆ |
| RT-UT-022 | `runtime/tests/test_rag_pipeline_units.py` | 23 | 23 | `runtime/rag/normalize_documents.py`縲～chunk_documents.py`縲～build_index.py`縲～embed_chunks.py` | normalize縲…hunk縲（ndex縲‘mbedding縲‥efensive fallback縲《cript path load | RAG pipeline縺ｮ譛蟆丞腰菴阪ｒ螳医ｊ縲∵悽譁・ｒ螟ｱ繧上↑縺・舞蜻ｽ邉ｸ繧堤｢ｺ隱阪☆繧・|
| RT-UT-023 | `runtime/tests/test_rag_retrieve_context.py` | 17 | 17 | `runtime/rag/retrieve_context.py` | JSONL隱ｭ霎ｼ縲》okenize縲〔eyword/semantic/hybrid search縲．uckDB backend縲｜udget蝨ｧ邵ｮ縲…ontext pack蜃ｺ蜉・| 髢狗匱蜑抗AG load縺ｧ蠢・ｦ√↑context繧貞ｮ牙・縺ｫ蝨ｧ邵ｮ縺励※貂｡縺・|
| RT-UT-024 | `runtime/tests/test_remaining_policy_vscode_runtime.py` | 26 | 26 | `runtime/workflow/human_gate_policy.py`縲～vscode_task_runner.py` | human gate registry縲∵価隱榊愛螳壹〃SCode task runner縲￣ATH譖ｴ譁ｰ縲．ocker/Go/MSYS2 helper | 莠ｺ髢捺価隱阪→VSCode螳溯｡瑚｣懷勧繧池untime縺九ｉ蜻ｼ縺ｹ繧句ｽ｢縺ｫ縺吶ｋ |
| RT-UT-025 | `runtime/tests/test_remaining_rag_scm_runtime.py` | 10 | 10 | `runtime/rag/jsonize_rag_tree.py`縲～runtime/scm/compare_requirements.py` | RAG tree jsonize縲《ource蜑企勁縲〉equirements豈碑ｼ・“it diff縲∥rtifact蜃ｺ蜉・| RAG/SCM縺ｮ谿句ｭ倬㍾隕［odule繧呈ｨｪ譁ｭ逧・↓螳医ｋ |
| RT-UT-026 | `runtime/tests/test_retrieval_runtime.py` | 16 | 23 | `runtime/retrieval/task_runner.py` | task plan讀懆ｨｼ縲‥ependency縲‥ry-run縲｝arallel/sequential縲〕ogs縲〉eports縲，LI | agent task螳溯｡瑚ｨ育判繧剃ｾ晏ｭ倬未菫ゅ▽縺阪〒螳牙・縺ｫ蜍輔°縺・|
| RT-UT-027 | `runtime/tests/test_scm_runtime.py` | 52 | 52 | `runtime/scm/*` | prepare repository縲（ssue branch縲｝ush縲…ommit縲｜ootstrap縲》oken askpass縲‥ry-run/non-dry-run | Git謫堺ｽ懊ｒremote mutation蜑肴署縺ｧ繧ょｮ牙・縺ｫmock繝ｻdry-run讀懆ｨｼ縺吶ｋ |
| RT-UT-028 | `runtime/tests/test_self_improvement_workflow.py` | 14 | 14 | `runtime/workflow/self_improvement.py`縲～skills/*/SKILL.md`縲～db/registries/registry.duckdb` | feedback report菴懈・縲？uman Review霑ｽ險倥！ssue body逕滓・縲‘vidence scaffold縲’eedback蜃ｺ蜉帛･醍ｴ・”elp registry螂醍ｴ・| Ariadne閾ｪ霄ｫ縺ｮworkflow謾ｹ蝟・呵｣懊ｒ螳牙・縺ｫ菫晏ｭ倥＠縲∵治逕ｨ蛻､譁ｭ縺九ｉ謾ｹ蝟Иssue縺ｸ縺､縺ｪ縺・|
| RT-UT-029 | `runtime/tests/test_sdk_analysis.py` | 11 | 11 | `runtime/workflow/sdk_analysis.py`縲～runtime/ctl.py` | SDK蜈･蜉孕kip縲［etadata謚ｽ蜃ｺ縲、WS/GCP cloud metadata謚ｽ蜃ｺ縲ヾtripe payment metadata謚ｽ蜃ｺ縲，ontext First逋ｻ骭ｲ縲゜nowledge JSON蛟呵｣懊《ecret蛟､髱槭さ繝斐・縲∝､夜Κdiscovery蛟呵｣懃函謌舌∥iwfctl蜈･蜿｣ | 隕∽ｻｶ螳夂ｾｩ蟾･遞九〒SDK繝励Ο繧ｰ繝ｩ繝繧貞ｮ牙・縺ｫ蜑榊・逅・＠縲∝､夜Κ髢｢騾｣雉・侭縺ｮ遒ｺ隱崎ｦｳ轤ｹ縺ｨ莠ｺ髢鍋｢ｺ隱阪′蠢・ｦ√↑謗｡逕ｨ蛻､譁ｭ繧定ｦ玖誠縺ｨ縺輔↑縺・|
| RT-UT-030 | `runtime/tests/test_system_integration.py` | 15 | 15 | `runtime/workflow/system_integration.py`縲～runtime/ctl.py` | 繧ｷ繧ｹ繝・Β邨ｱ蜷・ontext逕滓・縲ヾDK cloud/payment metadata隱ｭ蜿悶√お繝溘Η繝ｬ繝ｼ繧ｿ蛟呵｣懷・鬘槭‘mulator template螻暮幕縲‘mulator health/preflight縲！ntegration Test runbook逕滓・縲！ntegration Test evidence/finalize遒ｺ隱阪，ontext First逋ｻ骭ｲ縲∥iwfctl蜈･蜿｣ | 逕滓・繝ｻ謾ｹ菫ｮ繧ｳ繝ｼ繝峨ｒ蟇ｾ雎｡繧ｷ繧ｹ繝・Β縺ｸ閾ｪ辟ｶ縺ｫ邨ｱ蜷医＠縲√お繝溘Η繝ｬ繝ｼ繧ｿ縺ｨ譛ｬ逡ｪ蟾ｮ蛻・ｄ襍ｷ蜍募燕謠舌・谺關ｽ縲！ntegration Test謇矩・・譖匁乂縺輔∝ｮ御ｺ・愛螳壹・貍上ｌ繧定ｦ玖誠縺ｨ縺輔↑縺・|
| RT-UT-031 | `runtime/tests/test_svg_layout_modes.py` | 19 | 19 | `runtime/workflow/gui_mode.py`縲～web_svg_layout_mode.py` | SVG隗｣譫舌（nput claim縲￣yQt/QTest蛟呵｣懊ヽeact/Playwright蛟呵｣懊」alidation縲《elf-test | GUI/Web SVG蜈･蜉帙°繧臥判髱｢蛟呵｣懃函謌舌∪縺ｧ繧蜘orkflow諡｡蠑ｵ縺ｨ縺励※螳医ｋ |
| RT-UT-032 | `runtime/tests/test_vscode_environment_workflow.py` | 10 | 10 | `runtime/workflow/vscode_environment.py` | self-provision縲‥raft/open questions縲ヽAG template縲〉equirements縲」alidation縲，LI | AI workflow螳溯｡檎腸蠅・ｒVSCode workspace as code縺ｨ縺励※謨ｴ縺医ｋ |
| RT-UT-033 | `runtime/tests/test_vscode_workspace.py` | 2 | 2 | `.vscode/*`縲～runtime/tools/aiwfctl.cmd` | aiwfctl PATH task縲…md usage | VSCode縺九ｉ`aiwfctl`繧定ｿｷ繧上★蜻ｼ縺ｹ繧句ｰ守ｷ壹ｒ螳医ｋ |
| RT-UT-034 | `runtime/tests/test_workflow_doctor.py` | 25 | 25 | `runtime/workflow/workflow_doctor.py` | tracked policy縲〉equired files縲”uman gate registry縲…lose archive completeness縲ゞT莉墓ｧ俶嶌蜷梧悄繝√ぉ繝・け縲’ail-on-warning | workflow repository閾ｪ霄ｫ縺ｮ蛛･蠎ｷ險ｺ譁ｭ繧定・蜍募喧縺吶ｋ |
| RT-UT-035 | `runtime/tests/test_workflow_state_noise_validation.py` | 20 | 20 | `runtime/workflow/workflow_state.py`縲～noise_reduction.py`縲～validate_output_language.py`縲～validate_vscode_workspace.py` | workflow state縲］oise reduction縲゛apanese output guard縲〃SCode workspace JSON讀懆ｨｼ | 隕∽ｻｶ螳夂ｾｩ蜑榊・逅・・迥ｶ諷狗ｮ｡逅・・蜃ｺ蜉幄ｨ隱槫刀雉ｪ繧貞ｮ医ｋ |

## 隕ｳ轤ｹ蛻･縺ｮ蟇ｾ蠢懃ｯ・峇

| 隕ｳ轤ｹ | 荳ｻ縺ｪpytest file |
| --- | --- |
| Context First / dispatcher | `test_context_first.py`, `test_dispatcher_context.py`, `test_ctl_help.py` |
| Workflow lifecycle | `test_intake_requirements.py`, `test_corrective_action_report.py`, `test_init_corrective_action_fix.py`, `test_knowledge_capture.py`, `test_docs_sync_workflow.py`, `test_self_improvement_workflow.py` |
| RAG pipeline / retrieval | `test_rag_pipeline_units.py`, `test_rag_build.py`, `test_rag_ingestion_optimizer.py`, `test_rag_duckdb_store.py`, `test_rag_retrieve_context.py`, `test_rag_dispatcher.py`, `test_rag_artifact_migration.py`, `test_remaining_rag_scm_runtime.py` |
| SCM / GitHub mutation boundary | `test_scm_runtime.py`, `test_github_runtime.py`, `test_github_knowledge_maintenance.py` |
| Environment / VSCode / preflight | `test_preflight.py`, `test_remaining_policy_vscode_runtime.py`, `test_vscode_environment_workflow.py`, `test_vscode_workspace.py` |
| GUI / Web SVG workflow extension | `test_svg_layout_modes.py` |
| Flutter multi-platform workflow | `test_flutter_multiplatform.py` |
| Runtime quality guard | `test_coverage_audit.py`, `test_pytest_ut_spec_sync.py`, `test_self_improvement_workflow.py`, `test_workflow_doctor.py`, `test_workflow_state_noise_validation.py` |

## 驕狗畑繝ｫ繝ｼ繝ｫ

- 縺薙・陦ｨ縺ｯ `runtime/tests` 縺ｮUT鬆・岼繧剃ｺｺ髢薙′謚頑升縺吶ｋ縺溘ａ縺ｮ蜿ｰ蟶ｳ縺ｧ縺吶・
- pytest node蜊倅ｽ阪・螳悟・縺ｪ螳溯｡御ｸ隕ｧ縺ｯ `pytest --collect-only -q tests` 繧呈ｭ｣縺ｨ縺励∪縺吶・
- test function謨ｰ縺ｨcollected tests謨ｰ縺檎焚縺ｪ繧句ｴ蜷医・縲～pytest.mark.parametrize` 縺ｫ繧医▲縺ｦ1縺､縺ｮ髢｢謨ｰ縺九ｉ隍・焚case縺悟庶髮・＆繧後※縺・∪縺吶・
- runtime縺ｮ驥崎ｦ，LI縲，ontext First gate縲ヾCM/GitHub mutation蠅・阜縲ヽAG pipeline縲；UI/SVG workflow繧貞､画峩縺励◆蝣ｴ蜷医・縲∬ｩｲ蠖楢｡後・UT隕ｳ轤ｹ繧呈峩譁ｰ縺励∪縺吶・
- coverage縺ｮ謨ｰ蛟､螻･豁ｴ縺ｯ縲〉oot逶ｴ荳九・ `Runtime pytest 蛻・ｲ舌・CLI繝ｻcoverage逶｣譟ｻ繝ｬ繝昴・繝・md` 縺ｫ霑ｽ險倥＠縺ｾ縺吶・
