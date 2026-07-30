---
language: ja-JP
---

# Repository Layout

この文書は、Ariadne AI Workflow Platform が生成、変更、保守する repositoryの基本構造、配置責務、命名、source of truth を定義します。

repository layout は見た目を揃えるためだけのものではありません。

人間と AI Agent が、目的の artifact、source、test、configuration、documentation、Evidence へ迷わず到達できる状態を作ります。

## 目的

* artifactの配置責務を明確にする。
* source、generated artifact、test、Evidence を混同しない。
* repository全体を読まずに必要箇所へ到達できるようにする。
* boilerplate間で最低限の一貫性を保つ。
* build、test、deployment、RAG absorption を安定させる。

## General Principles

### MUST

* top-level directoryの責務を明確にする。
* 同じ種類の artifact を複数箇所へ無秩序に分散させない。
* source、generated、temporary、evidence、archive を区別する。
* secret を repository へ配置しない。
* build output や cache を source と混同しない。
* entrypoint と主要 docs への導線を用意する。
* repository 固有の構造を README へ記載する。

### SHOULD

* repository root を過度に肥大化させない。
* technology よりも responsibility を基準に整理する。
* 深すぎる directory階層を避ける。
* navigation用 README を必要な階層へ配置する。
* machine-readable artifactの保存先を固定する。

## Recommended Layout

成果物の種類に応じて調整しますが、次を基本形とします。

```text
repository/
├── README.md
├── docs/
├── src/
├── tests/
├── config/
├── scripts/
├── schemas/
├── templates/
├── examples/
├── evidence/
├── generated/
├── tools/
└── .github/
```

すべての directory を必須とはしません。

空 directory を構造維持のためだけに増やしません。

## Root Directory

### MUST

repository root には、原則として次だけを配置します。

* primary README。
* license。
* dependency manifest。
* lock file。
* build configuration。
* lint、format、test configuration。
* container entry configuration。
* repository-level metadata。

一時 file、実行結果、download artifact を root へ放置しません。

## Source Code

### MUST

* production sourceの primary location を一つ定義する。
* source と generated code を区別する。
* feature、domain、layerなど、採用した構造方針を統一する。
* test helper を production source へ混在させない。
* platform 固有 script と application source を分離する。

### SHOULD

* package構造と directory構造を対応させる。
* public API と internal implementation を区別する。
* technology adapter を境界へ配置する。
* repository全体に複数の構造方針を混在させない。

## Tests

### MUST

* testの配置規則を統一する。
* unit、integration、end-to-endの区別を明確にする。
* fixture、mock、evidence を混同しない。
* production data や secret を test directory へ置かない。
* test 実行 entrypoint を README または script で示す。

## Documentation

### MUST

docs には次を必要に応じて配置します。

* architecture。
* operation。
* configuration。
* API。
* security。
* development。
* migration。
* decision record。
* troubleshooting。

README へすべてを書き込まず、入口と導線を持たせます。

### SHOULD

* current docs と archive docs を区別する。
* docs 内 link を relative path で安定させる。
* diagramの source と rendered artifact を区別する。
* generated docs には生成方法を記載する。

## Configuration

### MUST

* example configuration と real configuration を区別する。
* secret を含む file を commit しない。
* environmentごとの差分管理方法を明確にする。
* configuration schema を適切な場所へ配置する。
* deprecated configuration を識別可能にする。

## Scripts

### MUST

* scriptの目的と実行環境を明確にする。
* platform別 script を無秩序に同一階層へ配置しない。
* destructive script を識別可能にする。
* script 内へ environment 固有 path を hard-code しない。
* common logic を重複させすぎない。

### SHOULD

例:

```text
scripts/
├── common/
├── unix/
├── windows/
├── development/
├── test/
├── build/
└── maintenance/
```

成果物規模に応じて簡略化します。

## Schemas

### MUST

* schemaの source of truth を明確にする。
* versioning方針を定義する。
* generated model と schema source を区別する。
* schema 変更時に consumer impact を確認する。
* test fixture を schema directory へ混在させない。

## Generated Artifacts

### MUST

* generated artifact を識別可能にする。
* generator と source input を明確にする。
* 手動編集可否を明記する。
* regenerated artifact を review可能にする。
* build cache と versioned generated artifact を区別する。

## Evidence

### MUST

Evidence directory では、次を追跡可能にします。

* work-id。
* issue。
* phase。
* test result。
* artifact。
* Human Check。
* environment。
* timestamp。
* residual risk。

### MUST NOT

* secret。
* credential。
* personal data。
* production data。
* 不要な巨大 binary。
* 一時的な debug dump。

## Temporary and Local Files

### MUST

次は version control から除外します。

* cache。
* local environment file。
* secret。
* temporary file。
* build output。
* IDE-specific state。
* local database。
* downloaded dependency。
* generated runtime log。

必要に応じて `.gitignore`、`.dockerignore`などを管理します。

## Monorepo

monorepo を採用する場合、次を明確にします。

* package boundary。
* shared module。
* dependency direction。
* build scope。
* test scope。
* release unit。
* versioning。
* ownership。
* common configuration。

### MUST

* package間の internal参照を無秩序に許可しない。
* root script がすべての package詳細を抱え込まない。
* shared package を責務不明の集積所にしない。

## Repository Evolution

repository layout 変更時は次を確認します。

* import。
* script。
* CI/CD。
* documentation link。
* schema reference。
* build。
* test。
* container。
* RAG source path。
* Evidence path。
* external consumer。

rename や move を、file操作だけで完了としません。

## AI Agent 向け規範

AI Agent は artifact を作成する前に次を確認します。

1. 既存の配置規則。
2. source of truth。
3. generatedか manualか。
4. current docs。
5. test location。
6. Evidence location。
7. repository root を汚さないか。
8. RAG absorption への影響。
9. path を参照する script。
10. rename や moveの consumer。

## まとめ

* repository layout は navigation、responsibility、source of truth を支える。
* source、test、generated、Evidence、temporary を分離する。
* root directory を一時 artifact で肥大化させない。
* repository 変更時は script、CI、docs、RAG 参照まで確認する。
* 空の分類を維持するためだけに directory を増やさない。
