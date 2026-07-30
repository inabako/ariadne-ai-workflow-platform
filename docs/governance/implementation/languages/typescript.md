---
language: ja-JP
---

# TypeScript Rules

この文書は、Ariadne AI Workflow Platform が生成、変更、保守する TypeScript成果物へ適用する言語固有規範を定義します。

言語別規範は、言語 Tips や好みの実装スタイルを集めるための文書ではありません。各言語で発生しやすい security issue、vulnerability、unsafe side effect、secret leakage、検証不能な実装を防ぐための最低規範です。

対象には次を含みます。

* Web application。
* Node.js service。
* CLI。
* library。
* worker。
* frontend。
* server-side application。
* integration tool。

## 目的

* static typing と runtime validation を適切に分離する。
* browser、server、build-timeの境界を明確にする。
* `any` や暗黙変換による不確実性を減らす。
* asynchronous error と resource lifecycle を管理する。
* package、module、build、test を再現可能にする。
* secret を client bundle へ露出しない。

## Runtime and Module System

### MUST

* target runtime を明示する。
* Node.js、browser、edge等を区別する。
* ESM または CommonJSの方針を統一する。
* module resolution設定を明示する。
* runtime で利用できない API を compile成功だけで採用しない。
* Node.js version または browser support range を定義する。

### SHOULD

* 新規 project では ESM を検討する。
* mixed module system を避ける。
* build output と source mapの扱いを定義する。
* runtime targetごとに entrypoint を分ける。

## Compiler Configuration

### MUST

* `strict`相当の厳格な型検査を基本とする。
* `noImplicitAny` を無効化しない。
* `strictNullChecks` を有効にする。
* source、test、generated codeの対象範囲を明確にする。
* emit有無と build toolの責務を区別する。
* path alias を利用する場合、runtime と test で同じ解決ができるようにする。

### SHOULD

* unused code検出を有効にする。
* unchecked index access を必要に応じて厳格化する。
* exact optional propertyの扱いを project方針として定義する。
* library では declaration 生成を検証する。

## Project Structure

推奨構成:

```text
src/
├── app/
├── domain/
├── adapters/
├── config/
├── types/
└── index.ts

tests/
scripts/
docs/
package.json
tsconfig.json
```

### MUST

* browser code と server code を分離する。
* feature 内部実装を他 feature から直接参照しない。
* type定義だけを無秩序に `types/` へ集めない。
* generated code を識別可能にする。
* circular import を作らない。
* barrel export による dependency不透明化を増やしすぎない。

## Naming

### MUST

* variable、function は camelCase を使用する。
* class、type、interface、enum は PascalCase を使用する。
* constant は repository方針に従い統一する。
* boolean は状態や判定が分かる名称にする。
* `IUser`のような interface prefix は、repository で採用する場合のみ統一して使用する。
* type 名と runtime value 名の衝突を避ける。

## Type Safety

### MUST

* `any` を無制限に使用しない。
* unknownな external input は `unknown` として受け、validation する。
* non-null assertion を理由なく使用しない。
* type assertion で runtime不整合を隠さない。
* optional、nullable、missingの意味を区別する。
* union typeの case を網羅する。
* external API response を compile-time typeだけで信頼しない。

### SHOULD

* discriminated union を state や result表現へ利用する。
* branded type や value object を重要 identifier へ検討する。
* generic を過度に複雑化しない。
* enum より union literal が適する場合は検討する。
* exhaustive check を実装する。

## Runtime Validation

TypeScriptの型情報は runtime で消失します。

### MUST

次の入力は runtime validation を行います。

* HTTP request。
* environment variable。
* configuration file。
* external API response。
* message。
* queue event。
* file input。
* local storage。
* user input。
* database からの非保証 data。

### MUST

* validation 失敗を明示的 error として扱う。
  * 型 assertionだけで validation 済みとしない。
* validation schema と domain modelの重複を管理する。
* secret を validation error へ表示しない。

## Null and Undefined

### MUST

* `null` と `undefined`の用途を project 内で定義する。
* optional field と明示的 null を混同しない。
* default値適用に論理 OR を不用意に使用しない。
* zero、false、empty string を missing として扱わない。
* optional chaining で必要な failure を隠さない。

### SHOULD

* nullish coalescing を用途に応じて使用する。
* boundary で値を正規化する。
* domain 内部では可能な限り状態数を減らす。

## Error Handling

### MUST

