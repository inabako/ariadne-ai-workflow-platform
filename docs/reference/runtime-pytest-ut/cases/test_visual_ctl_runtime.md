# test_visual_ctl_runtime.py

This file lists pytest node ids for `runtime/tests/test_visual_ctl_runtime.py` as runtime UT cases.

| Item | Value |
| --- | ---: |
| cases | 3 |

## Cases

#### RT-UT-CASE-607

- pytest node id:

```text
runtime/tests/test_visual_ctl_runtime.py::test_ctl_gui_init_input_writes_inbox_readme_and_runtime_log
```

- Confirm: `aiwfctl gui init-input` is routed through the shared CTL entrypoint, writes the GUI inbox README, and emits the expected runtime command path.
- Input:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_visual_ctl_runtime.py:14`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none, case=none
  - inline input: `repo_root`, `args`, `result`, `readme`, `log_text`
- Expected:
  - exit code is 0
  - `work/requirements/gui-input/README.md` is created
  - runtime log includes `gui init-input` or `gui:init-input`

#### RT-UT-CASE-608

- pytest node id:

```text
runtime/tests/test_visual_ctl_runtime.py::test_ctl_gui_self_test_runs_runtime_checks
```

- Confirm: `aiwfctl gui self-test` runs GUI/Web SVG runtime self checks through the shared CTL entrypoint and returns a pass result.
- Input:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_visual_ctl_runtime.py:38`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none, case=none
  - inline input: `repo_root`, `args`, `result`
- Expected:
  - exit code is 0
  - result status is `pass`
  - result checks contain self-test entries

#### RT-UT-CASE-609

- pytest node id:

```text
runtime/tests/test_visual_ctl_runtime.py::test_ctl_web_svg_run_skips_without_matching_svg
```

- Confirm: `aiwfctl web-svg run --issue-id <id>` is routed through CTL and safely skips when no matching SVG input exists.
- Input:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_visual_ctl_runtime.py:59`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none, case=none
  - inline input: `repo_root`, `args`, `result`, `log_text`
- Expected:
  - exit code is 0
  - result status is `skipped`
  - runtime log includes `web-svg run` or `web-svg:run`
