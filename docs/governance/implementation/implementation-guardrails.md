---
language: ja-JP
---

# Implementation Guardrails

この文書は、Ariadne AI Workflow Platform が生成、変更、保守する成果物に適用する、最上位の実装規範を定義します。

Implementation Guardrails は、特定のプログラミング言語、フレームワーク、アーキテクチャパターンを強制するための文書ではありません。

成果物の種類や technology stack が変わっても守るべき、安全性、責任境界、変更境界、検証、Evidence の最低条件を定義します。

## 目的

Implementation Guardrails の目的は、実装を細かく統制することではありません。

人間と AI Agent が、次を推論せずに判断できる状態を作ります。

* 何を変更してよいか。
* 何を変更してはいけないか。
* どこで Human Check が必要か。
* 何を検証すべきか。
* 何を Evidence として残すべきか。
* どの状態を完了と扱うか。
* どの情報を source code や log へ残してはいけないか。

## 適用範囲

この Guardrails は、次の成果物へ共通して適用します。

* Application source code。
* Script、CLI、runtime helper。
* API、worker、batch、gateway。
* Web、desktop、mobile application。
* Docker、Kubernetes、IaC。
* CI/CD。
* configuration、schema、migration。
* boilerplate template。
* test、mock、fixture。
* Agent prompt、workflow artifact。
* documentation、report、Evidence。

より具体的な rule がある場合は、各 category および language 文書を追加参照します。

## 規範レベル

この文書では、規範の強さを次の3段階で表します。

### MUST

守らなければ、安全性、責任境界、platform integrity、再現性、検証可能性が損なわれる規範です。

例外には Human Check と Evidence が必要です。

### SHOULD

原則として守る推奨事項です。

成果物の特性により別の方法を選択できますが、意図と理由を説明できる必要があります。

### MAY

状況に応じて選択できる事項です。

選択しないことを違反として扱いません。

## 1. Change Boundary

### MUST

* 承認された目的、scope、完了条件を確認してから変更を開始する。
* 対象外の責務、module、repository、configuration を暗黙に変更しない。
* 変更に必要な Context が不足する場合は、推測で補わず Context 生成または Human Check へ戻る。
* public interface、schema、migration、external contract を変更する場合は、利用側への影響を確認する。
* 自動生成物を直接編集する場合は、その成果物が再生成で失われないことを確認する。
* security、権限、外部公開、network、secret、production data へ影響する変更は Human Check を行う。

### SHOULD

* 一つの変更では、一つの主要な責務または目的を扱う。
* 関連変更が必要な場合は、主変更との関係を Evidence へ残す。
* refactoring と behavior change を可能な範囲で分離する。

## 2. Security and Secrets

### MUST

* API key、token、password、private key、credential を source code へ埋め込まない。
* secret を log、test result、screenshot、Evidence、prompt、exception message へ出力しない。
* local secret file、environment variable、secret manager など、成果物に適した安全な管理方法を使用する。
* 外部入力、user input、file、network response、environment variable を信頼済みとして扱わない。
* path、command、query、template、URL へ外部入力を渡す場合は、validation または安全な API を使用する。
* TLS 検証、authentication、authorization、signature verification を、理由なく無効化しない。
* production data や個人情報を test fixture として直接使用しない。
* dependency 追加時は、取得元、license、保守状態、既知 risk を確認する。

### SHOULD

* 最小権限を採用する。
* secret が不要な設計を優先する。
* security failure は、通常の validation error と区別して記録する。
* failure 時に secret や内部構造が露出しない error message を設計する。

## 3. Human Check and Side Effects

### MUST

次の操作は、workflow または project 固有規則で明示的に許可されていない限り、Human Check を必要とします。

ただし、workflow または project 固有規則は、Ariadne Governance、Implementation Governance、Human Responsibility を上書きできません。

* push、merge、release、publish。
* 外部 service への mutation。
* infrastructure 作成、変更、削除。
* package install または system configuration 変更。
* network 公開、port 公開、firewall 変更。
* production または shared environment への接続。
* data migration、data deletion、archive、prune。
* RAG 登録、rebuild、knowledge 削除。
* license、security policy、Governance の変更。

AI Agent は、Human Check を形式的な停止点として扱いません。

判断に必要な次の情報を準備します。

