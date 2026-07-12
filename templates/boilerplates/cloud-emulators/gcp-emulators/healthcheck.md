# GCP Emulators Health Check

## 起動確認

```powershell
docker compose ps
docker compose logs --tail=100 pubsub-emulator
docker compose logs --tail=100 firestore-emulator
docker compose logs --tail=100 fake-gcs
```

## 環境変数例

```powershell
$env:GOOGLE_CLOUD_PROJECT="local-emulator-project"
$env:PUBSUB_EMULATOR_HOST="localhost:8085"
$env:FIRESTORE_EMULATOR_HOST="localhost:8080"
```

## Evidence記録

```text
work/<work-id>/test-evidence/emulator/gcp-emulators/healthcheck.md
```

記録項目:

- 実行日時
- compose file path
- 対象service
- health result
- app connection result
- 本番GCPとの差分
- Human Check
