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

- 確認内容: `aiwfctl preflight` がshared CTL entrypoint経由でenvironment preflight実装を実行し、JSON出力を維持し、process reportとruntime command logを出力することを確認します。
- 入力値:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_preflight_ctl_runtime.py:17`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `repo`, `args`, `result`, `completed`
- 期待結果:
  - exit code is 0
  - result status is `ready`
  - preflight report path is under `work/<work-id>/process-report/`
  - runtime log command and operation id are `preflight`

#### RT-UT-CASE-611

- pytest node id:

```text
runtime/tests/test_preflight_ctl_runtime.py::test_ctl_preflight_returns_blocked_when_required_tool_is_missing
```

- 確認内容: `aiwfctl preflight` preserves the environment preflight blocked exit code when a required tool is missing and records the blocked runtime event.
- 入力値:
  - pytest node: node id in the code block above
  - source: `runtime/tests/test_preflight_ctl_runtime.py:63`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `repo`, `args`, `result`, `completed`
- 期待結果:
  - exit code is 2
  - result status is `install-list-required`
  - gate restart starts from `environment-preflight-gate`
  - runtime log output status is `blocked`
