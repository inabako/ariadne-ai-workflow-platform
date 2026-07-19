# Web SVG Layout Mode Template

SVGで表現されたNext.js画面レイアウト案を、route、section、component責務、responsive layout、React候補、Playwright候補へ変換する共通サブワークフロー用templateです。

Issue作成前の入力:

```text
work/requirements/svg-input/WEB_SYS_<name>.svg
work/requirements/svg-input/WEB_FEAT_<name>.svg
work/requirements/svg-input/WEB_FIX_<name>.svg
```

初期化:

```powershell
python runtime/workflow/web_svg_layout_mode.py init-input
```

生成:

```powershell
python runtime/workflow/web_svg_layout_mode.py run --issue-id SYS-0001
```

`WEB_SYS_`、`WEB_FEAT_`、`WEB_FIX_` のファイル名で親フローとWeb UI modeを選別します。Issue作業領域作成後、対象SVGは `work/<issue-id>/input/web-ui/` へ移動されます。

生成物は `work/<issue-id>/web-ui/` へ保存され、既存sourceへ自動コピーされません。

