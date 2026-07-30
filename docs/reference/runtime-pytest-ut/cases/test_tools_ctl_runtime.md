# test_tools_ctl_runtime.py

This file lists pytest node ids for `runtime/tests/test_tools_ctl_runtime.py` as runtime UT cases.

| Item | Value |
| --- | ---: |
| cases | 3 |

## Cases

#### RT-UT-CASE-612

- pytest node id:

```text
runtime/tests/test_tools_ctl_runtime.py::test_ctl_tools_bom_scan_runs_utf8_bom_tool_and_writes_runtime_log
```

- Confirm: `aiwfctl tools bom-scan` runs the UTF-8 BOM scanner through the shared CTL entrypoint, preserves JSON output, and emits the expected runtime command log.
- Input:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_tools_ctl_runtime.py:14`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none, case=none
  - inline input: `repo`, `docs`, `args`, `result`, `completed`
- Expected:
  - exit code is 0
  - result artifact type is `utf8-bom-scan`
  - result status is `ok`
  - runtime log command is `tools bom-scan`

#### RT-UT-CASE-616

- pytest node id:

```text
runtime/tests/test_tools_ctl_runtime.py::test_ctl_tools_coverage_audit_skip_run_writes_outputs_and_runtime_log
```

- Confirm: `aiwfctl tools coverage-audit --skip-run` runs the coverage audit through the shared CTL entrypoint, writes audit outputs, and emits the expected runtime command log.
- Input:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_tools_ctl_runtime.py:43`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none, case=none
  - inline input: `repo`, `runtime_dir`, `args`, `result`, `completed`
- Expected:
  - exit code is 0
  - coverage measurement status is `skipped`
  - audit JSON and Markdown outputs are written
  - runtime log command is `tools coverage-audit`

#### RT-UT-CASE-613

- pytest node id:

```text
runtime/tests/test_tools_ctl_runtime.py::test_ctl_tools_encoding_guard_preserves_finding_exit_code
```

- Confirm: `aiwfctl tools encoding-guard` preserves the tool exit code when a text finding is detected and records the failed runtime event.
- Input:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_tools_ctl_runtime.py:71`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none, case=none
  - inline input: `repo`, `docs`, `args`, `result`, `completed`
- Expected:
  - exit code is 1
  - result artifact type is `text-encoding-guard`
  - result status is `finding`
  - runtime log output status is `failed`
