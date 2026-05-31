# GUI SVG Input Inbox

Issue作成前に、画面実装の入力となるSVGをこのディレクトリへ配置します。

ファイル名:

```text
SYS_<name>.svg
FEAT_<name>.svg
FIX_<name>.svg
```

- `SYS_`: 新システム開発
- `FEAT_`: 新機能・保守開発
- `FIX_`: 改修改善

親フローがIssue作業領域を作成した後、対応するSVGは次へ移動され、GUI Modeで処理されます。

```text
work/<issue-id>/input/gui/
```

同じプレフィックスのSVGが複数ある場合、同一Issueの複数画面入力としてまとめて取り込みます。

SVGは完成画像ではなく、Semantic Layout Graph、Widget Mapping、Layout Spec、PyQt6候補、QTest候補を作る入力として扱います。