* rejected Promise を放置しない。
* `catch`した値を `Error` と仮定しない。
* error を握り潰さない。
* asynchronous callback 内の error を回収する。
* domain error と infrastructure error を区別する。
* secret や request全文を error へ含めない。
* process-level error handlerだけに依存しない。

### SHOULD

* Result型を利用する場合、例外との境界を明確にする。
* custom Error へ code や cause を持たせる。
* `Error.cause` を利用できる runtime では検討する。
* retry可能性を識別可能にする。

## Async

### MUST

* Promise を返す function を明示する。
* fire-and-forget を原則避ける。
* `void promise` を使用する場合は failure処理を明確にする。
* timeout と cancellation を必要に応じて扱う。
* `Promise.all`の failure behavior を理解して使用する。
* unbounded parallel execution を行わない。
* resource cleanup を `finally`等で保証する。

### SHOULD

* AbortSignal を利用可能な API へ伝播する。
* concurrency limit を設ける。
* sequential と parallel を意図的に選択する。
* async function 内で blocking operation を避ける。

## Immutability

### SHOULD

* readonly を利用して変更意図を明確にする。
* function argument を無断で mutation しない。
* shared state を immutable に保つ。
* state 更新を明示的にする。
* 深い copy を無意味に繰り返さない。

## Dependency Management

### MUST

* package manager を repository 内で統一する。
* lock file を version control する。
* dependency と devDependency を区別する。
* lifecycle scriptの副作用を確認する。
* package source、license、maintenance、vulnerability を確認する。
* dependency version を再現可能にする。
* private registry credential を configuration へ安全に分離する。

### MUST NOT

* lock file を複数種類混在させない。
* package manager を無断で変更しない。
* major version を検証なしに更新しない。
  * 同じ目的の library を複数導入しない。

## Configuration

### MUST

* environment variable を一か所で読込、validation する。
* browser 公開値と server-only値を区別する。
* secret を client bundle へ含めない。
* build-time と runtime configuration を区別する。
* configuration object を typed にする。
* required setting不足時に明示的に失敗する。

## Formatter and Lint

### MUST

* formatter を一つ定義する。
* lint tool を定義する。
* TypeScript-aware rule を使用する。
* CI で同じ command を実行する。
* disable comment に理由を付ける。
* generated codeの除外範囲を明示する。
* import order と unused import を自動検出する。

## Testing

### MUST

* test runner を統一する。
* unit、integration、browser E2E を区別する。
* test で real production endpoint へ接続しない。
* clock、random、network を制御する。
* unhandled Promise rejection を failure として扱う。
* test順序へ依存しない。
* DOM または browser test では accessibility を必要に応じて確認する。
* client bundle への secret混入を確認する。

### SHOULD

* type-level test を library で検討する。
* property-based test を parser や validation へ検討する。
* mock を implementation detail へ固定しすぎない。
* representative runtime で build test を行う。

## Build

### MUST

* build target を明示する。
* source mapの公開範囲を確認する。
* build artifact へ secret や不要 source を含めない。
* tree shaking や minification に依存した security を設計しない。
* build output と source revision を対応付ける。
* package publish 前に artifact 内容を確認する。

## Browser Security

browser対象では次を守ります。

### MUST

* user-provided HTML を無加工で描画しない。
* DOM injection を防止する。
* token を安全性の低い storage へ無条件に保存しない。
* client-side authorizationだけに依存しない。
* public environment variable は誰でも見られる前提で扱う。
* external URL と redirect 先を validation する。

## Node.js Security

server対象では次を守ります。

### MUST

* request size と timeout を制限する。
* process execution へ外部入力を直接渡さない。
* path traversal を防止する。
* prototype pollution につながる unsafe merge を避ける。
* unsafe deserialization を避ける。
* process signal と graceful shutdown を扱う。

## AI Agent 向け規範

AI Agent は TypeScript code 変更時に次を確認します。

1. runtime target。
2. module system。
3. strict compiler setting。
4. runtime validation。
5. `any`、assertion、null。
6. Promise error。
7. concurrency。
8. browser/server boundary。
9. dependency と lock file。
10. formatter、lint。
11. build。
12. test と secret exposure。

## まとめ

* TypeScriptの型を runtime validationの代替にしない。
* browser、server、build-timeの境界を明確にする。
* `any`、assertion、non-null assertion を制限する。
* Promise failure、timeout、cancel、parallelism を明示的に扱う。
* package manager、lock file、build target を repository 内で統一する。