* 変更内容。
* 実行目的。
* 対象範囲。
* 影響範囲。
* 検証結果。
* rollback または復旧方法。
* 残存リスク。
* 実行しない場合の影響。

## 4. Configuration

### MUST

* environment 固有値を source code へ hard-code しない。
* configuration の source、default、override 順序を明確にする。
* 必須 configuration が不足する場合は、曖昧な fallback を行わず明示的に失敗させる。
* secret と通常 configuration を同じ扱いにしない。
* configuration 変更が runtime behavior へ与える影響を test または Evidence で確認する。
* example configuration には実在 secret や内部情報を記載しない。

### SHOULD

* configuration schema または validation を用意する。
* default 値は安全側に倒す。
* environment ごとの差分を最小化する。
* configuration 名から用途、単位、scope が分かるようにする。

## 5. Error Handling

### MUST

* error を黙って握り潰さない。
* failure を success として返さない。
* retry 可能な error と、即時停止すべき error を区別する。
* fallback を実行した場合は、fallback が発生したことを観測可能にする。
* error message には、原因調査に必要な対象、phase、operation を含める。
* secret、credential、personal data を error message へ含めない。
* cleanup や rollback が必要な処理では、failure path を検証する。

### SHOULD

* error へ context を追加しながら、元の原因を追跡可能にする。
* 呼び出し側が判断すべき error と、内部で回復すべき error を分離する。
* exit code、HTTP status、result schema など、成果物に適した failure contract を持つ。

## 6. Logging and Observability

### MUST

* operation の開始、完了、失敗を必要に応じて追跡可能にする。
* work-id、request-id、correlation-id など、処理を関連付ける識別子を適切に使用する。
* secret、credential、personal data、不要な request body を log へ出力しない。
* retry、fallback、Human Check、external mutation は観測可能にする。
* log だけを唯一の Evidence にしない。
* structured data が必要な場合は、machine-readable な report または metrics を生成する。

### SHOULD

* log level を意味に応じて使い分ける。
* 同じ error を複数 layer で重複出力しすぎない。
* 人間が次の行動を判断できる message を残す。
* observability 追加によって本来の処理を過度に複雑化しない。

## 7. Testing and Verification

### MUST

* 変更後は、変更内容に対応する検証を実施する。
* test 未実施、test 失敗、環境不足を success として扱わない。
* bug fix には、可能な限り再発防止 test を追加する。
* external I/O、clock、random、network、filesystem など、test を不安定にする境界を分離する。
* test を通すためだけの production code 分岐を追加しない。
* security、permission、error handling を変更した場合は、failure case を確認する。
* schema、migration、serialization 変更では、compatibility を確認する。
* 実行できなかった test は、理由、影響、代替 Evidence を記録する。

### SHOULD

* 最小の test だけでなく、主要な利用経路を確認する。
* test 名から、条件と期待結果が分かるようにする。
* flaky test を放置せず、原因を特定する。
* unit、integration、end-to-end の責務を混同しない。

## 8. Evidence and Completion

### MUST

重大な変更または workflow で管理される変更では、次を Evidence として残します。

* 変更目的。
* 変更範囲。
* 主な変更内容。
* 実施した test または verification。
* test 結果。
* Human Check の有無。
* 未検証事項。
* 残存リスク。
* rollback または復旧方法。
* 関連 Issue、artifact、docs。

次の状態を完了として扱いません。

* test 結果が不明。
* 変更 scope が説明できない。
* 必要な Human Check が未実施。
* secret 露出の可能性が未確認。
* docs または schema との不整合が残っている。
* failure を success として隠している。
* 成果物の保存先が不明。
* 再現方法が残っていない。

### SHOULD

* Evidence は後続 workflow が機械的に参照できる形式を併用する。
* 会話ログだけを判断根拠にしない。
* Evidence から RAG 候補、Issue、review 材料へ接続できるようにする。

## 9. Documentation and Source of Truth

### MUST

* current source、current schema、current configuration、current docs の関係を確認する。
* 古い RAG や過去の会話を、current repository evidence より優先しない。
* behavior、interface、configuration、operation が変わる場合は、docs 更新要否を確認する。
* 同じ規範を複数の文書へコピーして source of truth を曖昧にしない。
* deprecated な手順や file を残す場合は、状態と移行先を明示する。

