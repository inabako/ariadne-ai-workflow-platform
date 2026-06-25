# Noise Reduction Templates

このdirectoryは、要件定義段階のNoise Reduction Phaseで使う成果物templateを置きます。

保存先:

```text
work/requirements/draft/<draft-stem>-noise-reduction/
```

## Templates

| File | Purpose |
| --- | --- |
| `unknown-words-report-template.md` | 未知用語一覧 |
| `terminology-conflict-report-template.md` | 一般知識との用語衝突一覧 |
| `terminology-alias-report-template.md` | 表記揺れ、略称、同義語候補一覧 |
| `document-conflict-report-template.md` | 資料間矛盾一覧 |
| `ambiguous-language-report-template.md` | 曖昧表現一覧 |
| `ai-confusion-report-template.md` | AIが推測しそうな箇所一覧 |
| `missing-definition-report-template.md` | 不足定義、業務ルール不足一覧 |
| `human-interview-sheet-template.md` | 人間への質問票 |
| `project-glossary-template.md` | プロジェクト用語集 |
| `readiness-report-template.md` | PASS / WARNING / BLOCK判定 |

## Rule

- 推測で補完しません。
- 一般知識でプロジェクト固有定義を上書きしません。
- Human Interviewを必ず作成します。
- `readiness-report.md` が `BLOCK` の場合、要件定義書を完成扱いにしません。
