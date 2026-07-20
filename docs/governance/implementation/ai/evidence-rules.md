---
language: ja-JP
---

# Evidence Rules

この文書は、AI Agent および workflow が実行した調査、変更、test、Human Check、結果を、検証可能な artifact として保存するための規範を定義します。

Evidence は、作業を行ったと主張するための装飾ではありません。

人間と AI Agent が、何を行い、何が確認され、何が未確認で、どの risk が残っているかを後から再構成するための情報です。

## 目的

* 実行内容と報告内容を一致させる。
* test や verificationの結果を追跡可能にする。
* Human Check と実 operation を対応付ける。
* failure と partial success を隠さない。
* rollback と recovery を支援する。
* RAG、Corrective Action、self-improvementの信頼できる入力を作る。
* 会話や人間の記憶だけに依存しない。

## Evidence Principles

### Traceable

何の作業に対する Evidence か追跡できる。

### Reproducible

可能な範囲で同じ verification を再実行できる。

### Verifiable

第三者が内容を確認できる。

### Minimal

不要な secret や大量 data を含めない。

### Immutable or Auditable

変更された場合に履歴を確認できる。

### Contextual

結果だけでなく、対象、条件、environment を持つ。

## Evidence Scope

Evidence 対象には次を含みます。

* Context 確認。
* repository調査。
* design decision。
* implementation。
* file 変更。
* command execution。
* test。
* lint。
* build。
* security scan。
* migration。
* deployment。
* Human Check。
* failure。
* rollback。
* runtime result。
* RAG retrieval。
* self-improvement candidate。

## Minimum Evidence

workflow で管理される変更では、最低限次を保存します。

* work-id。
* Intent。
* Scope。
* Target。
* Started At。
* Completed At。
* Actor。
* Environment。
* Changed Artifacts。
* Verification。
* Result。
* Human Check。
* Remaining Risks。
* Related Issue。
* Evidence Version。

## Evidence Types

### Process Report

作業全体の目的、変更、結果、risk をまとめます。

### Command Evidence

実行 command、exit status、重要 output を記録します。

### Test Evidence

test対象、command、結果、failed、skipped、coverage を記録します。

### Artifact Evidence

生成または変更した file、package、image、report への参照です。

### Human Check Evidence

承認要求、判断、条件、実行結果を記録します。

### Error Evidence

failure、再現条件、影響、復旧を記録します。

### Security Evidence

scan、permission、secret 確認などの結果を記録します。

### Runtime Evidence

起動、state、処理、shutdown、recovery を記録します。

## Evidence Directory

repository 固有規則がない場合、次のような構造を推奨します。

```text
evidence/
└── <work-id>/
    ├── process-report.md
    ├── evidence.json
    ├── commands/
    ├── tests/
    ├── artifacts/
    ├── human-check/
    ├── errors/
    └── runtime/
```

### MUST

* work-id または同等の識別子で分離する。
* current result と過去 result を混同しない。
* temporary file を Evidence directory へ無秩序に置かない。
* source artifact と Evidence copyのどちらが source of truthか明示する。
* Evidence path を安定させる。

## Machine-Readable Evidence

重要な workflow では、human-readable report に加えて machine-readable Evidence を用意します。

例:

```json
{
 "schema_version": "1.0",
 "work_id": "issue-123",
 "intent": "Add configuration validation",
 "status": "completed",
 "environment": "local",
 "changed_artifacts": [
 "src/config/validator.go"
 ],
 "verification": [
 {
 "type": "test",
 "command": "go test ./...",
 "status": "passed"
 }
 ],
 "human_check": {
 "required": false
 },
 "remaining_risks": []
}
```

### MUST

* schema version を持つ。
* statusの許容値を定義する。
* timestamp format を統一する。
* path format を統一する。
* secret を含めない。
* report との矛盾を避ける。

## Status

Evidence status には、少なくとも次を区別します。

* planned。
* in-progress。
* waiting-human-check。
* completed。
* completed-with-risk。
* failed。
* cancelled。
* rolled-back。
* partially-completed。

### MUST

* test failure や未検証がある状態を `completed` にしない。
* partial success を完全成功として扱わない。
* Human Check 待ちを completed として扱わない。
* cancelled と failed を区別する。

## Command Evidence

### MUST

command execution Evidence には必要に応じて次を含めます。

* command。
* working directory。
* environment。
* started time。
* completed time。
* exit code。
* stdout summary。
* stderr summary。
* generated artifact。
* timeout。
* retry。
* sanitization status。

### MUST NOT