### SHOULD

* docs には「何をするか」だけでなく「なぜ必要か」を記載する。
* entrypoint、関連 docs、成果物、test、Evidence への導線を持たせる。
* AI Agent と人間が同じ文書を参照できる構造を優先する。

## 10. Dependencies and External Tools

### MUST

* dependency 追加の目的を明確にする。
* 標準機能または既存 dependency で十分な場合、不要な追加を避ける。
* dependency の license、distribution 条件、security risk を確認する。
* version を暗黙の latest へ依存させない。
* external tool が利用できない場合の failure behavior を定義する。
* tool 実行結果を無条件に信頼せず、exit status、output、artifact を確認する。

### SHOULD

* dependency 境界を狭く保つ。
* technology 固有処理を adapter または boundary へ閉じ込める。
* replacement または upgrade が可能な構造を優先する。
* 利便性だけを理由に platform 全体へ dependency を波及させない。

## 11. Boilerplate Expansion

### MUST

boilerplate を追加または拡張する場合は、次を確認します。

* template の目的と対象。
* 対象外。
* 必須入力。
* 生成物。
* configuration 方法。
* test 方法。
* security boundary。
* external I/O。
* Human Check 条件。
* Evidence 出力。
* update または migration 方針。
* removal または archive 方針。

template 固有の経験知や technology 解説を、共通 Guardrails へ大量に追加しません。

### SHOULD

* 共通規範を継承し、template 固有差分だけを定義する。
* copy 後に変更すべき箇所を明示する。
* placeholder の置換漏れを検出可能にする。
* README、test、example configuration、license 情報を揃える。
* 最小構成で動作確認できる状態を提供する。

## 12. AI Agent Implementation

### MUST

AI Agent は、成果物を変更するとき次を守ります。

* Context を先に読む。
* 指示された scope を確認する。
* 不足情報を無断で仮定しない。
* 既存の規範、schema、test、repository structure を確認する。
* 対象外変更を混ぜない。
* Human Check を迂回しない。
* scope、Human Check、secret、production、Governance の境界を自己判断で拡張しない。
* approval 済みでない外部公開、破壊的操作、production mutation を実行しない。
* 実施した変更と検証結果を説明する。
* 実行できなかった内容を隠さない。
* current evidence と RAG が矛盾する場合は、current evidence を優先する。
* Governance 変更を通常の docs 修正と同じ扱いで行わない。

### SHOULD

* 変更前に risk と影響範囲を整理する。
* 小さく検証可能な単位で変更する。
* runtime 中に見つけた friction は、現在の scope へ混ぜず改善候補として分離する。
* 人間がレビューしやすい diff、Evidence、説明を生成する。

## Exception Handling

Guardrails の例外が必要な場合は、次を記録します。

* 対象 rule。
* 例外が必要な理由。
* 代替案。
* 採用した方法。
* 影響範囲。
* 追加する安全策。
* 検証方法。
* 期限または解除条件。
* Human Check 結果。

例外を恒久的な暗黙運用にしません。

同じ例外が繰り返される場合は、rule、architecture、template、workflow のいずれを改善すべきか再評価します。

## Governance Update

Implementation Guardrails は、日常的な技術知識の蓄積先ではありません。

次に該当する場合に更新を検討します。

* security または safety 上、全成果物で守る必要がある。
* Human Responsibility や Human Check に影響する。
* platform integrity または source of truth を守る必要がある。
* 同種の重大な failure を、共通規範で防ぐ必要がある。
* 法令、license、契約上の制約がある。
* 自動化が責任境界を曖昧にする可能性がある。

技術的な best practice、障害事例、performance 知見、framework 固有ノウハウは、原則として RAG または technology docs へ保存します。

## まとめ

* Implementation Guardrails は、成果物へ共通して適用する最上位の実装規範である。
* 特定言語や framework の実装方法ではなく、安全性、責任境界、変更境界、検証、Evidence を扱う。
* secret、外部入力、副作用、権限、Human Check を明示的に管理する。
* test 未実施や failure を success として扱わない。
* boilerplate は共通 Guardrails を継承し、固有差分だけを追加する。
* 経験知や技術ノウハウは主に RAG へ保存し、Governance を肥大化させない。
* Governance 変更は、通常の knowledge 追加よりも強い Human Review を必要とする。
