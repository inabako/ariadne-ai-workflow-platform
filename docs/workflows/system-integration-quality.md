# システム統合品質向上ワークフロー

このワークフローは、生成・改修したコードを「単体で動く成果物」ではなく、対象システムの構造、規約、試験、運用へ自然に統合された成果物として確認するためのゲートです。

## CLI

```powershell
aiwfctl integration analyze --work-id <work-id>
aiwfctl integration verify --work-id <work-id>
aiwfctl integration verify --work-id <work-id> --with-emulator
aiwfctl integration emulator prepare --work-id <work-id>
aiwfctl integration emulator health --work-id <work-id>
aiwfctl integration test-plan --work-id <work-id>
aiwfctl integration finalize --work-id <work-id>
```

対象repositoryが `work/<work-id>/source/repository` 以外にある場合:

```powershell
aiwfctl integration analyze --work-id <work-id> --target-repo C:\path\to\repo
```

## 入力

- `work/<work-id>/source/repository/`
- `work/<work-id>/context/sdk-analysis-context.json`
- `work/<work-id>/context/sdk-external-discovery.json`
- `work/<work-id>/context/environment-selection.json`
- 既存のtests、docs/evidence、設定ファイル、Docker / compose、Adapter / Port / Interface

SDK解析contextがある場合、AWS/GCPの `cloud` metadataやStripeの `payment` metadataを統合品質確認へ引き継ぎます。

## 出力

```text
work/<work-id>/reports/system-integration-report.md
work/<work-id>/context/integration-context.json
```

`integration-context.json` は Context First manifestへ `system-integration` として登録されます。

## エミュレータ方針

`--with-emulator` を指定すると、クラウドエミュレータやサービス固有test helperの候補を整理します。

分類は次の3つです。

```text
emulator_verified
real_cloud_verification_required
unsupported_by_emulator
```

- AWS: LocalStack候補を優先します。
- GCP: 公式エミュレータまたはservice-specific test double候補を優先します。
- Stripe: Stripe CLI / test modeを候補にし、live billing動作はHuman Checkへ残します。

このworkflowは実クラウドや本番credentialを無条件に使いません。エミュレータ起動も、親workflowまたはHuman Checkで明示判断します。

## エミュレータtemplate

恒久templateは次に置きます。

```text
templates/boilerplates/integration/cloud-emulators/
├─ localstack/
├─ gcp-emulators/
└─ stripe-cli/
```

案件ごとの展開先は `work/<work-id>/` 配下です。

```text
work/<work-id>/test-environment/emulator/localstack/
work/<work-id>/test-environment/emulator/gcp-emulators/
work/<work-id>/test-environment/emulator/stripe-cli/
work/<work-id>/test-evidence/emulator/
```

`integration-context.json` の `emulator_candidates[*].template_path` にコピー元templateが記録されます。

template本体は直接編集せず、コピー先だけを編集します。

Phase 2では、次のCLIで候補templateをwork配下へ展開できます。

```powershell
aiwfctl integration emulator prepare --work-id <work-id>
```

出力:

```text
work/<work-id>/context/emulator-context.json
work/<work-id>/context/emulator-health-context.json
work/<work-id>/context/integration-test-plan-context.json
work/<work-id>/context/integration-finalization-context.json
work/<work-id>/test-evidence/emulator/health-summary.md
work/<work-id>/test-evidence/integration-test/integration-test-runbook.md
work/<work-id>/reports/system-integration-final-report.md
work/<work-id>/test-environment/emulator/
work/<work-id>/test-evidence/emulator/
```

既存のコピー先がある場合、既定では上書きせず `existing` として記録します。再展開が必要な場合のみ `--force` を使います。

Phase 3では、展開済みtemplateを起動前に点検します。

```powershell
aiwfctl integration emulator health --work-id <work-id>
```

このhealthは非破壊です。Docker composeを起動せず、template配置、`.env.example`、README、health確認資料、evidence directory、Docker CLIの存在を確認し、`emulator-health-context.json` と `health-summary.md` を出力します。`--probe-docker` を付けた場合だけ、`docker version` と `docker compose version` の非破壊確認を行います。

`emulator-health-context.json` は Context First manifest に `emulator-health` として登録されます。後続workflowはここを読んで「DuckDB参照OK」のように「エミュレータ準備/前提OK」または「Human Checkが必要」を判断します。

Phase 4では、Integration Testの実行計画を作ります。

```powershell
aiwfctl integration test-plan --work-id <work-id>
```

このcommandはDocker composeや対象システムを起動しません。指示書のIntegration Test順序に沿って、試験環境構築、外部依存起動、Health Check、初期データ投入、対象システム起動、正常系、異常系、ログ・データ確認、環境初期化を `integration-test-plan-context.json` と `integration-test-runbook.md` に落とします。

`integration-test-plan-context.json` は Context First manifest に `integration-test-plan` として登録されます。Docker起動、seed投入、対象system起動、cleanupなどローカル状態を変更する操作はHuman Check後に実行します。

Phase 5では、Integration Test実行後のEvidenceを整理し、違和感と完了条件を判定します。

```powershell
aiwfctl integration finalize --work-id <work-id>
```

このcommandはテストやDockerを実行しません。`work/<work-id>/test-evidence/`、`work/<work-id>/evidence/`、対象repositoryの `docs/evidence/` を読み、完了条件、Evidence有無、空ファイル、emulator health、Integration Test plan、Knowledge化対象をまとめます。

`integration-finalization-context.json` は Context First manifest に `integration-finalization` として登録されます。`system-integration-final-report.md` はKnowledge化フローへ渡す最終レポート候補です。ただし、ソースコード全体をそのままKnowledge化しません。

## 確認観点

- 既存アーキテクチャと依存方向
- Adapter / Port / Interface境界
- SDK固有型や例外が内部へ漏れていないか
- Endpoint、Region、Project ID、API Key、Credential Path、Timeout、Retry、Emulator接続先が直書きされていないか
- Unit Test / Integration Test / Evidence配置
- ログ、メトリクス、Health Check、異常系
- Emulatorと本番の差分
- Knowledge化すべき判断

## Human Check

次の場合はHuman Checkへ戻します。

- 既存アーキテクチャや依存方向を変える
- 本番credential、本番クラウド、本番決済、本番networkを使う
- SDKをApplication Logicから直接呼び出す
- 共通部品を新規作成または大きく変更する
- エミュレータと本番に大きな差がある
- 既存試験では検証できない
- 運用手順が増える
- 違和感を解消できない
