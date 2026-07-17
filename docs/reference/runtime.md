# Runtime

`runtime/` は、workflow を実行・補助するための処理機能を置く場所です。

## Runtime Areas

| Directory | Purpose |
| --- | --- |
| `runtime/common/` | intake / retrieval / scmで共通利用するutility |
| `runtime/environment/` | tool / package preflight とinstall list作成 |
| `runtime/github/` | GitHub Issue draft / create |
| `runtime/intake/` | 要件定義書の受付とwork directory初期化 |
| `runtime/rag/` | report normalization、chunking、index、retrieval |
| `runtime/retrieval/` | sequential / parallel task runner |
| `runtime/scm/` | repository sync、branch、commit、push |
| `runtime/workflow/` | docs-sync、corrective-action-fix、GaC/UaC GUI mode、Web SVG Layout mode、Flutter Multi-platform、knowledge-captureの補助CLI |

## Common CLI

| Script | Responsibility |
| --- | --- |
| `runtime/ctl.py` | `runtime/tools/aiwfctl.cmd` から呼び出される `aiwfctl help` / `aiwfctl env` の実体。help検索、Environment Dispatcher、`work/<work-id>/context/environment-selection.json` 作成を行う |
| `db/registries/registry.duckdb` | `aiwfctl env` が参照する利用者向けEnvironmentと内部Backend profile registry |
| `runtime/intake/intake_requirements.py` | `work/requirements/` の要件定義書を受付ID単位で移動し、初期contextを作る |
| `runtime/environment/preflight.py` | 必要tool / packageを確認し、install listを作る |
| `runtime/scm/prepare_repository.py` | target repository / branchを取得し、`scm-state.json` を作る |
| `runtime/scm/create_issue_branch.py` | GitHub上に `feature/issue-<number>` branchを作り、clone / checkoutする |
| `runtime/scm/commit_changes.py` | semantic commit messageでcommitする |
| `runtime/scm/push_branch.py` | human check承認後にpush recordを残してpushする |
| `runtime/github/issue_manager.py` | GitHub Issue draft / createを行う |
| `runtime/github/pull_request_manager.py` | Issue branch push後にPull Request draft / createを行う |
| `runtime/scm/bootstrap_repository.py` | precreated-new repository modeで初期git repository化、initial branch push recordを作る |
| `runtime/workflow/docs_sync.py` | docs-syncのcontext、analysis scaffold、Issue bodyを作る |
| `runtime/workflow/github_knowledge_maintenance.py` | GitHub knowledge maintenanceのcontext、analysis scaffold、repair plan、small rebase detection / plan / approved apply、GitHub sync plan / approved apply、RAG candidateを作る |
| `runtime/workflow/init_corrective_action_fix.py` | corrective-action-fixのbase / issue work folderを初期化する |
| `runtime/workflow/vscode_environment.py` | VSCode Environment workflowのwork folder、requirements scaffold、validation scaffoldを作る |
| `runtime/workflow/gui_mode.py` | `work/requirements/svg-input/<PREFIX>_*.svg`をIssueへ取り込み、GUI設計、PyQt6候補、QTest候補を`gac-uac/`へ生成・検証する |
| `runtime/workflow/web_svg_layout_mode.py` | `work/requirements/svg-input/WEB_<PREFIX>_*.svg`をIssueへ取り込み、Web layout、React候補、Playwright候補を`web-ui/`へ生成・検証する |
| `runtime/workflow/flutter_multiplatform.py` | Flutter target宣言、host OS別build可否、boilerplate選択、静的解析/test/build計画、Flutter contextとreportを生成する |
| `runtime/workflow/knowledge_capture.py` | PR材料、knowledge capture report、archive readinessを作り、target repository側の `docs/evidence/<issue-id>/` scaffoldを自動生成する |
| `runtime/workflow/close_archive.py` | `work/close/<category>/<archive-id>`を軽量なreport-only archiveとして作成、監査、承認付きpruneする |
| `runtime/workflow/noise_reduction.py` | 要件定義前の不明ワード、Critical項目不足、曖昧表現を抽出し、Human InterviewとReadinessを生成する |
| `runtime/workflow/sdk_analysis.py` | 要件定義工程で `work/requirements/sdk/` のSDKプログラムを事前解析し、SDK分析context、外部関連資料discovery context、要件追記候補、Knowledge JSON候補を生成する。AWS/GCPはcloud metadata、Stripeはpayment metadataとして専用Human Checkを出す |
| `runtime/workflow/system_integration.py` | 対象repositoryの統合ポイント、既存試験/evidence、SDK cloud/payment metadata、エミュレータ候補、本番差分、Human Check、Knowledge化対象、エミュレータtemplate health、Integration Test runbook、最終Evidence判定を整理する |
| `runtime/workflow/iac_template.py` | Infrastructure boilerplateを `work/<work-id>/source/infrastructure/` へコピーし、非破壊health checkとContext First evidenceを生成する |
| `runtime/workflow/workflow_state.py` | workflowの現在地を `context/workflow-state.json` として標準化する |
| `runtime/workflow/context_first.py` | Context First manifestを作成・確認し、必須Dispatcher Context不足時にHuman Checkへ戻す |
| `runtime/workflow/human_gate_policy.py` | 人間承認が必要な操作をregistryで確認する |
| `runtime/workflow/workflow_doctor.py` | workflow repositoryの軽量診断を行う |
| `runtime/workflow/validate_output_language.py` | 生成済みMarkdownが英語主体になっていないか検出する |
| `runtime/tools/text_encoding_convert.py` | Markdown / JSON / Python などのtext fileをhex preview / encoding別decode previewで確認し、指定encodingでstrict decodeしてUTF-8へ安全変換する |
| `runtime/tools/text_encoding_guard.py` | UTF-8として読んだtextのdecode errorと不可逆欠落を検出する。固定の文字化けmarker判定は行わない |
| `runtime/rag/rag_dispatcher.py` | 複数queryのRAG loadを計画・実行・集約する |

