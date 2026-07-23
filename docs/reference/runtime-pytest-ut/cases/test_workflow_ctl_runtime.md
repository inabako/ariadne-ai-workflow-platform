# test_workflow_ctl_runtime.py

このファイルは `runtime/tests/test_workflow_ctl_runtime.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 4 |

## ケース一覧

#### RT-UT-CASE-WFCTL-001

- pytest node id:

```text
runtime/tests/test_workflow_ctl_runtime.py::test_ctl_workflow_state_set_writes_state_and_runtime_log
```

- Confirm: `aiwfctl workflow state set` が `workflow-state.json` を更新し、runtime logへ `workflow state set` / `workflow:state:set` として記録されることを確認する。
- Input:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_ctl_runtime.py:14`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: temporary repo root, `ctl.build_parser().parse_args(...)`
- Expected: exit code が 0 で、stateのphaseが更新され、`logs/runtime/runtime-events.log` の最終イベントが `command=workflow state set`、`operation_id=workflow:state:set` になる。

#### RT-UT-CASE-WFCTL-002

- pytest node id:

```text
runtime/tests/test_workflow_ctl_runtime.py::test_ctl_workflow_docs_sync_init_creates_contexts
```

- Confirm: `aiwfctl workflow docs-sync init` がdocs-sync work contextを作成できることを確認する。
- Input:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_ctl_runtime.py:49`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: repository `owner/repo`, target branch `feature/docs`, work id `docs-feature`
- Expected: exit code が 0 で、`work/docs-feature/context/agent-context.json` が作成される。

#### RT-UT-CASE-WFCTL-003

- pytest node id:

```text
runtime/tests/test_workflow_ctl_runtime.py::test_ctl_workflow_iac_handoff_creates_execution_plan
```

- Confirm: `aiwfctl workflow iac-handoff create` がrealtime IaC handoffとexecution-plan contextを生成できることを確認する。
- Input:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_ctl_runtime.py:77`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: work id `issue-iac`, validator judgment `pass`
- Expected: exit code が 0 で、execution plan artifactが存在し、Context First manifestに `execution-plan` が登録される。

#### RT-UT-CASE-WFCTL-004

- pytest node id:

```text
runtime/tests/test_workflow_ctl_runtime.py::test_ctl_workflow_validate_vscode_workspace_checks_json
```

- Confirm: `aiwfctl workflow validate-vscode-workspace check` がVSCode JSON filesを検証できることを確認する。
- Input:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_ctl_runtime.py:104`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - inline input: temporary `.vscode/*.json`, `ctl.build_parser().parse_args(...)`
- Expected: exit code が 0 で、既定の4つのVSCode JSON fileが `validated_files` に含まれる。
