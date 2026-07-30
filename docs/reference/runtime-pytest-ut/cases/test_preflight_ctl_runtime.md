# test_preflight_ctl_runtime.py

This file lists pytest node ids for `runtime/tests/test_preflight_ctl_runtime.py` as runtime UT cases.

| Item | Value |
| --- | ---: |
| cases | 2 |

## Cases

#### RT-UT-CASE-610

- pytest node id:

```text
runtime/tests/test_preflight_ctl_runtime.py::test_ctl_preflight_runs_environment_preflight_and_writes_runtime_log
```

- Confirm: `aiwfctl preflight` runs the environment preflight implementation through the shared CTL entrypoint, preserves JSON output, writes process reports, and emits the runtime command log.
- Input:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_preflight_ctl_runtime.py:17`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=none, case=none
  - inline input: `repo`, `args`, `result`, `completed`
- Expected:
  - exit code is 0
  - result status is `ready`
  - preflight report path is under `work/<work-id>/process-report/`
  - runtime log command and operation id are `preflight`

#### RT-UT-CASE-611

- pytest node id:

```text
runtime/tests/test_preflight_ctl_runtime.py::test_ctl_preflight_returns_blocked_when_required_tool_is_missing
```

- Confirm: `aiwfctl preflight` preserves the environment preflight blocked exit code when a required tool is missing and records the blocked runtime event.
- Input:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_preflight_ctl_runtime.py:63`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=none, case=none
  - inline input: `repo`, `args`, `result`, `completed`
- Expected:
  - exit code is 2
  - result status is `install-list-required`
  - gate restart starts from `environment-preflight-gate`
  - runtime log output status is `blocked`
