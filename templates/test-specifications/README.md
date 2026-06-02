# Test Specification Templates

このディレクトリは、テスト仕様書とテストケース表の標準フォーマットを格納します。

test specification は、実装後に慌てて確認項目を作るためではなく、実装前に「何を満たせば安全に次へ進めるか」を決める artifact です。

## Templates

| File | Purpose |
| --- | --- |
| `robotics-test-specification-template.md` | robotics の test strategy と test case table |

## Quality Rule

test specification では、最低限以下を必ず埋めます。

- Test objective
- Scope / out of scope
- Requirement traceability
- Risk based test priority
- Test environment
- Test case table
- Required evidence
- Entry / exit criteria
- Safety gate

high / critical risk の変更では、simulation または bench test を field test より前に定義します。

## Output Location

実案件では以下に保存します。

```text
work/<receipt-id>/test-specifications/
```

生成後は `work/<receipt-id>/context/artifact-index.json` に登録します。
