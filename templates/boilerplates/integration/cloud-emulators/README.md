# Cloud Emulator Boilerplates

このディレクトリは、System Integration Quality workflowで使うクラウド / 外部サービスエミュレータ用boilerplateです。

template本体は直接編集しません。案件ごとに `work/<work-id>/test-environment/emulator/` へコピーし、コピー先だけを編集します。

## Templates

| Template | 主用途 | 主な対象 |
| --- | --- | --- |
| `localstack/` | AWS local integration test | S3, DynamoDB, SQS, SNS, Lambda, Kinesis, Secrets Manager |
| `gcp-emulators/` | GCP local integration test | Pub/Sub, Firestore, fake GCS, service-specific fake client |
| `stripe-cli/` | Stripe test mode / webhook forwarding | Checkout, PaymentIntent, Webhook, idempotency |

## 展開先

```text
work/<work-id>/test-environment/emulator/
work/<work-id>/test-evidence/emulator/
work/<work-id>/context/emulator-context.json
```

## 共通ルール

- 本番credentialを使わない。
- production cloud / live payment endpointへ接続しない。
- endpoint、region、project、credential path、webhook secretは設定またはAdapter経由で差し替える。
- エミュレータ成功を本番同等と扱わない。
- 検証範囲は `emulator_verified`、`real_cloud_verification_required`、`unsupported_by_emulator` で記録する。
- 起動、停止、health check、差分、Human Check結果を `work/<work-id>/test-evidence/emulator/` に残す。

## 推奨コピー例

```powershell
Copy-Item -Recurse templates\boilerplates\integration\cloud-emulators\localstack work\<work-id>\test-environment\emulator\localstack
Copy-Item -Recurse templates\boilerplates\integration\cloud-emulators\gcp-emulators work\<work-id>\test-environment\emulator\gcp-emulators
Copy-Item -Recurse templates\boilerplates\integration\cloud-emulators\stripe-cli work\<work-id>\test-environment\emulator\stripe-cli
```

コピー後、対象systemの設定方式に合わせて `.env.example` を `.env` に複製し、値を調整します。
