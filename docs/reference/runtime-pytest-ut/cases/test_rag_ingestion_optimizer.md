# test_rag_ingestion_optimizer.py

このファイルは `runtime/tests/test_rag_ingestion_optimizer.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 9 |

## ケース一覧

#### RT-UT-CASE-322

- pytest node id:

```text
runtime/tests/test_rag_ingestion_optimizer.py::test_ingestion_optimizer_accepts_complete_traceable_chunk
```

- 確認内容: pytest case `ingestion optimizer accepts complete traceable chunk` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ingestion_optimizer.py:69`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `optimized`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-323

- pytest node id:

```text
runtime/tests/test_rag_ingestion_optimizer.py::test_ingestion_optimizer_rewrites_noise_then_accepts
```

- 確認内容: pytest case `ingestion optimizer rewrites noise then accepts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ingestion_optimizer.py:99`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `rewritten_rows`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-324

- pytest node id:

```text
runtime/tests/test_rag_ingestion_optimizer.py::test_ingestion_optimizer_routes_governance_conflict_to_human_check
```

- 確認内容: pytest case `ingestion optimizer routes governance conflict to human check` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ingestion_optimizer.py:116`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `human_rows`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-325

- pytest node id:

```text
runtime/tests/test_rag_ingestion_optimizer.py::test_ingestion_optimizer_rejects_duplicates_and_credentials
```

- 確認内容: pytest case `ingestion optimizer rejects duplicates and credentials` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ingestion_optimizer.py:133`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `content`, `rejected`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-326

- pytest node id:

```text
runtime/tests/test_rag_ingestion_optimizer.py::test_ingestion_optimizer_helpers_and_cli_paths
```

- 確認内容: pytest case `ingestion optimizer helpers and cli paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ingestion_optimizer.py:149`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-327

- pytest node id:

```text
runtime/tests/test_rag_ingestion_optimizer.py::test_ingestion_optimizer_missing_and_invalid_policy_paths
```

- 確認内容: pytest case `ingestion optimizer missing and invalid policy paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ingestion_optimizer.py:174`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-328

- pytest node id:

```text
runtime/tests/test_rag_ingestion_optimizer.py::test_ingestion_optimizer_scoring_boundary_specimens
```

- 確認内容: pytest case `ingestion optimizer scoring boundary specimens` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ingestion_optimizer.py:195`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `empty_chunk`, `heading_chunk`, `low_trust_chunk`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-329

- pytest node id:

```text
runtime/tests/test_rag_ingestion_optimizer.py::test_ingestion_optimizer_rewrite_retry_limit_and_duplicate_line_specimen
```

- 確認内容: pytest case `ingestion optimizer rewrite retry limit and duplicate line specimen` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ingestion_optimizer.py:234`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `duplicate_text`, `rewrite_policy`, `chunk`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-330

- pytest node id:

```text
runtime/tests/test_rag_ingestion_optimizer.py::test_ingestion_optimizer_clean_output_empty_run_and_invalid_chunk_specimens
```

- 確認内容: pytest case `ingestion optimizer clean output empty run and invalid chunk specimens` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ingestion_optimizer.py:277`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
