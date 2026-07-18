# Workflow Flowcharts

各AI workflowの動作イメージを掴むためのMermaid式flowchartです。

詳細手順は `docs/workflows/` と `skills/<skill-name>/SKILL.md` を優先します。

## Requirement Discovery

```mermaid
flowchart TD
  A[Draft requirement bullets] --> B[Inspect draft]
  B --> C[Noise Reduction Phase]
  C --> D{Readiness BLOCK?}
  D -- yes --> E[Human Interview sheet]
  E --> F[Ask human questions]
  F --> G[Review answers]
  D -- no --> H{Blocking clarification?}
  H -- yes --> F
  H -- no --> G
  G --> I{Knowledge gap?}
  I -- yes --> J[Internal RAG / External Web RAG]
  J --> K[Specialist QA support if needed]
  I -- no --> K
  K --> L[Requirement review draft]
  L --> M{Human OK?}
  M -- no --> F
  M -- yes --> N[Save completed requirement]
```

## Ariadne New System

```mermaid
flowchart TD
  A[Completed requirement] --> B[Intake / repository sync]
  B --> C[Issue draft / create]
  C --> D[Create linked issue branch]
  D --> E[RAG load]
  E --> F[Intent / operational context]
  F --> G[Hazard and safety requirements]
  G --> H[Architecture]
  H --> I[Runtime / network / deployment design]
  I --> J[Test strategy]
  J --> K{PyQt / Qt GUI?}
  K -- yes --> L[QTest source plan]
  K -- no --> M{Web SVG?}
  L --> M
  M -- yes --> N[Web SVG Layout Mode]
  M -- no --> O[Implementation]
  N --> O
  O --> P[Integration / bench test]
  P --> Q[Limited field test]
  Q --> R[Release / handover]
```

## Ariadne New System + Realtime IaC

```mermaid
flowchart TD
  A[Completed requirement] --> B[New system workflow]
  B --> C[Intent / safety / architecture]
  C --> D[Runtime / network / deployment design]
  D --> E[Shared Artifacts generation]
  E --> F[Requirements]
  E --> G[Communication specification]
  E --> H[Port definition]
  E --> I[Network boundary definition]
  E --> J[ADR]
  E --> K[Software inventory]
  F --> L[Shared Artifact Validator]
  G --> L
  H --> L
  I --> L
  J --> L
  K --> L
  L --> M{Validation judgment}
  M -- fail --> N[Open questions / return to design]
  N --> D
  M -- conditional-pass --> O{Human approves conditions?}
  O -- no --> N
  O -- yes --> P[Realtime IaC handoff]
  M -- pass --> P
  P --> Q[Realtime IaC workflow]
  Q --> R[IaC design / generation / validation / docs]
```

## Ariadne Feature Maintenance

```mermaid
flowchart TD
  A[Completed requirement or incident] --> B[Intake / repository sync]
  B --> C[Issue draft / create]
  C --> D[Create linked issue branch]
  D --> E[Current state capture]
  E --> F[Impact analysis]
  F --> G[Specialist review if needed]
  G --> H[Risk classification]
  H --> I[Change design]
  I --> J[Test plan]
  J --> K{PyQt / Qt GUI?}
  K -- yes --> L[QTest source plan]
  K -- no --> M{Web SVG?}
  L --> M
  M -- yes --> N[Web SVG Layout Mode]
  M -- no --> O[Implementation]
  N --> O
  O --> P[Verification]
  P --> Q[Deployment plan]
  Q --> R[Post-change observation]
```

## Corrective Action Report

```mermaid
flowchart TD
  A[Target repository / branch] --> B[Read-only inspection]
  B --> C[Internal RAG load]
  C --> D{Knowledge gap?}
  D -- yes --> E[External Web RAG dispatch]
  D -- no --> F[Findings with repo evidence]
  E --> G[Specialist review if needed]
  G --> F
  F --> H[Corrective action report]
  H --> I[RAG capture candidates]
```

## Realtime IaC

```mermaid
flowchart TD
  A[Completed requirement document] --> B[Pre-development preparation]
  B --> C{Repository mode?}
  C -- existing --> D[Repository sync / comparison]
  D --> E[Issue draft / create]
  E --> F1[Create linked issue branch]
  C -- precreated-new --> N1[Generate local bootstrap workspace]
  N1 --> N2[Confirm GitHub repository exists]
  N2 --> N4[Initial commit and branch push]
  N4 --> N5[Issue draft / create]
  N5 --> N6[Create linked issue branch]
  F1 --> RAG[RAG load]
  N6 --> RAG
  RAG --> F{Required shared artifacts present?}
  F -- no --> G[open-questions.md and stop]
  F -- yes --> H[Requirements organization]
  H --> I[Network / security design]
  I --> J[Runtime design]
  J --> K[Observability design]
  K --> L[IaC implementation]
  L --> M[Security review]
  M --> N{High / critical finding?}
  N -- yes --> I
  N -- no --> O[Docker Desktop validation]
  O --> P[Linux runtime validation]
  P --> Q[Integration validation]
  Q --> R[Documentation and handoff]
```

