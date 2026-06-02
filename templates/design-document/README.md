# Design Document Templates

このディレクトリは、設計書の標準フォーマットを格納します。

設計書は「何を作るか」だけではなく、「なぜその設計にしたか」「何を守るための設計か」「どのtest / evidenceで妥当性を確認するか」まで残します。

## Templates

| File | Purpose |
| --- | --- |
| `robotics-design-document-template.md` | robotics system / feature / maintenance に共通で使う設計書 |

## Quality Rule

設計書では、最低限以下を必ず埋めます。

- Intent
- Decision
- Reason
- Scope / Non-goals
- Repository / branch / commit
- Safety impact
- Responsibility boundary
- Failure behavior
- Test strategy
- Open QA
- Approval / review status

STOP、communication loss、startup safe state、shutdown safe state が未定義の場合は、設計書を `approved` にしません。

## Output Location

実案件では以下に保存します。

```text
work/<receipt-id>/design-document/
```

生成後は `work/<receipt-id>/context/artifact-index.json` に登録します。
