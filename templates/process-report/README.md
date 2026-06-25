# Process Report Templates

このディレクトリは、工程ごとの実行レポートの標準フォーマットを格納します。

process report は、Agent や tool が何を入力にし、何を確認し、何を判断し、何を次へ渡したかを記録するための artifact です。

## Templates

| File | Purpose |
| --- | --- |
| `robotics-process-report-template.md` | intake、comparison、review、implementation、handoff など工程共通のreport |
| `boilerplate-template-selection-report-template.md` | 新システム実装前にboilerplate template採用可否、コピー元、コピー先、fallback理由を記録するreport |
| `nextjs-webapp-implementation-prep-template.md` | Next.js画面機能実装前に新規/既存分類、画面契約、API契約、auth、env、test、実装開始可否を記録するreport |

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
