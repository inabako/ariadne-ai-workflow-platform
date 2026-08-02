# aiwfctl Runtime Command Map

この文書は、`aiwfctl` の主要commandがどのruntime moduleを呼び、どのartifactを読む・書くのかを図で示します。

詳細なコマンド仕様は `aiwfctl help`、`docs/reference/runtime.md`、各 `docs/workflows/`、`runtime/ctl/ctl_parser.py` を優先します。

## 全体像

```mermaid
flowchart TD
  User[Human / Agent] --> Wrapper[runtime/windows-script/aiwf.cmd or runtime/posix-bash/aiwf.sh]
  Wrapper --> Parser[runtime/ctl/ctl_parser.py]
  Parser --> Dispatch[runtime/ctl/ctl_dispatch.py and adapters]

  subgraph CtlAdapters[runtime/ctl adapters]
    Help[help]
    Env[env]
    Context[context]
    HumanGate[human-gate]
    Trace[trace]
    Workflow[workflow]
    SCM[scm]
    GitHub[github]
    RAG[rag]
    Knowledge[knowledge]
    Review[review]
    Design[design expectation]
    IaC[iac]
    E2E[e2e]
    Doctor[doctor]
    Tools[tools / release / preflight]
    Feedback[self-improvement]
  end

  Dispatch --> Help
  Dispatch --> Env
  Dispatch --> Context
  Dispatch --> HumanGate
  Dispatch --> Trace
  Dispatch --> Workflow
  Dispatch --> SCM
  Dispatch --> GitHub
  Dispatch --> RAG
  Dispatch --> Knowledge
  Dispatch --> Review
  Dispatch --> Design
  Dispatch --> IaC
  Dispatch --> E2E
  Dispatch --> Doctor
  Dispatch --> Tools
  Dispatch --> Feedback

  subgraph RuntimeModules[runtime modules]
    Registry[runtime/common/registry_store.py]
    ContextFirst[runtime/workflow/context_first.py]
    WorkflowModules[runtime/workflow/*]
    SCMModules[runtime/scm/*]
    GitHubModules[runtime/github/*]
    RAGModules[runtime/rag/*]
    ReviewModules[runtime/review/*]
    DesignModules[runtime/design/expectation/*]
    TestingModules[runtime/testing/*]
    IaCModules[runtime/workflow/iac_template.py and kubernetes_runtime.py]
    Observability[runtime/observability/*]
    Maintenance[runtime/tools and runtime/release]
  end

  Help --> Registry
  Env --> Registry
  Context --> ContextFirst
  HumanGate --> Registry
  Trace --> Observability
  Workflow --> WorkflowModules
  SCM --> SCMModules
  GitHub --> GitHubModules
  RAG --> RAGModules
  Knowledge --> RAGModules
  Review --> ReviewModules
  Design --> DesignModules
  IaC --> IaCModules
  E2E --> TestingModules
  Doctor --> WorkflowModules
  Tools --> Maintenance
  Feedback --> WorkflowModules

  Observability --> RuntimeLog[logs/runtime/runtime-events.log]
```

## Command群と主な入出力

| Command | 主なruntime module | 主に読むもの | 主に書くもの |
| --- | --- | --- | --- |
| `aiwfctl help` | `runtime/ctl/ctl_help.py`, `runtime/common/registry_store.py` | `db/registries/registry.duckdb`, `templates/registries/*.json` | `work/help/ai-workflow-help.md` |
| `aiwfctl env` | `runtime/ctl/ctl.py`, registry store | environment profiles registry | `work/<work-id>/context/environment-selection.json`, `context-manifest.json` |
| `aiwfctl context` | `runtime/workflow/context_first.py`, dispatcher context | Dispatcher input, existing context | `workflow-selection.json`, `tool-selection.json`, `runtime-context.json`, `execution-plan.json`, `context-manifest.json` |
| `aiwfctl human-gate` | `runtime/ctl/ctl_human_gate_adapter.py`, registry store | human gate registry | Human Gate check result |
| `aiwfctl trace` | `runtime/observability/logger.py` | `logs/runtime/active-trace.json` | `active-trace.json`, `runtime-events.log` |
| `aiwfctl intake` | `runtime/intake/intake_requirements.py` | `work/requirements/` | `work/<receipt-id>/context/*`, initial artifact index |
| `aiwfctl workflow` | `runtime/workflow/*` | work context, workflow-specific inputs | process report, workflow state, docs-sync / knowledge-capture artifacts |
| `aiwfctl scm` | `runtime/scm/*` | requirements, repository state, Git settings | `scm-state.json`, comparison report, branch / commit / push record |
| `aiwfctl github` | `runtime/github/*` | `scm-state.json`, Issue / PR body input | Issue draft, Pull Request draft, approved GitHub mutation result |
| `aiwfctl rag` | `runtime/rag/*` | RAG source Markdown / JSON, indexes | normalized, chunks, optimized-chunks, indexes, embeddings, retrieval artifacts |
| `aiwfctl knowledge` | `runtime/rag/duckdb_store.py`, source repo helpers | optimized RAG JSON source | `db/rag/ariadne-knowledge.duckdb`, context JSON, reference evidence |
| `aiwfctl review` | `runtime/review/*` | Review Packet, evidence, changed files | Review Council session, handoff, finding, issue, evidence gate, verdict, knowledge capture |
| `aiwfctl design expectation` | `runtime/design/expectation/*` | requirement, usage context, candidates, Review Council feedback | expectation artifacts, comparison report, selected design, contracts, verification, feedback |
| `aiwfctl iac deployment` | `runtime/workflow/iac_deployment_runtime.py` | requirement, design, app runtime state, deployment assumptions | app runtime assessment, deployment contract, IaC deployment gap report |
| `aiwfctl iac kubernetes` | `runtime/workflow/kubernetes_runtime.py` | requirement, Kubernetes/k3s target, image, port, manifest gap | compatibility assessment, gap report, manifest scaffold, dry-run evidence, integration E2E plan |
| `aiwfctl e2e` | `runtime/testing/e2e_runtime.py` | test objective, test contract, test plan, Stub, run result, observation, verification, trace id, Review Council / SCM hints | E2E / integration plan, verification contract, readiness, run result, observation, verification, Review Council bridge, explanation, fix loop |
| `aiwfctl doctor` | `runtime/workflow/workflow_doctor.py` | repository layout, registry, docs, tests, generated read models | doctor report, optional repairs |
| `aiwfctl self-improvement` | self-improvement adapter / workflow helpers | runtime log, feedback input, human review | `work/feedback/*`, Issue body, evidence scaffold |
| `aiwfctl tools` / `release` / `preflight` | runtime maintenance modules | repo files, release docs, local tools | audit report, release manifest, preflight result |

