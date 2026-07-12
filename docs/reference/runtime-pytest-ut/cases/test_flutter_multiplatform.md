# test_flutter_multiplatform.py

このファイルは `runtime/tests/test_flutter_multiplatform.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 16 |

## ケース一覧

#### RT-UT-CASE-591

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_analyze_without_targets_requires_human_check
```

- 確認内容: Flutter target未指定時に全platform対応と推測せず、Human Check状態とContext First manifest登録を返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:39`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: work-id=`issue-1`, command=`analyze`, targets未指定
- 期待結果: statusが`human-check-required`になり、targetsは空配列、human check理由に全platform推測禁止が含まれ、manifestに`flutter-development`が登録される。

#### RT-UT-CASE-592

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_yaml_target_declaration_is_loaded
```

- 確認内容: `work/<work-id>/requirements/flutter-targets.yaml` から有効targetとrequirementsを読み取ることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:52`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: android/web/windows enabled、ios disabled、responsive_ui=trueのyaml
- 期待結果: sourceが`yaml`になり、targetsが`android, web, windows`として読み込まれ、responsive_uiがboolean trueとして保持される。

#### RT-UT-CASE-593

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_cli_targets_override_yaml_and_unknown_targets_are_reported
```

- 確認内容: CLI `--targets` がyamlより優先され、不明targetがHuman Check対象として残ることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:85`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: yamlはweb enabled、CLIは`android,web,unknown`
- 期待結果: sourceが`cli`になり、targetsは`android, web`、unknown_targetsは`unknown`、human checkに未登録targetが含まれる。

#### RT-UT-CASE-594

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_environment_decision_marks_ios_as_remote_build_when_not_macos
```

- 確認内容: Windows host上でiOS targetを選んだ場合にremote build requiredへ分類することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:107`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: host_os_nameを`windows`へ差し替え、target=`ios`
- 期待結果: statusが`remote_build_required`、required_environmentが`macOS`になる。

#### RT-UT-CASE-595

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_init_copies_boilerplate_and_generates_target_declaration
```

- 確認内容: initでFlutter boilerplateをwork配下へコピーし、CLI targetからtarget宣言、context、reportを生成することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:116`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: temporary template、work-id=`issue-4`、targets=`android,web,windows`
- 期待結果: boilerplate copy_statusが`copied`になり、`flutter-targets.yaml`、`implementation/flutter-project/pubspec.yaml`、context、reportが生成される。

#### RT-UT-CASE-596

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_verify_writes_verification_evidence
```

- 確認内容: verifyでFlutter静的解析/test計画をevidence Markdownとして保存し、tool存在時にavailableになることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:134`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: shutil.whichをFlutter/Dartありに差し替え、targets=`web`
- 期待結果: statusが`available`になり、`evidence/flutter/common/verification-plan.md` に`flutter analyze`が記録される。

#### RT-UT-CASE-597

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_build_dispatch_creates_target_specific_commands
```

- 確認内容: build dispatcherがtarget別のFlutter build commandとhost OS制約を生成することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:150`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: host=`windows`、flutterあり、targets=`android,web,windows,ios`、mode=`release`
- 期待結果: Android/Web/Windowsのrelease build commandが生成され、iOSは`remote_build_required`、release Human Checkにより全体statusは`human-check-required`になる。

#### RT-UT-CASE-598

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_ctl_parser_accepts_flutter_subcommands
```

- 確認内容: `aiwfctl flutter build` のparserがwork-id、targets、modeを受け付けることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:171`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: argv=`flutter build --work-id issue-7 --targets android,web --mode profile`
- 期待結果: commandが`flutter`、flutter_commandが`build`、targetsとmodeが入力どおりにparseされる。

#### RT-UT-CASE-599

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_aiwfctl_flutter_namespace_runs_runtime
```

- 確認内容: `runtime/ctl.py` がFlutter namespaceをruntime moduleへdispatchし、CLI出力を整形することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:191`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: repo-rootをtmp_pathへ指定し、`flutter analyze --work-id issue-8 --targets web` をparse、flutter runtime runをfake化
- 期待結果: exit codeが0、runtimeへcommand=`analyze`とrepo_rootが渡り、出力に`Flutter Multi-platform`が含まれる。

#### RT-UT-CASE-600

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_verify_execute_runs_commands_and_captures_evidence
```

- 確認内容: `verify --execute` 相当で検証commandを実行し、stdout/stderr/summaryをevidenceへ保存することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:223`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: subprocess.runをsuccessにfake化、targets=`web`、init済みboilerplate、execute=True
- 期待結果: verification executionが`passed`になり、4 command分の結果と`flutter-analyze-summary.md`、stdout evidenceが保存される。

#### RT-UT-CASE-601

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_build_execute_captures_failed_command_and_status
```

- 確認内容: `build --execute` でbuild失敗時にtarget別evidenceと全体failed statusを残すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:251`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: host=`windows`、toolあり、subprocess.runをreturncode=1にfake化、targets=`web`
- 期待結果: context statusとbuild statusが`failed`になり、`evidence/flutter/web/build-web-stderr.txt` に失敗ログが保存される。

#### RT-UT-CASE-602

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_release_build_execute_requires_human_check
```

- 確認内容: release buildの実行はHuman Check承認なしでは実行されず、skip evidenceを残すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:277`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: targets=`web`、mode=`release`、execute=True、human_check未指定
- 期待結果: statusが`human-check-required`になり、build executionは`skipped`、release buildのHuman Check理由が残る。

#### RT-UT-CASE-603

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_finalize_reports_passed_when_verify_and_build_evidence_pass
```

- 確認内容: verify/buildの実行証跡がpassしている場合、finalizeが完了判定passedを生成することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:297`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: verify/build subprocessをsuccessにfake化、targets=`web`
- 期待結果: finalize後のstatusが`passed`、stageが`finalize`になり、`evidence/flutter/finalization-summary.md` が生成される。

#### RT-UT-CASE-604

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_finalize_requires_execute_evidence_when_missing
```

- 確認内容: execute証跡がない場合、finalizeが完了扱いせずHuman Check requiredへ戻すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:318`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: analyzeのみ実行済み、targets=`web`
- 期待結果: final statusが`human-check-required`になり、completion checksでverification/buildが`missing`になる。

#### RT-UT-CASE-605

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_webdriver_failure_is_environment_required
```

- 確認内容: Flutter Web integration testでWebDriver/chromedriver不足が起きた場合、通常のtest失敗ではなく環境不足として分類することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:330`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `flutter drive` だけWebDriver不足stderrを返すfake subprocess、targets=`web`、execute=True
- 期待結果: context statusとverification execution statusが`build-environment-required`になり、Web integrationに必要なtool不足として識別される。

#### RT-UT-CASE-606

- pytest node id:

```text
runtime/tests/test_flutter_multiplatform.py::test_ctl_parser_accepts_flutter_finalize_and_execute
```

- 確認内容: `aiwfctl flutter verify --execute` と `aiwfctl flutter finalize` のparserが必要引数を受け付けることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_flutter_multiplatform.py:349`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: argv=`flutter verify --work-id issue-14 --targets web --execute --timeout-seconds 30` と `flutter finalize --work-id issue-14`
- 期待結果: verify argsのexecuteがtrue、timeout_secondsが30、finalizeのflutter_commandが`finalize`になる。
