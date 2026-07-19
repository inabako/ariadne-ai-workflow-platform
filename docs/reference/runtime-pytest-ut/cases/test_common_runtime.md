# test_common_runtime.py

このファイルは `runtime/tests/test_common_runtime.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 10 |

## ケース一覧

#### RT-UT-CASE-017

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_slugify_and_relative_to_repo_are_stable
```

- 確認内容: pytest case `slugify and relative to repo are stable` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:34`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-018

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_ensure_work_tree_creates_standard_directories
```

- 確認内容: pytest case `ensure work tree creates standard directories` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:45`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-019

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_artifact_index_upsert_replaces_existing_artifact
```

- 確認内容: pytest case `artifact index upsert replaces existing artifact` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:53`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-020

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_write_json_writes_utf8_json_with_parent_dirs
```

- 確認内容: pytest case `write json writes utf8 json with parent dirs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:65`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-021

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_common_root_receipt_json_and_markdown_edges
```

- 確認内容: pytest case `common root receipt json and markdown edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:73`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-022

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_env_line_and_repository_slug_normalization
```

- 確認内容: pytest case `env line and repository slug normalization` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:94`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-023

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_env_file_process_and_github_resolution_edges
```

- 確認内容: pytest case `env file process and github resolution edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:111`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-024

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_extract_repository_config_from_markdown_text
```

- 確認内容: pytest case `extract repository config from markdown text` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:140`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-025

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_defensive_specimen_repository_config_ignores_empty_values_and_remote_alias
```

- 確認内容: defensive specimen repository config ignores empty values and remote alias を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:158`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-026

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_requirement_config_files_and_artifact_index_edges
```

- 確認内容: pytest case `requirement config files and artifact index edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:170`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
