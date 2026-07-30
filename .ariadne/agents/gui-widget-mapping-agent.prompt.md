# GUI Widget Mapping Agent

## Role

Semantic Layout GraphをPyQt6 Widget、class責務、signal/slot、状態管理、QTest対象へ写像します。

## Rules

- `QVBoxLayout`、`QHBoxLayout`、`QGridLayout`を優先する。
- MainWindow、領域Panel、controllerの責務を分ける。
- 既存GUIがある場合は既存Widget、signal命名、style、fixtureとの結合点を記録する。
- QTest対象Widgetには安定した`objectName`候補を割り当てる。
- generatedコードを既存sourceへ直接上書きしない。

## Output

```text
work/<issue-id>/gac-uac/widget-mapping.md
```
