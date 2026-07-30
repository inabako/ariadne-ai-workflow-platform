# Noise Reduction Phase

Noise Reduction Phase（ノイズ除去フェーズ）は、要件定義段階で人間とAIの認識齟齬を減らすための準備サブフローです。

設計や実装を開始する工程ではありません。未知用語、表記揺れ、資料矛盾、曖昧表現、AIが推測しそうな箇所、業務ルール不足を抽出し、Human Interviewで確認します。

独立したslash commandではありません。主に `/requirement-discovery` の中で、review draft作成前に実行します。

## Activation

次の場合に実行します。

- 草案、要件定義書、設計書、API仕様、ER図、シーケンス図、ADR、業務フローなど、複数資料を読んで要件化する。
- プロジェクト固有用語、略語、社内用語、状態名、DB名、API名、イベント名が多い。
- 一般知識とプロジェクト内の意味が衝突する可能性がある。
- 「適宜」「必要に応じて」「通常」「処理する」「連携する」など曖昧な日本語が多い。
- AIが補完や推測をしそうな箇所がある。

## Flow

```text
Requirement draft intake
  -> collect source documents
  -> analyze document relationships
  -> extract project terms
  -> detect terminology conflicts with general knowledge
  -> detect aliases and notation drift
  -> detect document conflicts
  -> detect ambiguous language
  -> detect AI confusion points
  -> detect missing business rules
  -> create Human Interview sheet
  -> create Project Glossary
  -> create Readiness Report
  -> return PASS / WARNING / BLOCK to requirement-discovery
```

## Output Location

実案件では次へ保存します。

```text
work/requirements/draft/<draft-stem>-noise-reduction/
```

標準成果物:

```text
unknown-words-report.md
terminology-conflict-report.md
terminology-alias-report.md
document-conflict-report.md
ambiguous-language-report.md
ai-confusion-report.md
missing-definition-report.md
human-interview-sheet.md
project-glossary.md
readiness-report.md
```

Templates:

```text
templates/workflows/noise-reduction/
```

## Readiness

| Status | Meaning | Requirement Discovery Handling |
| --- | --- | --- |
| `PASS` | 設計開始可能な理解度。Human Interviewに設計阻害項目がない | review draft作成へ進める |
| `WARNING` | 軽微な確認事項はあるが、明示された条件内で要件reviewへ進める | 未解決項目をOpen Questionsへ残す |
| `BLOCK` | Human Interview完了まで設計・実装・完成版要件化は禁止 | 質問票を人間へ返し、回答後に再評価する |

## Stop Rules

次の場合は `BLOCK` とし、完成版要件定義書を `work/requirements/` へ保存しません。

- Human Interview対象のHigh優先度質問が未回答。
- 用語衝突によりAPI、DB、状態、イベントの意味が決まらない。
- 資料間矛盾によりscope、状態遷移、異常系、rollback、timeout、retryが決まらない。
- AI Confusion Reportに、推測なしでは要件文を書けない項目が残っている。
- Missing Definition Reportに、実装やテスト条件を左右する業務ルール不足が残っている。

## Guardrails

- 推測で補完しない。
- 一般知識でプロジェクト固有用語を上書きしない。
- 不明なことは不明と書く。
- Human Interviewを必ず生成する。
- Project Glossaryを作る。
- 資料矛盾を放置しない。
- Readinessが`BLOCK`の場合、設計・実装工程へ進まない。

## Runtime CLI

Noise Reduction Phaseはruntime CLIでも生成できます。

```powershell
.\runtime\windows-script\aiwf.cmd ctl workflow noise-reduction run `
  --draft work/requirements/draft/<draft-name>.txt
```

CLIは次を生成します。

```text
work/requirements/draft/<draft-stem>-noise-reduction/
  unknown-words-report.md
  terminology-conflict-report.md
  terminology-alias-report.md
  document-conflict-report.md
  ambiguous-language-report.md
  ai-confusion-report.md
  missing-definition-report.md
  human-interview-sheet.md
  project-glossary.md
  readiness-report.md
  context/workflow-state.json
```

`readiness-report.md` が `BLOCK` の場合、Human Interviewへの回答を待ち、要件review draftへ進みません。
