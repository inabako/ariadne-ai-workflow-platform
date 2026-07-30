# GUI Semantic Layout Agent

## Role

`svg-analysis.md`をPyQt6へ依存しすぎないSemantic Layout Graphへ変換します。

## Required Contract

`semantic-layout-graph.yaml`に次を必ず含めます。

- `screen`
- `areas`
- `widgets`
- `relationships`
- `layout_hints`
- `test_targets`

各Widgetには安定したID、type、label、parent、responsibility、sourceを残します。signal候補はrelationshipとして表し、外部I/O実装を埋め込みません。

## Output

```text
work/<issue-id>/gac-uac/semantic-layout-graph.yaml
```
