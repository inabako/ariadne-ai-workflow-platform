---
language: ja-JP
---

# Ariadne Review Council Runtime

Review Council Runtime は、Specialist Review の結果を「読めるMarkdown」だけで終わらせず、Runtime が判定できる Review Packet、Finding、Review Issue、Verdict として扱うための共通機能です。

## Purpose

目的は、レビュー工程を次工程へ渡せる検査済みバトンにすることです。

- Review Packet でレビュー対象、Intent、要求、変更ファイル、Guardrails、Evidence、必要Reviewerを固定する。
- Specialist Agent の指摘を Finding Contract に正規化する。
- 重複または関連する Finding を Review Issue に集約する。
- Verdict Policy で `APPROVED` / `APPROVED_WITH_RISK` / `CHANGES_REQUIRED` / `HUMAN_DECISION_REQUIRED` / `REJECTED` を判定する。
- Human Check、Evidence、Runtime log、Knowledge Capture へ後続接続できる形で保存する。

## MVP Scope

v0.0.2 の初期Runtimeでは、LangGraph orchestration や自動Reviewer実行は入れません。

今回の責務は次に限定します。

- `runtime/review` に共通contract、永続化、issue集約、verdict policyを持つ。
- `aiwfctl review plan` で必要Reviewerと選定理由を事前に記録できる。
- `aiwfctl review start` から review session を作成・確認できる。
- `aiwfctl review handoff` でReviewer別のhandoff packetを作成できる。
- `aiwfctl review orchestrate` で LangGraph orchestration の node 状態と次アクションを記録できる。
- `aiwfctl review next-action` で担当者が次に実行する1手を取り出せる。
- `aiwfctl review run-specialist` でSpecialist Reviewer Agent向けの実行パケットを作成できる。
- 構造化findingを登録できる。
- challenge round、reinspection、evidence gateをsessionへ保存できる。
- blocking finding、未完了reviewer、未検証evidence、challenge未完了、counterexampleを最終判定で止める。

## Review Planning

Review Council Runtime は、実装対象の Intent、変更ファイル、Evidence、Guardrails、既知制約をもとに必要Reviewerを選定します。

Reviewer選定は、専門Agentを即時実行するためではなく、レビュー責務を曖昧にしないための計画成果物です。セキュリティ、Runtime、Network、Deployment、Safety、Observability、Testing などの観点を先に固定し、必要であれば人間がReviewerを追加できます。

この段階で作成される成果物は、後続の `review start` と `review handoff` の入力になります。

## Orchestration

`review orchestrate` は、Specialist Agent を勝手に起動するコマンドではありません。

Review Council session を読み取り、LangGraph adapter が持つ node graph に沿って現在地を評価します。結果として、Reviewer finding が不足している場合は `add-finding`、blocking issue が残る場合は `reinspect`、challenge が未完了なら `challenge`、evidence が未検証なら `evidence-gate`、判定可能なら `verdict`、verdict後は `capture-knowledge` を次アクションとして提示します。

これにより、レビュー工程はバトン方式でも、将来のAgent並列実行でも同じRuntime状態を共有できます。

LangGraph package が利用可能な環境では `StateGraph.compile().invoke()` で実node遷移を実行し、`execution_mode: langgraph` と `graph_execution.trace` を保存します。
未導入または実行失敗時は `execution_mode: runtime-runbook` へfallbackし、同じReview Council contractで状態評価を継続します。
これにより、依存関係の有無でFinding、Issue、Verdictの契約が変わらないようにします。

## Summary Export

`review summary` は、Review Council sessionの現在地をJSON/Markdownでexportします。
正式Verdict前でも使用でき、Reviewer進捗、Finding候補数、正式Finding、Review Issue、Evidence Gate、Challenge、Verdict、次アクションを1つのsnapshotとして残します。

このsummaryは次の用途に使います。
- Human Gate前に、レビュー状況と残ブロッカーを短く共有する。
- 担当Agent間のhandoffで、session全体ではなく確認に必要な要点だけを渡す。
- Knowledge/RAG吸収前に、どのartifactを判断材料にしたかを追えるようにする。

## Human Gate

`review human-gate` は、Review Councilの人間判断を既存のHuman Gate registry方針に沿って記録します。
gate定義は `human-gate` runtimeと同じ `approved_value` を使い、Review Council専用gateがregistry未登録の場合はruntime内のdefault gateを使います。

主なdefault gateは次の通りです。
- `review-council-final-verdict`: 最終判定を人間が確認する。
- `review-council-risk-acceptance`: non-blocking riskを承認し、`APPROVED_WITH_RISK` の判断材料にする。
- `review-council-counterexample`: counterexampleが残る場合の人間判断を残す。

## Specialist Agent Connection

`review run-specialist` は、Specialist Reviewer Agent を無承認で自動実行するコマンドではありません。

Reviewer名から `.github/agents/` 配下のpromptを選び、Review Packet、handoff packet、期待されるreview report、finding登録commandを1つの実行パケットにまとめます。これにより担当Agentまたは人間は、同じ入力と同じ出力contractで専門レビューを開始できます。

