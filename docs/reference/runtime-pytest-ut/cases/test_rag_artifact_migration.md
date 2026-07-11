# test_rag_artifact_migration.py

このファイルは `runtime/tests/test_rag_artifact_migration.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 19 |

## ケース一覧

#### RT-UT-CASE-272

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_renames_legacy_json_and_rewrites_references
```

- 確認内容: pytest case `migrate retrieval artifacts renames legacy json and rewrites references` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:25`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `migrated_context`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-273

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_deletes_duplicate_markdown_for_migrated_companion
```

- 確認内容: pytest case `migrate retrieval artifacts deletes duplicate markdown for migrated companion` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:86`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-274

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_repairs_from_jsonized_wrapper
```

- 確認内容: pytest case `migrate retrieval artifacts repairs from jsonized wrapper` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:115`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `payload`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-275

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_defensive_specimen_migration_does_not_duplicate_existing_legacy_path
```

- 確認内容: defensive specimen migration does not duplicate existing legacy path を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:153`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `payload`
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-276

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_jsonizes_non_duplicate_markdown
```

- 確認内容: pytest case `migrate retrieval artifacts jsonizes non duplicate markdown` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:194`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `payload`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-277

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_parser_and_helper_edges
```

- 確認内容: pytest case `migrate retrieval artifacts parser and helper edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:221`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-278

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_missing_retrieval_dir_fails
```

- 確認内容: pytest case `migrate retrieval artifacts missing retrieval dir fails` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:277`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-279

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_delete_source_and_generic_artifact
```

- 確認内容: pytest case `migrate retrieval artifacts delete source and generic artifact` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:293`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `payload`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-280

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_jsonized_repair_skips_invalid_wrappers
```

- 確認内容: pytest case `migrate retrieval artifacts jsonized repair skips invalid wrappers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:321`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `wrappers`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-281

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_prunes_legacy_migration_outputs
```

- 確認内容: pytest case `migrate retrieval artifacts prunes legacy migration outputs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:367`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-282

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_delete_markdown_source_and_skip_readme
```

- 確認内容: pytest case `migrate retrieval artifacts delete markdown source and skip readme` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:422`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-283

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_main_paths
```

- 確認内容: pytest case `migrate retrieval artifacts main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:448`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-284

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_renames_legacy_report_and_updates_references
```

- 確認内容: pytest case `standardize report names renames legacy report and updates references` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:469`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-285

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_skips_already_standard_and_readme
```

- 確認内容: pytest case `standardize report names skips already standard and readme` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:511`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-286

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_rejects_source_dir_outside_repo
```

- 確認内容: pytest case `standardize report names rejects source dir outside repo` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:533`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-287

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_parser_and_helper_fallbacks
```

- 確認内容: pytest case `standardize report names parser and helper fallbacks` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:548`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-288

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_missing_dir_and_target_collision
```

- 確認内容: pytest case `standardize report names missing dir and target collision` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:607`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-289

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_replace_text_references_updates_supported_files
```

- 確認内容: pytest case `standardize report names replace text references updates supported files` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:633`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `old_rel`, `new_rel`, `files`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-290

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_main_paths
```

- 確認内容: pytest case `standardize report names main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:668`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
