# GCP Emulators Template

GCP SDK連携のIntegration Testを、実GCPへ接続せずに確認するためのtemplateです。

## 想定サービス

- Pub/Sub emulator
- Firestore emulator
- fake GCS server
- service-specific fake client

GCPはサービスごとにエミュレータ対応状況が異なるため、すべてを同一視しません。

## 展開先

```text
work/<work-id>/test-environment/emulator/gcp-emulators/
```

## 起動

```powershell
cd work\<work-id>\test-environment\emulator\gcp-emulators
docker compose up -d
```

## 停止

```powershell
docker compose down
```

## アプリ側で差し替える設定

- `PUBSUB_EMULATOR_HOST`
- `FIRESTORE_EMULATOR_HOST`
- fake GCS endpoint
- project id
- credential mode

本番Service Account keyは使いません。

## Evidence

以下を `work/<work-id>/test-evidence/emulator/gcp-emulators/` に保存します。

- 起動コマンド
- health check結果
- 対象service一覧
- `emulator_verified` / `real_cloud_verification_required` / `unsupported_by_emulator` の分類
- 本番GCPとの差分
- Human Check結果
