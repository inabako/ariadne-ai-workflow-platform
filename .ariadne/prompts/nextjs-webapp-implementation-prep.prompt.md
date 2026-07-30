---
name: nextjs-webapp-implementation-prep
description: 親workflow内でNext.js画面機能の実装前に、新規/既存分類、boilerplate採用可否、画面契約、API契約、auth、env、testを整理します。
argument-hint: "<work-id> [target-app-path]"
agent: agent
---

# Next.js Webapp Implementation Preparation

このpromptは独立した大本流ではありません。`/ariadne-new-system`、`/ariadne-feature-maintenance`、`/corrective-action-fix` のImplementation前に差し込む準備サブワークフローです。

目的は、画面実装を始める前に曖昧な判断を残さないことです。特に、画面だけ先に作ってAPI契約、認証、環境変数、テスト証跡が後から合わなくなる状態を防ぎます。新規アプリではboilerplateを安全にコピーできるかを確認し、既存アプリでは既存構成を壊さず参照だけに留めます。未確認事項が残る場合は実装へ進まず、Open QAとして人間確認に戻します。

## 入力

- requirements document
- architecture / runtime / deployment design
- backend API contract
- UI requirements or screen list
- target repository / branch / app path
- Web SVG Layout Mode output, when `WEB_*` SVG exists
- test strategy
- boilerplate-template-selection report, when available

上記の入力は、会話ログだけで済ませません。要件定義書、設計文書、API契約、既存source確認結果、またはprocess reportとして参照できるpathを残してください。

## 出力

```text
work/<work-id>/process-report/nextjs-webapp-implementation-prep.md
```

次のtemplateを使います。

```text
templates/artifacts/process-report/nextjs-webapp-implementation-prep-template.md
```

## 流れ

1. 作業modeを `new-app`、`existing-app-feature`、`corrective-fix` のどれかに分類する。
2. `new-app` の場合、`templates/boilerplates/apps/nextjs-app-template/` をcopy source候補として評価する。
3. `existing-app-feature` または `corrective-fix` の場合、templateはreference-onlyとして扱い、既存appのrouting、layout、test runner、env規約を先に確認する。
4. Node.js、npm、scripts、env files、port、Docker要否、tool install承認状態を確認する。
5. `node_modules/` が無い、または依存関係が古い場合は、承認後に対象app directoryで `npm install` を実行する。
6. `WEB_SYS_`、`WEB_FEAT_`、`WEB_FIX_` SVGがある場合、`.ariadne/prompts/web-svg-layout-mode.prompt.md` に従って `web-ui/` を生成し、review結果を参照する。
7. route、screen purpose、user role、entry action、loading state、empty state、error stateを定義する。
8. API method、request、success response、error response、auth requirement、ownerを定義する。
9. auth/session policy、browser-visible env、server-only env、secret ownershipを定義する。
10. typecheck、lint、unit、e2e、health、UI smoke、API connectivity、Docker smokeの採否を決める。
11. blocking QAが残る場合は停止する。
12. `Implementation may start: yes` の場合だけ実装へ渡す。

## 停止条件

- target repository、branch、app pathが不明。
- 新規appか既存app拡張か分類できない。
- 必須route、user action、UI stateが不足している。
- 必須API contractまたはerror responseが不足している。
- auth/session policyが画面に影響するのに未定。
- envまたはsecret ownershipが不明。
- required tool installが必要だが人間承認されていない。
- `npm install` が必要なのに未実行、または失敗している。
- template copy destinationが既存sourceを上書きする恐れがある。
- `WEB_*` SVGがあるのにWeb SVG Layout Modeのreviewが未完了。
- test evidence targetが未定。

## 守ること

- 既存app source treeへ `nextjs-app-template` を丸ごとコピーしない。
- backend contractが不足している状態でAPI request / responseを推測して固定しない。
- `NEXT_PUBLIC_*` にsecretを置かない。
- deployable webapp microserviceで `/api/health` を省略しない。
- UI smokeをtypecheck、unit tests、API connectivity、auth checksの代替にしない。
