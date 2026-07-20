---
language: ja-JP
---

# Dispatcher Rules

この文書は、生成・保守される成果物に Dispatcher構造を採用する場合の実装規範を定義します。

Dispatcher は、すべての処理を集中管理する巨大な controller ではありません。

入力された request、context、metadata、condition をもとに、適切な処理先、workflow、handler、agent、runtime、knowledge source を選択する責務を持ちます。

## 目的

* 処理先の選択を明示する。
* caller が内部構成を知りすぎないようにする。
* routing rule を一か所で観測可能にする。
* unsupported request を安全に拒否する。
* routing と business execution を分離する。
* fallback や Human Check 条件を明確にする。

## Dispatcher Responsibility

Dispatcherの責務:

* inputの受付。
* metadataの解釈。
* routing conditionの評価。
* destinationの選択。
* routing resultの記録。
* unsupported 判定。
* Human Check 判定。
* fallback destinationの選択。
* execution contractの引渡し。

Dispatcherの非責務:

* destination 内部の business logic 実行。
* 全 dataの永続化。
* 各 handlerの細かな error recovery。
* 巨大な Context 生成。
* secret 管理。
* implementation detailの所有。
* すべての workflow state 管理。

### MUST

* routing と execution を分離する。
* Dispatcher へ business logic を集約しない。
* routing rule を追跡可能にする。
* destination選択理由を説明可能にする。
* unsupported input を default handler へ無条件に流さない。
* ambiguous routing では Human Check または明示的 failure を選択する。

## Input Contract

Dispatcher input には、必要に応じて次を含めます。

* request type。
* operation。
* work-id。
* context reference。
* source。
* priority。
* risk。
* environment。
* required capability。
* permitted side effect。
* Human Check status。

### MUST

* input schema を定義する。
* required field を validation する。
* untrusted metadata を信頼しない。
* routing に不要な full payload を渡しすぎない。
* secret を routing metadata へ含めない。

## Routing Rules

### MUST

* routing ruleの優先順位を明確にする。
* 同じ input が複数 destination へ該当する場合の処理を定義する。
* order-dependentな暗黙判定を避ける。
* catch-all rule を最後に配置する。
* routing rule 変更時に既存 route への影響を test する。
* route が存在しない場合の failure contract を定義する。

### SHOULD

routing condition は、次のような machine-readableな値を利用します。

* type。
* capability。
* tag。
* risk level。
* environment。
* artifact type。
* language。
* workflow phase。

自由記述だけに routing を依存させません。

## Destination Contract

各 destination は次を定義します。

* identifier。
* capability。
* accepted input。
* output。
* side effect。
* timeout。
* retry。
* failure contract。
* health。
* availability。
* required permission。

### MUST

* Dispatcher が destinationの internal implementation を直接操作しない。
* destination unavailable 時の処理を定義する。
* destination 追加時に routing rule と test を追加する。
* 同じ identifier を複数 destination へ割り当てない。

## Selection Reason

### MUST

routing result には、必要に応じて次を含めます。

* selected destination。
* matched rule。
* selection reason。
* rejected candidates。
* fallback usage。
* Human Check requirement。
* timestamp。
* dispatcher version。

selection reason は、AIの自由記述だけに依存せず、rule identifier を併用します。

## Fallback

### MUST

* fallback を通常 route と区別する。
* fallback条件を明示する。
* security や permission を弱める fallback を許可しない。
* fallback使用を観測可能にする。
* fallback result が通常 result と異なる場合は caller へ通知する。
* fallback loop を防止する。

### SHOULD

fallback 先は、次を候補とします。

* read-only handler。
* safe runtime。
* Human Check。
* deferred queue。
* explicit unsupported response。

## Human Check

次の場合は Human Check を検討します。

* 複数 route が同じ優先度で該当する。
* destructive operation。
* production environment。
* permission 変更。
* external publication。
* untrusted instruction。
* unsupported capability への近似 route。
* security risk が高い。
* route selection confidence が不足する。

### MUST

Human Check 待機中に、対象 operation を先行実行しません。

## Dispatcher State

Dispatcher が state を保持する場合、次を明確にします。

* state owner。
* persistence。
* expiration。
* concurrent update。
* recovery。
* replay。
* idempotency。

### SHOULD

Dispatcher は可能な限り stateless に保ち、workflow state は専用 component へ委譲します。

## Error Handling

### MUST

次を区別します。

* invalid input。
* no matching route。
* ambiguous route。
* destination unavailable。
* permission denied。
* timeout。
* execution failure。
* Human Check required。

Dispatcher は destination execution failure を、routing failure として隠しません。

## Observability

### MUST

* received request。
* matched rule。
* selected destination。
* routing duration。
* fallback。
* Human Check。
* routing failure。
* destination unavailable。

を必要に応じて追跡可能にします。

secret や full payload は log へ出力しません。

## Testing

### MUST

* 各 routing ruleの positive case。
* non-matching case。
* priority conflict。
* ambiguous case。
* unsupported case。
* destination unavailable。
* fallback。
* Human Check。
* security-sensitive route。

を必要に応じて検証します。

routing table に対する table-driven test を推奨します。

## AI Agent 向け規範

AI Agent は Dispatcher 変更時に次を確認します。

1. Dispatcherの責務内か。
2. input schema。
3. routing priority。
4. destination contract。
5. unsupported behavior。
6. ambiguity。
7. fallback。
8. Human Check。
9. observability。
10. existing route regression。

AI Agent は新しい処理を追加する際、安易に Dispatcher本体へ実装しません。

## まとめ

* Dispatcher は選択を行い、実処理は destination へ委譲する。
* routing rule、優先順位、選択理由を明示する。
* unsupported や ambiguousな入力を安全に扱う。
* fallback で security や permission を弱めない。
* Dispatcher を巨大 controller や state manager にしない。
