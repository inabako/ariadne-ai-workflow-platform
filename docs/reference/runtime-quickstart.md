# Runtime UX Quickstart

Ariadne Runtime で迷ったときは、まず `status` で現在地を確認し、必要に応じて `trace`、`doctor`、`preflight` へ進みます。

## 最短確認

```powershell
.\runtime\windows-script\aiwfctl.cmd status
.\runtime\windows-script\aiwfctl.cmd status --summary --json
.\runtime\windows-script\aiwfctl.cmd status --problems --json
.\runtime\windows-script\aiwfctl.cmd ready
.\runtime\windows-script\aiwfctl.cmd ready --json
```

`--summary --json` は dashboard や Agent 向けの軽量ビューです。

`--problems --json` は、失敗、warning、未準備項目など、対応が必要な情報だけを見るための調査ビューです。問題がない `doctor` や空の `runtime` ブロックは省略されます。

`--verbose --json` は、すべての状態を明示的に確認したいときに使います。

`ready` は、workflow を始めてよいかをまとめて確認する入口です。`status`、`doctor`、dependency readiness、UT spec sync を集約し、`ready`、`attention`、`blocked` のいずれかを返します。

Release 前や CI 相当の確認では、`attention` も `blocked` として扱う `--strict` を使います。

```powershell
.\runtime\windows-script\aiwfctl.cmd ready --strict --json
.\runtime\windows-script\aiwfctl.cmd ready --json --output work/evidence/runtime-ready.json
```

状態の意味は [Runtime State Glossary](runtime-state-glossary.md) にまとめています。

## attention reasons

`status` は、なぜ `attention` になっているかを `attention_reasons` に分けて出力します。

主な理由は次の通りです。

- `git-dirty`: working tree に未コミット差分があります。
- `trace-active` / `trace-invalid` / `trace-stale`: workflow trace の確認または復旧が必要です。
- `runtime-last-problem-event`: 未 acknowledgement の問題 event が runtime log に残っています。
- `doctor-warnings`: `doctor` warning が残っています。
- `dependency-readiness`: runtime 実行に必要な依存関係の確認が必要です。

## preflight と doctor

| Command | 見るもの | 主な用途 |
| --- | --- | --- |
| `aiwfctl status` | 現在地、直近問題、doctor warning count、dependency readiness | 最初の確認 |
| `aiwfctl preflight` | OS、tool、package、credential readiness | fresh checkout 後、GitHub 操作前、ローカル予行前 |
| `aiwfctl doctor` | repository 構造、schema、runtime contract、docs/test evidence | release 前、warning 調査、runtime 修復前 |

`preflight` は環境依存の準備確認、`doctor` は repository 自身の健全性確認です。`status` は両方の要約を入口として表示します。

## workflow が止まった

```powershell
.\runtime\windows-script\aiwfctl.cmd status --problems --json
.\runtime\windows-script\aiwfctl.cmd trace show --problems
.\runtime\windows-script\aiwfctl.cmd doctor --fix-suggestion-only
```

`trace show --problems` は blocked / failed / warning / error event に絞ります。

`doctor --fix-suggestion-only` は修復を実行せず、推奨コマンドだけを確認します。

## Runtime Log Acknowledgement

解決済み、または既知として人間が確認済みの問題が `status` の last problem に残る場合は、ログを削除せず acknowledgement を残します。

trace id と sequence が分かっている場合:

```powershell
.\runtime\windows-script\aiwfctl.cmd log acknowledge-problem --trace-id <trace-id> --sequence <sequence> --reason "known and reviewed"
```

同じ command の問題 event をまとめて acknowledgement する場合:

```powershell
.\runtime\windows-script\aiwfctl.cmd log acknowledge-problem --command "env select" --all --reason "known and reviewed"
```

acknowledgement は `logs/runtime/problem-acknowledgements.json` に保存されます。元の `logs/runtime/runtime-events.log` は証跡として残り、`status` の last problem 判定からだけ除外されます。

`status` が未 acknowledgement の問題を検出した場合は、次のような具体コマンドを `next_actions` と `attention_reasons` に表示します。

```powershell
.\runtime\windows-script\aiwfctl.cmd log acknowledge-problem --trace-id <trace-id> --sequence <sequence> --reason "known and reviewed"
```

同種の古い問題 event が複数残っている場合は、まず `log tail --problems` か `log grep --trace-id <trace-id> --problems` で対象を確認し、問題ないものだけ acknowledgement してください。

```powershell
.\runtime\windows-script\aiwfctl.cmd log tail --problems -n 20
.\runtime\windows-script\aiwfctl.cmd log grep --trace-id <trace-id> --problems
```

## Runtime Log Maintenance

`log summary --json` と `status --summary --json` は、runtime log の件数、保持件数、閾値、archive候補件数を `maintenance` に出力します。

```powershell
.\runtime\windows-script\aiwfctl.cmd log summary --json
.\runtime\windows-script\aiwfctl.cmd log archive --keep-last 1000 --dry-run
```

`archive` は古いログを `logs/runtime/archive/` に退避し、直近分を `runtime-events.log` に残します。実書き込みには `--human-check approved` が必要です。

## RAG が検索できない

```powershell
.\runtime\windows-script\aiwfctl.cmd status --problems --json
.\runtime\windows-script\aiwfctl.cmd rag duckdb rebuild --source-repo work/db/ariadne-knowledge-platform --reset --dry-run
.\runtime\windows-script\aiwfctl.cmd doctor --fix-suggestion-only
```

DuckDB read model が不足している場合は、`doctor` と `status` の next action に再生成コマンドが出ます。実行前に `--dry-run` で対象を確認してください。

## GitHub push 前

```powershell
.\runtime\windows-script\aiwfctl.cmd preflight --profile github-cli
.\runtime\windows-script\aiwfctl.cmd doctor --json
.\runtime\windows-script\aiwfctl.cmd status --summary --json
```

GitHub credential、repository health、直近 trace/log の問題を分けて確認します。

## E2E/結合試験を残したい

```powershell
.\runtime\windows-script\aiwfctl.cmd e2e plan --work-id <work-id> --objective "試験目的"
.\runtime\windows-script\aiwfctl.cmd e2e contract scaffold --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd e2e contract --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd e2e readiness --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd e2e run --work-id <work-id> --dry-run
.\runtime\windows-script\aiwfctl.cmd e2e verify --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd e2e review-plan --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd e2e coverage --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd e2e explain --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd e2e final-gate --work-id <work-id> --human-decision approved --reviewer <name>
.\runtime\windows-script\aiwfctl.cmd e2e evidence-package --work-id <work-id> --trace-id <trace-id> --output docs/evidence/<work-id>/e2e-package.json
.\runtime\windows-script\aiwfctl.cmd e2e loop --work-id <work-id>
```

実行予定を確認したあと、実際に test plan 内の command を動かす場合だけ `--human-check approved` を付けます。詳細は [E2E Test Runtime](e2e-test-runtime.md) を参照してください。

## dry-run capabilities

機械可読な一覧は次で確認できます。

```powershell
.\runtime\windows-script\aiwfctl.cmd help runtime --json
```

よく使う dry-run:

```powershell
.\runtime\windows-script\aiwfctl.cmd rag build --dry-run --output work/evidence/rag-build-dry-run.json
.\runtime\windows-script\aiwfctl.cmd doctor --repair-encoding --dry-run --output work/evidence/doctor-repair-dry-run.json
.\runtime\windows-script\aiwfctl.cmd log archive --keep-last 1000 --dry-run --output work/evidence/runtime-log-archive-dry-run.json
```
