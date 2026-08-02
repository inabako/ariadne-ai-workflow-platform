# Runtime Logs

`logs/runtime/` は、`aiwfctl` と runtime helper が出力する runtime event log の既定ディレクトリです。

主な出力:

- `runtime-events.log`: runtime command の開始、完了、失敗、block、diagnostics を trace id と sequence 付きで記録する JSONL 形式のイベントログ。
- `runtime-events.log.1`: サイズ上限を超えた場合の rotation file。
- `active-trace.json`: `aiwfctl trace begin` から `aiwfctl trace end` までの workflow execution trace state。

## 使い方

`runtime-events.log` は、workflow の失敗調査、Feedback 作成、Review Council / Human Gate の判断材料として参照します。

1つの workflow 実行を同じ trace id で追跡する場合は、開始時に trace を begin し、終了時に end します。

```powershell
aiwfctl trace begin --workflow /runtime-health-check
aiwfctl trace status
aiwfctl trace end
```

`active-trace.json` が存在する間、後続の `aiwfctl` 実行は同じ trace id を使用します。`AIWF_TRACE_ID` を明示した場合は、環境変数の値が優先されます。

`active-trace.json` は `last_sequence` を保持します。`trace begin` から `trace end` までの runtime event は、同じ trace id の中で `00001` から workflow 全体の通番として増加します。

長期的に残すべき内容は、log file をそのまま保存せず、必要な trace id、command、status、reason、duration、failed / blocked event を要約して evidence artifact へ転記します。

## Git 管理

このディレクトリの README 以外は Git 管理しません。

実ログには machine-local path、環境情報、command argument が含まれる可能性があります。公開前や commit 前に、実ログが stage されていないことを確認してください。
