# Runtime

`runtime/` は、workflow を実行・補助するための処理機能を置く場所です。

## Official Runtime Entrypoint

通常のworkflow実行では、`aiwfctl` / `runtime/ctl/ctl.py` を正式入口として使います。

- 共通policyは `.ariadne/shared/runtime-entrypoint-policy.md` です。
- `runtime/workflow/*.py` は内部実装moduleです。runtime開発や単体テストを除き、workflow手順・SKILL・agent promptから直接実行しません。
- Context First は `aiwfctl context ...` で確認します。
- Human Check registry は `aiwfctl human-gate ...` で確認します。
- GitHub knowledge maintenance は `aiwfctl github-knowledge ...` で実行します。
- close archive は `aiwfctl close-archive ...` で実行します。
- self-improvement feedback は `aiwfctl self-improvement ...` で実行します。

必要な操作が `aiwfctl` に存在しない場合は、その場で握りつぶさず、まず `aiwfctl self-improvement create-feedback` でFeedback reportを作成します。Human ReviewでAcceptedになったFeedbackだけを、後続の正式な改修候補にします。active workflow内で黙って `runtime/ctl/ctl.py` を拡張してはいけません。workflow側に新しい `python runtime/workflow/*.py ...` の直叩き手順を増やしてはいけません。

## Windows 11 PowerShell Runtime

Windows 11 で AI workflow を実行する場合は、まず PowerShell native runtime を使います。

```powershell
.\runtime\windows-script\aiwf.cmd help
.\runtime\windows-script\aiwf.cmd ctl help search github knowledge
.\runtime\windows-script\aiwf.cmd pytest -q
.\runtime\windows-script\aiwf.cmd spec-check
```

`runtime/windows-script/aiwf.cmd` はPATH登録しやすいWindows向け入口です。内部では `runtime/windows-script/aiwf.ps1` を process scoped `-ExecutionPolicy Bypass` 付きで呼び出すため、利用者のPowerShell policyを恒久変更せずに実行できます。

`runtime/windows-script/aiwf.ps1` は PowerShell の UTF-8 no BOM 入出力、repo root / runtime root 解決、`uv run ... python ...` の固定だけを担当します。Context First、Human Check、GitHub knowledge maintenance などの workflow 判断は引き続き `aiwfctl` / `runtime/ctl/ctl.py` が担当します。

不足している操作がある場合は、PS1 に直接 workflow logic を増やさず、まず self-improvement Feedback に流します。Accepted Feedback になった後でのみ、`runtime/ctl/ctl.py` の正式入口改修候補にします。

## POSIX Bash Runtime

Linux / WSL / macOS で AI workflow を実行する場合は、まず bash native runtime を使います。

```bash
./runtime/posix-bash/aiwf.sh help
./runtime/posix-bash/aiwf.sh ctl help search github knowledge
./runtime/posix-bash/aiwf.sh pytest -q
./runtime/posix-bash/aiwf.sh spec-check
```

`runtime/posix-bash/aiwf.sh` は Bash の `set -Eeuo pipefail`、repo root / runtime root 解決、`PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8`、`uv run ... python ...` の固定だけを担当します。Context First、Human Check、GitHub knowledge maintenance などの workflow 判断は引き続き `aiwfctl` / `runtime/ctl/ctl.py` が担当します。

不足している操作がある場合は、bash に直接 workflow logic を増やさず、まず self-improvement Feedback に流します。Accepted Feedback になった後でのみ、`runtime/ctl/ctl.py` の正式入口改修候補にします。

## GitHub CLI Preflight

GitHub metadata / sync workflow では、`gh --version` と `gh auth status` を別々に判定します。
Windows 11 では次を正式入口にします。

```powershell
.\runtime\windows-script\aiwf.cmd preflight --profile github-cli --work-id "<work-id>"
```