`review next-action` は `review orchestrate` の結果を運用向けに整えます。missing reviewer がある場合は、直接 `review run-specialist --reviewer <reviewer>` を次アクションとして提示します。

## Finding Draft Extraction

`review draft-findings` は、Specialist review reportを読み取り、正式登録前のFinding候補をJSON/Markdownで保存します。
このコマンドは `session.findings` には追加しません。抽出結果は人間または担当Agentが確認し、必要なものだけ `registration_command` または `review add-finding` で正式登録します。

主な用途は次の通りです。
- Specialist Agentの自由記述レポートをReview CouncilのFinding contractへ寄せる。
- severity / verdict / evidence / required tests / requested actionを登録前に可視化する。
- 誤抽出や過剰な指摘をVerdict Policyに混ぜず、確認可能なドラフトとして止める。

## Challenge And Reinspection

`review challenge` は、対象issueとfindingを固定し、反証確認の質問と counterexample check を `challenge_plan` として保存します。

`review reinspect` は、対象findingの前回status、関連Review Issue、再検査evidenceの存在確認を保存します。これにより、単なる「確認済み」ではなく、どの指摘をどの証跡で再検査したかが残ります。

## Evidence Gate

`review evidence-gate` は、Reviewer evidence、required tests、Review Council自身のartifactを分けて検査します。

- `evidence_results`: finding / packet 由来のevidence pathごとの存在、file判定、size
- `missing_required_tests`: required test文言がtest specificationに見つからない場合の不足一覧
- `artifact_checks`: session、report、orchestration、specialist runなどReview Council artifactの存在確認
- `missing_artifacts`: Review Council artifactが欠落した場合の不足一覧

## Specialist Agent Execution

`review run-specialist` は Specialist Agent を直接起動せず、reviewer別の実行packetを作成します。
`review execute-specialist` は、そのpacketを入力として承認済みのローカルAgent commandを実行します。
実行には `--human-check approved` が必要です。commandは `--agent-command` または `ARIADNE_SPECIALIST_AGENT_COMMAND` で指定します。

利用できる主なplaceholderは `{packet_report}` / `{packet_report_q}`、`{packet_json}` / `{packet_json_q}`、`{prompt}` / `{prompt_q}`、`{handoff}` / `{handoff_q}`、`{output}` / `{output_q}`、`{reviewer}`、`{review_id}`、`{work_id}`、`{agent_id}` です。
stdout/stderrは `work/<work-id>/process-report/review-council/` に保存され、Agentがreportを直接書かなかった場合はstdoutをspecialist review reportとして保存します。
成功時は既定で `draft-findings` まで実行し、Finding候補を登録前のdraftとして残します。

## Knowledge Capture

`review capture-knowledge` は、Review Council session、report、orchestration、specialist run、evidence linkをRAG/Knowledge候補として整理します。

これはRAG登録そのものではなく、後続のKnowledge Capture AgentやRAG buildが扱うための候補化です。

`review rag-build` は、`capture-knowledge` の候補を読み取り、既存のfile-based RAG buildが扱えるMarkdown sourceへ変換します。
sourceは `work/db/<knowledge-repo>/rag/review-council/<work-id>/<review-id>/` に保存されます。
通常実行ではbridge manifestと再現可能な `aiwfctl rag build` commandだけを作成し、`--run` を明示した場合だけ既存RAG build pipelineを呼び出します。
これにより、Review Councilの判定、Finding、Human Gate、Evidence Gate、再検査結果を、後続Agentが検索可能なKnowledgeへ接続できます。

## CLI

```powershell
.\runtime\windows-script\aiwf.cmd ctl review plan `
  --work-id issue-123 `
  --intent "runtime変更を専門reviewに通す" `
  --changed-file runtime/review/council.py `
  --evidence logs/runtime/runtime-events.log

.\runtime\windows-script\aiwf.cmd ctl review start `
  --work-id issue-123 `
  --intent "runtime変更を専門reviewに通す" `
  --reviewer security `
  --reviewer runtime

.\runtime\windows-script\aiwf.cmd ctl review handoff `
  --review-id review-20260723_120000

.\runtime\windows-script\aiwf.cmd ctl review orchestrate `
  --review-id review-20260723_120000

.\runtime\windows-script\aiwf.cmd ctl review next-action `
  --review-id review-20260723_120000

.\runtime\windows-script\aiwf.cmd ctl review summary `
  --review-id review-20260723_120000

.\runtime\windows-script\aiwf.cmd ctl review human-gate `
  --review-id review-20260723_120000 `
  --gate review-council-final-verdict `
  --human-check approved `
  --reviewer Human `
  --reason "summary and evidence were reviewed"

.\runtime\windows-script\aiwf.cmd ctl review run-specialist `
  --review-id review-20260723_120000 `
  --reviewer security

.\runtime\windows-script\aiwf.cmd ctl review execute-specialist `
  --review-id review-20260723_120000 `
  --reviewer security `
  --human-check approved `
  --agent-command "local-agent --prompt {prompt_q} --packet {packet_report_q} --output {output_q}"

