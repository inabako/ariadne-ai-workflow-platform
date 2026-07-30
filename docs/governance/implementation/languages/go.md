---
language: ja-JP
---

# Go Rules

この文書は、Ariadne AI Workflow Platform が生成、変更、保守する Go成果物へ適用する言語固有規範を定義します。

言語別規範は、言語 Tips や好みの実装スタイルを集めるための文書ではありません。各言語で発生しやすい security issue、vulnerability、unsafe side effect、secret leakage、検証不能な実装を防ぐための最低規範です。

対象には次を含みます。

* API。
* CLI。
* worker。
* gateway。
* batch。
* daemon。
* runtime component。
* library。
* integration tool。

## 目的

* package responsibility と dependency direction を明確にする。
  * 標準 library を中心に小さく保つ。
* error、context、goroutine lifecycle を正しく扱う。
* graceful shutdown と resource 管理を標準化する。
* build、test、race detection を再現可能にする。
* interface や frameworkの過剰導入を防ぐ。

## Supported Version

### MUST

* supported Go version を `go.mod`等へ記載する。
* CI と build environment で version を揃える。
* support終了済み version を新規採用しない。
* toolchain directive を利用する場合は目的を明示する。
* version 更新時に language、standard library、dependency compatibility を確認する。

## Project Structure

推奨構成:

```text
cmd/
└── app/
    └── main.go

internal/
├── app/
├── domain/
├── adapters/
├── config/
└── observability/

tests/
scripts/
docs/
go.mod
go.sum
```

### MUST

* executable entrypoint を明確にする。
* repository 内部のみで利用する code を `internal/` へ配置する。
* `pkg/` を理由なく作成しない。
* package 名を責務に対応させる。
* import cycle を作らない。
* `util`、`common`、`helper` package へ無秩序に処理を集めない。

### SHOULD

* package を小さく保つが、file数だけで分割しない。
* domain capability または責務で package を分ける。
* technology adapter を core logic から分離する。
* package documentation を public package へ用意する。

## Main Package

### MUST

`main` packageの責務を次へ限定します。

* configuration読込。
* dependency construction。
* signal setup。
* application起動。
  * 終了 code決定。

business logic、database query、HTTP handler詳細を `main` へ直接記述しません。

## Naming

### MUST

* package 名は短く、単数形を基本とする。
* package 名へ `util` や `common` を安易に使用しない。
* exported identifier は責務が分かる名称にする。
* acronymの表記を repository 内で統一する。
* receiver 名は短く一貫させる。
* getter へ不要な `Get` prefix を付けない。

### SHOULD

* interface は behavior を表す名称にする。
  * 一方法の interface は必要に応じて `-er`形式を使用する。
* package 名と exported type 名の重複を避ける。
* boolean は状態や判定として読める名称にする。

## Formatting

### MUST

* `gofmt`相当の標準 formatter を使用する。
* import ordering を自動 tool へ委ねる。
* formatter差分を review対象の本質的変更へ混在させない。
* generated code を識別可能にする。

## Error Handling

### MUST

* error を明示的に返す。
* error を握り潰さない。
* context を追加しても original error を追跡可能にする。
  * 通常の failure へ `panic` を使用しない。
* library package 内で `os.Exit` や `log.Fatal` を実行しない。
* sentinel error、typed error、wrapped error を用途に応じて使い分ける。
* secret を error message へ含めない。

### SHOULD

* error message は小文字で始め、末尾に句点を付けない慣例に従う。
* `errors.Is`、`errors.As` を利用可能にする。
* caller が判断すべき error を contract として定義する。
  * 同じ error を複数 layer で log しない。
* transport error と domain error を分ける。

## Context

### MUST

* operation lifecycle へ `context.Context` を伝播する。
* `context.Context` を struct field へ長期保存しない。
* functionの第一引数とする慣例に従う。
* cancellation と deadline を尊重する。
* optional argumentの代替として context value を濫用しない。
* context keyの衝突を防ぐ。
* callerの context を無断で `context.Background()` へ置き換えない。

### SHOULD

* request-scoped metadataだけを context へ入れる。
* business data を context へ保存しない。
* timeout を boundary で設定する。
* child operation へ context を渡す。

## Interfaces

### MUST

* interface は利用側で定義することを基本とする。
* 差替え需要のない実装へ無理に interface を作らない。
  * 巨大 interface を作らない。
* external SDKの全 method をそのまま interface 化しない。
* interface を単なる mock 生成目的だけで増やさない。

### SHOULD

* 小さな behavior単位で定義する。
* concrete type を適切に利用する。
* interface satisfaction を compile 時に確認する場合は意図を明確にする。
* return type を不必要に interface へ抽象化しない。

## Goroutine Lifecycle

### MUST

* goroutineの owner を明確にする。
  * 終了条件を定義する。
