---
language: ja-JP
---

# Dart Rules

この文書は、Ariadne AI Workflow Platform が生成、変更、保守する Dart成果物へ適用する言語固有規範を定義します。

言語別規範は、言語 Tips や好みの実装スタイルを集めるための文書ではありません。各言語で発生しやすい security issue、vulnerability、unsafe side effect、secret leakage、検証不能な実装を防ぐための最低規範です。

対象には次を含みます。

* Flutter application。
* Dart CLI。
* package。
* server-side Dart。
* code generator。
* integration tool。

Flutter 固有の UI、platform、build規範については、`templates/flutter-template.md`も参照します。

## 目的

* null safety と type system を適切に利用する。
* application logic と Flutter framework dependency を分離する。
* Future、Stream、isolateの lifecycle を管理する。
* package、dependency、analysis、test を再現可能にする。
* platform 固有処理を boundary へ閉じ込める。
* generated code と manual code を分離する。

## Supported Version

### MUST

* supported Dart SDK version を `pubspec.yaml` へ記載する。
* Flutter利用時は Flutter SDK version との compatibility を確認する。
* CI と local developmentの version を揃える。
* support終了済み version を新規採用しない。
* language feature利用時に minimum SDK を確認する。

## Project Structure

Dart packageの基本構成:

```text
lib/
├── src/
└── package_name.dart

bin/
test/
tool/
example/
docs/
pubspec.yaml
analysis_options.yaml
```

Flutter application では feature構造を採用できます。

### MUST

* public API と internal implementation を分離する。
* `lib/src/` を package 内部実装に利用する。
* package 外へ公開する symbol を限定する。
* feature 固有処理を `core` や `utils` へ無秩序に集めない。
* generated code を識別可能にする。
* circular dependency を作らない。

## Naming

### MUST

* file 名は lowercase_with_underscores を使用する。
* class、enum、typedef、extension は UpperCamelCase を使用する。
* variable、function、parameter は lowerCamelCase を使用する。
* private identifier には leading underscore を使用する。
* constant は Dartの一般的慣例に従い lowerCamelCase を基本とする。
* boolean は状態や判定が分かる名称にする。

## Null Safety

### MUST

* nullable と non-nullable を意図的に区別する。
* null assertion operator を理由なく使用しない。
* late modifier を初期化責務が明確な場合だけ使用する。
* optional parameter と nullable value を混同しない。
* null を error stateの代替として濫用しない。
* external data を validationしてから non-null type へ変換する。

### SHOULD

* domain 内部では nullable state を必要最小限にする。
* sealed class や result type で状態を表現する。
* required named parameter を適切に使用する。
* default値で null を隠しすぎない。

## Type System

### MUST

* `dynamic` を無制限に使用しない。
* external input は validation する。
* cast で runtime failure を隠さない。
* generic type を過度に複雑化しない。
* collectionの element type を明示する。
* public API で implementation 固有 type を不用意に公開しない。

### SHOULD

* immutable value へ `final` を使用する。
* value object には必要に応じて equality を定義する。
* record、sealed class、pattern matching を version と用途に応じて利用する。
* abstract class と interface class を責務に応じて使い分ける。

## Final and Const

### SHOULD

* reassignment しない local variable は `final` にする。
* compile-time constant にできる object は `const` を検討する。
* Flutter widget では const constructor を利用可能な場合に使用する。
* const 化を可読性より優先しすぎない。

## Error Handling

### MUST

* exception を黙って握り潰さない。
* `catch`対象を必要に応じて限定する。
* original stack trace を失わない。
* expected failure と programming error を区別する。
* Future 内の error を未処理にしない。
* secret や personal data を exception へ含めない。
* library code から process を無断終了しない。

### SHOULD

* domain failure を sealed type等で表現することを検討する。
* exception wrapping 時に cause と stack trace を保持する。
* boundary で external exception を変換する。
* retry可能性を識別可能にする。

## Future

### MUST

* Future を返す function を明示する。
* awaitされない Future を無意識に作らない。
* fire-and-forget には error handling を用意する。
* timeout と cancellation相当の仕組みを必要に応じて設ける。
* Future chainの error を回収する。
* sequential と parallel execution を意図的に選択する。

