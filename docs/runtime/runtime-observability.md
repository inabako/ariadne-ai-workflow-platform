# Runtime Observability

Runtime Observability は、Ariadne AI Workflow Platform の runtime がどのように動いたかを人間とAI Agentの双方が確認するための観測基盤です。

目的は、単にログを増やすことではありません。workflow、agent、Context First、RAG、token、cost、Human Check、evidence、error の状態を、後続workflowが読める形で残すことです。

## 取得するメトリクス

| 分類 | 内容 |
| --- | --- |
| Workflow | workflow id、workflow name、開始、完了、失敗、実行時間 |
| Agent | agent name、開始、完了、処理時間 |
| Token | input token、output token、total token、推定値かどうか |
| Cost | input cost、output cost、total cost、通貨、推定値かどうか |
| Context | 選択されたContext数、推定Context token、RAG参照回数、Dispatcher経路 |
| Runtime | retry回数、Human Check発生有無、Evidence生成有無、error数 |

## Runtime全体ログ

Runtime全体の時系列ログは、既定で月次ローテーションされます。

```text
runtime/logs/runtime-metrics-YYYYMM.jsonl
```

1イベントを1 JSON行として追記します。

例:

```jsonl
{"event":"workflow_started","workflow_name":"/runtime-health-check","duration_ms":0}
{"event":"token_usage_recorded","token_usage":{"input":1200,"output":300,"total":1500,"estimated":true}}
{"event":"workflow_completed","workflow_name":"/runtime-health-check","duration_ms":3200}
```

`runtime/logs/` はローカル生成物であり、Git管理対象にしません。

## Workflow単位の証跡

workflow単位の要約は、必要に応じて次の場所へ保存します。

```text
work/<work-id>/test-evidence/runtime-metrics.json
work/<work-id>/context/runtime-metrics.json
```

`context/runtime-metrics.json` は Context First manifest に `runtime-metrics` として登録できます。後続workflowは、runtimeの実行時間、token見積もり、context量、Human Check、error数を読み取れます。

## TokenとCostの扱い

正確な token / cost が外部から渡される場合は、その値を記録します。

正確な値が取れない場合は、推定値として記録し、必ず次を含めます。

```json
{
  "estimated": true
}
```

価格表は変化するため、初期実装ではruntime内に固定価格を持ちません。costは外部から渡された値、または推定値として扱います。

## 失敗時の扱い

Observabilityの書き込みに失敗しても、workflow本体は失敗させません。

ただし、失敗を握りつぶさず、collectorの `write_warnings` と戻り値に warning として残します。

## 拡張余地

- agent別の累積cost集計
- workflow別の月次cost集計
- runtime health checkへの observability summary 追加
- OpenTelemetry exporterへの変換
- `aiwfctl doctor` での直近metrics異常検知
