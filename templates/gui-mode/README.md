# GaC / UaC GUI Mode Template

SVGで表現された画面意図を、PyQt6へ直接座標転写せず、論理Layout、Widget責務、signal、QTest候補へ変換する共通サブワークフロー用templateです。

Issue作成前の入力:

```text
work/requirements/svg-input/SYS_<name>.svg
work/requirements/svg-input/FEAT_<name>.svg
work/requirements/svg-input/FIX_<name>.svg
```

初期化:

```powershell
python runtime/workflow/gui_mode.py init-input
```

生成:

```powershell
python runtime/workflow/gui_mode.py run --issue-id SYS-0001
```

`SYS_`、`FEAT_`、`FIX_`のファイル名で親フローを選別します。Issue作業領域作成後、対象SVGは`work/<issue-id>/input/gui/`へ移動されます。

`SYS-*`、`FEAT-*`、`FIX-*`から生成方針も自動選択します。既存の`work/issue-<number>`などを使う親フローは、`--work-dir`と`--mode`を明示してください。

生成物は`work/<issue-id>/gac-uac/`へ保存され、既存sourceへ自動コピーされません。

ランタイム自己検証:

```powershell
python runtime/workflow/gui_mode.py self-test
```