## Corrective Action Fix

```mermaid
flowchart TD
  A[Target repository / branch] --> B[Base work checkout]
  B --> C[Corrective action report]
  C --> D[RAG build / load]
  D --> E[External Web RAG if needed]
  E --> F[Specialist review if needed]
  F --> G[Issue title prefix and Issue draft]
  G --> H{Human approves Issue?}
  H -- no --> G
  H -- yes --> I[Create GitHub Issue]
  I --> J[Create linked issue branch]
  J --> K[Implement fix]
  K --> L[Test specification]
  L --> M{PyQt / Qt GUI?}
  M -- yes --> N[Create QTest integration sources]
  M -- no --> O[Unit / integration tests]
  N --> O
  O --> P{Web SVG?}
  P -- yes --> Q[Web SVG Layout Mode]
  P -- no --> R[Human startup / integration gate]
  Q --> R
  R --> S[Knowledge capture / PR materials]
  S --> T[Push issue branch]
  T --> U[Open PR to develop]
```

## Docs Sync

```mermaid
flowchart TD
  A[Target repository / branch] --> B[Docs drift analysis JSON]
  B --> C[Issue body from JSON]
  C --> D{Human approves Issue?}
  D -- no --> B
  D -- yes --> E[Create GitHub Issue]
  E --> F[Create linked issue branch]
  F --> G[Docs-only update]
  G --> H[Commit / push]
  H --> I[Knowledge capture candidates]
```

## GitHub Knowledge Maintenance

```mermaid
flowchart TD
  A[Target repository / scan mode / repair mode] --> B[Initialize work context]
  B --> C[GitHub metadata collection plan]
  C --> D[Read GitHub Issues / PRs / comments / releases]
  D --> E{GitHub CLI / API evidence enough?}
  E -- no --> F{Human approves clone?}
  F -- no --> G[Record open question and stop]
  F -- yes --> H[Clone for approved read-only analysis]
  E -- yes --> I[Knowledge asset discovery]
  H --> I
  I --> J[Intent / scope / decision / maintenance knowledge]
  J --> K[Narrative analysis]
  K --> L[Issue -> PR -> Review -> Comment -> Docs consistency]
  L --> M[Repair proposals]
  M --> N[Human Review]
  N --> O{Approved GitHub sync actions?}
  O -- no --> P[Keep proposal / update analysis JSON]
  P --> M
  O -- yes --> Q[GitHub documentation sync]
  Q --> R[Issue / PR edit or comment]
  R --> S[Knowledge DB candidates]
  S --> T{RAG output approved?}
  T -- no --> U[Keep RAG candidate in work report]
  T -- yes --> V[Publish approved RAG candidate]
```

## VSCode Environment

```mermaid
flowchart TD
  A[Target workspace] --> B[Workspace requirements]
  B --> C[Shared artifact validation]
  C --> D{Validation judgment}
  D -- fail --> E[open-questions.md]
  E --> B
  D -- conditional-pass --> F{Human approves conditions?}
  F -- no --> E
  F -- yes --> G[VSCode design]
  D -- pass --> G
  G --> H[Terminal design]
  H --> I[Environment preflight]
  I --> J[Implement .vscode files]
  J --> K[Workspace tests and evidence]
  K --> L[Setup and troubleshooting docs]
```

## Knowledge Capture

```mermaid
flowchart TD
  A[Completed issue work] --> B[Generate PR materials]
  B --> C[Add Mermaid sequence diagram]
  C --> D[Confirm docs evidence]
  D --> E{Evidence complete?}
  E -- no --> F[Stop and report missing evidence]
  E -- yes --> G[Push issue branch]
  G --> H[Open PR to develop]
  H --> I[RAG / docs candidates]
  I --> J[Archive readiness]
```

## RAG Build / Load

```mermaid
flowchart TD
  A[Markdown source reports] --> B[Normalize JSON]
  B --> C[Chunk documents]
  C --> D[Build JSONL indexes]
  D --> E[Local embeddings]
  E --> F[RAG dispatcher]
  F --> G[Context packs]
  G --> H[Development / review workflow]
```

## External Web RAG

```mermaid
flowchart TD
  A[Knowledge gap] --> B[knowledge-sources.md]
  B --> C[External Web Source Reviewer]
  C --> D[Claims / metadata / verification notes]
  D --> E[work/db/ariadne-knowledge-platform/rag/external-web category files]
  E --> F[External Web RAG Dispatcher]
  F --> G[Specialist review]
  G --> H[Trusted external knowledge record]
  H --> I[Internal RAG candidate after approval]
```
