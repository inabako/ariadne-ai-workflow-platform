# Runtime Health Check Skill

## 目的

ユーザーが `/runtime-health-check` を選択した場合、または Ariadne AI Workflow Platform 自身の自己診断を依頼した場合に、この skill を使います。

この workflow は、target application repository ではなく、Ariadne の workflow platform runtime そのものの健全性を確認します。

## 対象範囲

この workflow では、次を確認します。

- runtime pytest
- UT仕様書と pytest 実体の同期
- `workflow_doctor`
- `aiwfctl doctor`
- Context First `test-evidence` 登録
- 人間が読める runtime quality report
- 日本語 Markdown 出力ガード

GitHub Actions workflow は作成しません。

## 入力

必須引数はありません。

任意引数:

- `work_id`: Context First evidence 登録用の work id。既定値は `runtime-health-check`。
- `report_dir`: report 出力先。既定値は `runtime/.pytest_cache`。

## 標準実行

特に指定がない限り、repository root から開始します。

`<repository-root>` は現在の Ariadne repository checkout root を指します。
`<uv-command>` は、Windows では `runtime/windows-script/uv.cmd`、macOS / Linux / WSL では PATH 上の `uv` を指します。

```shell
cd <repository-root>
```

workflow execution trace を開始します。

```shell
<uv-command> run --project runtime --group dev python runtime/ctl/ctl.py --repo-root . trace begin --workflow /runtime-health-check
```

runtime pytest を実行します。

```shell
<uv-command> run --project runtime --group dev pytest -c runtime/pytest.ini runtime/tests -q
```

UT仕様書同期チェックを実行し、Context First test evidence として登録します。

```shell
<uv-command> run --project runtime --group dev python runtime/tools/pytest_ut_spec_sync.py --spec docs/reference/runtime-pytest-ut/case-specification.md --runtime-root runtime check --repo-root . --work-dir runtime/.pytest_cache/runtime-health-check --report runtime/.pytest_cache/pytest-ut-spec-sync-report.json --markdown runtime/.pytest_cache/pytest-ut-spec-sync-report.md --register-context --required-context
```

workflow doctor を実行します。

```shell
<uv-command> run --project runtime --group dev python runtime/workflow/workflow_doctor.py --repo-root . --fail-on-warning
```

aiwfctl doctor を実行します。

```shell
<uv-command> run --project runtime --group dev python runtime/ctl/ctl.py --repo-root . doctor --json --fail-on-warning
```

warning が明示的に修復可能な場合だけ、repair option を指定して実行します。

```shell
cd <repository-root>

<uv-command> run --project runtime --group dev python runtime/ctl/ctl.py --repo-root . doctor --repair-spec-index --repair-encoding --fail-on-warning
```

`--repair-spec-index` は、pytest collection には存在するが `docs/reference/runtime-pytest-ut/cases/*.md` に未登録の node id に対して、最小限の UT仕様 case scaffold を生成します。health check 完了扱いにする前に、生成された Confirm / Input / Expected の内容を必ず確認してください。

`--repair-encoding` は、UTF-8 BOM と安全に復元可能な text-boundary finding だけを修復します。repair 後は `aiwfctl doctor --json --fail-on-warning` を再実行してください。

日本語 Markdown ガードを実行します。

```shell
<uv-command> run --project runtime --group dev python runtime/workflow/validate_output_language.py --paths docs/reference/runtime-pytest-ut/test-items.md docs/reference/runtime-pytest-ut/case-specification.md .ariadne/schemas/README.md .ariadne/agents/runtime-quality-gate-agent.prompt.md --fail-on-violation
```

すべての確認が終わったら、workflow execution trace を終了します。

```shell
<uv-command> run --project runtime --group dev python runtime/ctl/ctl.py --repo-root . trace end
```

## 停止条件

次のいずれかに該当する場合は停止し、原因と次の修正対象を報告します。

- pytest が失敗した。
- UT仕様書同期チェックで missing、stale、order mismatch、input-position mismatch が出た。
- Context First `test-evidence` 登録に失敗した。
- `workflow_doctor --fail-on-warning` が失敗した。
- `aiwfctl doctor --fail-on-warning` が失敗した。
- repair を実行したが、修復された artifact の人間レビューが未完了である。
- 日本語 Markdown ガードが失敗した。

## 出力

想定する local output は次のとおりです。

- `runtime/.pytest_cache/pytest-ut-spec-sync-report.json`
- `runtime/.pytest_cache/pytest-ut-spec-sync-report.md`
- `runtime/.pytest_cache/runtime-health-check/context/context-manifest.json`

これらは local evidence artifact であり、Git 管理対象にはしません。

## 完了条件

標準コマンドがすべて pass し、最終報告に次が含まれている場合に完了です。

- pytest 件数
- UT仕様書同期ステータス
- doctor ステータス
- aiwfctl doctor ステータス
- repair option を使った場合の repair count と修復 artifact 概要
- workflow execution trace id
- Context First `test-evidence` path
- 残 warning がある場合は、その内容

## Workflow Feedback Output

AI workflow 実行中に再利用可能な摩擦や改善候補を見つけた場合は、`work/feedback/` に記録します。

曖昧さ、繰り返し発生する確認、context / docs 不足、runtime observation gap、handoff のノイズ、encoding 問題、workflow 改善候補を観測した場合は、Feedback report を作成または更新してください。

新しい report を作成する場合は、既存 helper を使います。

```powershell
<uv-command> run --project runtime python runtime/ctl/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "<slash-command>" `
  --reporter "AI workflow" `
  --situation "<what was happening>" `
  --friction "<observed friction>" `
  --impact "<impact on quality, speed, or safety>" `
  --proposed-improvement "<candidate improvement>"
```

初期 `Review Status` は `Proposed` のままにします。この workflow の中で `/self-improvement` を自動実行しません。Do not run `/self-improvement` automatically. `/self-improvement` は、feedback が蓄積し、人間が Accepted / Rejected / Deferred の判断を行う準備ができてから実行します。
