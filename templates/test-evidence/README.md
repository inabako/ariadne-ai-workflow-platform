# Test Evidence Templates

このディレクトリは、テスト証跡の標準フォーマットを格納します。

test evidence は、「テストした」という主張ではなく、「どの条件で、何を実行し、何が観測され、なぜ合格または不合格と判断したか」を残す artifact です。

## Templates

| File | Purpose |
| --- | --- |
| `robotics-test-evidence-template.md` | robotics の unit / integration / simulation / bench / limited-field / rollback test 共通の証跡 |

## Quality Rule

test evidence では、最低限以下を必ず埋めます。

- Test identity
- Requirement / test case traceability
- Repository / branch / commit
- Test environment
- Preconditions
- Steps executed
- Expected result
- Actual result
- Evidence paths
- Pass / fail judgment
- Anomalies and follow-up

safety-critical test では、STOP、communication loss、startup safe state、shutdown safe state の確認結果を必ず記録します。

## Output Location

実案件では以下に保存します。

```text
work/<receipt-id>/test-evidence/
```

生成後は `work/<receipt-id>/context/artifact-index.json` に登録します。
