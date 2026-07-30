# Web SVG Layout Mode

SVGで表現された画面レイアウト案を、Web画面向けのroute、section、component責務、responsive layout、React候補、Playwright候補へ変換する共通サブフローです。Next.jsは、このフローが扱うWeb framework profileの1つです。

独立したslash commandではありません。Web画面機能を含む親workflowのImplementation前に実行します。

- `/ariadne-new-system`
- `/ariadne-feature-maintenance`
- `/corrective-action-fix`

## Activation

Issue作成前に、共有inboxへWeb画面向けSVGを配置します。

```text
work/requirements/svg-input/WEB_SYS_<name>.svg
work/requirements/svg-input/WEB_FEAT_<name>.svg
work/requirements/svg-input/WEB_FIX_<name>.svg
```

`SYS_`、`FEAT_`、`FIX_` はPyQt / Qt向けのGaC / UaC GUI Modeで使うため、Web画面向けは `WEB_` prefix を使います。既存互換として `NEXT_SYS_`、`NEXT_FEAT_`、`NEXT_FIX_` も取り込みます。

## Flow

```text
Parent workflow creates Issue work area
  -> Webapp implementation preparation
  -> work/requirements/svg-input/WEB_<PREFIX>_*.svg check
  -> claim SVG into work/<issue-id>/input/web-ui/
  -> skipped when absent
  -> SVG Analysis
  -> Route Layout Map
  -> Component Mapping
  -> Responsive Layout Spec
  -> generated React component candidate
  -> generated Playwright candidate
  -> review
  -> parent workflow implementation / test
```

## Runtime

実行前に推奨環境を確認します。

```powershell
aiwfctl env select web-svg
```

入力directoryのWeb画面向けREADMEを作成します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl web-svg init-input
```

自動判定して生成します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl web-svg run --issue-id SYS-0001
```

既存Corrective Action work directoryで実行します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl web-svg run `
  --issue-id FIX-123 `
  --work-dir work/issue-123 `
  --mode corrective-fix
```

完了検証:

```powershell
.\runtime\windows-script\aiwf.cmd ctl web-svg validate `
  --issue-id SYS-0001
```

既存成果物は既定で上書きしません。人間が意図的に再生成する場合だけ `--force` を使います。

## Artifacts

```text
work/<issue-id>/
  input/web-ui/
    WEB_<PREFIX>_<name>.svg
  web-ui/
    svg-analysis.md
    route-layout-map.yaml
    component-mapping.md
    responsive-layout-spec.md
    react-generation-plan.md
    playwright-generation-plan.md
    web-svg-layout-state.json
    generated/
      web/SvgLayoutCandidate.tsx
      tests/svg-layout.spec.ts
    review/web-svg-layout-review.md
```

`web-svg-layout-state.json` は `.ariadne/schemas/web-svg-layout-state.schema.json` に従い、親workflowへの返却可否と成果物pathを記録します。成果物は `context/artifact-index.json` にも登録されます。

SVGが無い場合も `work/<issue-id>/context/web-svg-layout-state.json` へ `status: skipped` を残します。

## Generated Candidate Policy

- SVGを画像として貼るだけで完了しません。
- SVG座標をCSS absolute positionへ転写しません。
- React候補はroute / section / component責務を確認するための候補です。
- Playwright候補はvisual smoke / reachability候補であり、API contract、auth、unit testの代替ではありません。
- generated配下を既存sourceへ無条件コピーしません。
- 既存appでは既存routing、design system、test runner、env conventionを優先します。

## Completion Gate

次が存在し、`validate` が `pass` の場合に親workflowへ返します。

```text
web-ui/responsive-layout-spec.md
web-ui/component-mapping.md
web-ui/generated/web/
web-ui/generated/tests/
```

API、auth、role、loading / empty / error state、env / secret境界は、このサブフローだけでは確定しません。必ずWebapp実装前準備と親workflowの要件に戻して確認します。

