# Corrective Action Fix

Corrective Action Report を作成し、RAG build/load、GitHub Issue、remote-first branch作成、修正、test、人間確認、pushまで進めるworkflowです。

## Command

```text
/corrective-action-fix <target-repository> <target-branch>
```

例:

```text
/corrective-action-fix localty-system-gui develop
```

## Directory Model

```text
work/<target-branch>/source/repository
work/issue-<issue-number>/source/repository
```

Git branch は次の形式にします。

```text
feature/issue-<issue-number>
```

## Flow

1. `work/<target-branch>` を初期化する。
2. target branchをbase checkoutへ取得する。
3. Corrective Action Reportを作る。
4. environment preflightを実行し、不足toolがあればinstall listを出して止まる。
5. `/rag-build` 相当のpipelineでreportをRAG化する。
6. `/rag-load` で開発前contextを読む。
7. 不明な実装領域があれば外部Web RAGをsupporting referenceとしてdispatchする。
8. 専門知識がIssue scope / 実装方針 / test specificationに影響する場合はSpecialist Agent reviewを実行する。
9. support repository / tool / packageの必要性を確認する。
10. GitHub Issue draftを作る。
11. 人間承認後にGitHub Issueを作成する。
12. GitHub上に `feature/issue-<issue-number>` を作り、`work/issue-<issue-number>` にcloneする。
13. encoding / mojibake gateを確認する。
14. corrective fixを実装する。
15. test specificationとtest evidenceを残す。
16. startup / integration checkとhuman check gateを通す。
17. PR材料とknowledge capture packageを作る。
18. 人間承認後にpushする。

## External Web RAG Support

外部Web RAGは、不明な実装領域や公式仕様確認が必要な箇所のsupporting referenceとして使います。

```text
corrective action report
  -> RAG build/load
  -> external-web RAG dispatch for unknown implementation areas
  -> Issue bodyにsupporting referenceと未確認事項を書く
  -> implementation
  -> tests / evidence
  -> human check
```

使う例:

- Go realtime gateway
- UDP / TCP / QUIC behavior
- NAT traversal
- GStreamer pipeline behavior
- Docker / Windows / Raspberry Pi platform behavior
- Prometheus / OpenTelemetry design

外部WebRAGは、実装方針、test specification、risk checkを補助します。

ただし、採用した挙動はlocal test、integration evidence、human checkで確認します。

## Specialist Review Gate

Corrective Action Fixでは、外部Web RAGを読んだあと、専門知識が実装判断に影響する場合にSpecialist Agent reviewを挟みます。

review対象:

- Issue scope
- implementation plan
- test specification
- safety / security / network / observability review
- startup / integration check plan

review結果は次に保存します。

```text
work/<target-branch>/process-report/specialist-review-<domain>.md
work/issue-<issue-number>/process-report/specialist-review-<domain>.md
```

Specialist Agentは、次を明示します。

- 採用した内部RAG
- 採用した外部Web RAG
- 信じなかった、または条件付きにした外部claim
- current source code / test evidenceとの整合
- 追加すべきtest case
- unresolved QA / human check item

High / critical finding が残る場合、implementationまたはpushへ進めません。

完了後、review結果は [Knowledge Capture](knowledge-capture.md) でRAG候補として抽出します。

## Issue Body Template

Issue body は次の優先順位で選びます。

1. 明示された `--body-file`
2. target repository の `.github/ISSUE_TEMPLATE.md`
3. `runtime/github/issue_manager.py` のfallback本文

target repository templateを使う場合、`Report`、`Target branch`、`Target commit` はworkflow contextから補完します。

## Human Gates

- GitHub Issue 作成
- missing tool のinstall
- startup / integration check
- push
- RAG登録
- archive移動

## Guardrails

- 外部WebRAGは current source code、test evidence、corrective action report、人間承認済みfindingを上書きしません。
- 外部Web由来の修正方針は、test evidenceで確認してから採用します。
- Issue bodyとtest specificationには、外部WebRAGを使った箇所と未確認事項を残します。
- Specialist Agent reviewで採用した外部知識は、どのtest evidenceまたはhuman checkで検証したかを残します。

## Source Skill

```text
skills/corrective-action-fix/SKILL.md
```
