# test_runtime_ready.py

This file records pytest node ids for `runtime/tests/test_runtime_ready.py`.

| Item | Value |
| --- | ---: |
| cases | 4 |

## Cases

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_runtime_ready.py::test_runtime_ready_reports_ready_when_gates_pass
```

- Confirm: `aiwfctl ready` reports `ready` when runtime gates pass.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_ready.py:34`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: mocked status payload with pass doctor, ready dependency readiness, clean trace/log state, and ok UT spec sync
- Expected: ready check returns `runtime-ready-check`, overall status is `ready`, and doctor / UT spec gates are `pass`.

#### RT-UT-CASE-AUTO-002

- pytest node id:

```text
runtime/tests/test_runtime_ready.py::test_runtime_ready_reports_attention_for_nonblocking_runtime_log_problem
```

- Confirm: `aiwfctl ready` reports `attention` for a nonblocking runtime log problem.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_ready.py:46`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: mocked status payload with one last problem event and matching attention reason
- Expected: overall status is `attention`, runtime log gate is `attention`, and attention reason count is preserved.

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_runtime_ready.py::test_runtime_ready_strict_promotes_attention_to_blocked
```

- Confirm: `aiwfctl ready --strict` promotes nonblocking `attention` to `blocked`.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_ready.py:66`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: mocked dirty git status with attention reason and ok UT spec sync
- Expected: strict ready check returns `blocked`, preserves `non_strict_status: attention`, and marks `strict_blocked` as true.

#### RT-UT-CASE-AUTO-003

- pytest node id:

```text
runtime/tests/test_runtime_ready.py::test_ctl_ready_json_route_returns_runtime_ready_check
```

- Confirm: CTL dispatch routes `aiwfctl ready --json` to the runtime ready check.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_ready.py:66`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: CTL parser args for `ready --work-id issue-1 --skip-spec-check --strict --output work/evidence/runtime-ready.json --json`
- Expected: command exits with code 0, returns `runtime-ready-check`, preserves work id / strict flag, marks spec check as skipped, and writes the JSON evidence file.
