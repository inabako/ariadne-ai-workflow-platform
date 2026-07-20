---
language: ja-JP
---

# Boilerplate Rules

この文書は、Ariadne AI Workflow Platform が生成、保守、利用する boilerplate template に共通して適用する規範を定義します。

boilerplate は、source codeの雛形を複製するだけのものではありません。

新しい成果物を、安全かつ再現可能に開始するための次の要素を含む実装契約です。

* repository structure。
* dependency。
* configuration。
* runtime。
* test。
* security。
* build。
* observability。
* documentation。
* Evidence。
* extension point。
* update strategy。

## 目的

Boilerplate Rulesの目的は、すべての成果物を同じ形へ固定することではありません。

次の状態を実現します。

* 初期構築時の認識負荷を減らす。
* 必要な品質要素の実装漏れを防ぐ。
* 人間と AI Agent が同じ入口から作業を開始できる。
* technology 固有部分と共通規範を分離する。
* template から生成された成果物を継続的に更新できる。
* 不要な dependency や過剰実装を持ち込まない。

## Boilerplate Definition

boilerplate は、少なくとも次を定義します。

* template name。
* purpose。
* supported use case。
* non-goals。
* prerequisites。
* input parameters。
* generated artifacts。
* directory structure。
* runtime entrypoint。
* configuration。
* test command。
* build command。
* security boundary。
* extension point。
* update method。
* removal method。

### MUST

* templateの対象と対象外を明確にする。
* 利用開始に必要な入力を明示する。
* 生成後に変更すべき placeholder を識別可能にする。
* 最小構成で起動または検証できる状態を提供する。
* template 固有の制約を README へ記載する。
* 上位の Implementation Governance を継承する。

## Minimal Template Principle

### MUST

* 利用されない機能を初期状態で大量に含めない。
* sample code と production-ready code を区別する。
* optional component を必須 dependency として組み込まない。
* technologyの紹介目的だけの実装を含めない。
* hidden setup を必要としない。
* 最小構成でも security上危険な default を採用しない。

### SHOULD

template は次の層へ分割します。

```text
Required Core
 最低限必要な構成

Optional Features
 利用目的に応じて追加する構成

Examples
 実装例および学習用構成
```

## Template Inputs

### MUST

入力 parameter には、必要に応じて次を定義します。

* project name。
* module name。
* package name。
* service name。
* runtime mode。
* port。
* output path。
* license。
* repository information。
* enabled features。
* external dependency。
* deployment target。

### MUST

* 入力値を validation する。
* path traversal を防止する。
* package 名や module 名の形式を確認する。
* secret を template parameter として直接埋め込まない。
* 未指定値へ危険な default を適用しない。
* 同じ入力から再現可能な成果物を生成する。

## Placeholder

### MUST

* placeholderの形式を統一する。
* placeholder一覧を管理する。
* 置換漏れを自動検出できるようにする。
* secret や credential を placeholder として repository へ残さない。
* placeholder と通常文字列を区別できる形式にする。

例:

```text
{{PROJECT_NAME}}
{{MODULE_NAME}}
{{PACKAGE_NAME}}
{{SERVICE_PORT}}
```

### SHOULD

* placeholder を増やしすぎない。
* derived value は generator 側で生成する。
* 同じ値を複数入力させない。
* optional placeholder には明確な default または削除規則を持たせる。

## Generated Structure

### MUST

生成物には、必要に応じて次を含めます。

* README。
* source entrypoint。
* test。
* configuration example。
* dependency manifest。
* formatter、lint設定。
* build または run script。
* container definition。
* CI entrypoint。
* security note。
* license information。
* `.gitignore`。
* Evidence 出力先。

すべての template へすべての artifact を必須とはしません。

対象 technology と用途に応じて選択します。

## Configuration

### MUST

* environment 固有値を hard-code しない。
* example configuration と実設定を分離する。
* secret を含まない。
* configuration source と override順序を記載する。
* safe default を採用する。
* 必須設定の不足時は明示的に失敗する。

## Dependencies

### MUST

