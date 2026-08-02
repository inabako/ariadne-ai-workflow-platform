# Human Gate / Side Effect Map

この文書は、人間承認が必要な副作用操作と、その前後で残すartifactを図で示します。

詳細な承認ルールは `docs/reference/human-gates.md`、`docs/reference/operations.md`、`.ariadne/shared/gate-restart-policy.md` を優先します。

## 全体像

```mermaid
flowchart TD
  Intent[Human / Agent intent] --> Runtime[aiwfctl command]
  Runtime --> Detect{Side effect?}
  Detect -- no --> LocalArtifact[Local artifact / report]
  Detect -- yes --> GateLookup[Human Gate Registry lookup]
  GateLookup --> Registry[db/registries/registry.duckdb]
  Registry --> GateDecision{human-check approved?}

  GateDecision -- no --> Stop[Stop / return gate restart]
  Stop --> Restart[gate-restart command / reason]
  Restart --> HumanReview[Human review]
  HumanReview --> Runtime

  GateDecision -- yes --> Execute[Execute approved side effect]
  Execute --> Evidence[Operation evidence]
  Evidence --> Manifest[context-manifest / artifact-index]
  Evidence --> RuntimeLog[logs/runtime/runtime-events.log]
```

## 副作用操作の分類

| Gate ID | 操作 | 主な入口 | 主な証跡 |
| --- | --- | --- | --- |
| `github-issue-create` | GitHub Issue作成 | `aiwfctl github issue --create` | Issue record、Issue body、runtime event |
| `branch-create` | GitHub branch作成 | `aiwfctl scm branch` | branch record、`scm-state.json` |
| `push` | remote push | `aiwfctl scm push --human-check approved` | push record、commit hash、runtime event |
| `pull-request-create` | Pull Request作成 | `aiwfctl github pr --create` | PR title/body、PR record |
| `rag-register` | RAG登録 / rebuild | `aiwfctl rag build`, `aiwfctl knowledge rebuild` | RAG source、build run、DuckDB migration evidence |
| `close-prune` | close archive prune | `aiwfctl close-archive prune --execute` | audit result、prune result |
| `work-delete` | work削除 | `aiwfctl work cleanup-apply` | cleanup-check、cleanup-apply record |
| `tool-install` | tool / package install | `aiwfctl preflight` generated install plan | preflight report、human approval |
| `external-io-test` | 実機 / 外部I/Oテスト | startup / integration workflow | test evidence、human check result |

## GitHub副作用

```mermaid
flowchart TD
  Work[work/issue-id] --> IssueDraft[Issue body draft]
  IssueDraft --> IssueGate{github-issue-create approved?}
  IssueGate -- no --> StopIssue[Stop before GitHub mutation]
  IssueGate -- yes --> Issue[Create GitHub Issue]

  Issue --> BranchGate{branch-create approved?}
  BranchGate -- yes --> Branch[Create feature/issue-number]
  BranchGate -- no --> StopBranch[Stop before branch mutation]

  Branch --> Commit[Semantic commit]
  Commit --> PushGate{push approved?}
  PushGate -- yes --> Push[Push issue branch]
  PushGate -- no --> StopPush[Stop before remote push]

  Push --> PRGate{pull-request-create approved?}
  PRGate -- yes --> PR[Create Pull Request]
  PRGate -- no --> StopPR[Stop before PR mutation]

  Issue --> ScmState[context/scm-state.json]
  Branch --> ScmState
  Push --> PushRecord[process-report push record]
  PR --> PRRecord[process-report PR record]
```

GitHub上の状態を変える操作は、draft / local record を作ってから承認を確認します。
承認なしに Issue、branch、push、Pull Request を作りません。

## Knowledge / Cleanup副作用

```mermaid
flowchart TD
  CompletedWork[Completed work] --> KnowledgeCandidate[Knowledge / RAG candidate]
  KnowledgeCandidate --> RagGate{rag-register approved?}
  RagGate -- no --> KeepCandidate[Keep candidate as review pending]
  RagGate -- yes --> RagSource[Write approved RAG source]
  RagSource --> RagBuild[RAG build / knowledge rebuild]

  CompletedWork --> ClosePrepare[close-archive prepare]
  ClosePrepare --> CloseAudit[close-archive audit]
  CloseAudit --> PruneGate{close-prune approved?}
  PruneGate -- no --> KeepWork[Keep work artifacts]
  PruneGate -- yes --> Prune[Prune generated/source checkout artifacts]

  CompletedWork --> CleanupCheck[work cleanup-check]
  CleanupCheck --> DeleteGate{work-delete approved?}
  DeleteGate -- no --> KeepWork
  DeleteGate -- yes --> CleanupApply[work cleanup-apply]
```

RAG登録やcleanupは、将来のAI判断や証跡保持に影響します。
そのため、承認前は候補・監査結果として止め、承認後にだけ登録・削除します。

## External I/O / Tool Install

```mermaid
flowchart TD
  Preflight[preflight / integration plan] --> Missing{Missing tool or external I/O?}
  Missing -- no --> Continue[Continue workflow]
  Missing -- yes --> Plan[Install list / external test plan]
  Plan --> Gate{tool-install or external-io-test approved?}
  Gate -- no --> Blocked[Stop with reason and resume command]
  Gate -- yes --> Execute[Install or run external I/O test]
  Execute --> Evidence[Test / preflight evidence]
```

ローカル環境変更や外部I/Oは、runtimeが勝手に実行しません。
不足tool、実機、network、camera、field environment は、計画と停止理由を残して人間判断へ渡します。

## Gate Restart

```mermaid
flowchart LR
  Blocked[blocked command] --> Restart[gate_restart]
  Restart --> Reason[restart_reason]
  Restart --> Command[repair_command / resume command]
  Command --> Approved[rerun with --human-check approved]
```

Gateで止まることは失敗ではありません。
停止理由、再開コマンド、必要な承認値を構造化して残すことで、後続Agentや人間が同じ場所から再開できます。
