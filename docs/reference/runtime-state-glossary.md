# Runtime State Glossary

Ariadne Runtime の状態語彙は、日常運用と release 前確認で同じ意味になるように扱います。

## Overall Status

| Status | Meaning | Typical Action |
| --- | --- | --- |
| `ready` | workflow を開始できる状態です。 | 対象 workflow を開始します。 |
| `attention` | 作業は続けられますが、確認した方がよい項目があります。 | `attention_reasons` と `next_actions` を確認します。 |
| `blocked` | workflow 開始または継続前に解消が必要です。 | `doctor`、`preflight`、`trace recover`、Human Check へ進みます。 |
| `pass` | 個別 gate が通っています。 | 次の gate へ進みます。 |
| `warning` | 個別 check に警告があります。 | warning の severity / category / repair command を確認します。 |
| `failed` / `fail` | 実行または検査が失敗しています。 | failure event と resume command を確認します。 |

## ready と strict

`aiwfctl ready` は、`status`、`doctor`、dependency readiness、UT spec sync をまとめて確認します。

通常モードでは、未コミット差分や未 acknowledgement の runtime log problem など、作業を直ちに止める必要がないものは `attention` です。

`aiwfctl ready --strict` では、`attention` も `blocked` として扱います。Release 前、CI相当確認、PR直前の最終確認では `--strict` を使います。

## attention_reasons

`attention_reasons` は、なぜ `attention` になったかを明示する配列です。

主な `id` は次の通りです。

| ID | Meaning |
| --- | --- |
| `git-dirty` | working tree に未コミット差分があります。 |
| `trace-active` | workflow trace が active です。 |
| `trace-invalid` | `active-trace.json` が壊れている可能性があります。 |
| `trace-stale` | active trace が古く、復旧確認が必要です。 |
| `runtime-last-problem-event` | 未 acknowledgement の問題 event が runtime log に残っています。 |
| `doctor-warnings` | `aiwfctl doctor` の warning が残っています。 |
| `dependency-readiness` | runtime 実行に必要な依存関係の確認が必要です。 |

## Runtime Log Acknowledgement

`log acknowledge-problem` は runtime log を削除しません。既知または解決済みとして人間が確認した problem event を、`status` の last problem 判定から除外するための記録を残します。

```powershell
.\runtime\windows-script\aiwfctl.cmd log acknowledge-problem --trace-id <trace-id> --sequence <sequence> --reason "known and reviewed"
```

複数候補がある場合は、先に次で対象を確認します。

```powershell
.\runtime\windows-script\aiwfctl.cmd log tail --problems -n 20
.\runtime\windows-script\aiwfctl.cmd log grep --trace-id <trace-id> --problems
```
