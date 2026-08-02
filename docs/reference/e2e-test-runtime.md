# E2E Test Runtime

`aiwfctl e2e` は、結合試験およびE2Eテストを runtime artifact として扱うための入口です。

目的は、試験を単発の手作業ログで終わらせず、計画、成立条件、Stub、実行結果、観測、期待結果との照合、説明を同じ流れで残すことです。

## Flow

```text
試験目的を定義
  -> 成立条件を確認
  -> 必要Stubを判定
  -> E2E/結合試験を実行
  -> 処理経路を観測
  -> 期待結果と照合
  -> 不足・異常を説明
  -> 修正指示と再テスト導線を生成
  -> Human Check
```

## Commands

```powershell
aiwfctl e2e plan --work-id <work-id> --objective "試験目的"
aiwfctl e2e contract scaffold --work-id <work-id>
aiwfctl e2e contract --work-id <work-id>
aiwfctl e2e readiness --work-id <work-id>
aiwfctl e2e run --work-id <work-id> --dry-run
aiwfctl e2e run --work-id <work-id> --human-check approved
aiwfctl e2e observe --work-id <work-id>
aiwfctl e2e verify --work-id <work-id>
aiwfctl e2e review-plan --work-id <work-id>
aiwfctl e2e coverage --work-id <work-id>
aiwfctl e2e explain --work-id <work-id>
aiwfctl e2e final-gate --work-id <work-id> --human-decision approved --reviewer <name>
aiwfctl e2e evidence-package --work-id <work-id> --trace-id <trace-id> --output docs/evidence/<work-id>/e2e-package.json
aiwfctl e2e loop --work-id <work-id>
```

結合試験として扱う場合は、同じ command に `--test-kind integration` を付けます。

## Verification Contract

`aiwfctl e2e contract` は、AIへテストを書かせる前に検証契約を固定するための工程です。

契約では、目的、trigger、前提条件、期待される処理経路、状態遷移、副作用、観測endpoint、timing / ordering制約、重複実行、retry / recovery、必要Stub、失敗signal、evidence要件、Human Review観点を `test_contract` として保存します。

`readiness` と `verify` は、この契約が存在しない場合、または必須観点が未定義の場合に blocked / human-check-required として扱います。これにより、テスト実装やE2E実行の前に「何をもって成功とするか」を人間とAgentが共有できます。

`aiwfctl e2e contract scaffold` は、既存planから objective、trigger候補、Stub、evidence要件を引き継いだ `draft-with-gaps` の契約ひな形を作成します。既存の契約を上書きしないため、再生成する場合は `--force` を明示します。

`readiness` は、契約とplanの軽量な整合性も確認します。shell commandに見える `trigger` が `plan.commands` に含まれない場合は blocker とし、API/UIの観測点に対して実行commandの手がかりが弱い場合は warning として `contract_consistency_checks` に残します。

## Responsibility Split

E2E / integration test は、単一Agentに丸ごと委ねません。

- Contract Designer: 検証契約を作成し、成功条件、失敗条件、観測点、evidence要件を固定します。
- Readiness Checker: 契約、Stub、実行command、contract / plan整合性を確認します。
- Runner: Human Check後に、契約されたcommandだけを実行します。
- Observer: 経路、状態遷移、副作用、endpoint、失敗signalを観測します。
- Verifier: 観測結果と契約を照合します。
- Explainer: 不足、異常、再テスト理由を説明します。
- Review Council: UX、Accessibility、Frontend Architecture、Runtime Architectureなどの専門観点で、E2E evidenceをレビューします。
- Human Reviewer: contract、evidence、Review Council結果をもとに最終判断します。

## Review Council Bridge

`aiwfctl e2e review-plan` は、`verify` 後のE2E evidenceをReview Councilへ渡すためのbridge artifactを作成します。

出力には、必要reviewer、E2E evidence path、`aiwfctl review plan`、`aiwfctl review start`、`aiwfctl review evidence-gate` の次コマンドが含まれます。E2E runtimeは専門レビューを自動承認せず、Review Councilが扱える入力だけを固定します。

## Coverage / Final Gate

`aiwfctl e2e coverage` は、plan、contract、readiness、run-result、observation、verification などの required evidence と、contract の `evidence_requirements` が揃っているかを確認し、`coverage.json` / `coverage.md` に保存します。

`aiwfctl e2e final-gate` は、verification、Review Council bridge、coverage、explanation を最終判断の入力として束ね、Human Reviewer の `pending` / `approved` / `rejected` を `human-final-gate.json` / `human-final-gate.md` に保存します。`--decision-reason` と `--review-reference` を付けると、判断理由と参照したReview Council / PR / Human Check番号も一緒に残せます。

`aiwfctl e2e evidence-package` は、E2E / 結合試験の plan、contract、各 evidence、Review Council bridge、coverage、explanation、Human final gate を1つの handoff package として集約し、PR / Human Check / 後続Agentが参照しやすい `evidence-package.json` / `evidence-package.md` を保存します。`--output` で `docs/evidence/...` などへJSON copyを保存できます。`--trace-id` を付けると、`trace show`、`log grep`、`log export` の参照コマンドも package に残ります。

`loop.json` が存在し、status が `pass` ではない場合、`evidence-package` は未解決の修正ループが残っているものとして `blocked` にします。

## Artifact

作業中の計画は `work/<work-id>/test-specifications/` に保存します。

```text
work/<work-id>/test-specifications/
  e2e-test-plan.json
  e2e-test-plan.md
  e2e-test-contract.json
  e2e-test-contract.md
```

実行・観測・照合・説明の証跡は `work/<work-id>/test-evidence/e2e-test/` に保存します。

```text
work/<work-id>/test-evidence/e2e-test/
  readiness.json
  run-result.json
  observation.json
  verification.json
  review-plan.json
  review-plan.md
  coverage.json
  coverage.md
  human-final-gate.json
  human-final-gate.md
  evidence-package.json
  evidence-package.md
  explanation.json
  explanation.md
  loop.json
  loop.md
```

`--test-kind integration` の場合は、`integration-test-plan.*` と `test-evidence/integration-test/` に保存します。

## Safety

`aiwfctl e2e run` は、既定では実行を止めます。

実際に plan 内の `--run-command` を実行するには、事前に `readiness` を確認し、`--human-check approved` を明示します。

```powershell
aiwfctl e2e run --work-id <work-id> --human-check approved
```

外部環境、クラウド、実機、credential、破壊的操作を含む試験は、Runtime上で通っていても Human Check を最終判断にします。

## Fix Loop

`aiwfctl e2e loop` は、問題発見後の修正指示と再テスト導線を1つの runtime artifact に束ねます。

```powershell
aiwfctl e2e loop `
  --work-id <work-id> `
  --trace-id <trace-id> `
  --review-id <review-id> `
  --problem "画面遷移後に完了状態が観測できない" `
  --fix-summary "完了状態の保存とUI反映を修正する" `
  --fix-command "aiwfctl scm compare --work-id <work-id>"
```

この command は、既存の `run-result`、`observation`、`verification`、`explanation` を読み、足りない観測・照合があれば補完します。そのうえで、次の情報を `loop.json` / `loop.md` に保存します。

- 検出された問題
- 修正指示
- Review Council plan command
- trace/log確認導線
- SCM compare / commit dry-run導線
- 再テスト command

修正作業そのものは自動実行しません。

修正後は、`loop.md` の `Retest Commands` に従い、同じ `work-id` で再テストします。
