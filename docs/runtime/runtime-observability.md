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
logs/runtime-metrics-YYYYMM.jsonl
```

1イベントを1 JSON行として追記します。

例:

```jsonl
{"event":"workflow_started","workflow_name":"/runtime-health-check","duration_ms":0}
{"event":"token_usage_recorded","token_usage":{"input":1200,"output":300,"total":1500,"estimated":true}}
{"event":"workflow_completed","workflow_name":"/runtime-health-check","duration_ms":3200}
```

`logs/` はローカル生成物であり、Git管理対象にしません。

## Runtime Event Log

Runtime Event Log は、runtime の実行順序を人間と AI Agent が追跡するための時系列ログです。

保存先:

```text
logs/runtime/runtime-events.log
```

1イベントを1行として追記します。1ファイルが5MBを超える場合はローテーションし、既定では最大5世代を保持します。

形式:

```text
timestamp | trace-id | sequence | json
```

例:

```text
2026-07-21T06:15:32.692+09:00 | 8b8d3b4c1a2d4e6f8091b3c5 | 00002 | {"schema_version":"1.0","level":"warning","component":"ctl","event":"runtime_command_completed","workflow":"self-improvement","phase":"execute","operation_id":"self-improvement:create-feedback","attempt":1,"command":"self-improvement create-feedback","diagnostics":{"recoverable":true,"next_action":"review_command_usage","resume_command":"aiwfctl self-improvement create-feedback"},"input":{"json":false,"repo_root":"C:\\github\\v0.0.2\\ariadne-ai-workflow-platform","work_id":""},"output":{"status":"blocked","exit_code":2,"duration_ms":29,"output_bytes":562,"reason":"required_argument_missing"}}
```

各項目の意味:

| 項目 | 内容 |
| --- | --- |
| timestamp | local timezone付きの ISO-8601 timestamp |
| trace-id | 1回の runtime 実行を関連付ける24桁hexの識別子。明示指定された `AIWF_TRACE_ID` は相関用にそのまま使用する |
| sequence | 同一 trace 内のイベント順序。`00001` から始まる |
| json | component、event、input、output、関連 metadata |

`command` は JSON root の metadata として記録し、`input` へは重複して入れません。`input` には実行条件、`output` には終了状態、exit code、duration、出力量、共通 reason を記録します。

JSON payload には、後続workflowが読み取りやすいように次の標準項目を含めます。

| 項目 | 内容 |
| --- | --- |
| schema_version | Runtime Event Log の JSON payload schema version |
| level | `debug` / `info` / `warning` / `error` 相当の重要度 |
| workflow | Runtime command の主要workflow |
| phase | `prepare` / `validate` / `execute` / `cleanup` / `report` などの処理段階 |
| operation_id | 同一trace内で start / completed / failed を関連付ける処理単位 |
| attempt | retry / 再実行回数。初回は `1` |
| diagnostics | 復帰可能性、次アクション、復帰コマンド候補 |

Runtime Event Log は実行時の観測材料です。secret、token、password、credential などの機密情報は mask し、必要な判断材料だけを Evidence や process report へ昇格させます。

## Workflow単位の証跡

workflow単位の要約は、必要に応じて次の場所へ保存します。

```text
work/<work-id>/test-evidence/runtime-metrics.json
work/<work-id>/context/runtime-metrics.json
```

`context/runtime-metrics.json` は Context First manifest に `runtime-metrics` として登録できます。後続workflowは、runtimeの実行時間、token見積もり、context量、Human Check、error数を読み取れます。

## aiwfctl workflow入口

`aiwfctl github-knowledge <subcommand> --work-id <work-id>` は Runtime Observability を自動で記録します。
成功時、Human Check停止時、例外停止時のいずれでも、可能な範囲で次の出力を残します。

```text
logs/runtime-metrics-YYYYMM.jsonl
work/<work-id>/test-evidence/runtime-metrics.json
work/<work-id>/context/runtime-metrics.json
work/<work-id>/context/context-manifest.json
```

`context-manifest.json` には `runtime-metrics` として登録します。以降の本線workflowは、doctor gate や repair 復帰後もこの context を読み、同じgateから再開した実行結果を追跡できます。

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
