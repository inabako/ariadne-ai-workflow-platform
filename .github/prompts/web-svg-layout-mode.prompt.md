---
name: web-svg-layout-mode
description: 既存Issue駆動workflow内でWeb画面向けSVGを検出し、route/layout/component設計、React候補、Playwright候補を生成して親workflowへ返します。
argument-hint: "<issue-id> [work-dir]"
agent: agent
---

# Web SVG Layout Mode

このpromptは独立した大本流ではありません。`/ariadne-new-system`、`/ariadne-feature-maintenance`、`/corrective-action-fix` のIssue作業領域作成後、Web画面機能がある場合に差し込む共通サブワークフローです。

## Dispatcher

入力:

- `issue_id`
- `work_dir`
- `work/requirements/svg-input/WEB_SYS_*.svg`
- `work/requirements/svg-input/WEB_FEAT_*.svg`
- `work/requirements/svg-input/WEB_FIX_*.svg`
- Webapp implementation prep report
- 既存Web app source / tests

実行:

```powershell
python runtime/workflow/web_svg_layout_mode.py run `
  --issue-id "<issue-id>" `
  --work-dir "<work-dir>"
```

親workflowが `work/issue-<number>` を使う場合は、モードを明示します。

```powershell
python runtime/workflow/web_svg_layout_mode.py run `
  --issue-id "FIX-<number>" `
  --work-dir "work/issue-<number>" `
  --mode corrective-fix
```

SVGが無い場合、結果は `status: skipped` です。Web UI成果物を作らず、そのまま親workflowへ戻ります。

## Mode

| Prefix | Mode | Focus |
| --- | --- | --- |
| `WEB_SYS_*.svg` | `new-app` | 新規web appの初期route、layout、component責務、Playwright導線 |
| `WEB_FEAT_*.svg` | `existing-app-feature` | 既存routing、design system、component規約との整合と差分統合 |
| `WEB_FIX_*.svg` | `corrective-fix` | 最小変更、既存画面挙動維持、visual regression防止 |
| other | `generic-web-ui` | Web画面向けの論理layout、component責務、responsive構成 |

## Phases

1. SVG構造を `svg-analysis.md` へ変換する。
2. `route-layout-map.yaml` でroute候補、section、component候補を整理する。
3. `component-mapping.md` でReact component、HTML要素、test id候補へ写像する。
4. `responsive-layout-spec.md` でmobile / tablet / desktopとUI stateを整理する。
5. `generated/web/SvgLayoutCandidate.tsx` にReact候補を出す。
6. `generated/tests/svg-layout.spec.ts` にPlaywright smoke候補を出す。
7. `review/web-svg-layout-review.md` で人間・親workflowの差分reviewを受ける。

## Parent Workflow Return Gate

次が存在し、validateが `pass` の場合だけWeb UI成果物を親workflowへ返します。

```text
web-ui/responsive-layout-spec.md
web-ui/component-mapping.md
web-ui/generated/web/
web-ui/generated/tests/
```

generated配下は候補です。既存sourceへ無条件上書きせず、Issue scope、既存routing、design system、test fixtureとの差分をreviewし、採用部分だけ統合します。

## Stop Rules

- SVG XMLが壊れている場合は停止する。
- 既存成果物がある場合は上書きせず停止し、意図的な再生成時だけ `--force` を使う。
- API contract、auth、role、env、loading / empty / error stateをSVGだけから推測して確定しない。
- CSS absolute positionへの座標転写、画像貼り付けだけの実装、`dangerouslySetInnerHTML` を完了扱いにしない。
- Playwright候補をunit test、API connectivity、auth checkの代替にしない。

