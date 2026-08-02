# Requirement Discovery

`/requirement-discovery` は、人間が書いた箇条書き草案から、後続の開発workflowへ渡せる完成版の要件定義書を作るworkflowです。

このworkflowは要件定義専用です。実装、Issue作成、branch作成、設計決定は開始しません。

## Command

```text
/requirement-discovery
```

## Input

草案は次へ配置します。

```text
work/requirements/draft/
```

例:

```text
work/requirements/draft/target-system-smoke-test.txt
```

## Optional SDK Program Pre-Analysis

SDKプログラムが要件定義の判断材料になる場合は、次へ配置します。

```text
work/requirements/sdk/
```

このディレクトリが無い、空、解析対象のSDKプログラムファイルが無い、または明示的にskipされた場合は、SDK事前解析をスキップして要件定義を継続します。

解析する場合:

```powershell
aiwfctl sdk analyze --work-id <work-id>
aiwfctl sdk discover --work-id <work-id>
```

出力:

```text
work/<work-id>/reports/sdk-analysis-report.md
work/<work-id>/context/sdk-analysis-context.json
work/<work-id>/context/sdk-files.json
work/<work-id>/requirements/sdk-integration-requirements.md
work/<work-id>/reports/sdk-external-discovery-report.md
work/<work-id>/context/sdk-external-discovery.json
work/<work-id>/requirements/sdk-external-requirements.md
```

When `sdk analyze` writes Knowledge JSON under `work/db/.../rag/jsonized`, it also records cleanup evidence in `artifact-index.json`. After the Knowledge source is absorbed, confirm temporary work cleanup through the generic ctl:

```powershell
.\runtime\windows-script\aiwf.cmd ctl work cleanup-check --work-id <work-id>
.\runtime\windows-script\aiwf.cmd ctl work cleanup-apply --work-id <work-id> --human-check approved
```

`sdk-analysis-context.json` は Context First manifest に `sdk-analysis` として登録されます。`sdk-integration-requirements.md` は要件review draftへ取り込むための追記候補です。

AWS / GCP SDKの場合は、cloud provider、言語、package manager、SDK世代、候補サービス、credential model、region / project要件、local test候補、cloud固有のHuman Checkも整理します。
Stripe SDKの場合は、payment vendor、言語、package manager、候補payment service、API key / webhook signing secret、test mode、idempotency、PCI境界、返金・chargeback・税・通貨などのHuman Checkも整理します。`sdk-files.json` には解析対象ファイルのSHA-256付きinventoryを残します。

`sdk-external-discovery.json` は Context First manifest に `sdk-external-discovery` として登録されます。これは公式docs、package registry、release notes、security advisory、deprecated / unsupported確認のための検索計画・証跡handoffです。外部ページ本文を丸ごと保存しません。

ただし、SDK採用可否、license、vendor lock-in、credential管理、production network利用、cost、deprecated / unsupported SDK、security不明点は人間確認が必要です。SDK解析結果だけで確定しません。

## Output

人間レビューでOKになった完成版だけを次へ保存します。

```text
work/requirements/<completed-requirements>.md
```

## Flow

1. `work/requirements/draft/` の草案を読む。
2. 不足、曖昧、矛盾、Critical項目不足を確認する。
3. [Noise Reduction Phase](noise-reduction-phase.md) を実行し、不明ワード、表記揺れ、資料矛盾、曖昧表現、Human Interview、Project Glossary、Readinessを作成する。
4. Readinessが `BLOCK` の場合はHuman Interviewへ戻り、review draftへ進まない。
5. `work/requirements/sdk/` が存在し解析対象ファイルがある場合は、SDK事前解析と外部関連資料discoveryを実行する。無い場合はスキップする。
6. 知識不足の領域を `knowledge gap` として記録する。
7. 必要なら内部RAG contextを補助的に読む。
8. 外部知識が必要なら [External Web RAG](external-web-rag.md) を使う。
9. 専門知識が質問品質、制約整理、risk、test観点に影響する場合はSpecialist AgentへQA観点のreviewを渡す。
10. 必要な質問を人間へ返す。
11. 人間回答、Noise Reduction出力、SDK解析context、SDK外部discovery context、RAG contextを再確認する。
12. review draftを作る。
13. 人間OK後に `work/requirements/` へ完成版を保存する。

## Noise Reduction Phase

要件review draftを作る前にNoise Reduction Phaseを実行します。

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

要件を読んで、知らない領域や判断材料が足りない領域が出た場合は、外部Web RAGの補助フローを使います。

```text
要件を読む
  -> 知らない領域が出る
  -> work/db/ariadne-knowledge-platform/rag/external-web/knowledge-sources.md を参照する
  -> 外部Webを精査する
  -> work/db/ariadne-knowledge-platform/rag/external-web/<category>/ に蓄積する
  -> 要件定義review draftに根拠pathと未確認事項を反映する
```

知識不足の記録先:

```text
work/requirements/draft/<draft-stem>-knowledge-gaps.md
```

外部Web RAGのsource index:

```text
work/db/ariadne-knowledge-platform/rag/external-web/knowledge-sources.md
```

外部Web RAGは補助contextです。Repository、Target Branch、STOP、Communication loss、Safety requirementsは人間確認なしに確定しません。

## Specialist QA Support

要件定義では、Specialist Agentは要件を確定しません。不明領域に対する質問、制約、risk、test観点を補強します。

review結果は次に保存します。

```text
work/requirements/draft/<draft-stem>-specialist-review-<domain>.md
```

採用した外部Web RAG、採用しなかったclaim、人間確認が必要な項目をreview draftへ反映します。

## Gate

次の項目が不足または曖昧な場合、開発workflowへ進めません。

- 対象repository
- target branch
- 変更intent
- safety / rollback / test / evidence の最低限の判断材料
- `Repository Control`

## Next

- 新規systemなら [Ariadne New System](ariadne-new-system.md)
- 既存対象システムの変更なら [Ariadne Feature Maintenance](ariadne-feature-maintenance.md)