.\runtime\windows-script\aiwf.cmd ctl review draft-findings `
  --review-id review-20260723_120000 `
  --reviewer security `
  --report work/issue-123/process-report/specialist-review-security.md

.\runtime\windows-script\aiwf.cmd ctl review add-finding `
  --review-id review-20260723_120000 `
  --reviewer security `
  --category security `
  --severity high `
  --claim "remote command path lacks authorization evidence" `
  --verdict changes-required `
  --requested-action "authorization evidence and tests are required"

.\runtime\windows-script\aiwf.cmd ctl review status --review-id review-20260723_120000
.\runtime\windows-script\aiwf.cmd ctl review issues --review-id review-20260723_120000
.\runtime\windows-script\aiwf.cmd ctl review challenge `
  --review-id review-20260723_120000 `
  --challenger runtime-quality `
  --summary "no counterexample found"

.\runtime\windows-script\aiwf.cmd ctl review evidence-gate `
  --review-id review-20260723_120000

.\runtime\windows-script\aiwf.cmd ctl review reinspect `
  --review-id review-20260723_120000 `
  --finding-id FND-001 `
  --status verified `
  --reviewer security `
  --summary "required evidence was added"

.\runtime\windows-script\aiwf.cmd ctl review verdict --review-id review-20260723_120000

.\runtime\windows-script\aiwf.cmd ctl review capture-knowledge `
  --review-id review-20260723_120000

.\runtime\windows-script\aiwf.cmd ctl review rag-build `
  --review-id review-20260723_120000
```

## Storage

Review session は作業ID配下に保存します。

```text
work/<work-id>/context/review-council/<review-id>.json
work/<work-id>/context/review-council/index.json
work/<work-id>/process-report/review-council-plan-<timestamp>.json
work/<work-id>/process-report/review-council-plan-<timestamp>.md
work/<work-id>/process-report/review-council-<review-id>.md
work/<work-id>/process-report/review-council/reviewer-packet-<reviewer>.md
work/<work-id>/process-report/review-council/orchestration-<run-id>.json
work/<work-id>/process-report/review-council/orchestration-<run-id>.md
work/<work-id>/process-report/review-council/summary-<timestamp>.json
work/<work-id>/process-report/review-council/summary-<timestamp>.md
work/<work-id>/process-report/review-council/human-gate-<gate-id>-<timestamp>.json
work/<work-id>/process-report/review-council/human-gate-<gate-id>-<timestamp>.md
work/<work-id>/process-report/review-council/specialist-run-<reviewer>.json
work/<work-id>/process-report/review-council/specialist-run-<reviewer>.md
work/<work-id>/process-report/review-council/specialist-execution-<reviewer>-<timestamp>.json
work/<work-id>/process-report/review-council/specialist-execution-<reviewer>-<timestamp>.md
work/<work-id>/process-report/review-council/specialist-execution-<reviewer>-<timestamp>-stdout.txt
work/<work-id>/process-report/review-council/specialist-execution-<reviewer>-<timestamp>-stderr.txt
work/<work-id>/process-report/review-council/finding-draft-<reviewer>-<timestamp>.json
work/<work-id>/process-report/review-council/finding-draft-<reviewer>-<timestamp>.md
work/<work-id>/process-report/review-council/knowledge-capture-<timestamp>.json
work/<work-id>/process-report/review-council/knowledge-capture-<timestamp>.md
work/<work-id>/process-report/review-council/rag-build-<timestamp>.json
work/<work-id>/process-report/review-council/rag-build-<timestamp>.md
work/db/<knowledge-repo>/rag/review-council/<work-id>/<review-id>/<review-id>.md
```

JSON はRuntime判定用、Markdown は人間がreview経緯を読むためのreportです。

## Verdict Policy

`APPROVED` になるには、少なくとも次を満たす必要があります。

- blocking issue が 0 件
- unresolved high / critical issue が 0 件
- unsupported required claim が 0 件
- missing required reviewer が 0 件
- evidence が検証済み
- challenge round が完了済み
- target revision が Review Packet 固定時点と一致
- challenge round でcounterexampleが残っていない

`APPROVED_WITH_RISK` は、non-blocking risk が残っており、Human Checkでrisk acceptanceが確認された場合にだけ使います。

## LangGraph Adapter

`runtime/review/graph/langgraph_adapter.py` は、Review Councilのorchestration plan と state evaluation を返すadapterです。

Domain層、contract層、verdict policy層からLangGraphを参照しません。LangGraphが未導入でもReview Council Runtimeは動作し、adapterは `available: false` を返します。

LangGraphが利用可能な場合、adapterはReview Council専用の `StateGraph` をcompileし、現在のsession状態に応じて reviewer / reinspection / challenge / evidence / verdict / knowledge capture のnodeへ遷移します。
実際のSpecialist Agent起動は `execute-specialist` の責務であり、LangGraph nodeはRuntime状態と次アクションを決定する制御層に限定します。

## Next Extension

次の段階では、以下を追加します。

- Specialist Agentの並列実行
- Specialist review reportからFindingを補助抽出する仕組み
- Required Tests と test specification / evidence の照合
- Knowledge CaptureへのReview Council artifact連携
