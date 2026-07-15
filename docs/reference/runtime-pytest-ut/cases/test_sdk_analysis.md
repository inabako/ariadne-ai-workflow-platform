# test_sdk_analysis.py

このファイルは `runtime/tests/test_sdk_analysis.py` のpytest node id単位UT仕様です。

## 対象

- `runtime/workflow/sdk_analysis.py`
- `runtime/ctl.py`

| 項目 | 値 |
| --- | ---: |
| cases | 9 |

## ケース一覧

#### RT-UT-CASE-565

- pytest node id:

```text
runtime/tests/test_sdk_analysis.py::test_sdk_analysis_skips_when_sdk_input_is_missing
```

- 確認内容: `work/requirements/sdk/` が無い場合、SDK事前解析が `skipped` として終了し、要件定義workflowを止めないことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_sdk_analysis.py:10`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果:
  - `status == "skipped"`
  - `skip_reason == "missing-or-empty-sdk-input"`
  - source pathが `work/requirements/sdk`
  - skip messageが返る

#### RT-UT-CASE-566

- pytest node id:

```text
runtime/tests/test_sdk_analysis.py::test_sdk_analysis_writes_context_report_requirements_and_knowledge
```

- 確認内容: SDKプログラム内のREADME、package metadata、source fileを解析し、SDK名、version、license、auth/network/test観点、Context First登録、Knowledge JSON候補を生成することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_sdk_analysis.py:21`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `context`, `knowledge`
- 期待結果:
  - `status == "available"`
  - SDK name/version/licenseを抽出する
  - auth、network、testsのfindingsを持つ
  - `sdk-analysis-report.md` と `sdk-integration-requirements.md` を生成する
  - `sdk-analysis-context.json` が `artifact_type: sdk-analysis-context` を持つ
  - Context First manifestに `sdk-analysis` が登録される
  - `work/db/ariadne-knowledge-platform/rag/jsonized/*.json` にKnowledge JSON候補が生成される

#### RT-UT-CASE-567

- pytest node id:

```text
runtime/tests/test_sdk_analysis.py::test_sdk_analysis_detects_secret_like_literals_without_copying_values
```

- 確認内容: SDKプログラムにsecret-like literalが含まれていても、値そのものをcontext/report/Knowledgeへコピーせず、検出事実だけをHuman Checkへ渡すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_sdk_analysis.py:58`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `context_text`
- 期待結果:
  - `status == "human-check-required"`
  - `secret_findings` に対象fileとredaction方針が入る
  - `sdk-analysis-context.json` にsecret値そのものが含まれない

#### RT-UT-CASE-568

- pytest node id:

```text
runtime/tests/test_sdk_analysis.py::test_aiwfctl_sdk_analyze_command
```

- 確認内容: `aiwfctl sdk analyze --work-id <work-id>` からSDK事前解析runtimeを呼び出し、CLI出力に生成context pathが表示されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_sdk_analysis.py:80`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果:
  - exit codeが0
  - CLI outputに `SDK Analysis` が含まれる
  - CLI outputに `work/issue-9/context/sdk-analysis-context.json` が含まれる

#### RT-UT-CASE-569

- pytest node id:

```text
runtime/tests/test_sdk_analysis.py::test_sdk_discovery_skips_when_sdk_program_input_is_missing
```

- 確認内容: `work/requirements/sdk/` が無い場合でもSDK外部discoveryがskip contextを生成し、親workflowを止めないことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_sdk_analysis.py:98`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果:
  - `status == "skipped"`
  - `artifact_type == "sdk-external-discovery"`
  - source pathが `work/requirements/sdk`
  - `work/issue-404/context/sdk-external-discovery.json` が生成される

#### RT-UT-CASE-570

- pytest node id:

```text
runtime/tests/test_sdk_analysis.py::test_sdk_discovery_generates_external_candidates_queries_and_context
```

- 確認内容: SDKプログラムからpackage registry、homepage、repository、README内URL、security確認queryを生成し、Context First manifestへ `sdk-external-discovery` を登録することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_sdk_analysis.py:109`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果:
  - `status == "available"`
  - npm registry候補URLが生成される
  - homepage / repository / README内URLが候補に含まれる
  - security目的のqueryが生成される
  - `sdk-external-discovery` がmanifest contextに含まれる
  - `sdk-external-discovery-report.md` と `sdk-external-requirements.md` が生成される

