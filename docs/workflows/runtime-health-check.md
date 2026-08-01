# Runtime Health Check

`/runtime-health-check` は、Ariadne AI Workflow Platform 自身の健全性を確認する自己診断workflowです。

通常の開発workflowがtarget repositoryを扱うのに対し、このworkflowは `runtime/`、`runtime/tests/`、`docs/reference/`、Context First、`aiwfctl`、schema、agent prompt の整合性を確認します。

## 使う場面

- runtime配下を変更した後。
- pytestを追加、削除、renameした後。
- UT仕様書を更新した後。
- `aiwfctl`、`workflow_doctor`、Context First、schema、agent promptを変更した後。
- commit前にAIワークフロー基盤そのものの健康状態を確認したいとき。

## 実行担当

主担当Agent:

- `.ariadne/agents/runtime-quality-gate-agent.prompt.md`

このworkflowはGitHub Actionsではなく、Agentが明示的に実行します。

## 入力

必須引数はありません。

| 引数 | 必須 | 内容 |
| --- | --- | --- |
| `work_id` | no | Context First test-evidence登録用のwork id。既定は `runtime-health-check` |
| `report_dir` | no | report出力先。既定は `runtime/.pytest_cache` |

## 実行内容

```text
runtime pytest
  ↓
UT仕様書同期チェック
  ↓
JSON / Markdown report生成
  ↓
Context First manifestへ test-evidence 登録
  ↓
workflow_doctor
  ↓
aiwfctl doctor
  ↓
日本語Markdown品質ガード
  ↓
pass / fail 報告
```

## 標準コマンド

`<repository-root>` は現在の Ariadne repository checkout root を指します。
`<uv-command>` は、Windows では `runtime/windows-script/uv.cmd`、macOS / Linux / WSL では PATH 上の `uv` を指します。

```shell
cd <repository-root>

<uv-command> run --project runtime --group dev python runtime/ctl/ctl.py --repo-root . trace begin --workflow /runtime-health-check

<uv-command> run --project runtime --group dev pytest -c runtime/pytest.ini runtime/tests -q

<uv-command> run --project runtime --group dev python runtime/tools/pytest_ut_spec_sync.py --spec docs/reference/runtime-pytest-ut/case-specification.md --runtime-root runtime check --repo-root . --work-dir runtime/.pytest_cache/runtime-health-check --report runtime/.pytest_cache/pytest-ut-spec-sync-report.json --markdown runtime/.pytest_cache/pytest-ut-spec-sync-report.md --register-context --required-context

<uv-command> run --project runtime --group dev python runtime/workflow/workflow_doctor.py --repo-root . --fail-on-warning

<uv-command> run --project runtime --group dev python runtime/ctl/ctl.py --repo-root . doctor --json --fail-on-warning

<uv-command> run --project runtime --group dev python runtime/workflow/validate_output_language.py --paths docs/reference/runtime-pytest-ut/test-items.md docs/reference/runtime-pytest-ut/case-specification.md .ariadne/schemas/README.md .ariadne/agents/runtime-quality-gate-agent.prompt.md --fail-on-violation

<uv-command> run --project runtime --group dev python runtime/ctl/ctl.py --repo-root . trace end
```

UT仕様書のcase scaffold不足や安全に修復可能なtext boundary findingをまとめて修復する場合:

```shell
cd <repository-root>

<uv-command> run --project runtime --group dev python runtime/ctl/ctl.py --repo-root . doctor --repair-spec-index --repair-encoding --fail-on-warning
```

`--repair-spec-index` は pytest collection に存在するが `docs/reference/runtime-pytest-ut/cases/*.md` に未登録の node id に対して、最小限の case block を生成します。生成後は必ず内容を読み、Confirm / Input / Expected が人間に伝わる粒度になっているか確認してください。stale case の削除や意味のある説明文への書き換えは自動では行いません。

`--repair-encoding` は BOM 除去や安全に復元可能な文字境界findingのみを書き換えます。repair後も `aiwfctl doctor --json --fail-on-warning` を再実行し、`warning_count: 0` を確認してください。

## 出力

標準出力:

- pytest result
- UT仕様書同期チェック結果
- workflow doctor結果
- aiwfctl doctor結果
- 日本語Markdown品質チェック結果

local evidence:

- `runtime/.pytest_cache/pytest-ut-spec-sync-report.json`
- `runtime/.pytest_cache/pytest-ut-spec-sync-report.md`
- `runtime/.pytest_cache/runtime-health-check/context/context-manifest.json`

`runtime/.pytest_cache` 配下の生成物はGit管理しません。repository root 直下の `pytest.ini` と `.pytest_cache` は生成しません。

## 成功条件

- pytestが全件passする。
- UT仕様書同期チェックが `status: ok` を返す。
- `missing_in_spec`、`stale_in_spec`、`bad_input_position` が空である。
- `order_matches` が `true` である。
- `workflow_doctor --fail-on-warning` がpassする。
- `aiwfctl doctor --json --fail-on-warning` がpassする。
- 必要に応じて `aiwfctl doctor --repair-spec-index --repair-encoding --fail-on-warning` を実行し、repair結果を確認済みである。
- Context First manifestに `test-evidence` が登録される。
- 日本語Markdown品質ガードがpassする。

## 停止条件

次のいずれかが発生した場合、修正またはHuman Checkへ戻します。

- pytest failure。
- UT仕様書とpytest実体の不一致。
- `確認内容 / 入力値 / 期待結果` の位置ずれ。
- Context First manifestへの `test-evidence` 登録失敗。
- `workflow_doctor` warning。
- `aiwfctl doctor` warning。
- 日本語Markdown品質ガード違反。

## 位置づけ

このworkflowは、各workflowの最後に暗黙で実行される処理ではありません。

必要なタイミングで明示的に呼び出す、AIワークフロー基盤の自己ヘルスチェックです。