## Context First Commands

```mermaid
flowchart TD
  Env[aiwfctl env select] --> EnvCtx[environment-selection.json]
  Ctx[aiwfctl context init] --> WorkflowSel[workflow-selection.json]
  Ctx --> ToolSel[tool-selection.json]
  Ctx --> RuntimeCtx[runtime-context.json]
  Ctx --> ExecPlan[execution-plan.json]

  EnvCtx --> Manifest[context-manifest.json]
  WorkflowSel --> Manifest
  ToolSel --> Manifest
  RuntimeCtx --> Manifest
  ExecPlan --> Manifest

  Manifest --> Workflow[workflow command]
  Workflow --> WorkState[workflow-specific state]
  WorkState --> Manifest
```

Context First系commandは、後続Workflowが環境、tool、runtime、次commandを推測しないための標準入力を作ります。

## RAG / Knowledge Commands

```mermaid
flowchart TD
  RagBuild[aiwfctl rag build] --> Normalize[normalize]
  Normalize --> Chunk[chunk]
  Chunk --> Optimize[optimize]
  Optimize --> Index[index]
  Optimize --> Embed[embed]
  Index --> RagRun[rag-build-run-latest.json]
  Embed --> RagRun

  RagLoad[aiwfctl rag load] --> DispatchPlan[rag-dispatch-plan.json]
  DispatchPlan --> Retrieve[aiwfctl rag retrieve]
  Retrieve --> ContextPack[rag-context-pack.json]
  ContextPack --> LoadDispatch[rag-load-dispatch.json]

  Knowledge[aiwfctl knowledge rebuild / migrate] --> DuckDB[db/rag/ariadne-knowledge.duckdb]
  DuckDB --> KnowledgeSearch[knowledge search / export-context]
  DuckDB --> RagLoad
```

`aiwfctl rag` はfile-based RAG artifactを扱い、`aiwfctl knowledge` はDuckDB read modelへの投影と検索を扱います。
DuckDBはsource of truthではなく、RAG sourceから再生成できるread modelです。

## Review / Design Commands

```mermaid
flowchart TD
  DesignInit[design expectation init] --> Expectations[expectation-set / weights / critical]
  DesignInit --> Candidates[design-candidates]
  Candidates --> Feasibility[feasibility-report]
  Expectations --> Compare[compare / multi-axis / trade-off]
  Feasibility --> Compare
  Compare --> Gate[design expectation gate]
  Gate --> Refine[refine selected design]
  Refine --> Contracts[interaction-contracts]
  Contracts --> Verify[expectation-verification]
  Verify --> Feedback[expectation-feedback]

  Compare --> ReviewDispatch[design expectation dispatch]
  ReviewDispatch --> ReviewStart[review start / handoff]
  ReviewStart --> Findings[review add-finding / draft-findings]
  Findings --> EvidenceGate[review evidence-gate]
  EvidenceGate --> Verdict[review verdict]
  Verdict --> CouncilSync[design expectation council-sync]
  CouncilSync --> Compare
```

Expectation-Driven Design と Review Council は、Human Gate前の判断材料を構造化するために接続します。
レビュー結果は比較reportへ戻し、blocking issue が残る場合は選択済みデザインへ進めません。

## E2E / Integration Test Commands

