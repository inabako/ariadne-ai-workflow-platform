# test_vscode_environment_workflow.py

このファイルは `runtime/tests/test_vscode_environment_workflow.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 10 |

## ケース一覧

#### RT-UT-CASE-510

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_build_parser_parses_all_commands
```

- 確認内容: pytest case `vscode environment build parser parses all commands` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:17`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-511

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_init_work_writes_state_and_runtime_context
```

- 確認内容: pytest case `vscode environment init work writes state and runtime context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:28`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `state`, `runtime_context`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-512

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_draft_template_and_discovery
```

- 確認内容: pytest case `vscode environment draft template and discovery` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:70`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-513

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_open_questions_records_drafts
```

- 確認内容: pytest case `vscode environment open questions records drafts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:88`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `open_questions`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-514

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_rag_filename_and_template
```

- 確認内容: pytest case `vscode environment rag filename and template` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:107`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-515

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_write_rag_template_requires_repo_local_source_dir
```

- 確認内容: pytest case `vscode environment write rag template requires repo local source dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:127`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-516

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_requirements_and_validation_templates
```

- 確認内容: pytest case `vscode environment requirements and validation templates` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:159`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `requirements`, `validation_json`, `validation_md`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-517

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_validation_markdown_empty_lists
```

- 確認内容: pytest case `vscode environment validation markdown empty lists` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:187`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-518

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_main_dispatch_success_and_error
```

- 確認内容: pytest case `vscode environment main dispatch success and error` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:200`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-519

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_main_dispatches_remaining_commands_and_script_load
```

- 確認内容: pytest case `vscode environment main dispatches remaining commands and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:215`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `commands`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
