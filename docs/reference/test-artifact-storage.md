# Test Artifact Storage

このページは、テスト仕様書、QTestソース、実行証跡、人間確認結果をどこに保存するかを定義します。

## Canonical Layout

作業中の一次成果物は `work/<id>/` に保存します。

```text
work/<id>/
  test-specifications/
    test-specification.md
  test-evidence/
    unit_test/
    qtest_integration/
    integration_connectivity_test/
    human_check/
```

Issue branchでpush対象にする永続証跡は、target repositoryの `docs/evidence/issue-<issue-number>/` に保存します。

```text
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/
  test_specifications/
    unit-test-cases.md
    integration-test-cases.md
    human-check-list.md
  ut/
  integration/
    qtest/
    manual/
    startup/
  human_check/
```

## Automatic Scaffold

`runtime/workflow/knowledge_capture.py` は、存在しない場合にtarget repository側の証跡フォルダを自動生成します。

```text
docs/evidence/issue-<issue-number>/
  README.md
  test_specifications/README.md
  ut/README.md
  integration/README.md
  integration/qtest/README.md
  integration/manual/README.md
  integration/startup/README.md
  human_check/README.md
```

空フォルダはGitに残らないため、scaffold用の `README.md` を作成します。
ただし、`README.md` だけではテスト証跡とはみなしません。
push前の判定では、テスト仕様書、実行ログ、スクリーンショット、human check結果などの実エビデンスが保存されていることを確認します。

## Test Case Specification Files

`test_specifications/` には、UT、結合試験、人間確認の計画を分けて保存します。

```text
docs/evidence/issue-<issue-number>/test_specifications/
  unit-test-cases.md
  integration-test-cases.md
  human-check-list.md
```

| File | Purpose | Result Location |
| --- | --- | --- |
| `unit-test-cases.md` | unit testで確認する項目、対象関数/クラス、入力、期待結果、pass criteriaを定義する | `docs/evidence/issue-<issue-number>/ut/` |
| `integration-test-cases.md` | 結合疎通試験、QTest候補、manual/startup確認、外部I/O方針を定義する | `docs/evidence/issue-<issue-number>/integration/` |
| `human-check-list.md` | 人間が確認する項目、確認者、確認条件、合否基準を定義する | `docs/evidence/issue-<issue-number>/human_check/` |

単一の包括的な `test-specification.md` を作る場合でも、push前には上記3観点が識別できるようにします。
推奨は、Issueごとに3ファイルへ分割して保存する方式です。

## Artifact Mapping

| Artifact | Work Location | Target Repository Docs Location | Required Before Push |
| --- | --- | --- | --- |
| Unit test case table | `work/<id>/test-specifications/` | `docs/evidence/issue-<issue-number>/test_specifications/unit-test-cases.md` | yes when unit tests exist |
| Integration test case table | `work/<id>/test-specifications/` | `docs/evidence/issue-<issue-number>/test_specifications/integration-test-cases.md` | yes when integration checks exist |
| Human check list | `work/<id>/test-specifications/` | `docs/evidence/issue-<issue-number>/test_specifications/human-check-list.md` | yes when human check is required |
| Unit test command and result | `work/<id>/test-evidence/unit_test/` | `docs/evidence/issue-<issue-number>/ut/` | yes when unit tests exist |
| PyQt QTest source | target source tree, usually `src/tests/qt/` | referenced from `docs/evidence/issue-<issue-number>/integration/qtest/` | yes when QTest candidates exist |
| PyQt QTest command and result | `work/<id>/test-evidence/qtest_integration/` | `docs/evidence/issue-<issue-number>/integration/qtest/` | yes when QTest candidates exist |
| Manual integration / connectivity result | `work/<id>/test-evidence/integration_connectivity_test/` | `docs/evidence/issue-<issue-number>/integration/manual/` | yes when manual integration is required |
| Startup / external I/O launch logs | `work/<id>/test-evidence/integration_connectivity_test/` | `docs/evidence/issue-<issue-number>/integration/startup/` | yes when startup check is required |
| Human check result | `work/<id>/test-evidence/human_check/` | `docs/evidence/issue-<issue-number>/human_check/` | yes when human check is required |

## PyQt QTest Rule

PyQt / Qt GUIの場合、QTestソースはtarget repositoryの通常のテスト配置に置きます。

推奨:

```text
work/issue-<issue-number>/source/repository/src/tests/qt/test_<feature>_integration.py
```

QTest実行証跡は次に保存します。

```text
work/issue-<issue-number>/test-evidence/qtest_integration/
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/integration/qtest/
```

QTestで自動化できない実機、実カメラ、physical STOP、router / VPN / field networkは、manualまたはstartup evidenceとして残します。

## Push Gate

push前に、少なくとも次を確認します。

- `docs/evidence/issue-<issue-number>/test_specifications/unit-test-cases.md` またはunit test不要理由が保存されている。
- `docs/evidence/issue-<issue-number>/test_specifications/integration-test-cases.md` または結合試験不要理由が保存されている。
- human checkが必要な場合、`docs/evidence/issue-<issue-number>/test_specifications/human-check-list.md` が保存されている。
- `docs/evidence/issue-<issue-number>/ut/` または、unit test不要理由がtest specificationに記録されている。
- `docs/evidence/issue-<issue-number>/integration/` が存在し、QTest / manual / startup の該当証跡が保存されている。
- human checkが必要な場合、`docs/evidence/issue-<issue-number>/human_check/` に確認結果が保存されている。
- QTest candidateがある場合、`integration/qtest/` に実行コマンドと結果が保存されている。
- 自動生成された `README.md` だけでpush可と判断しない。
