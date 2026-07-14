# LocalStack Health Check

## 起動確認

```powershell
docker compose ps
docker compose logs --tail=100 localstack
```

## HTTP Health

```powershell
curl http://localhost:4566/_localstack/health
```

## AWS CLI例

AWS CLIがある場合のみ実行します。

```powershell
$env:AWS_ACCESS_KEY_ID="test"
$env:AWS_SECRET_ACCESS_KEY="test"
$env:AWS_DEFAULT_REGION="ap-northeast-1"
aws --endpoint-url http://localhost:4566 s3 ls
```

## Evidence記録

```text
work/<work-id>/test-evidence/emulator/localstack/healthcheck.md
```

記録項目:

- 実行日時
- compose file path
- 対象service
- health result
- app connection result
- 本番AWSとの差分
- Human Check