* dependency を必要最小限にする。
* version を再現可能に管理する。
* license を確認する。
* unsupported dependency を使用しない。
* install 時の副作用を確認する。
* optional dependency を core へ混在させない。

### SHOULD

* standard library を優先する。
* technology 固有 dependency を boundary へ閉じ込める。
* major framework version を template metadata へ記録する。
* dependency 更新手順を用意する。

## Security

### MUST

* template 内に実在 secret を含めない。
* authentication や TLS を無効にする default を採用しない。
* external service へ自動接続しない。
* production環境を default target にしない。
* container を不要な root権限で実行しない。
* generated application に入力 validationの入口を用意する。
* security-sensitive operation に Human Check の導線を持たせる。

## Testing

### MUST

* template自体の生成 test を用意する。
* 生成後の最低限の build または run test を行う。
* placeholder置換漏れを検出する。
* expected fileの存在を確認する。
* optional featureの組合せを必要に応じて検証する。
* template 更新時に既存生成パターンの regression を確認する。

### SHOULD

* golden file test を利用する。
* representative parameter set を用意する。
* Windows、Linux、containerなど対象環境を必要に応じて検証する。
* generated repository に smoke test を含める。

## Documentation

### MUST

各 templateの README には次を含めます。

* purpose。
* target。
* prerequisites。
* generation method。
* input。
* output。
* directory structure。
* run。
* test。
* configuration。
* security。
* optional features。
* extension。
* update。
* known limitations。

## Extension Points

### MUST

* 利用者が変更する箇所を明確にする。
* core fileの直接改変が必要かを示す。
* plugin、adapter、configurationなどの拡張方法を定義する。
* generated code と manual codeの境界を明確にする。
* 再生成時に手動変更が失われない構造にする。

### SHOULD

* customization を特定 directory へ寄せる。
* hook や interface を必要以上に増やさない。
* extension point には sample を用意する。
* template 内部構造への依存を最小化する。

## Template Versioning

### MUST

* template version を管理する。
* breaking change を識別する。
* generated artifact が利用した version を追跡可能にする。
* migration が必要な変更には手順を用意する。
* deprecated template を明示する。
* template 削除時に代替先を示す。

### SHOULD

version情報を次へ記録します。

* generated metadata。
* README。
* manifest。
* Evidence。
* repository label または file。

## Update Strategy

template 更新と、既に生成された repository 更新は別の operation として扱います。

### MUST

* template 更新が既存成果物へ自動反映されると仮定しない。
* update対象を明確にする。
* generated artifact との差分を確認する。
* manual customization を上書きしない。
* security updateの適用方法を定義する。
* rollback方法を用意する。

## Template Metadata

各 template は machine-readable metadata を持つことを推奨します。

例:

```yaml
name: go-service
version: 1.0.0
language: go
runtime: server
supports:
 - docker
 - http
 - health-check
requires:
 - go
optional:
 - grpc
 - postgres
```

### SHOULD

metadata には次を含めます。

* identifier。
* version。
* category。
* supported environment。
* required tools。
* optional features。
* output structure。
* security classification。
* maintenance status。

## AI Agent 向け規範

AI Agent は boilerplate を追加または変更する際、次を確認します。

1. 対象 use case。
2. non-goals。
3. required input。
4. safe default。
5. dependency。
6. placeholder。
7. generated structure。
8. security。
9. test。
10. update strategy。
11. generated artifact への影響。
12. documentation。

AI Agent は、便利そうな technology を理由なく template へ追加しません。

## Completion Criteria

次の状態を boilerplate完成としません。

* generation command が不明。
* placeholder が残る。
* build または smoke test が通らない。
* secret が含まれる。
* required configuration が不明。
* generated code と manual codeの境界がない。
* version が追跡できない。
* update方法がない。
* target と non-goals が不明。
* README が生成物と一致していない。

## まとめ

* boilerplate は再利用可能な実装契約である。
* 最小構成、安全な default、再現性を重視する。
* placeholder、dependency、configuration を管理する。
* template自体と生成成果物の両方を test する。
* generated code と manual customization を分離する。
* template 更新と既存 repository 更新を別の責務として扱う。
