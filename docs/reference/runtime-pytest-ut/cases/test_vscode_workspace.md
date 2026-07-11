# test_vscode_workspace.py

このファイルは `runtime/tests/test_vscode_workspace.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 2 |

## ケース一覧

#### RT-UT-CASE-520

- pytest node id:

```text
runtime/tests/test_vscode_workspace.py::test_aiwfctl_path_shell_task_is_provisioned
```

- 確認内容: pytest case `aiwfctl path shell task is provisioned` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_workspace.py:17`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-521

- pytest node id:

```text
runtime/tests/test_vscode_workspace.py::test_aiwfctl_cmd_exposes_path_usage
```

- 確認内容: pytest case `aiwfctl cmd exposes path usage` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_workspace.py:27`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
