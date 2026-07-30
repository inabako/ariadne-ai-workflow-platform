---
language: ja-JP
---

# Next.js Template

この文書は、Next.js を利用する web application、dashboard、management UI、server-rendered applicationの boilerplate に適用する規範を定義します。

Next.jsの version や routing方式に依存する詳細は、template versionごとの documentation で管理します。

この文書では、server と clientの境界、data access、configuration、security、test、deploymentの最低条件を定義します。

## 目的

* server と clientの責務を明確にする。
* browser へ secret や internal logic を漏らさない。
* routing、data fetching、mutation を整理する。
* loading、error、not-found状態を扱う。
* API、authentication、authorization を安全に実装する。
* build と runtime configuration を区別する。

## Recommended Structure

```text
src/
├── app/
├── features/
├── components/
├── server/
├── lib/
├── config/
├── styles/
└── types/

public/
tests/
scripts/
```

### MUST

* server-only code と client code を分離する。
* client component を必要以上に増やさない。
* domain または business logic を page component へ直接詰め込まない。
* data access を UI component へ分散させない。
* shared directory を責務不明の置き場にしない。

## Server and Client Boundary

### MUST

* secret を client bundle へ含めない。
* browser から信頼できない値を server へ渡す前提で validation する。
* client-side authorizationだけに依存しない。
* server-only module を client から import しない。
* environment variableの公開範囲を明確にする。
* hydration 前後で security上重要な判定を変えない。

## Routing

### MUST

* route structure を feature責務と対応させる。
* dynamic route parameter を validation する。
* route group や layoutの責務を明確にする。
* authentication が必要な route を server 側でも保護する。
* not-found、unauthorized、forbidden を区別する。
* redirect 先を無条件に user input から構築しない。

## Data Fetching

### MUST

* data source と cache behavior を明示する。
* stale data が許容される範囲を定義する。
* user-specific data を public cache へ保存しない。
* timeout と error handling を実装する。
* external API response を validation する。
* server と client で同じ request を重複させないよう確認する。

### SHOULD

* data fetching を server 側で行える場合は検討する。
* query と mutation を分離する。
* cache invalidation条件を明確にする。
* loading、empty、error状態を UI で扱う。

## Mutation

### MUST

* mutation 入力を server 側で validation する。
* authentication と authorization を確認する。
* CSRF risk を考慮する。
* destructive operation へ確認導線を設ける。
* idempotency が必要な operation を識別する。
* mutation 結果を明示的に返す。
* error を success response へ隠さない。

## API and Route Handlers

### MUST

* input schema を定義する。
* HTTP method を責務に応じて使用する。
* status code を適切に返す。
* internal stack trace を公開しない。
* request size を制限する。
* rate limit を必要に応じて設ける。
* CORS を無制限に許可しない。
* secret や personal data を response へ含めない。

## Authentication and Authorization

### MUST

* session または token を server 側で検証する。
* authorization を resource単位で確認する。
* UI非表示だけで permission を保証しない。
* callback URL や redirect URL を validation する。
* session cookie に適切な security attribute を設定する。
* authentication provider 固有 type を application全体へ拡散させない。

## Configuration

### MUST

* server-only configuration と public configuration を区別する。
* public prefixの付いた値は browser から見える前提で扱う。
* production endpoint や secret を source へ hard-code しない。
* build-time と runtime configuration の違いを明示する。
* required configuration を startup または build 時に validation する。

## Security Headers

### SHOULD

application特性に応じて次を設定します。

* Content-Security-Policy。
* Strict-Transport-Security。
* X-Content-Type-Options。
* Referrer-Policy。
* Permissions-Policy。
* frame 制御。

設定時は利用する external resource との整合を確認します。

## UI

### MUST

* loading、empty、error、not-found状態を実装する。
* form 入力を client と serverの両方で適切に validation する。
* destructive action を誤操作しにくくする。
* accessibility を考慮する。
* user-provided HTML を無加工で描画しない。
* image、file uploadの type と size を確認する。

## Logging

### MUST

* server log と browser log を区別する。
* secret、cookie、authorization header を出力しない。
* browser console を production observabilityの唯一手段にしない。
* request identifier を必要に応じて利用する。
* user-specific dataの log 出力を制限する。

## Testing

### MUST

* server-side logicの unit test。
* input validation test。
* authentication、authorization test。
* route または componentの主要 test。
* mutation failure test。
* build test。
* environment validation test。
* client bundle への secret混入確認。

### SHOULD

* browser E2E test を主要 flow へ用意する。
* accessibility test を行う。
* mock server を利用する。
* cache と revalidationの test を必要に応じて行う。

## Deployment

### MUST

* target runtime を明示する。
* Node.js、edge、serverlessなどの制約を確認する。
* filesystem や long-running process への依存を target に合わせる。
* build artifact と commit を対応付ける。
* preview と productionの configuration を分離する。
* production deployment を Human Check 対象とする。

## Generated Structure

template は必要に応じて次を含めます。

```text
src/
tests/
public/
scripts/
docs/
.env.example
next.config.*
package.json
lock-file
README.md
```

## AI Agent 向け規範

AI Agent は Next.js template 変更時に次を確認します。

1. server/client boundary。
2. secret exposure。
3. route。
4. data fetching。
5. cache。
6. mutation。
7. authentication。
8. authorization。
9. headers。
10. test。
11. runtime target。
12. deployment。

## まとめ

* Next.js template は server と clientの境界を最優先する。
* client-side 判定だけで security を保証しない。
* data fetching、cache、mutation を明示的に設計する。
* public configuration は browser へ露出する前提で扱う。
* build、preview、productionの差異を管理する。
