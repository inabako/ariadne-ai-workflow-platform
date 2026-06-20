---
name: gac-uac-gui-mode
description: 既存Issue駆動workflow内でSVGを検出し、GUI設計中間成果物、PyQt6候補、QTest候補を生成して親workflowへ返します。
argument-hint: "<issue-id> [work-dir]"
agent: agent
---

# GaC / UaC GUI Mode

このpromptは独立した大本流ではありません。`/robotics-new-system`、`/robotics-feature-maintenance`、`/corrective-action-fix`のIssue作業領域作成後に差し込む共通サブワークフローです。

## Dispatcher

入力:

- `issue_id`
- `work_dir`
- `work/requirements/svg-input/<PREFIX>_*.svg`
- 既存source / tests

実行:

```powershell
python runtime/workflow/gui_mode.py run `
  --issue-id "<issue-id>" `
  --work-dir "<work-dir>"
```

親workflowが`work/issue-<number>`などの既存IDを使う場合は、モードを明示します。

```powershell
python runtime/workflow/gui_mode.py run `
  --issue-id "FIX-<number>" `
  --work-dir "work/issue-<number>" `
  --mode corrective-improvement
```

Issue作業領域ができた後、対応する`SYS_`、`FEAT_`、`FIX_` SVGを`work/<issue-id>/input/gui/`へ移動して確保します。SVGが無い場合、結果は`status: skipped`です。GUI成果物を作らず、そのまま親workflowへ戻ります。

## Mode

| Prefix | Mode | Focus |
| --- | --- | --- |
| `SYS-*` | `system-development` | 初期構成、責務分離、拡張性 |
| `FEAT-*` | `feature-development` | 既存GUIとの差分、結合点、影響範囲 |
| `FIX-*` | `corrective-improvement` | 最小変更、既存挙動維持、回帰防止 |
| other | `generic-gui` | 論理Layoutと安全な統合候補 |

## Phases

1. `gui-svg-analyzer-agent`がSVG構造を`svg-analysis.md`へ変換する。
2. `gui-semantic-layout-agent`がPyQt非依存の`semantic-layout-graph.yaml`を作る。
3. `gui-widget-mapping-agent`がPyQt6 Widget、class、signal/slot、test対象へ写像する。
4. `gui-layout-spec-agent`がIssue mode別の`layout-spec.md`を確定する。
5. `gui-pyqt6-generator-agent`が外部I/Oなしの候補を`generated/pyqt6/`へ出す。
6. `gui-qtest-generator-agent`がoffscreen実行可能な候補を`generated/tests/`へ出す。
7. `review/gac-uac-review.md`で人間・親workflowの差分reviewを受ける。

標準ランタイムは上記成果物のdeterministic baselineを一括生成します。Agentはbaselineを要件、既存source、既存testsと照合し、必要な箇所だけ精緻化します。

## Output

```text
work/<issue-id>/gac-uac/
  svg-analysis.md
  semantic-layout-graph.yaml
  widget-mapping.md
  layout-spec.md
  pyqt6-generation-plan.md
  qtest-generation-plan.md
  gui-mode-state.json
  generated/pyqt6/
  generated/tests/test_gui_smoke.py
  review/gac-uac-review.md
```

検証:

```powershell
python runtime/workflow/gui_mode.py validate `
  --issue-id "<issue-id>" `
  --work-dir "<work-dir>"
```

## Parent Workflow Return Gate

次が存在し、validateが`pass`の場合だけGUI成果物を親workflowへ返します。

```text
gac-uac/layout-spec.md
gac-uac/widget-mapping.md
gac-uac/generated/pyqt6/
gac-uac/generated/tests/
```

generated配下は候補です。既存sourceへ無条件上書きせず、Issue scope、既存architecture、既存test fixtureとの差分をreviewし、採用部分だけ統合します。

## Stop Rules

- SVG XMLが壊れている場合は停止する。
- 既存成果物がある場合は上書きせず停止し、意図的な再生成時だけ`--force`を使う。
- controller API、状態遷移、業務validationをSVGだけから推測して確定しない。
- `setGeometry`による座標転写、外部I/O直結、objectNameなし、QTest不能な候補を完了扱いにしない。
- SYS / FEAT / FIXのmode方針を無視して同じ統合判断をしない。
