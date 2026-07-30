---
language: ja-JP
---

# Go Template

この文書は、Go を利用する API、CLI、worker、gateway、batch、runtime componentの boilerplate に適用する規範を定義します。

Go template は、過度な framework や抽象化を初期状態へ持ち込まず、標準 library を中心に、明確な package boundary と runtime lifecycle を提供します。

## 目的

* 小さく起動可能な Go application を提供する。
* package責務と dependency direction を明確にする。
* context、error、shutdown を適切に扱う。
* external I/O を adapter へ分離する。
* testしやすい構造を提供する。
* build、container、cross-platform利用を支える。

## Recommended Structure

```text
cmd/
└── app/
    └── main.go

internal/
├── app/
├── domain/
├── adapter/
├── config/
└── observability/

pkg/
tests/
scripts/
docs/
```

### MUST

* executable entrypoint を `cmd/`など明確な場所へ配置する。
* private implementation を `internal/` へ配置する。
* `pkg/` を不要に作成しない。
* package 名を責務に対応させる。
* `utils` や `common` へ処理を集めない。
* import cycle を作らない。

## Main Package

### MUST

`main`の責務を次へ限定します。

* configuration読込。
* dependency construction。
* signal setup。
* application起動。
  * 終了 code決定。

business logic を `main` へ記述しません。

## Context

### MUST

* request または operation lifecycle へ `context.Context` を伝播する。
* `context.Context` を struct field へ長期保存しない。
* cancellation と timeout を尊重する。
* optional parameterの代替として context value を濫用しない。
* context keyの衝突を防ぐ。
* `context.Background()` で callerの cancel を無断に切断しない。

## Error Handling

### MUST

* error を明示的に返す。
* error を握り潰さない。
* context を付加する場合も元 error を追跡可能にする。
* `panic` を通常の error処理に使用しない。
* sentinel error、typed error、error wrapping を責務に応じて選択する。
* library package 内で無断に process終了しない。

### SHOULD

* caller が判断すべき error を定義する。
* error message は小文字で始め、句点を付けない一般的慣例に従う。
* `errors.Is`、`errors.As` を利用可能な形にする。

## Interfaces

### MUST

* interface は利用側で定義することを基本とする。
* 実装が一つしかなく差替え需要もない interface を無理に作らない。
* 巨大 interface を作らない。
* external dependency の全 API をそのまま interface 化しない。

### SHOULD

* 小さな behavior単位の interface を使用する。
* testabilityだけを理由に全 struct を interface 化しない。
* concrete type を適切に利用する。

## Concurrency

### MUST

* goroutineの owner と終了条件を明確にする。
* goroutine leak を防止する。
* channelの close責任を送信側へ置くことを基本とする。
* shared state を同期する。
* unbounded goroutine を生成しない。
* error propagation を設計する。
* shutdown 時に child goroutine を待機する。

### SHOULD

* `errgroup`等を必要に応じて利用する。
* channel より単純な同期手段で足りる場合はそちらを選択する。
* mutex scope を小さくする。
* race detector を test で利用する。

## Configuration

### MUST

* environment variable を domain package から直接読まない。
* configuration を typed struct へ変換する。
* required value を startup 時に validation する。
* duration、size、countの単位を明示する。
* secret を log へ出力しない。

## HTTP Server

HTTP serviceの場合、次を守ります。

### MUST

* read、write、idle、header timeout を設定する。
* request body size を制限する。
* graceful shutdown を実装する。
* input を validation する。
* status code と error response を統一する。
* panic recovery を boundary で行う。
* request identifier を必要に応じて付与する。
* server instance を直接 `ListenAndServe`だけで放置しない。

## CLI

CLIの場合、次を守ります。

### MUST

* exit code を定義する。
* stdout と stderr を区別する。
* destructive operation に確認または明示 flag を必要とする。
* `--help` を提供する。
* machine-readable output を必要に応じて提供する。
* secret を command history へ露出しやすい引数として要求しない。

## Logging

### MUST

* structured logging を必要に応じて利用する。
* logger を global mutable state として乱用しない。
* secret を出力しない。
* context から correlation情報を取得する場合は型安全に扱う。
* library package で出力先を勝手に決めない。

## Testing

### MUST

* `go test ./...`相当の entrypoint を提供する。
* table-driven test を適切に利用する。
* external I/O を boundary で差し替える。
* race risk がある場合は race detector を実行する。
* time、filesystem、network依存を制御する。
* test で goroutine leak を残さない。

### SHOULD

* example test を public API へ用意する。
* fuzz test を parser や input boundary へ検討する。
* benchmark を performance-sensitive path へ用意する。
* integration test を build tag等で区別する。

## Dependency

### MUST

* Go Modules を使用する。
* `go.mod` と `go.sum` を管理する。
* unnecessary dependency を追加しない。
* replace directiveの用途と期限を明示する。
* private moduleの取得方法を README へ記載する。
* tool dependency を application dependency と区別する。

## Build

### MUST

* build command を再現可能にする。
* version、commit、build time を必要に応じて埋め込む。
* cross compile対象を明示する。
* CGO依存を明確にする。
* binary へ secret を埋め込まない。
* static linking を前提とする場合は license と runtime制約を確認する。

## Generated Structure

template は必要に応じて次を含めます。

```text
cmd/
internal/
tests/
scripts/
docs/
go.mod
go.sum
Makefile または task entrypoint
Dockerfile
README.md
```

## AI Agent 向け規範

AI Agent は Go template 変更時に次を確認します。

1. package responsibility。
2. import direction。
3. context。
4. error。
5. goroutine lifecycle。
6. interface necessity。
7. timeout。
8. shutdown。
9. dependency。
10. race。
11. build。
12. test。

## まとめ

* Go template は標準 library を中心に小さく保つ。
* `main`、package、external adapterの責務を分離する。
* context、error、goroutine lifecycle を明示する。
* interface と dependency を増やしすぎない。
* test、race detection、graceful shutdown を初期構成へ含める。
