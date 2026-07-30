---
language: ja-JP
---

# Testing Rules

この文書は、成果物の変更を検証し、failureの再発を防ぎ、完了条件を判断するための testing rule を定義します。

test は coverage数値を増やすためだけのものではありません。

成果物が期待どおり動作し、安全性、compatibility、failure behavior を維持していることを確認する Evidence です。

## 目的

* behaviorの正しさを確認する。
* regression を防止する。
* failure path を検証する。
* external boundary を安定して試験する。
* refactoring可能な安全網を作る。
* 完了判定を人間の感覚だけに依存させない。

## Test Scope

成果物に応じて次を組み合わせます。

* unit test。
* component test。
* integration test。
* contract test。
* end-to-end test。
* smoke test。
* migration test。
* security test。
* performance test。
* manual verification。

すべての変更へすべての test を要求しません。

変更内容と risk に応じて必要な層を選択します。

## Required Verification

### MUST

* 変更内容に対応する test または verification を実施する。
* test 未実施を success として扱わない。
* test 失敗を無関係として無断で無視しない。
* bug fix では、可能な限り再現 test を追加する。
* public contract 変更では consumer影響を確認する。
* security、permission、validation 変更では negative case を確認する。
* schema、serialization、migration 変更では compatibility を確認する。
* external mutation を伴う test には安全な environment を使用する。
* 実施できなかった test は理由と影響を Evidence へ残す。

## Unit Tests

### SHOULD

* business rule と重要な分岐を検証する。
* external I/O を分離する。
* 一つの test では一つの主要 behavior を確認する。
* input と expected result を明確にする。
* implementation detail へ過度に依存しない。

### MUST NOT

* production code と同じ logic を test 内へ複製して期待値を作らない。
* sleep や実時間待機に依存する不安定な test を作らない。
* test順序へ依存しない。
* shared mutable state を無管理で使用しない。

## Integration Tests

### MUST

* integration対象と test boundary を明確にする。
* database、queue、filesystem、networkなどの初期状態を制御する。
* test 後の cleanup を行う。
* environment依存値を明示する。
* external service を使用する場合は、誤接続を防止する。
* production environment へ接続しない。

### SHOULD

* container、emulator、mock server を活用する。
* real protocol や serialization boundary を確認する。
* timeout、retry、failure response を検証する。
* test data を再利用可能な fixture として管理する。

## End-to-End and Smoke Tests

### MUST

* 主要な利用経路を明確にする。
* test開始条件と完了条件を定義する。
* external side effect を把握する。
* failure 時にどの phase で止まったか追跡可能にする。
* evidence artifact を保存する。

### SHOULD

* 最小構成で王道経路を確認する。
* 長時間 test と日常 test を分離する。
* environment構築手順を自動化する。
* flakyな UI操作や network条件を必要以上に増やさない。

## Test Doubles

利用可能な種類:

* stub。
* mock。
* fake。
* simulator。
* emulator。

### MUST

* test double が何を代替しているか明示する。
* real contract との差異を把握する。
* mock へ実装詳細を過度に固定しない。
* success responseだけでなく failure responseも用意する。
* outdatedな mock や fixture を放置しない。

## Test Data

### MUST

* production data や personal data を直接使用しない。
* secret を fixture へ含めない。
* test dataの作成目的を明確にする。
* timezone、encoding、locale、boundary value を考慮する。
* data cleanup または isolation を行う。

### SHOULD

* deterministicな data を使用する。
* random を使用する場合は seed を制御する。
* factory や builder を用いて意図を読みやすくする。
* 巨大 fixture を無秩序に共有しない。

## Time, Random and Concurrency

### MUST

* clock を制御可能にする。
* timeout test を実時間待機へ過度に依存させない。
* random 結果を再現可能にする。
* concurrency test では race、deadlock、ordering を考慮する。
* 非同期処理の完了条件を明確にする。

## Flaky Tests

### MUST

* flaky test を単に再実行して成功扱いにしない。
* failure条件を Evidence へ残す。
* timing、shared state、external dependency、ordering を調査する。
* quarantine する場合は理由と解除条件を記載する。

## Coverage

coverage は判断材料の一つとして使用します。

### MUST

* coverage数値だけで品質を判断しない。
* 未検証の重大 risk を、coverage率で隠さない。
* 除外設定を無断で増やさない。

### SHOULD

* 重要な business rule と failure path を優先する。
* branch coverage や mutation testing を必要に応じて検討する。
* coverage低下の理由を確認する。

## Test Naming

test 名から次を理解できるようにします。

* 対象。
* 条件。
* 期待結果。

例:

```text
returns_error_when_required_configuration_is_missing
retries_only_for_retryable_external_errors
requires_human_check_before_external_mutation
```

## Test Evidence

test result には必要に応じて次を残します。

* 実行 command。
* environment。
* test target。
* result。
* failed test。
* skipped test。
* coverage。
* generated artifact。
* execution time。
* 未実施項目。
* residual risk。

## Completion Criteria

次の状態を完了としません。

* test が実行されていない。
* test failure が残っている。
* skipped理由が不明。
* external dependency への誤接続可能性がある。
* failure path が未確認。
* test result が Evidence として残っていない。
* production code へ test専用分岐が追加されている。

## AI Agent 向け規範

AI Agent は test 追加または変更時に次を確認します。

1. 変更した behavior。
2. regression risk。
3. normal case。
4. failure case。
5. boundary。
6. external dependency。
7. side effect。
8. compatibility。
9. test stability。
10. Evidence。

## まとめ

* test は behavior と risk を検証する Evidence である。
* 変更内容に応じた test layer を選択する。
* failure path、external boundary、compatibility を確認する。
* flaky test や未実施 test を success として隠さない。
* coverage率だけで品質を判断しない。
