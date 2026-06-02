# Process Report Templates

このディレクトリは、工程ごとの実行レポートの標準フォーマットを格納します。

process report は、Agent や tool が何を入力にし、何を確認し、何を判断し、何を次へ渡したかを記録するための artifact です。

## Templates

| File | Purpose |
| --- | --- |
| `robotics-process-report-template.md` | intake、comparison、review、implementation、handoff など工程共通のreport |

## Quality Rule

process report では、最低限以下を必ず埋めます。

- Process identity
- Input artifacts
- Repository state
- Actions performed
- Findings
- Decisions
- Generated artifacts
- Risks / blockers
- Next actions
- Handoff summary

report は単なる作業日報ではありません。次のAgentや人間が再探索せず、判断の続きから始められる context package として作成します。

## Output Location

実案件では以下に保存します。

```text
work/<receipt-id>/process-report/
```

生成後は `work/<receipt-id>/context/artifact-index.json` に登録します。
