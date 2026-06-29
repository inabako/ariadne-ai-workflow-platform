# GaC / UaC GUI Mode

SVGで表現された人間の画面意図を、Semantic Layout Graph、Widget Mapping、Layout Spec、PyQt6候補、QTest候補へ変換し、既存Issue駆動workflowへ安全に返す共通拡張です。

独立した大本流やslash commandではありません。次の親workflowから自動dispatchします。

- `/robotics-new-system`
- `/robotics-feature-maintenance`
- `/corrective-action-fix`

## Activation

Issue作成前に、次の共有inboxへSVGを配置します。

```text
work/requirements/svg-input/SYS_<name>.svg
work/requirements/svg-input/FEAT_<name>.svg
work/requirements/svg-input/FIX_<name>.svg
```

親workflowがIssue作業領域を作成した後、対応プレフィックスのSVGを`work/<issue-id>/input/gui/`へ移動して確保します。SVGが無い場合、ランタイムは`status: skipped`を返し、親workflowを継続します。

## Issue Mode

| Issue prefix | Mode | Integration policy |
| --- | --- | --- |
| `SYS_*.svg` / `SYS-*` | system development | MainWindow、主要Panel、責務分離、拡張性 |
| `FEAT_*.svg` / `FEAT-*` | feature development | 既存GUIとの差分、結合点、影響範囲 |
| `FIX_*.svg` / `FIX-*` | corrective improvement | 最小変更、既存挙動維持、固定座標排除、回帰防止 |

新システムと機能開発のintakeは、それぞれ`SYS-*`、`FEAT-*`を既定採番します。Corrective Action Fixは既存の`work/issue-<number>`を保ち、論理Issue IDとして`FIX-<number>`と`--mode corrective-improvement`を渡します。

## Flow

```text
Parent workflow creates Issue work area
  -> work/requirements/svg-input/<PREFIX>_*.svg check
  -> claim SVG into Issue input/gui/
  -> skipped when absent
  -> SVG Analysis
  -> Semantic Layout Graph
  -> Widget Mapping
  -> Layout Spec
  -> generated PyQt6 candidate
  -> generated QTest candidate
  -> validation and review
  -> parent workflow implementation / test
```

## Runtime

入力directoryを準備:

```powershell
python runtime/workflow/gui_mode.py init-input
```

自動判定して生成:

```powershell
python runtime/workflow/gui_mode.py run --issue-id SYS-0001
```

既存Corrective Action work directoryで実行:

```powershell
python runtime/workflow/gui_mode.py run `
  --issue-id FIX-123 `
  --work-dir work/issue-123 `
  --mode corrective-improvement
```

完了検証:

```powershell
python runtime/workflow/gui_mode.py validate `
  --issue-id SYS-0001
```

ランタイム自己検証:

```powershell
python runtime/workflow/gui_mode.py self-test
```

既存成果物は既定で上書きしません。人間が意図的に再生成する場合だけ`--force`を使います。

## Artifacts

```text
work/<issue-id>/
  input/gui/
    <PREFIX>_<name>.svg
    README.md
  gac-uac/
    svg-analysis.md
    semantic-layout-graph.yaml
    widget-mapping.md
    layout-spec.md
    pyqt6-generation-plan.md
    qtest-generation-plan.md
    gui-mode-state.json
    generated/
      pyqt6/
        main_window.py
        widgets/
      tests/test_gui_smoke.py
    review/gac-uac-review.md
```

`gui-mode-state.json`は`.github/schemas/gui-mode-state.schema.json`に従い、親workflowへの返却可否と成果物pathを記録します。成果物は`context/artifact-index.json`にも登録されます。

SVGが無い場合も`work/<issue-id>/context/gui-mode-state.json`へ`status: skipped`を残します。SVGがある場合は、元inbox pathとIssue配下へ取り込んだpathをstateへ記録し、同じstateを`context/`と`gac-uac/`の両方へ保存します。

## Generated Candidate Policy

- SVGを画像として貼るだけで完了しません。
- SVG座標を`setGeometry`へ転写しません。
- PyQt6候補はLayoutを使い、対象Widgetへ`objectName`を設定します。
- controllerは注入可能にし、network、camera、robot、processなどの外部I/Oを直接起動しません。
- QTest候補はoffscreen実行、MainWindow生成、findChild、button signalを確認します。
- generated配下を既存sourceへ無条件コピーしません。親workflowで差分reviewし、必要部分だけを通常のsource / testsへ統合します。

## Completion Gate

次が存在し、`validate`が`pass`の場合に親workflowへ返します。

```text
gac-uac/layout-spec.md
gac-uac/widget-mapping.md
gac-uac/generated/pyqt6/
gac-uac/generated/tests/
```

実robot、実camera、physical STOP、field networkなどは、このサブワークフローのQTestだけで完了扱いにせず、親workflowのbench / integration / human checkへ残します。
