# Stripe Webhook Test

## 前提

- test mode keyだけを使う。
- live keyを `.env` に入れない。
- Webhook endpointはlocal appのendpointへ向ける。

## 起動

```powershell
docker compose up
```

## Trigger例

Stripe CLIがhost側にも入っている場合のみ実行します。

```powershell
stripe trigger checkout.session.completed
stripe trigger payment_intent.succeeded
stripe trigger payment_intent.payment_failed
```

## Evidence記録

```text
work/<work-id>/test-evidence/emulator/stripe-cli/webhook-test.md
```

記録項目:

- 実行日時
- test event
- webhook signature verification result
- duplicate event behavior
- idempotency behavior
- app log
- Human Check
