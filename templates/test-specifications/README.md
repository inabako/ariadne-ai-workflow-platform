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
- PyQt QTest source plan when the target uses PyQt / Qt GUI
- Required evidence
- Entry / exit criteria
- Safety gate

high / critical risk の変更では、simulation または bench test を field test より前に定義します。

PyQt / Qt GUI の結合疎通試験では、テストケース表からQTest化できるケースを選別します。

- QTest化できるものは target source、fixture / stub、GUI action、assertionを記録します。
- 実robot、実camera、physical STOP、field networkなどは人間確認またはbench evidenceとして残します。
- QTestで外部I/Oを起動する場合は、テストケース表に明示し、通常はstub / disable方針を優先します。

## Output Location

実案件では以下に保存します。

```text
work/<receipt-id>/test-specifications/
```

生成後は `work/<receipt-id>/context/artifact-index.json` に登録します。
