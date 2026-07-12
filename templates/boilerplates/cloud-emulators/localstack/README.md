# LocalStack Emulator Template

AWS SDK連携のIntegration Testを、実AWSへ接続せずに確認するためのtemplateです。

## 想定サービス

- S3
- DynamoDB
- SQS
- SNS
- Lambda
- Kinesis
- Secrets Manager
- CloudWatch

## 展開先

```text
work/<work-id>/test-environment/emulator/localstack/
```

## セットアップ

```powershell
Copy-Item -Recurse templates\boilerplates\cloud-emulators\localstack work\<work-id>\test-environment\emulator\localstack
Copy-Item work\<work-id>\test-environment\emulator\localstack\.env.example work\<work-id>\test-environment\emulator\localstack\.env
```

## 起動

```powershell
cd work\<work-id>\test-environment\emulator\localstack
docker compose up -d
```

## 停止

```powershell
docker compose down
```

## アプリ側で差し替える設定

- endpoint: `http://localhost:4566`
- region: `.env` の `AWS_DEFAULT_REGION`
- access key: dummy value
- secret key: dummy value
- credential provider: emulator用profileまたは環境変数

本番credentialは使いません。

## Evidence

以下を `work/<work-id>/test-evidence/emulator/localstack/` に保存します。

- 起動コマンド
- health check結果
- 対象service一覧
- `emulator_verified` / `real_cloud_verification_required` / `unsupported_by_emulator` の分類
- 本番AWSとの差分
- Human Check結果
