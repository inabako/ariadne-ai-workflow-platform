---
language: ja-JP
---

# Error Handling

この文書は、成果物における errorの検出、分類、伝播、回復、記録の方針を定義します。

error handling は、失敗を隠すための処理ではありません。

失敗の原因、影響、回復可能性、次の行動を、人間と AI Agent が判断できる状態を作ります。

## 目的

* failure を success として扱わない。
* errorの発生箇所と原因を追跡可能にする。
* retry、fallback、abort を適切に判断する。
* secret や内部情報を露出しない。
* failure から復旧または改善へ接続できる Evidence を残す。

## Error Classification

error は、少なくとも次の観点で分類します。

* validation error。
* configuration error。
* authentication / authorization error。
* external dependency error。
* timeout。
* resource exhaustion。
* conflict。
* data integrity error。
* retryable error。
* non-retryable error。
* programming error。
* Human Check required。
* cancelled operation。

分類方法は成果物に応じて enum、error type、status code、result schemaなどで表現します。

## Detection

### MUST

* invalid input や前提条件違反を可能な限り早く検出する。
* 必須 configuration の不足を起動時または処理開始前に検出する。
* external commandの exit status を確認する。
* network responseの status、body、timeout を確認する。
* write operation では、実際に反映されたか確認する。
* partial success を完全な success として扱わない。

## Propagation

### MUST

* error を黙って破棄しない。
* caller が判断すべき error を内部で success へ変換しない。
* error へ context を追加しても、元の原因を追跡可能にする。
* layer を越える際は、その layer に適した error contract へ変換する。
* internal exception detail を外部利用者へ無条件に公開しない。

### SHOULD

* 同じ error を複数 layer で重複処理しすぎない。
* transport error と domain error を区別する。
* recover できない error は早期に停止する。
* caller へ不要な implementation detail を露出しない。

## Retry

### MUST

* retry可能性を明示的に判断する。
* authentication failure、validation failure、permission denial を無条件に retry しない。
* retry回数、間隔、timeout を無制限にしない。
* retry対象 operationの idempotency を確認する。
* retry exhaustion を観測可能にする。
* retry による重複処理や二重登録を考慮する。

### SHOULD

* exponential backoff や jitter を検討する。
* retry budget を設定する。
* external serviceの rate limit を尊重する。
* retry 前に cancel状態を確認する。

## Fallback

### MUST

* fallback を暗黙に実行しない。
* fallback発生を log または Evidence へ残す。
* fallback 結果が通常結果と異なる場合、その状態を caller へ伝える。
* security や data integrity を弱める fallback を採用しない。
* stale data を返す場合は、その状態を明示する。

## Cleanup and Rollback

### MUST

* resource取得後の cleanup を保証する。
* partial update が起こり得る処理では、rollback または recovery方法を定義する。
* cleanup failure を無条件に無視しない。
* original error を cleanup error で失わない。
* temporary file、lock、session、transactionの終了を確認する。

## Error Messages

### MUST

error message には、必要に応じて次を含めます。

* operation。
  * 対象。
* phase。
* failure reason。
* retry可能性。
* next action。

次を含めません。

* password。
* token。
* private key。
* personal data。
* 不要な request body。
* 内部 network情報。
* stack traceの無制限な外部公開。

### SHOULD

* 人間向け message と machine-readable code を分ける。
* 同じ error codeの意味を安定させる。
* 利用者が修正可能な error では、具体的な対応を示す。

## Cancellation and Timeout

### MUST

* cancellation と failure を区別する。
* timeout値を無制限または暗黙にしない。
* timeout 後に処理が継続しないことを確認する。
* child operation へ cancel を伝播する。
* timeout発生時の partial state を確認する。

## AI Agent Behavior

AI Agent は error を発見した場合、次を整理します。

1. 発生箇所。
2. 再現条件。
3. error分類。
4. retry可能性。
5. 影響範囲。
6. data や state への影響。
7. 回避策または復旧方法。
8. 必要な test。
9. Human Check 要否。

原因不明の error を、推測だけで修正済みと判断しません。

## Evidence

重大な failure では、次を Evidence へ残します。

* error identifier。
* 発生日時。
* operation と phase。
* 入力の安全な要約。
* environment。
* stack trace または log location。
* retry、fallback、rollback 結果。
* 影響範囲。
* 再現手順。
* corrective action。
* residual risk。

## まとめ

* error を分類し、caller が次の行動を判断できる状態にする。
* retry、fallback、rollback を暗黙に実行しない。
* failure を success として隠さない。
* message と Evidence へ secret を残さない。
* error は改善へ接続できる共有情報として扱う。
