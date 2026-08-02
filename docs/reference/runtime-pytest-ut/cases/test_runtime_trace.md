# test_runtime_trace.py

This file records pytest node ids for `runtime/tests/test_runtime_trace.py`.

| Item | Value |
| --- | ---: |
| cases | 6 |

## Cases

#### RT-UT-CASE-AUTO-002

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

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_runtime_trace.py::test_runtime_trace_show_problems_mode_filters_timeline
```

- Confirm: `trace show --problems` keeps summary counts while filtering the visible timeline to problem events only.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_trace.py:92`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: runtime event log fixture with completed and blocked commands, and `problems_only=True`
- Expected: `view_mode` is `problems`, timeline contains only the blocked command, and human-readable output omits `Commands` and `Timeline` sections.

#### RT-UT-CASE-AUTO-003

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

#### RT-UT-CASE-AUTO-004

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

#### RT-UT-CASE-AUTO-005

- pytest node id:

```text
runtime/tests/test_runtime_trace.py::test_ctl_trace_begin_records_work_id_in_active_trace
```

- Confirm: `aiwfctl trace begin --work-id` records the work id in the active trace state.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_trace.py:117`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: CTL parser arguments with `--workflow /docs-sync`, `--work-id issue-1`, and `--trace-id trace-work-id`
- Expected: command output and `logs/runtime/active-trace.json` both preserve `work_id=issue-1`.

#### RT-UT-CASE-AUTO-006

- pytest node id:

```text
runtime/tests/test_runtime_trace.py::test_ctl_trace_recover_previews_invalid_active_trace_and_archives_with_approval
```

- Confirm: `aiwfctl trace recover` previews and then archives an invalid `active-trace.json` only after Human Check approval.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_trace.py:144`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: malformed `logs/runtime/active-trace.json`, `trace status --json`, `trace recover --dry-run --json`, and `trace recover --human-check approved --json`
- Expected: status reports `invalid`, dry-run keeps the active trace in place, approved recovery moves it under `logs/runtime/recovery/`.
