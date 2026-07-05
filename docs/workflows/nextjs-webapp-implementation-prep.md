# Next.js Webapp Implementation Preparation

Next.js 画面機能を実装する前に、対象が新規webappか既存webapp拡張かを分類し、`nextjs-webapp-template` の採用可否、画面契約、API契約、認証、環境変数、テスト方針を揃える準備サブフローです。

独立したslash commandではありません。親workflowのImplementation前に実行します。

- `/robotics-new-system`
- `/robotics-feature-maintenance`
- `/corrective-action-fix`

## Activation

次の場合にこの準備を行います。

- 新規Next.js dashboard / admin / monitoring / business webappを作る。
- 既存Next.js webappへ画面、route、component、API接続、UI stateを追加する。
- `templates/boilerplates/nextjs-webapp-template/` を採用するか判断する。
- 画面機能の要件はあるが、API、認証、テスト、環境変数の境界が未整理である。

実行前に推奨環境を確認します。

```powershell
aiwfctl env select nextjs-webapp-implementation-prep
```

## Inputs

```text
requirements document
architecture / runtime / deployment design
backend API contract
UI requirements or screen list
test strategy
boilerplate-template-selection report, when available
```

既存webapp拡張では、target repository / branch / app path を必須入力にします。新規webappでは、copy destination と service name を必須入力にします。

## Flow

```text
Parent workflow reaches implementation planning
  -> classify new-app / existing-app-feature / corrective-fix
  -> inspect target app or select nextjs-webapp-template
  -> prepare nextjs-webapp-implementation-prep report
  -> check development environment and tool install needs
  -> run npm install after approval when dependencies are not installed
  -> run Web SVG Layout Mode when WEB_* SVG exists
  -> define route and screen contract
  -> define UI state and component plan
  -> define API contract and auth boundary
  -> define environment variables and secret boundary
  -> define unit / e2e / health / UI smoke / API connectivity tests
  -> stop on blockers or human approval gates
  -> hand off to implementation
```

## Artifact

実案件では次へ保存します。

```text
work/<receipt-id>/process-report/nextjs-webapp-implementation-prep.md
```

Template:

```text
templates/process-report/nextjs-webapp-implementation-prep-template.md
```

Web画面向けSVGがある場合は、次のサブフロー成果物も参照します。

```text
work/<issue-id>/web-ui/
```

詳細:

```text
docs/workflows/web-svg-layout-mode.md
```

生成後は可能な限り次にも登録します。

```text
work/<receipt-id>/context/artifact-index.json
```

## Mode Rules

| Mode | Use Case | Template Policy |
| --- | --- | --- |
| `new-app` | 新規Next.js webapp / microserviceを作る | `nextjs-webapp-template` をコピー候補にする |
| `existing-app-feature` | 既存Next.js appへ画面機能を追加する | templateはreference-only。既存構成を優先する |
| `corrective-fix` | 既存画面のbug fix /改善 | templateはreference-only。最小変更と回帰防止を優先する |

## Preparation Checks

| Area | Required Decision |
| --- | --- |
| Target | repository、branch、app path、service name |
| Runtime | Node.js version、npm、Next.js version、App Router有無 |
| Dependency install | `node_modules/` 有無、`npm install` 実行可否、人間承認、lockfile方針 |
| Screen | route、user role、user action、loading、empty、error state |
| SVG Layout | `WEB_SYS_` / `WEB_FEAT_` / `WEB_FIX_` SVG、responsive layout、component mapping、Playwright候補 |
| API | method、request、success response、error response、auth |
| Auth | login requirement、role、session、browser-visible data |
| Environment | `.env.example`、server-only env、`NEXT_PUBLIC_*` env |
| Test | typecheck、lint、unit、e2e、health、UI smoke、API connectivity |
| Docker | Dockerが必要な場合のbuild/run/health check |

## Stop Rules

次の場合は実装へ進まず、`Open QA` を埋めて人間確認に戻します。

- target repository / branch / app path が不明。
- 新規appか既存app拡張か分類できない。
- 必須screen route、user action、UI state が不明。
- 必須API contract または error response が不明。
- 認証・認可が必要そうだがpolicyが未定。
- `.env`、secret、browser-visible env の境界が不明。
- `npm install` など tool install が必要だが承認されていない。
- `npm install` が必要なのに未実行、または失敗している。
- template copy が既存sourceを上書きする恐れがある。
- Web画面向けSVG候補があるのに `web-ui/` のreviewが未完了。
- test evidence target が決まっていない。

## Handoff To Implementation

Implementationへ進める条件:

- `Implementation may start: yes`
- mode、target app path、template decision が明記されている。
- screen contract と API contract が最低1件以上ある、または対象外理由がある。
- `WEB_*` SVGを使う場合、`web-ui/responsive-layout-spec.md` と `component-mapping.md` がreview済みである。
- auth / env / secret boundary が明記されている。
- `npm run typecheck`、`npm run lint`、unit、e2e、health、UI smoke、API connectivity の採否が明記されている。
- 依存関係が必要な場合、承認済みの `npm install` が完了し、少なくとも `npm run typecheck` を実行できる状態である。
- blocker が `none` または human-approved conditional-pass である。

## Guardrails

- 新規app以外では template 本体をコピーして既存sourceへ上書きしない。
- 既存appでは既存の routing、design system、test runner、env convention を優先する。
- `NEXT_PUBLIC_*` にsecretを置かない。
- API contract が未確定のまま UI 側で推測した request / response を固定しない。
- health endpoint を持つmicroserviceでは `/api/health` の疎通確認を省略しない。
- visual smokeは実装確認であり、unit / API connectivity / auth check の代替にしない。
