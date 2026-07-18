# test_gate_restart.py

このファイルは `runtime/tests/test_gate_restart.py` の pytest node id 単位UT仕様です。

## Cases

#### RT-UT-CASE-GATE-RESTART-001

- pytest node id:

```text
runtime/tests/test_gate_restart.py::test_build_gate_restart_defaults_restart_from_to_gate
```

- 確認内容: gate restart helper が同じ gate への再開、修復可否、修復コマンド、pass/fail 後の固定遷移を返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_gate_restart.py:8`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: `schema_version`、`artifact_type`、`restart_from`、`next_on_pass`、`next_on_fail` が共通契約どおり固定される。

#### RT-UT-CASE-GATE-RESTART-002

- pytest node id:

```text
runtime/tests/test_gate_restart.py::test_build_gate_restart_rejects_missing_gate
```

- 確認内容: gate 名なしの gate restart record を作らせないことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_gate_restart.py:31`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: `ValueError` が返り、gate failure の起点が曖昧な record を残さない。

#### RT-UT-CASE-GATE-RESTART-003

- pytest node id:

```text
runtime/tests/test_gate_restart.py::test_build_gate_restart_requires_repair_command_when_repair_is_available
```

- 確認内容: 修復可能と宣言する場合に、実行すべき runtime command を必須にすることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_gate_restart.py:36`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: `repair_command` なしでは `ValueError` になり、AI が手作業へ逸れる余地を残さない。

#### RT-UT-CASE-GATE-RESTART-004

- pytest node id:

```text
runtime/tests/test_gate_restart.py::test_build_gate_restart_rejects_unknown_status
```

- 確認内容: gate restart 後の状態値を `pass` / `warning` / `fail` / `unknown` に制限することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_gate_restart.py:41`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 未定義 status は `ValueError` になり、後続 workflow の分岐判断を固定できる。

#### RT-UT-CASE-GATE-RESTART-005

- pytest node id:

```text
runtime/tests/test_gate_restart.py::test_build_status_gate_restart_enables_repair_for_non_pass_status
```

- 確認内容: `human-check-required` など pass ではない status のとき、復帰用 runtime command が repair として有効化されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_gate_restart.py:46`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: `repair_available` が `true` になり、修復後の期待状態が `pass` として返される。

#### RT-UT-CASE-GATE-RESTART-006

- pytest node id:

```text
runtime/tests/test_gate_restart.py::test_build_status_gate_restart_disables_repair_for_pass_status
```

- 確認内容: `ready` など pass 相当の status のとき、repair command が渡されても修復操作としては扱わないことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_gate_restart.py:59`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: `repair_available` が `false` になり、`repair_command` は空文字、修復後の期待状態は `pass` として返される。