### SHOULD

* independent operation には `Future.wait`等を利用する。
* partial failureの扱いを明確にする。
* UI lifecycle終了後の state 更新を防止する。
* long-running Future を resource owner へ紐付ける。

## Stream

### MUST

* subscriptionの owner を明確にする。
  * 不要になった subscription を cancel する。
* controllerの close責任を明確にする。
* broadcast と single-subscription を用途に応じて選択する。
* error event を扱う。
* unbounded event accumulation を防ぐ。

## Isolate

isolate利用時:

### MUST

* CPU-bound処理等、利用理由を明確にする。
* send可能な dataだけを境界で扱う。
* isolateの lifecycle と終了条件を管理する。
* error と exit を監視する。
  * 過度な isolate 生成を避ける。
* platform compatibility を確認する。

## Configuration

### MUST

* environment 固有値を source へ hard-code しない。
* compile-time と runtime configuration を区別する。
* secret を client application へ埋め込まない。
* configuration を typed object へ変換する。
* required configuration を起動時に validation する。
* Flutter Web では client 側 secret が保護できないことを前提とする。

## Dependency Management

### MUST

* dependency を `pubspec.yaml` へ記載する。
* dependency と dev_dependency を区別する。
* lock fileの管理方針を application と package で明示する。
* SDK constraint を定義する。
* packageの maintenance、license、platform support を確認する。
* dependency overrideの理由と解除条件を記載する。
* code generation dependency を通常 runtime dependency と区別する。

## Generated Code

### MUST

* generated file を直接編集しない。
* generator、input、command を追跡可能にする。
* generated file命名規則を統一する。
  * 生成後の diff を review可能にする。
* code generation failure を build failure として扱う。
* stale generated code を検出する。

## Analysis and Formatting

### MUST

* `analysis_options.yaml` を管理する。
* formatter を標準化する。
* analyzer warning と error を無断で無視しない。
* ignore comment には理由を付ける。
* generated code を必要に応じて除外する。
* CI で analysis と format check を実行する。

### SHOULD

- 公式 lint set または approved rule set を基礎にする。

* repository 固有 rule を増やしすぎない。
* lint rule 変更時に大量差分への影響を確認する。

## Testing

### MUST

* unit、widget、integration を用途に応じて分ける。
* Future、Streamの完了条件を明確にする。
* timer、clock、network、storage を制御する。
* test で subscription や controller を残さない。
* platform plugin を test double へ置換する。
* production data や secret を fixture へ含めない。
* supported platformの build を確認する。

### SHOULD

* state transition を test する。
* validation と serializationの boundary case を確認する。
* golden test は安定性を保てる範囲で利用する。
* package public API へ example を用意する。

## Serialization

### MUST

* external JSON等を validation する。
* missing、null、unknown fieldの扱いを定義する。
* transport model と domain model を必要に応じて分離する。
* generated serialization codeの version compatibility を確認する。
* date、timezone、number precision を明示する。
* unsafe cast を避ける。

## Security

### MUST

* secret を asset、source、build argument へ埋め込まない。
* secure storage と通常 storage を区別する。
* platform channel input を validation する。
* URL、deep link、file path を信頼しない。
* TLS verification を無効にしない。
* personal data を debug output へ含めない。
* client-side authorizationだけに依存しない。

## AI Agent 向け規範

AI Agent は Dart code 変更時に次を確認します。

1. Dart または Flutter version。
2. public API と internal code。
3. null safety。
4. dynamic と cast。
5. Future lifecycle。
6. Stream lifecycle。
7. isolate necessity。
8. configuration。
9. generated code。
10. analyzer と formatter。
11. platform compatibility。
12. test。

## まとめ

* Dart成果物は null safety と type system を積極的に利用する。
* Future、Stream、isolateの owner と終了条件を明確にする。
* generated code を直接編集しない。
* application logic と Flutter、platform dependency を分離する。
* analyzer、formatter、test、supported platform build を継続的に確認する。
