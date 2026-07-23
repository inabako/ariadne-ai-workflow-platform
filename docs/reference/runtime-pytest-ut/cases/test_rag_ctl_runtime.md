# test_rag_ctl_runtime.py

このファイルは `runtime/tests/test_rag_ctl_runtime.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 3 |

## ケース一覧

#### RT-UT-CASE-298A

- pytest node id:

```text
runtime/tests/test_rag_ctl_runtime.py::test_ctl_rag_retrieve_writes_context_pack_and_runtime_log
```

- Confirm: `aiwfctl rag retrieve` がfile backendのchunk indexからcontext packを生成し、runtime logへ `rag retrieve` / `rag:retrieve` として記録することを確認する。
- Input:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ctl_runtime.py:31`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: temporary RAG chunks index, empty embeddings index, `ctl.build_parser().parse_args(...)`
- Expected: exit code が 0 で、context pack JSON が作成され、`logs/runtime/runtime-events.log` の最終イベントが `command=rag retrieve`、`operation_id=rag:retrieve` になる。

#### RT-UT-CASE-298B

- pytest node id:

```text
runtime/tests/test_rag_ctl_runtime.py::test_ctl_rag_jsonize_converts_sources
```

- Confirm: `aiwfctl rag jsonize` がRAG source treeをUUID JSON wrapperへ変換できることを確認する。
- Input:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ctl_runtime.py:65`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: temporary `rag/note.md`, `ctl.build_parser().parse_args(...)`
- Expected: exit code が 0 で、`converted_count` が 1 になり、返却された `json_path` のartifactが存在する。

#### RT-UT-CASE-298C

- pytest node id:

```text
runtime/tests/test_rag_ctl_runtime.py::test_ctl_rag_migrate_legacy_root_moves_backup
```

- Confirm: `aiwfctl rag migrate-legacy-root` がlegacy root RAG backupを標準RAG treeへ移動できることを確認する。
- Input:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_ctl_runtime.py:92`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: temporary `legacy-root-rag-<timestamp>/chunks/one.json`, `ctl.build_parser().parse_args(...)`
- Expected: exit code が 0 で、`moved` に `chunks/one.json` が入り、標準RAG tree配下に移動後artifactが存在する。
