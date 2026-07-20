---
language: ja-JP
---

# Module Boundary

この文書は、成果物における module、component、service、packageの責務境界と通信方法を定義します。

module boundary は directory を分けるだけでは成立しません。

次を明確にすることで成立します。

* 所有する責務。
* 所有する data。
* 公開する contract。
* 許可する dependency。
* 許可する副作用。
* failureの扱い。
* change reason。

## 目的

* 責務の重複と漏れを防止する。
* 一つの変更が無関係な module へ波及することを防ぐ。
* module間 communication を明示する。
* AI Agent が変更 scope を判断できるようにする。
* module単位で test、replacement、ownership を可能にする。

## Boundary Definition

各 module は、少なくとも次を定義します。

* name。
* purpose。
* responsibility。
* non-responsibility。
* public interface。
* input。
* output。
* owned data。
* allowed dependencies。
* external side effects。
* failure contract。
* test boundary。

### MUST

* moduleの責務を一文で説明できるようにする。
* 対象外の責務を必要に応じて明記する。
* public interface と internal implementation を分離する。
* 他 module が internal class、file、table へ直接依存しない。
* module間で shared mutable state を暗黙に共有しない。
* data ownership を曖昧にしない。

## Responsibility

### MUST

* 一つの module へ無関係な責務を集めない。
* 同じ business responsibility を複数 module へ重複させない。
* orchestration責務と domain判断を混同しない。
* infrastructure operation を domain module へ直接記述しない。
* presentation都合を core module へ持ち込まない。

### SHOULD

module分割は次を基準に判断します。

* change reason。
* domain capability。
* lifecycle。
* security boundary。
* scaling characteristic。
* runtime characteristic。
* team ownership。
* external dependency。

file数や code量だけを基準に分割しません。

## Public Interface

### MUST

* module 外から利用可能な interface を限定する。
* public interfaceの input、output、error を定義する。
* internal type を public contract へ無制限に公開しない。
* interface 変更では consumer への影響を確認する。
* undocumentedな side effect を持たせない。

### SHOULD

* public interface を最小化する。
* query と command を区別する。
* bulk operation と single operationの意味を明確にする。
* synchronous と asynchronousの違いを contract へ反映する。

## Data Ownership

### MUST

* dataの primary owner を一つ定義する。
* 複数 module が同じ persistent data を無秩序に更新しない。
* 他 moduleの database table へ直接書き込まない。
* read replica、cache、index、projection を source of truth と混同しない。
* schema 変更の責任 module を明確にする。

### SHOULD

module間で data を共有する場合は、次を利用します。

* API。
* event。
* message。
* read model。
* exported artifact。
* versioned schema。

## Communication

module間 communication は、次から選択します。

* function call。
* interface。
* API。
* message。
* event。
* queue。
* shared artifact。
* database view。

### MUST

* communication方式を明確にする。
* timeout、retry、ordering、duplication を必要に応じて定義する。
* asynchronous communication では idempotency を考慮する。
* event を remote procedure callの代替として濫用しない。
* contract を schema または type で表現する。

## Boundary Violations

次は boundary violationの候補です。

* 他 moduleの internal directory を import する。
* 他 moduleの table を直接 update する。
* feature 固有 logic を shared へ移す。
* UI から database へ直接接続する。
* domain module から environment variable を直接読む。
* module間で global state を共有する。
* log message を module間 contract として利用する。

### MUST

boundary violation が必要な場合は、理由、scope、期限、代替策を Evidence へ残します。

## Module Size

### SHOULD

module が大きくなった場合、次を確認します。

* 責務が複数存在していないか。
* public interface が増えすぎていないか。
* change reason が複数ないか。
* security boundary が異ならないか。
* data ownership が複数ないか。
* test setup が過度に複雑でないか。

module を小さくすること自体を目的にしません。

## Shared Module

### MUST

shared module には、次を含めません。

* feature 固有 business rule。
* 特定 moduleだけで使う helper。
* external SDK 固有処理。
* ownership不明の data model。
* 一時的な処理。

### SHOULD

shared module には次を配置できます。

* stable schema。
* cross-cutting contract。
* common error type。
* observation interface。
* security primitive。
* general-purpose value object。

## Module Lifecycle

### MUST

moduleの追加、統合、分割、廃止時は次を確認します。

* responsibility。
* consumer。
* data ownership。
* dependency。
* configuration。
* test。
* deployment。
* documentation。
* migration。
* rollback。

## AI Agent 向け規範

AI Agent は module を変更する前に次を確認します。

1. moduleの責務。
2. non-responsibility。
3. public contract。
4. data ownership。
5. dependency direction。
6. communication方式。
7. side effect。
8. test boundary。
9. consumer impact。
10. boundary violationの有無。

変更先が判断できない場合、近い file へとりあえず追加しません。

## まとめ

* module boundary は責務、data、contract、dependency で定義する。
* directory分割だけでは boundary にならない。
* internal implementation を他 module へ公開しない。
* data owner を明確にし、直接更新を避ける。
* shared module を責務不明の置き場にしない。
