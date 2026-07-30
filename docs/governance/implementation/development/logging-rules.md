---
language: ja-JP
---

# Logging Rules

この文書は、成果物における logの目的、内容、level、構造、秘密情報の扱いを定義します。

log は、大量に出力することを目的としません。

operationの状態、失敗、判断、副作用を追跡し、人間と AI Agent が状況を理解できる状態を作ります。

## 目的

Logging Rules は、次を実現します。

* operationの開始、完了、失敗を追跡できる。
* 複数 component間の処理を関連付けられる。
* retry、fallback、Human Check、external mutation を確認できる。
* secret や personal data を保護する。
* log を metrics、report、Evidence と適切に分離する。

## Log Level

### ERROR

処理が失敗し、期待する成果を完了できない状態。

### WARN

処理は継続できるが、fallback、retry、degraded state、将来の failure につながる状態。

### INFO

重要な operation、state transition、external mutation、Human Check、処理結果。

### DEBUG

開発、調査、詳細追跡に必要な内部情報。

### TRACE

大量かつ詳細な処理追跡。通常運用では原則無効とします。

## Required Events

### MUST

必要に応じて次を記録します。

* application または operationの開始。
* application または operationの完了。
* failure。
* retry開始と retry exhaustion。
* fallback。
* Human Check 要求。
* external mutation。
* configuration validation failure。
* dependency unavailable。
* state transition。
* rollback または cleanup failure。

すべての function entry や変数値を無条件に記録しません。

## Structured Logging

### MUST

machine-readableな運用が必要な成果物では、structured logging を使用します。

推奨項目:

* timestamp。
* level。
* event name。
* component。
* operation。
* work-id。
* request-id。
* correlation-id。
* environment。
* status。
* error code。
* duration。
* retry count。

### SHOULD

* key 名と event 名を repository 内で統一する。
* message本文だけに重要情報を埋め込まない。
* 値の単位を明確にする。
* schema 変更時は consumer への影響を確認する。

## Correlation

### MUST

* 複数 component をまたぐ処理では、追跡 identifier を伝播する。
* work-id、request-id、correlation-idの意味を混同しない。
* identifier を無制限に新規発行しない。
* external response へ内部 identifier を露出する場合は安全性を確認する。

## Sensitive Information

### MUST NOT

次を log へ出力しません。

* password。
* API key。
* access token。
* refresh token。
* session secret。
* private key。
* authorization header。
* personal dataの全文。
* payment情報。
* production dataの無加工出力。
* secret を含む configuration。
* prompt や response 内の機密情報。

### MUST

* 必要な識別には mask、hash、部分表示を使用する。
* request、response bodyの出力は明示的に制限する。
* DEBUG level でも secret を出力しない。
* exception object に secret が含まれる可能性を考慮する。

## Error Logging

### MUST

* errorの operation、対象、phase、identifier を記録する。
* 同じ error を複数 layer で重複出力しすぎない。
* error を log へ出しただけで処理済みとしない。
* stack trace を必要な境界で一度記録する。
* external利用者向け message と内部調査 log を分離する。

## Performance

### MUST

* high-frequency path で過剰な log を出力しない。
* 巨大 object や binary data を出力しない。
* log 生成自体が主要処理を阻害しないようにする。
* log volume、retention、cost を考慮する。

### SHOULD

* sampling や aggregation を検討する。
* duration や件数は metrics として扱うことを検討する。
* routine success log を増やしすぎない。

## Logs, Metrics and Evidence

```text
Logs
 実行時の出来事を追跡する

Metrics
 状態や傾向を集計する

Evidence
 判断、検証、完了条件を保存する
```

### MUST

* logだけを完了 Evidence にしない。
* test 結果や Human Check 結果は専用 artifact へ残す。
* 長期分析が必要な値は metrics または process report へ出力する。
* chat log を system logの代替にしない。

## Retention and Access

### MUST

* logの保存期間と access権限を環境に応じて定義する。
* production log への access を最小権限にする。
* personal data を含む可能性がある log は取扱方針を明確にする。
* 不要になった log を無期限に保持しない。

## AI Agent 向け規範

AI Agent は logging を追加する際、次を確認します。

1. この log から誰が何を判断するか。
2. log level は適切か。
3. secret や personal data が含まれないか。
4. 既存 event と重複しないか。
5. correlation可能か。
6. log ではなく metrics や Evidence へ置くべきではないか。
7. volume と performance への影響。

## まとめ

* log は判断と追跡に必要な情報へ限定する。
* structured data と correlation identifier を適切に利用する。
* secret や personal data を level に関係なく出力しない。
* log、metrics、Evidence の責務を分離する。
* 大量出力ではなく、次の行動へ接続できる observability を目指す。
