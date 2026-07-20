---
language: ja-JP
---

# Coding Rules

この文書は、Ariadne AI Workflow Platform が生成、変更、保守する成果物に共通して適用する coding rule を定義します。

特定言語の syntax、formatter、library選定は、`../languages/` 配下の文書で定義します。

この文書では、言語や framework が異なっても維持すべき、可読性、責務分離、変更容易性、検証可能性を扱います。

## 目的

Coding Rulesの目的は、すべての code を同じ形にすることではありません。

人間と AI Agent が codeの意図、責務、変更範囲を理解しやすくし、局所的な実装が成果物全体の保守性を損なわない状態を作ります。

## 規範レベル

* **MUST**: 品質、安全性、責務境界を守るために必須とする。
* **SHOULD**: 原則として採用するが、成果物の特性に応じた例外を認める。
* **MAY**: 状況に応じて選択できる。

## Responsibility

### MUST

* 一つの module、class、function へ、無関係な責務を混在させない。
* 判断、実行、承認、記録を一つの処理へ暗黙に詰め込まない。
* external I/O、domain logic、presentation、configuration の境界を明確にする。
* public interface と internal implementation を区別する。
* testのためだけに production responsibility を歪めない。

### SHOULD

* function は一つの明確な意図を表現する。
* class や module は、変更理由が過度に増えない大きさに保つ。
* orchestration と business rule を分離する。
* 副作用を持つ処理を境界へ寄せる。
* 複雑な条件分岐は、意味のある判定へ分解する。

## Readability

### MUST

* code から目的や処理順序を追跡できるようにする。
* 不要な trick、暗黙変換、過度な省略を避ける。
* magic number、magic string、暗黙の状態値を直接散在させない。
* comment と実装が矛盾した状態を残さない。
* dead code、使用されない変数、無効な分岐を放置しない。

### SHOULD

* 深い nest を避け、early return や処理分割を検討する。
* 一つの式や statement へ複数の判断を詰め込みすぎない。
* 複雑な algorithm には、採用理由や前提条件を記録する。
* comment には「何をしているか」よりも「なぜ必要か」を記載する。
* code format は自動 formatter へ委ねる。

## Duplication and Reuse

### MUST

* 重複を減らす目的だけで、異なる責務を無理に共通化しない。
* 共通化によって依存方向や責務境界を壊さない。
* boilerplate 固有処理を platform共通処理へ無条件に持ち込まない。

### SHOULD

* 同じ意味と同じ変更理由を持つ処理は共通化を検討する。
* technology 固有処理は adapter や boundary へ閉じ込める。
* 単なる code量削減ではなく、変更容易性を基準に共通化する。
* 再利用される可能性だけを理由に早すぎる抽象化を行わない。

## State and Side Effects

### MUST

* mutable stateの所有者と変更箇所を明確にする。
* global state や shared state を暗黙に変更しない。
* 外部 service、filesystem、database、environment への副作用を識別可能にする。
* 複数の副作用を伴う処理では、failure 時の状態を考慮する。
* idempotency が必要な処理では、その条件を明示する。

### SHOULD

* pureな処理と副作用を持つ処理を分離する。
* state transition は明示的な operation として表現する。
* retryされる可能性がある処理では、重複実行の影響を確認する。
* transaction boundary を広げすぎない。

## Interfaces and Contracts

### MUST

* interfaceの入力、出力、failure contract を明確にする。
* nullable、optional、empty、missingの意味を混同しない。
* external contract を変更する場合は compatibility を確認する。
* undocumentedな side effect を interface へ持たせない。
* caller が必要とする情報を、log参照だけに依存させない。

### SHOULD

* interface は利用側の責務に合わせて最小化する。
* implementation detail を不必要に公開しない。
* boolean引数が意味を曖昧にする場合は、専用 type や operation へ分ける。
* 単位、format、timezone、encodingなどを contract で明示する。

## Comments and Documentation

### MUST

* security、compatibility、workaround、非自明な制約には理由を残す。
* TODO には、可能な限り理由、対応条件、関連 Issue を記載する。
* 現在の挙動と異なる comment を残さない。
* generated code へ手動変更を行う場合は、その扱いを明示する。

### SHOULD

* source codeだけでは理解しにくい設計判断は docs または ADR へ残す。
* 一時的な workaround には解除条件を記載する。
* comment で複雑さを隠すのではなく、code自体の単純化を優先する。

## Generated Code

### MUST

* generated codeか手動管理 codeかを識別可能にする。
* 再生成で失われる変更を直接加えない。
* generator、template、schemaのどこを source of truth とするか明確にする。
* 生成結果に secret や環境固有値を埋め込まない。

### SHOULD

* 生成後の手修正を最小化する。
* generatorの再現手順を残す。
* 生成差分を review可能にする。

## AI Agent 向け規範

AI Agent は coding 時に次を確認します。

1. 変更対象の責務。
2. 既存 module との境界。
3. public contract への影響。
4. test可能性。
5. side effect と failure path。
6. docs 更新要否。
7. 対象外変更が混入していないこと。

runtime 中に別の改善点を見つけた場合、現在の変更へ混ぜず、Improvement Candidate として分離します。

## まとめ

* Coding Rules は、可読性、責務分離、変更容易性、検証可能性を支える。
* formatter や syntaxの詳細は language rule へ委ねる。
* 共通化は code量ではなく、責務と変更理由を基準に判断する。
* external I/O、state、side effect、contract を明示する。
* AI Agent は対象外の改善を現在の scope へ混ぜない。