## Environment Files

GitHub / SCM 連携で必要な値は、repository root の環境ファイルで管理します。

```text
.env.example   共有可能なキー一覧
.env           ローカル実値、commit禁止
.gitignore     .env と .env.* を除外し、.env.example は追跡対象
```

現行キー:

```env
GITHUB_OWNER=
GITHUB_TOKEN=
```

`GITHUB_OWNER` を設定すると、`localty-system-gui` のようなrepository名だけの指定を `<GITHUB_OWNER>/localty-system-gui` として解決できます。

案件ごとに変わるrepositoryは `.env` に置きません。要件定義書の `Repository Control` またはworkflow inputを source of truth にします。

## GitHub Issue Body

`runtime/github/issue_manager.py` は、Issue bodyを次の優先順位で選びます。

1. `--body-file` で明示されたMarkdown
2. target repository の `.github/ISSUE_TEMPLATE.md`
3. runtime fallback body

GitHub APIで実Issueを作るのは `--create` 指定時だけです。

Issue title は workflow に応じて `[新規機能フロー]`、`[改善フロー]`、`[初期開発]`、`[IaC]` のprefixを付けます。

## Pull Request

Issue branch push後、`runtime/github/pull_request_manager.py` で `develop` へのPull Requestを作成します。

Pull Request title はGitHub Issue titleを使用します。

Pull Request bodyには、変更点のMermaid式sequence diagramを含めます。

## Validation Note

Windows環境では `python` / `py` がStore aliasに当たる場合があります。

このrepoでは検証時に次を優先します。

```powershell
uv run --project runtime python <script>
```

pytest / coverage は `runtime/pyproject.toml` の `dev` dependency groupで管理します。

```powershell
cd runtime
uv run --group dev pytest -q
uv run --group dev coverage run --branch -m pytest
uv run --group dev coverage report -m
```

`uv` がPATHにない場合は、Ariadne runtime toolsのPATHを登録します。

```powershell
.\runtime\tools\register-uv-path.cmd --shell
```

`runtime\tools\uv.cmd` は、実uvが見つからない場合にinstall guidanceを表示します。

生成物の既定言語を確認する場合:

```powershell
uv run --project runtime python runtime/workflow/validate_output_language.py `
  --paths work rag docs `
  --fail-on-violation
```
