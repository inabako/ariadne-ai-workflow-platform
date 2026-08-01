# test_runtime_trace_cli_integration.py

| 項目 | 値 |
| --- | ---: |
| cases | 2 |

## ケース一覧

#### RT-UT-CASE-RUNTIME-TRACE-CLI-001

- pytest node id:

```text
runtime/tests/test_runtime_trace_cli_integration.py::test_runtime_trace_sequence_continues_across_cli_processes
```

- Confirm: `aiwfctl trace begin` から `trace end` までの間に複数の通常 command を CLI process として実行しても、同じ trace id と workflow 全体の連番 sequence が維持されることを確認します。
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_trace_cli_integration.py:54`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: `target_repo`, `trace_id`, `commands`, `results`, `status`, `log_path`, `published_log_path`, `prefixes`, `trace_ids`, `sequences`, `payloads`
- Expected: `trace begin`、`help list`、`help markdown`、`trace status`、`trace end` の10イベントが同じ trace id で記録され、sequence が `00001` から `00010` まで連続する。

#### RT-UT-CASE-RUNTIME-TRACE-CLI-002

- pytest node id:

```text
runtime/tests/test_runtime_trace_cli_integration.py::test_runtime_trace_without_active_trace_keeps_command_scoped_sequences
```

- Confirm: active trace を開始していない状態で複数の CLI process を実行した場合、各 command が command scoped trace として記録され、sequence が command ごとに `00001` / `00002` へ戻ることを確認します。
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_trace_cli_integration.py:98`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: `target_repo`, `results`, `log_path`, `published_log_path`, `prefixes`, `trace_ids`, `sequences`
- Expected: `active-trace.json` が存在しない場合、2回の `help list` は異なる trace id で記録され、sequence は `00001`, `00002`, `00001`, `00002` になる。
