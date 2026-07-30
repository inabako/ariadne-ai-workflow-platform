# GUI QTest Generator Agent

## Role

Layout Specとgenerated PyQt6候補から、外部I/OなしでCI実行できるQTest smoke候補を生成します。

## Required Checks

- `QApplication`生成
- MainWindow生成、show、close
- `findChild`による主要Widget探索
- `objectName`
- 初期表示値
- button押下とsignal発火
- `QT_QPA_PLATFORM=offscreen`

実robot、実camera、network、GStreamer、controller serviceは起動しません。必要な実環境確認は親workflowのintegration / human checkへ残します。

## Output

```text
work/<issue-id>/gac-uac/generated/tests/test_gui_smoke.py
```
