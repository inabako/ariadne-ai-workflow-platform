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

- 確認内容: `aiwfctl gui init-input` がshared CTL entrypoint経由で実行され、GUI inbox READMEを作成し、期待するruntime command pathを出力することを確認します。
- 入力値:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_visual_ctl_runtime.py:14`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `repo_root`, `args`, `result`, `readme`, `log_text`
- 期待結果:
  - exit code is 0
  - `work/requirements/gui-input/README.md` が作成される
  - runtime logに `gui init-input` または `gui:init-input` が含まれる

#### RT-UT-CASE-608

- pytest node id:

```text
runtime/tests/test_visual_ctl_runtime.py::test_ctl_gui_self_test_runs_runtime_checks
```

- 確認内容: `aiwfctl gui self-test` がshared CTL entrypoint経由でGUI/Web SVG runtime self checkを実行し、pass resultを返すことを確認します。
- 入力値:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_visual_ctl_runtime.py:38`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `repo_root`, `args`, `result`
- 期待結果:
  - exit code is 0
  - result status is `pass`
  - result checks contain self-test entries

#### RT-UT-CASE-609

- pytest node id:

```text
runtime/tests/test_visual_ctl_runtime.py::test_ctl_web_svg_run_skips_without_matching_svg
```

- 確認内容: `aiwfctl web-svg run --issue-id <id>` がCTL経由で実行され、該当するSVG inputが無い場合に安全にskipすることを確認します。
- 入力値:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_visual_ctl_runtime.py:59`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `repo_root`, `args`, `result`, `log_text`
- 期待結果:
  - exit code is 0
  - result status is `skipped`
  - runtime logに `web-svg run` または `web-svg:run` が含まれる