```mermaid
flowchart TD
  Plan[aiwfctl e2e plan] --> TestPlan[test-specifications/e2e-test-plan.json]
  TestPlan --> Scaffold[aiwfctl e2e contract scaffold]
  Scaffold --> Contract[aiwfctl e2e contract]
  TestPlan --> Contract
  Contract --> TestContract[test-specifications/e2e-test-contract.json]
  TestContract --> Readiness[aiwfctl e2e readiness]
  Readiness --> Ready{ready?}
  Ready -- no --> Blockers[test-evidence/e2e-test/readiness.json]
  Ready -- yes --> Run[aiwfctl e2e run]
  Run --> RunResult[test-evidence/e2e-test/run-result.json]
  RunResult --> Observe[aiwfctl e2e observe]
  Observe --> Observation[test-evidence/e2e-test/observation.json]
  Observation --> Verify[aiwfctl e2e verify]
  Verify --> Verification[test-evidence/e2e-test/verification.json]
  Verification --> ReviewBridge[aiwfctl e2e review-plan]
  ReviewBridge --> ReviewPlan[test-evidence/e2e-test/review-plan.json and md]
  ReviewPlan --> Council[aiwfctl review plan / evidence-gate]
  ReviewPlan --> Coverage[aiwfctl e2e coverage]
  Coverage --> CoverageEvidence[test-evidence/e2e-test/coverage.json and md]
  Verification --> Explain[aiwfctl e2e explain]
  Explain --> Explanation[test-evidence/e2e-test/explanation.md]
  CoverageEvidence --> FinalGate[aiwfctl e2e final-gate]
  Explanation --> FinalGate
  FinalGate --> FinalGateEvidence[test-evidence/e2e-test/human-final-gate.json and md]
  FinalGateEvidence --> EvidencePackage[aiwfctl e2e evidence-package]
  EvidencePackage --> EvidencePackageArtifact[test-evidence/e2e-test/evidence-package.json and md]
  Verification --> Loop[aiwfctl e2e loop]
  RunResult --> Loop
  Loop --> LoopArtifact[test-evidence/e2e-test/loop.json and loop.md]
  LoopArtifact --> Trace[aiwfctl trace show --problems]
  LoopArtifact --> ReviewPlan[aiwfctl review plan]
  LoopArtifact --> SCMCompare[aiwfctl scm compare]
  LoopArtifact --> SCMCommit[aiwfctl scm commit --dry-run]
  LoopArtifact --> Retest[Retest commands]
  Retest --> Run
```

`aiwfctl e2e` は、結合試験とE2Eテストを同じruntimeで扱います。`--test-kind integration` を指定した場合は、`integration-test-plan.*` と `test-evidence/integration-test/` に保存します。

## Kubernetes / k3s IaC Commands

```mermaid
flowchart TD
  Prepare[aiwfctl iac prepare] --> AppAssess[aiwfctl iac deployment assess]
  AppAssess --> AppAssessment[context/iac-app-runtime-assessment.json]
  AppAssessment --> ContractCmd[aiwfctl iac deployment contract]
  ContractCmd --> Contract[context/iac-deployment-contract.json]
  Contract --> AppGap[aiwfctl iac deployment gap-report]
  AppGap --> AppGapReport[process-report/iac-deployment-gap-report.json and md]
  AppGapReport --> Assess[aiwfctl iac kubernetes assess]
  Assess --> Assessment[context/kubernetes-compatibility-assessment.json]
  Assessment --> Gap[aiwfctl iac kubernetes gap-report]
  Gap --> GapReport[process-report/kubernetes-gap-report.json and md]
  GapReport --> Generate[aiwfctl iac kubernetes generate]
  Generate --> Manifests[implementation/kubernetes/manifests]
  Manifests --> DryRun[aiwfctl iac kubernetes dry-run]
  DryRun --> DryRunEvidence[test-evidence/kubernetes/dry-run.json and md]
  DryRunEvidence --> E2EPlan[aiwfctl iac kubernetes e2e-plan]
  E2EPlan --> IntegrationPlan[test-specifications/integration-test-plan.json]
  IntegrationPlan --> E2ERun[aiwfctl e2e run --test-kind integration]
  E2ERun --> Evidence[aiwfctl iac kubernetes evidence]
```

`aiwfctl iac kubernetes` は実クラスタへ適用しません。manifest scaffold と dry-run evidence を残し、E2E / integration runtime に渡すための準備 runtime です。

## Observability Boundary

```mermaid
flowchart TD
  Command[any aiwfctl command] --> Started[runtime_command_started]
  Started --> Completed{completed or failed}
  Completed --> Log[logs/runtime/runtime-events.log]
  TraceState[logs/runtime/active-trace.json] --> Command
  Log --> Feedback[self-improvement create-feedback]
  Log --> Evidence[runtime evidence / process report]
```

Runtime Event Log は全commandの観測sourceです。
正式な判断材料として残す場合は、Feedback report、Review Council artifact、test evidence、process reportへ昇格させます。
