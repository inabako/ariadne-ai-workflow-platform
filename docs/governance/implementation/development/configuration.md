---
language: ja-JP
---

# Configuration

この文書は、成果物における configuration の定義、読込、validation、override、secret 分離、変更管理を定義します。

configuration は、source codeの外へ値を移すだけの仕組みではありません。

environment差分、runtime behavior、安全性、再現性を明示的に管理する contract です。

## 目的

* environment 固有値を code へ hard-code しない。
* configuration の source と優先順位を明確にする。
* invalid configuration を早期に検出する。
* secret と通常設定を分離する。
* 同じ入力から同じ runtime behavior を再現できるようにする。

## Configuration Sources

使用可能な source例:

* default values。
* configuration file。
* environment variables。
* CLI arguments。
* secret manager。
* deployment platform settings。
* test override。

### MUST

* sourceの優先順位を定義する。
* 同じ設定が複数 source にある場合の挙動を明確にする。
* runtime 中に意図せず値が変わらないようにする。
* effective configuration を安全な範囲で確認可能にする。
* configuration source を会話や人間の記憶だけに依存させない。

## Validation

### MUST

* required valueの存在を確認する。
* type、format、range、allowed values を確認する。
* dependent settings間の整合性を確認する。
* invalid configuration では fail fast を基本とする。
* error message には setting 名と修正方法を含める。
* secret valueそのものを error へ表示しない。

### SHOULD

* schema を定義する。
* application起動時に一括 validation する。
* validation logic を利用箇所へ分散させない。
* default値が適用されたことを必要に応じて観測可能にする。

## Defaults

### MUST

* default値は安全側に倒す。
* security機能を無効化する default を採用しない。
* production接続や external mutation を有効にする default を採用しない。
* timeout、retry、resource limit を無制限にしない。
* default値の意味を docs へ記載する。

### SHOULD

* local development で最小限起動できる default を検討する。
* environment差分を最小化する。
* default が変更された場合は behavior change として扱う。

## Secrets

### MUST

* secret を通常 configuration file へ平文保存しない。
* repository へ secret を commit しない。
* example file へ実在 secret を記載しない。
* secret を log、Evidence、error へ出力しない。
* secretの未設定と空文字を区別する。
* secret rotation を妨げる設計にしない。

### SHOULD

* environment variable、OS credential store、secret managerなどを利用する。
* secret参照名と secret value を分離する。
* local development用の安全な dummy value を用意する。

## Environment Separation

### MUST

* local、test、staging、productionの境界を明確にする。
* production向け設定を local で暗黙に利用しない。
* environment 名だけで security を保証しない。
* deployment 先と configuration の組合せを validation する。
* production 変更には Human Check を適用する。

## Naming

configuration 名には、必要に応じて次を含めます。

* 対象 component。
* 用途。
* 単位。
* scope。
* enable状態。
* timeout や limitの種類。

例:

```text
ARIADNE_RUNTIME_TIMEOUT_SECONDS
ARIADNE_RAG_MAX_RESULTS
ARIADNE_LOG_LEVEL
ARIADNE_EXTERNAL_MUTATION_ENABLED
```

否定形や二重否定を避けます。

## Loading and Access

### MUST

* configuration読込処理を無秩序に分散させない。
* application 内部では validation 済みの値を利用する。
* environment variable を domain logic から直接参照しない。
* configuration object を無制限に global共有しない。
* runtime 中の変更可否を明確にする。

### SHOULD

* immutableな configuration object を使用する。
* componentごとに必要な設定だけを渡す。
* test では明示的な configuration を組み立てる。
* configuration access を interface 化しすぎて複雑にしない。

## Change Management

### MUST

configuration を追加、変更、削除する場合は次を確認します。

* default behavior。
* existing environment への影響。
* backward compatibility。
* deployment設定。
* documentation。
* example configuration。
* test。
* secret classification。
* migration または deprecation。

deprecated setting には、移行先と削除時期または解除条件を記載します。

## Effective Configuration

### SHOULD

調査や Evidence のため、secret を除いた effective configuration を出力できる構造を検討します。

出力時は次を守ります。

* secret を mask する。
* personal data を含めない。
* source を必要に応じて示す。
* default適用を識別可能にする。
* production情報を過度に露出しない。

## AI Agent 向け規範

AI Agent は configuration 変更時に次を確認します。

1. hard-codeの有無。
2. source と override順序。
3. validation。
4. safe default。
5. secret分類。
6. environment差分。
7. docs と example 更新。
8. deployment への影響。
9. Human Check 要否。
10. backward compatibility。

## まとめ

* configuration は runtime behavior を定義する contract である。
* source、override、validation、default を明確にする。
* secret を通常設定と分離する。
* production や external mutation を安全でない default にしない。
* configuration 変更は code、docs、deployment、test を横断して確認する。