#### RT-UT-CASE-571

- pytest node id:

```text
runtime/tests/test_sdk_analysis.py::test_sdk_analysis_detects_aws_and_gcp_cloud_sdk_metadata
```

- 確認内容: AWS SDKとGCP SDKが同一SDKプログラム入力に含まれる場合、providerを `multiple` として扱い、services、region/project要件、Human Check前提、file inventoryを生成することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_sdk_analysis.py:144`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `inventory`
- 期待結果:
  - `cloud.provider == "multiple"`
  - `cloud.providers` に `aws` と `gcp` が含まれる
  - `cloud.services` に `s3` と `pubsub` が含まれる
  - `region_project_requirements` に `AWS Region` と `GCP Project` が含まれる
  - `adoption_status == "needs_human_check"`
  - `work/<work-id>/context/sdk-files.json` にSHA-256付きinventoryが生成される

#### RT-UT-CASE-572

- pytest node id:

```text
runtime/tests/test_sdk_analysis.py::test_sdk_discovery_carries_cloud_sdk_metadata
```

- 確認内容: `requirements.txt` からAWS/GCP Python packageを検出し、外部discovery contextへcloud metadataと公式docs検索queryを引き継ぐことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_sdk_analysis.py:180`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果:
  - `cloud.provider == "multiple"`
  - `cloud.providers` に `aws` と `gcp` が含まれる
  - `search_queries` に `official-docs` 目的のqueryが含まれる
  - `work/<work-id>/context/sdk-external-discovery.json` が生成される

#### RT-UT-CASE-573

- pytest node id:

```text
runtime/tests/test_sdk_analysis.py::test_sdk_analysis_detects_stripe_payment_sdk_metadata
```

- 確認内容: Stripe SDKがSDKプログラム入力に含まれる場合、paymentカテゴリとしてvendor、services、secret / webhook / idempotency / test modeのHuman Checkを生成することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_sdk_analysis.py:197`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果:
  - `payment.vendor == "stripe"`
  - `payment.vendors == ["stripe"]`
  - `payment.services` に `checkout`、`payment_intents`、`webhooks` が含まれる
  - `payment.local_testing.candidates` に `Stripe CLI webhook forwarding` が含まれる
  - `payment.authentication_candidates` に `Webhook signing secret` が含まれる
  - `payment.adoption_status == "needs_human_check"`
  - `human_checks` にStripe固有の確認項目が含まれる

#### RT-UT-CASE-574

- pytest node id:

```text
runtime/tests/test_sdk_analysis.py::test_sdk_discovery_carries_stripe_payment_sdk_metadata
```

- 確認内容: `requirements.txt` からStripe Python packageを検出し、外部discovery contextへpayment metadataとStripe公式docs / webhook確認queryを引き継ぐことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_sdk_analysis.py:233`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果:
  - `payment.vendor == "stripe"`
  - `payment.vendors == ["stripe"]`
  - `search_queries` に `Stripe official SDK documentation` が含まれる
  - `search_queries` に `webhook` 目的のqueryが含まれる
  - `work/<work-id>/context/sdk-external-discovery.json` が生成される

#### RT-UT-CASE-575

- pytest node id:

```text
runtime/tests/test_sdk_analysis.py::test_aiwfctl_sdk_discover_command
```

- 確認内容: `aiwfctl sdk discover --work-id <work-id>` からSDK外部discovery runtimeを呼び出し、CLI出力に生成context pathが表示されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_sdk_analysis.py:248`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果:
  - exit codeが0
  - CLI outputに `SDK External Discovery` が含まれる
  - CLI outputに `work/issue-10/context/sdk-external-discovery.json` が含まれる
