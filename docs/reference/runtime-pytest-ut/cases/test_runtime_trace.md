# test_runtime_trace.py

This file records pytest node ids for `runtime/tests/test_runtime_trace.py`.

| Item | Value |
| --- | ---: |
| cases | 3 |

## Cases

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_runtime_trace.py::test_runtime_trace_show_summarizes_commands_and_problem_events
```

- Confirm: `test_runtime_trace_show_summarizes_commands_and_problem_events` runtime contract is covered by pytest assertions.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_trace.py:61`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: runtime event log fixture with completed and blocked commands
- Expected: pytest assertion defines the expected result.

#### RT-UT-CASE-AUTO-002

- pytest node id:

```text
runtime/tests/test_runtime_trace.py::test_runtime_trace_show_latest_can_exclude_current_command_trace
```

- Confirm: `test_runtime_trace_show_latest_can_exclude_current_command_trace` runtime contract is covered by pytest assertions.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_trace.py:86`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: previous trace and current trace fixtures with current trace excluded
- Expected: pytest assertion defines the expected result.

#### RT-UT-CASE-AUTO-003

- pytest node id:

```text
runtime/tests/test_runtime_trace.py::test_ctl_trace_show_outputs_json_and_missing_trace_code
```

- Confirm: `test_ctl_trace_show_outputs_json_and_missing_trace_code` runtime contract is covered by pytest assertions.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_trace.py:97`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: CTL parser arguments for `trace show`, existing trace id, missing trace id
- Expected: pytest assertion defines the expected result.
