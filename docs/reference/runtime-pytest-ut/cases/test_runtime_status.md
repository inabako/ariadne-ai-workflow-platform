# test_runtime_status.py

This file records pytest node ids for `runtime/tests/test_runtime_status.py`.

| Item | Value |
| --- | ---: |
| cases | 2 |

## Cases

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_collects_trace_log_work_and_knowledge_state
```

- Confirm: `test_runtime_status_collects_trace_log_work_and_knowledge_state` runtime contract is covered by pytest assertions.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py:12`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: active trace, runtime event log, workflow-state, knowledge source and DuckDB fixtures
- Expected: pytest assertion defines the expected result.

#### RT-UT-CASE-AUTO-002

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_ctl_status_outputs_json_and_human_summary
```

- Confirm: `test_ctl_status_outputs_json_and_human_summary` runtime contract is covered by pytest assertions.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py:56`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: repository-local aiwfctl fixture and CTL parser arguments
- Expected: pytest assertion defines the expected result.
