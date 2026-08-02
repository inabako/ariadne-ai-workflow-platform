# test_rag_ctl_runtime.py

このファイルは `runtime/tests/test_rag_ctl_runtime.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 6 |

## ケース一覧

#### RT-UT-CASE-298A

- pytest node id:

```text
runtime/tests/test_rag_ctl_runtime.py::test_ctl_rag_retrieve_writes_context_pack_and_runtime_log
```

- 確認内容: `aiwfctl rag retrieve` がfile backendのchunk indexからcontext packを生成し、runtime logへ `rag retrieve` / `rag:retrieve` として記録することを確認する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ctl_runtime.py:31`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: temporary RAG chunks index, empty embeddings index, `ctl.build_parser().parse_args(...)`
- 期待結果: exit code が 0 で、context pack JSON が作成され、`logs/runtime/runtime-events.log` の最終イベントが `command=rag retrieve`、`operation_id=rag:retrieve` になる。

#### RT-UT-CASE-298B

- pytest node id:

```text
runtime/tests/test_rag_ctl_runtime.py::test_ctl_rag_jsonize_converts_sources
```

- 確認内容: `aiwfctl rag jsonize` がRAG source treeをUUID JSON wrapperへ変換できることを確認する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ctl_runtime.py:65`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: temporary `rag/note.md`, `ctl.build_parser().parse_args(...)`
- 期待結果: exit code が 0 で、`converted_count` が 1 になり、返却された `json_path` のartifactが存在する。

#### RT-UT-CASE-298C

- pytest node id:

```text
runtime/tests/test_rag_ctl_runtime.py::test_ctl_rag_migrate_legacy_root_moves_backup
```

- 確認内容: `aiwfctl rag migrate-legacy-root` がlegacy root RAG backupを標準RAG treeへ移動できることを確認する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ctl_runtime.py:92`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: temporary `legacy-root-rag-<timestamp>/chunks/one.json`, `ctl.build_parser().parse_args(...)`
- 期待結果: exit code が 0 で、`moved` に `chunks/one.json` が入り、標準RAG tree配下に移動後artifactが存在する。

#### RT-UT-CASE-298D

- pytest node id:

```text
runtime/tests/test_rag_ctl_runtime.py::test_ctl_rag_build_dry_run_reports_plan_without_writing_outputs
```

- 確認内容: `aiwfctl rag build --dry-run --output` がRAG build pipelineを実行せず、読み取り元と書き込み予定先をplanとして返し、plan JSONだけを保存することを確認する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ctl_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: temporary `rag/source/note.md`, `ctl.build_parser().parse_args(...)`
- 期待結果: exit code が0で、`artifact_type=rag-dry-run-plan`、`status=dry-run`、`would_run=false` となり、`rag/retrieval/build.json` にplan JSONが保存され、`rag/normalized` は作成されない。

#### RT-UT-CASE-298E

- pytest node id:

```text
runtime/tests/test_rag_ctl_runtime.py::test_ctl_rag_duckdb_rebuild_dry_run_reports_plan_without_creating_db
```

- 確認内容: `aiwfctl rag duckdb rebuild --dry-run --output` がDuckDB read modelを作成せず、rebuild予定をplanとして返し、plan JSONだけを保存することを確認する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ctl_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: temporary db path, `--source-repo`, `--reset`
- 期待結果: exit code が0で、`command=rag duckdb rebuild`、`reset=true` となり、`db/rag/knowledge.duckdb` は作成されない。

#### RT-UT-CASE-298F

- pytest node id:

```text
runtime/tests/test_rag_ctl_runtime.py::test_ctl_rag_semantic_hints_build_dry_run_reports_generation_and_build_outputs
```

- 確認内容: `aiwfctl rag semantic-hints build --dry-run` がsemantic hint source生成とRAG buildの予定をplanとして返すことを確認する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ctl_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: semantic hint backup/source/output path
- 期待結果: exit code が0で、`command=rag semantic-hints build` となり、semantic hint source directoryは作成されない。
