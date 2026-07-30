# test_retrieval_ctl_runtime.py

This file lists pytest node ids for `runtime/tests/test_retrieval_ctl_runtime.py` as runtime UT cases.

| Item | Value |
| --- | ---: |
| cases | 2 |

## Cases

#### RT-UT-CASE-614

- pytest node id:

```text
runtime/tests/test_retrieval_ctl_runtime.py::test_ctl_retrieval_run_writes_task_reports_and_runtime_log
```

- Confirm: `aiwfctl retrieval run` runs the task runner through the shared CTL entrypoint, writes task reports, and emits the expected runtime command log.
- Input:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_retrieval_ctl_runtime.py:14`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none, case=none
  - inline input: `repo`, `work_dir`, `context_dir`, `task_file`, `args`, `result`, `completed`
- Expected:
  - exit code is 0
  - result work id is `issue-1`
  - task JSON and Markdown reports are written
  - runtime log command and operation id are `retrieval run` / `retrieval:run`

#### RT-UT-CASE-615

- pytest node id:

```text
runtime/tests/test_retrieval_ctl_runtime.py::test_ctl_retrieval_run_reports_missing_work_directory
```

- Confirm: `aiwfctl retrieval run` reports task runner errors through CTL and records a failed runtime event.
- Input:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_retrieval_ctl_runtime.py:58`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none, case=none
  - inline input: `repo`, `task_file`, `args`, `completed`
- Expected:
  - exit code is 1
  - output starts with a retrieval runtime failure message
  - runtime log command is `retrieval run`
  - runtime log output status is `failed`