* token。
* password。
* secret environment variable。
* authorization header。
* personal data。
  * 不必要な full request または response。

command を保存する場合は、secret argument を maskします。

## Test Evidence

### MUST

* test command。
* target。
* environment。
* result。
* passed。
* failed。
* skipped。
* duration。
* coverage。
* retryの有無。
* flakyの疑い。
* generated report。
  * 未実施 test。

### MUST

* retry 後に成功した場合、初回 failure を隠さない。
* skipped testの理由を記録する。
* manual verification を automated test として扱わない。
* test outputの一部だけで成功と判断しない。

## Artifact Evidence

### MUST

* artifact path。
* type。
* purpose。
* generated または modified。
* checksum または revision を必要に応じて記録する。
* source revision へ対応付ける。
* artifact が temporaryか permanentか明示する。
* generated artifactの generator version を必要に応じて記録する。

## Human Check Evidence

Human Check Evidence には次を含めます。

* requested decision。
* reason。
* target。
* scope。
* risks。
* alternatives。
* decision。
* approver。
* timestamp。
* conditions。
* expiration。
* operation result。

### MUST

* approval と execution を分離して記録する。
  * 条件付き承認の条件を保存する。
  * 承認 scope を識別可能にする。
* rejected または deferredも記録する。

## Failure Evidence

### MUST

failure発生時は次を残します。

* phase。
* operation。
* error classification。
* error message。
* affected artifacts。
* partial state。
* rollback。
* retry。
* recovery。
* root cause status。
* next action。
* residual risk。

root cause未確定の場合は、仮説を確定事項として記載しません。

## Evidence and Logs

```text
Log
 Runtime 中の出来事

Evidence
 判断と完了を検証するartifact
```

### MUST

* logだけを Evidence の全体としない。
* 必要な log range や location を Evidence から参照する。
* log retention により Evidence が失われないようにする。
  * 巨大な log をそのまま repository へ保存しない。
* Evidence に必要な summary を作成する。

## Security and Privacy

### MUST

Evidence へ次を保存しません。

* secret。
* credential。
* private key。
* full authorization header。
* personal data。
* payment data。
* production dataの無加工 copy。
* confidential prompt全文。
* internal informationの不必要な詳細。

### SHOULD

* mask。
* hash。
* count。
* safe summary。
* referenceのみの保存。

を利用します。

## Integrity

### MUST

* Evidence 改変を追跡可能にする。
  * 完了後に内容を変更した場合、理由を記録する。
* source revision と Evidence を対応付ける。
* machine-readable Evidence を schema validation する。
* timestamp を一貫した timezone または UTC で保存する。
* generated report へ schema version を付与する。

### SHOULD

重要な artifact には checksum を利用します。

## Evidence Retention

### MUST

* retention period を成果物特性に応じて定義する。
* security incident や release Evidence を短期間で削除しない。
* personal data を含む可能性がある Evidence は保存期間を制限する。
* obsolete Evidence を current Evidence として検索させない。
* archive と delete を区別する。

## Evidence to RAG

Evidence は、すべて自動的に RAG へ登録しません。

### MUST

RAG 登録前に次を確認します。

* reuse value。
* source trust。
* secret。
* personal data。
* project boundary。
* freshness。
* duplication。
* verified status。
* license。
* retention。

### MUST

* failed hypothesis を verified knowledge として登録しない。
  * 一時的な environment情報を恒久 knowledge にしない。
* Human Check content を無加工で吸収しない。
* Evidence original への reference を保持する。

## Completion Check

次の場合、Evidence は不十分です。

* work-id がない。
* target が不明。
* verification方法が不明。
* resultだけで command がない。
* test failure が省略されている。
* Human Check 結果がない。
* artifact path が存在しない。
* report と machine-readable data が矛盾する。
* secret が含まれる。
* residual risk が記録されていない。

## AI Agent 向け規範

AI Agent は Evidence 生成時に次を確認します。

1. 何を証明する Evidence か。
2. work-id。
3. target。
4. environment。
 5.実際に実施した内容。
 6.未実施内容。
5. failure。
6. Human Check。
7. artifact。
8. secret。
9. reproducibility。
10. residual risk。

## まとめ

* Evidence は作業結果を再構成し、検証するための artifact である。
* 会話や logだけへ依存しない。
* resultだけでなく、target、environment、command、risk を保存する。
* partial success、retry、failure、skipped を隠さない。
* Human Check と実 operation を対応付ける。
* RAG 登録前に trust、security、再利用価値を確認する。