* cancellation を伝播する。
* goroutine 内の error を回収する。
* unbounded goroutine を生成しない。
* shutdown 時に child goroutine を待機する。
* goroutine leak を防止する。
* recover を無秩序に使用しない。

### SHOULD

* structured concurrency に近い管理を行う。
* worker pool や semaphore で concurrency を制限する。
* error group を必要に応じて利用する。
* fire-and-forget を原則避ける。

## Channels

### MUST

* channel を close する責任を明確にする。
* receiver 側で無断に channel を close しない。
* nil channel や closed channelの挙動を考慮する。
* unbuffered と buffered を目的に応じて選択する。
* channel size を無制限にしない。
* send または receive が永遠に block しないよう cancel を考慮する。

### SHOULD

* channel より単純な同期手段で足りる場合はそちらを使う。
* data ownershipの移譲を明確にする。
* channel を event bus として無秩序に利用しない。

## Shared State

### MUST

* shared mutable state を mutex、atomic、channel等で保護する。
* race detector で検出可能な test を用意する。
* lock取得順序を必要に応じて定義する。
* lock 中に長時間の external I/O を行わない。
* copy禁止 type を不用意に copy しない。

## Resource Management

### MUST

* resource取得後に `defer`等で release を保証する。
* `defer` を loop 内で無制限に積み上げない。
* file、response body、row、transaction を close する。
* close error が重要な場合は確認する。
* partial initialization 時の cleanup を行う。

## HTTP Server

HTTP serviceの場合:

### MUST

* read、write、idle、header timeout を設定する。
* request body size を制限する。
* graceful shutdown を実装する。
* input を validation する。
* status code と error response を統一する。
* panic recovery を boundary で行う。
* request identifier を必要に応じて付与する。
* default server を無制限設定で使用しない。
* `http.Client` へ timeout を設定する。

### SHOULD

* handler を薄く保つ。
* transport model と domain model を分離する。
* middlewareの順序を明確にする。
* health endpoint へ重大な副作用を持たせない。

## CLI

CLIの場合:

### MUST

* help を提供する。
* exit code を定義する。
* stdout と stderr を区別する。
* destructive operation へ明示 flag または Human Check を適用する。
* machine-readable output を必要に応じて提供する。
* token や password を command argument として要求しないことを基本とする。
* signal と cancel を扱う。

## Configuration

### MUST

* environment variable を domain package から直接読まない。
* typed configuration へ変換する。
* required value を startup 時に validation する。
* duration、size、countの単位を明示する。
* secret を `String()` や log へ含めない。
* safe default を使用する。

## Dependency Management

### MUST

* Go Modules を使用する。
* `go.mod` と `go.sum` を version control する。
  * 不要な dependency を追加しない。
* `replace` directiveの目的と解除条件を明示する。
* private module取得方法を docs へ記載する。
* tool dependency と runtime dependency を区別する。
* dependency update 後に test と vulnerability 確認を行う。

## Testing

### MUST

* `go test ./...`相当の共通 entrypoint を提供する。
* external I/O を boundary で差し替える。
* race risk がある場合は race detector を実行する。
* test で goroutine leak を残さない。
* clock、network、filesystem を制御する。
* test順序へ依存しない。
* table-driven test を意味のある case へ利用する。

### SHOULD

* parser、protocol、input validation へ fuzz test を検討する。
* performance-sensitive path へ benchmark を用意する。
* integration test を build tag等で区別する。
* example test を public API へ用意する。

## Build

### MUST

* build command を再現可能にする。
* version、commit、build metadata を必要に応じて埋め込む。
* target OS と architecture を明示する。
* CGO dependency を明確にする。
* binary へ secret を埋め込まない。
* cross compileの対象を test する。
* build artifact と source revision を対応付ける。

## Security

### MUST

* command引数を shell string へ直接連結しない。
* path traversal を防止する。
* HTTP response body や file size を無制限に読み込まない。
* random token には暗号学的に安全な source を利用する。
* TLS verification を無効にしない。
* template rendering や SQL には安全な API を使用する。
* unsafe packageの利用には明確な理由と review を必要とする。

## AI Agent 向け規範

AI Agent は Go code 変更時に次を確認します。

1. Go version。
2. package responsibility。
3. dependency direction。
4. error contract。
5. context。
6. goroutine lifecycle。
7. channel ownership。
8. resource cleanup。
9. timeout と shutdown。
10. interface necessity。
11. race detection。
12. build と test。

## まとめ

* Go成果物は package責務と dependency direction を明確にする。
* error、context、goroutine、resource lifecycle を明示する。
* interface や framework を必要以上に増やさない。
* timeout、graceful shutdown、race detection を標準的に扱う。
* build artifact と source revision を再現可能に対応付ける。
