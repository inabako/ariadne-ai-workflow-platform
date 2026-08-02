# test_iac_template.py

This file lists pytest node id based UT cases for `runtime/tests/test_iac_template.py`.

| Item | Value |
| --- | ---: |
| cases | 6 |

## Cases

#### RT-UT-CASE-IAC-001

- pytest node id:

```text
runtime/tests/test_iac_template.py::test_iac_template_list_includes_opentelemetry_collector
```

- 確認内容: IaC template catalogにOpenTelemetry Collector templateが含まれ、source template directoryが存在することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_iac_template.py:12`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: `opentelemetry-collector` appears in the template list with `exists=true`.

#### RT-UT-CASE-IAC-002

- pytest node id:

```text
runtime/tests/test_iac_template.py::test_iac_template_prepare_copies_opentelemetry_template
```

- 確認内容: `prepare_template` copies the OpenTelemetry Collector template into the work infrastructure area and writes Context First setup evidence.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_iac_template.py:20`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: copied template files, `iac-template-context.json`, and `iac-template-setup` manifest context exist.

#### RT-UT-CASE-IAC-003

- pytest node id:

```text
runtime/tests/test_iac_template.py::test_iac_template_prepare_preserves_existing_copy_without_force
```

- 確認内容: prepare does not overwrite an existing copied template unless `force` is explicitly used.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_iac_template.py:40`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: status is `existing` and the marker file remains unchanged.

#### RT-UT-CASE-IAC-004

- pytest node id:

```text
runtime/tests/test_iac_template.py::test_iac_template_health_checks_copied_template
```

- 確認内容: health verifies the copied template contract without starting Docker, Terraform, or Collector processes.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_iac_template.py:58`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: all file and directory checks are `ready`, health context/evidence are written, and `iac-template-health` is registered.

#### RT-UT-CASE-IAC-005

- pytest node id:

```text
runtime/tests/test_iac_template.py::test_iac_template_tool_preflight_uses_terraform_env_path
```

- 確認内容: Terraform CLIがPATH上にない場合でも、repo `.env` の `AIWF_TERRAFORM_EXE` からIaC template health用のtool preflightがTerraformを検出する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_iac_template.py:82`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: Terraformは`available=true`かつ`AIWF_TERRAFORM_EXE`のpathで検出され、ENVを持たないDockerは未検出になる。

#### RT-UT-CASE-IAC-006

- pytest node id:

```text
runtime/tests/test_iac_template.py::test_aiwfctl_iac_template_prepare_and_health
```

- 確認内容: `aiwfctl iac template prepare` and `aiwfctl iac template health` route to the runtime helper.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_iac_template.py:98`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `prepare_args`, `health_args`
- 期待結果: CLIが成功終了し、templateをコピーし、health context pathを出力する。