未ログインで `GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_API_TOKEN` / `GITHUB_API_KEY` が repository `.env` または process ENV にある場合は、次で `gh auth login --with-token` と `gh auth setup-git` を実行します。token値はreportへ出力しません。

```powershell
.\runtime\windows-script\aiwf.cmd preflight --profile github-cli --gh-login-from-env --human-check approved
```

GitHub passwordをENVに保存しません。GitHub CLI/API と git remote の認証情報はtokenを共用できますが、runtimeは値をログ出力しないことを前提に扱います。

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
| `runtime/ctl/ctl.py` | `runtime/windows-script/aiwfctl.cmd` から呼び出される `aiwfctl help` / `aiwfctl env` の実体。help検索、Environment Dispatcher、`work/<work-id>/context/environment-selection.json` 作成を行う |
| `db/registries/registry.duckdb` | `templates/registries/*.json` から再生成されるruntime registry read model。`aiwfctl help`、`aiwfctl env`、Context First Tool Dispatcher、Human Gate Policy、Workflow Doctor が参照する |
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
| `runtime/rag/semantic_hints.py` | project固有のsemantic hintを生成し、RAG source化、build、読み取りへ接続する |
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

## UTF-8 BOM Tool

```powershell
.\runtime\windows-script\aiwf.cmd ctl tools bom-scan --paths skills .github docs runtime --extensions .md .py .json .yaml .yml --fail-on-finding
.\runtime\windows-script\aiwf.cmd ctl tools bom-strip --paths skills .github docs runtime --extensions .md .py .json .yaml .yml --write
```

## Workflow Doctor Repair

`aiwfctl doctor` は workflow repository 自身のhealth checkを行います。通常は検出のみを行い、warningが残る場合は `--fail-on-warning` で非ゼロ終了できます。

```powershell
.\runtime\windows-script\aiwfctl.cmd doctor --json --fail-on-warning
```

修復可能な項目は、明示的にrepair optionを付けた場合だけ書き換えます。

```powershell
.\runtime\windows-script\aiwfctl.cmd doctor `
  --repair-spec-index `
  --repair-encoding `
  --fail-on-warning
```

- `--repair-spec-index`: pytest collectionに存在するがUT仕様書に未登録のnode idについて、`docs/reference/runtime-pytest-ut/cases/*.md` にcase scaffoldを追加します。
- `--repair-encoding`: UTF-8 BOMや安全に復元可能なtext-boundary findingを修復します。

通常表示では `Repair Count` と `Repairs` セクションに、どのrepair artifactが何件処理したかを表示します。JSON出力では `repairs[]` に詳細が残ります。

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
ARIADNE_KNOWLEDGE_REPOSITORY=ariadne-knowledge-platform
```

`GITHUB_OWNER` を設定すると、`target-system` のようなrepository名だけの指定を `<GITHUB_OWNER>/target-system` として解決できます。

案件ごとに変わるrepositoryは `.env` に置きません。要件定義書の `Repository Control` またはworkflow inputを source of truth にします。

## GitHub Issue Body

`aiwfctl github issue` は、Issue bodyを次の優先順位で選びます。

1. `--body-file` で明示されたMarkdown
2. target repository の `.github/ISSUE_TEMPLATE.md`
3. runtime fallback body

GitHub APIで実Issueを作るのは `--create` 指定時だけです。

Issue title は workflow に応じて `[新規機能フロー]`、`[改善フロー]`、`[初期開発]`、`[IaC]` のprefixを付けます。

## Pull Request

Issue branch push後、`aiwfctl github pr` で `develop` へのPull Requestを作成します。

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
.\runtime\windows-script\register-uv-path.cmd --shell
```

`runtime\windows-script\uv.cmd` は、実uvが見つからない場合にinstall guidanceを表示します。

生成物の既定言語を確認する場合:

```powershell
.\runtime\windows-script\aiwf.cmd ctl workflow validate-output-language check `
  --paths work rag docs `
  --fail-on-violation
```
