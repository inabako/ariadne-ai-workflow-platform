---
language: ja-JP
---

# Flutter Template

この文書は、Flutter を利用する mobile、desktop、web、multi-platform applicationの boilerplate に適用する規範を定義します。

この template は、特定の state management、routing、DI library を絶対的な標準として固定しません。

対象 applicationの規模、platform、offline要件、security、distribution方式に応じて選択できる構造を提供します。

## 目的

* multi-platform開発の共通基盤を提供する。
* UI、application logic、domain、external I/O を分離する。
* platform 固有処理を境界へ閉じ込める。
* configuration、secret、build flavor を安全に扱う。
* widget、logic、integration を適切な test層で検証する。
* mobile、desktop、webの差異を明示的に管理する。

## Supported Targets

template は、対象を明示します。

* Android。
* iOS。
* Web。
* Windows。
* macOS。
* Linux。

### MUST

* 未対応 platform を supported として表示しない。
* platformごとの制約を README へ記載する。
* platform 固有 dependency を共通 core へ拡散させない。
* target 追加時に build、test、configuration を確認する。

## Recommended Structure

```text
lib/
├── app/
├── core/
├── features/
│   └── example/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   └── presentation/
├── platform/
└── main.dart

test/
integration_test/
assets/
config/
```

小規模 application では簡略化できます。

### MUST

* UI と external I/O を直接密結合させない。
* feature間の internal implementation を直接参照しない。
* platform channel を専用 boundary へ配置する。
* shared utility を無秩序に `core` へ集めない。

## Application Entry

### MUST

* application initialization を一か所で管理する。
* configuration validation完了前に外部通信を開始しない。
* initialization failure を blank screen として放置しない。
* error handling と logging を setup する。
* flavor または runtime environment を明示する。

### SHOULD

* bootstrap処理を `main.dart` から分離する。
* dependency construction と UI起動を分離する。
* test用 bootstrap を用意する。

## State Management

### MUST

* state owner を明確にする。
* widget tree全体へ global mutable state を無秩序に共有しない。
* transient UI state と business state を区別する。
* asynchronous stateの loading、success、empty、error を表現する。
* state management library 固有 type を domain へ拡散させない。

### SHOULD

* feature単位で state を閉じ込める。
* immutable state を優先する。
* state transition を test可能にする。
* library選定理由を template metadata または docs へ記載する。

## Navigation

### MUST

* route定義を集中管理する。
* authentication や authorization が必要な route を明示する。
* deep link 入力を validation する。
* route parameter を無条件に信頼しない。
* platform別 navigation差異を確認する。

## Configuration and Flavor

### MUST

* environment 固有値を source へ hard-code しない。
* production API endpoint を安全でない default にしない。
* flavor、build mode、runtime configuration の責務を区別する。
* secret を Dart source や asset へ埋め込まない。
* web build では client 側 secret が保護できないことを前提とする。

### SHOULD

* development、staging、production flavor を必要に応じて用意する。
* compile-time value と runtime value を区別する。
* effective configuration を安全な範囲で確認可能にする。

## Networking

### MUST

* timeout を設定する。
* TLS verification を無効化しない。
* request、response を validation する。
* authentication token を安全に扱う。
* retry可能な operation を区別する。
* network error を UI へ適切に変換する。
* response body を無条件に log へ出力しない。

### SHOULD

* API client を infrastructure boundary へ配置する。
* domain model と transport model を分離する。
* offline 時の挙動を定義する。
* cancellation を画面 lifecycle へ連動させる。

## Local Storage

### MUST

* secret や credential を通常 preferences へ平文保存しない。
* sensitive data には secure storage を利用する。
* schema version を管理する。
* migration failure を扱う。
* logout や account 削除時の data cleanup を定義する。
* Web、desktop、mobile で storage特性が異なることを考慮する。

## Platform-Specific Code

### MUST

* `dart:io`など platform限定 APIの利用範囲を明確にする。
* platform branch を application全体へ散在させない。
* plugin availability を targetごとに確認する。
* permission requestの理由と拒否時挙動を定義する。
* method channelの input、output、error contract を定義する。

## UI and Accessibility

### MUST

* loading、empty、error、disabled状態を考慮する。
* user input を validation する。
* destructive operation に確認導線を設ける。
* touch target、keyboard操作、screen reader を対象 platform に応じて考慮する。
* text scale によって主要 UI が破綻しないようにする。
* hard-coded text を必要に応じて localization対象にする。

### SHOULD

* reusable widget と feature-specific widget を区別する。
* theme を集中管理する。
* responsive layout を target に応じて設計する。
* colorだけで状態を表現しない。

## Testing

### MUST

* domain または application logicの unit test。
  * 主要 widgetの widget test。
* navigation、configuration、error stateの test。
* platform integrationの必要な範囲の integration test。
* supported targetの build 確認。
* secret が artifact へ含まれないことの確認。

### SHOULD

* golden test を安定性が保てる範囲で利用する。
* clock、network、storage を test double へ置換する。
* representative device size を検証する。
* accessibility test を導入する。

## Build and Distribution

### MUST

* package identifier、application identifier を parameter 化する。
* signing credential を repository へ含めない。
* version と build number を管理する。
* development build と production build を区別する。
* debug flag を production で無効にする。
* platform permission を必要最小限にする。
* release artifact と commit を対応付ける。

## Generated Structure

template は必要に応じて次を含めます。

```text
lib/
test/
integration_test/
assets/
config/
scripts/
docs/
pubspec.yaml
analysis_options.yaml
README.md
```

## AI Agent 向け規範

AI Agent は Flutter template 変更時に次を確認します。

1. supported platform。
2. feature boundary。
3. state ownership。
4. platform dependency。
5. configuration。
6. secret。
7. navigation。
8. storage。
9. accessibility。
10. test。
11. build flavor。
12. distribution。

## まとめ

* Flutter template は multi-platform差異を境界へ閉じ込める。
* state、UI、domain、external I/O を分離する。
* secret を client application へ埋め込まない。
* platform 固有 API と permission を明示的に扱う。
* supported targetごとに build と test を確認する。
