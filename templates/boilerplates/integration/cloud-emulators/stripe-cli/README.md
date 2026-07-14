# Stripe CLI / Test Mode Template

Stripe SDK連携のIntegration Testを、live決済へ接続せずに確認するためのtemplateです。

## 想定機能

- Checkout
- PaymentIntent
- Webhook forwarding
- Webhook signature verification
- Idempotency
- test mode event replay

## 展開先

```text
work/<work-id>/test-environment/emulator/stripe-cli/
```

## 起動

```powershell
cd work\<work-id>\test-environment\emulator\stripe-cli
docker compose up
```

Stripe CLIはloginやAPI keyが必要になる場合があります。live keyは使わず、test mode keyのみを使います。

## アプリ側で差し替える設定

- Stripe secret key: test mode
- Stripe publishable key: test mode
- Webhook signing secret
- Webhook endpoint URL
- Idempotency key policy

## Evidence

以下を `work/<work-id>/test-evidence/emulator/stripe-cli/` に保存します。

- 起動コマンド
- webhook forwarding結果
- 署名検証結果
- idempotency確認結果
- live billingとの差分
- Human Check結果
