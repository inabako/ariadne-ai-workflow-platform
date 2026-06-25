---
project:
receipt_id:
repository:
branch:
commit:
workflow:
phase: nextjs-webapp-implementation-prep
status: draft
language: ja-JP
created_at:
---

# Next.js Webapp Implementation Preparation

## Intent

Next.js 画面機能の実装前に、新規webapp作成か既存webapp拡張かを分類し、boilerplate採用可否、画面契約、API契約、認証、環境変数、テスト、実装開始可否を明示する。

このreportは、実装者が画面だけを先に作って後から契約違いを直す状況を避けるための準備成果物です。未確認事項がある場合は、推測で埋めずにOpen QAへ残します。新規webappではtemplateを安全にコピーできるかを確認し、既存webappでは既存のrouting、layout、test runner、env規約を優先します。

## Activation

このreportは、次のいずれかに該当する場合に作成する。

- 新規のNext.js dashboard / admin / monitoring / business webappを作る。
- 既存Next.js webappへ画面、route、component、API接続、UI stateを追加する。
- `templates/boilerplates/nextjs-webapp-template/` を採用するか判断する。

## Inputs

入力はpathで追跡できるものを優先します。会話中の説明だけで確定扱いにせず、要件定義書、設計文書、API契約、既存source確認結果、または別process reportへの参照を残します。

| Artifact | Path | Status | Notes |
| --- | --- | --- | --- |
| Requirements |  | present / missing / partial |  |
| Product / UI requirements |  | present / missing / partial |  |
| Backend API contract |  | present / missing / partial |  |
| Existing app source |  | present / missing / not-applicable |  |
| Boilerplate selection report |  | present / missing / not-applicable |  |
| Test strategy |  | present / missing / partial |  |
| Deployment / runtime design |  | present / missing / partial |  |

## Implementation Mode

新規作成か既存拡張かでtemplateの扱いが変わります。新規作成ではcopy source候補、既存拡張や修正ではreference-onlyが原則です。

| Field | Value |
| --- | --- |
| Mode | new-app / existing-app-feature / corrective-fix |
| Target app path |  |
| Next.js detected | yes / no / not-applicable |
| App Router detected | yes / no / unknown / not-applicable |
| TypeScript detected | yes / no / unknown |
| Template candidate | `templates/boilerplates/nextjs-webapp-template/` / none |
| Template decision | use-template / reference-only / traditional-coding / blocked |
| Reason |  |

## Development Environment Preflight

開発環境は実装前に確認します。不足toolがある場合、勝手にinstallせず、必要なinstall listと理由を人間へ提示します。

| Check | Expected | Actual | Status |
| --- | --- | --- | --- |
| Node.js | `>=20.9` |  | pass / fail / not-checked |
| npm | available |  | pass / fail / not-checked |
| dependency install approval | approved before `npm install` when needed |  | pass / fail / not-checked |
| `npm install` | completed when `node_modules/` is missing or stale |  | pass / fail / not-needed / not-checked |
| `package.json` scripts | `dev`, `build`, `typecheck`, `lint`, `test` |  | pass / fail / not-checked |
| Docker runtime | needed / not-needed |  | pass / fail / not-checked |
| `.env.example` | exists and has no secrets |  | pass / fail / not-checked |
| local port | identified and not conflicting |  | pass / fail / not-checked |

## Screen Contract

画面契約は、routeとuser actionを中心に定義します。loading、empty、errorの状態を先に決めることで、後続実装が表示だけの仮置きにならないようにします。

| Screen / Route | Purpose | User Role | Entry Action | Primary State | Empty State | Error State |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## UI State And Component Plan

UI方針は既存design systemを優先します。新規appの場合だけtemplateのshellや共通componentを初期値として扱います。

| Area | Decision | Notes |
| --- | --- | --- |
| Layout shell | reuse template / existing shell / new shell |  |
| Navigation | sidebar / tabs / header-only / existing |  |
| Loading behavior | skeleton / spinner / disabled controls / none |  |
| Error behavior | inline / page-level / toast / existing |  |
| Form validation | client / server / both / not-applicable |  |
| Responsive requirement | desktop-only / desktop+tablet / desktop+mobile |  |
| Accessibility requirement | baseline / enhanced / product-specific |  |

## API Contract

API契約が不足している場合、画面側でrequestやresponseを推測して固定しません。mockを使う場合も、mockであることと未確定項目を明示します。

| API | Method | Request | Success Response | Error Response | Auth | Owner |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Auth And Data Boundary

認証、認可、secret、browser-visible dataの境界は必ず明示します。`NEXT_PUBLIC_*` はbrowserへ露出する値であり、secretを置く場所ではありません。

| Boundary | Decision | Evidence / Source |
| --- | --- | --- |
| Authentication required | yes / no / unknown |  |
| Authorization roles |  |  |
| Session storage | cookie / token / external / unknown |  |
| Secrets location | server-only env / external secret manager / none |  |
| Browser-visible env vars |  |  |
| Server-only env vars |  |  |
| Data persistence | backend API / local only / not-applicable |  |

## Boilerplate Copy Plan

Use only when `Template decision` is `use-template`.

| Source | Destination | Rename / Replace Rule | Keep Unchanged |
| --- | --- | --- | --- |
| `templates/boilerplates/nextjs-webapp-template/` |  |  |  |

## Test Plan

テスト方針は実装後の気分で決めません。実装前に、どの確認を自動化し、どの確認を人間確認やintegration evidenceへ残すかを決めます。

| Test Area | Required | Target Command | Evidence Target |
| --- | --- | --- | --- |
| TypeScript typecheck | yes / no | `npm run typecheck` |  |
| Lint | yes / no | `npm run lint` |  |
| Unit test | yes / no | `npm run test` |  |
| E2E / route smoke | yes / no | `npm run e2e` |  |
| Health check | yes / no | `/api/health` |  |
| UI smoke | yes / no | browser / Playwright |  |
| API connectivity | yes / no |  |  |
| Docker smoke | yes / no | `docker compose up --build` |  |

## Stop Rules

Implementation must not start when any blocking item is `yes`.

blocking itemがある場合は、表を空欄のまま進めず、ownerとresolutionを記録します。人間が条件付きで許可した場合は、conditional-passの理由と残リスクをDecisionsへ残します。

| Blocking Item | yes / no | Owner | Resolution |
| --- | --- | --- | --- |
| Target repository / branch is unknown |  |  |  |
| New app vs existing app mode is unclear |  |  |  |
| Required screen route or user action is missing |  |  |  |
| Required API contract is missing |  |  |  |
| Auth/session policy is unknown but affects the screen |  |  |  |
| Environment variable ownership is unclear |  |  |  |
| Test evidence target is missing |  |  |  |
| Required tool install is needed but not human-approved |  |  |  |
| `npm install` is required but has not completed successfully |  |  |  |
| Template copy destination may overwrite existing source |  |  |  |

## Decisions

| Decision | Reason | Evidence |
| --- | --- | --- |
|  |  |  |

## Open QA

| ID | Question | Blocks Implementation | Owner |
| --- | --- | --- | --- |
| QA-001 |  | yes / no |  |

## Handoff

| Field | Value |
| --- | --- |
| Implementation may start | yes / no |
| Mode | new-app / existing-app-feature / corrective-fix |
| Selected template |  |
| Target app path |  |
| Required commands |  |
| Required evidence |  |
| Blockers |  |
