# Requirement Discovery

箇条書きの草案から、開発workflowへ渡せる完成版の要件定義書を作るworkflowです。

## Command

```text
/requirement-discovery
```

## Input

草案は次の場所に置きます。

```text
work/requirements/draft/
```

例:

```text
work/requirements/draft/localty-gui-smoke-test.txt
```

## Output

人間レビューでOKになった完成版だけを次へ進めます。

```text
work/requirements/<completed-requirements>.md
```

## Flow

1. `work/requirements/draft/` の草案を読む。
2. blocking clarification があれば質問する。
3. [Noise Reduction Phase](noise-reduction-phase.md) を実行し、未知用語、表記揺れ、資料矛盾、曖昧表現、Human Interview、Project Glossary、Readinessを作成する。
4. Readinessが`BLOCK`ならHuman Interviewへ戻り、review draftへ進まない。
5. 知見不足の領域があれば `knowledge gap` として記録する。
6. 必要なら内部RAG contextを補助的に読む。
7. 外部知識が必要なら [External Web RAG](external-web-rag.md) を使う。
8. 専門知識が質問品質や制約整理に影響する場合はSpecialist AgentへQA観点のreviewを渡す。
9. review draftを作る。
10. 人間OK後に `work/requirements/` へ完成版を保存する。

## Noise Reduction Phase

要件review draftを作る前に、Noise Reduction Phaseを実行します。

出力先:

```text
work/requirements/draft/<draft-stem>-noise-reduction/
```

主な成果物:

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

`readiness-report.md` が `BLOCK` の場合、完成版要件定義書を `work/requirements/` へ保存しません。`WARNING` の場合は未解決項目をOpen Questionsへ残します。

## Knowledge Gap Flow

要件を聞いて、知らない領域や判断材料が足りない領域が出た場合は、外部Web RAGの補助フローを使います。

```text
要件を聞く
  -> 知らない領域が出る
  -> rag/external-web/knowledge-sources.md を参照する
  -> 外部Webを精査する
  -> rag/external-web/<category>/ に蓄積する
  -> 要件定義review draftに根拠pathと未確認事項を反映する
```

知見不足の記録先:

```text
work/requirements/draft/<draft-stem>-knowledge-gaps.md
```

外部Web RAGのsource index:

```text
rag/external-web/knowledge-sources.md
```

外部Web RAGは補助contextです。Repository、Target Branch、STOP、communication loss、safety requirements は人間確認なしに確定しません。

## Specialist QA Support

要件定義では、Specialist Agentは要件を確定しません。未知領域に対する質問、制約、risk、test観点を補強します。

review結果は次に保存します。

```text
work/requirements/draft/<draft-stem>-specialist-review-<domain>.md
```

採用した外部Web RAG、採用しなかったclaim、人間確認が必要な項目をreview draftへ反映します。

## Gate

次の項目が不足している場合は、開発workflowへ進めません。

- 対象repository
- target branch
- 変更intent
- safety / rollback / test / evidence の最低限の判断材料
- `Repository Control`

## Next

- 新規systemなら [Robotics New System](robotics-new-system.md)
- 既存systemの変更なら [Robotics Feature Maintenance](robotics-feature-maintenance.md)
