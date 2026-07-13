---
name: realtime-iac
description: Run the realtime-system Infrastructure as Code workflow for target systems, IoT, edge AI, video streaming, remote operation, or realtime gateway infrastructure. Use when the user selects /realtime-iac or asks to design, generate, review, test, and document IaC artifacts such as Docker Compose, systemd, firewall, reverse proxy, TURN/STUN, logrotate, monitoring, or runtime environment configuration.
---

# Realtime IaC

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.github/shared/output-language-policy.md`.

## Slash Command

Use this skill when the user specifies:

```text
/realtime-iac
```

This skill delegates the detailed workflow to:

```text
.github/prompts/realtime-iac.prompt.md
```

## Intake Gate

Before starting design or implementation, run or require the intake harness.

```powershell
uv run --project runtime python runtime/intake/intake_requirements.py --workflow realtime-iac
```

The harness must reject the order when:

- `work/requirements/` has no completed requirement document
- `work/requirements/` has two or more requirement documents
- the requirement document does not contain readable `Repository Control`

Do not treat chat history as a substitute for an accepted requirement document.

## Context First Environment Gate

Before `/realtime-iac` design, generation, Docker Desktop validation, Linux runtime validation, or integration validation, the work directory must have a Docker environment-selection context.

Create or refresh the context:

```powershell
aiwfctl env select docker --work-id <receipt-id>
```

Then verify it:

```powershell
uv run --project runtime python runtime/workflow/context_first.py `
  --work-dir work/<receipt-id> `
  require-environment --environment docker
```

If the context is missing or the selected environment is not `docker`, stop before IaC design and ask the human to select the correct environment. Do not infer Docker availability from chat history, OS name, or prior runs.

## Required Shared Artifacts

Do not proceed to IaC design or generation unless these shared artifacts exist in the accepted requirement document or work artifacts:

- communication specification
- port definition list
- network boundary definition
- software inventory for the infrastructure target

Recommended shared artifacts:

- protocol definition
- public / private network policy
- system architecture diagram or component map
- architecture decision records

The software inventory must list every software component that will be installed, packaged, started, supervised, proxied, monitored, or documented by the IaC workflow. At minimum, record:

- software name
- purpose
- owner / responsibility boundary
- version or version policy
- runtime unit, such as container, systemd service, host package, proxy, sidecar, or monitoring job
- required ports / protocols
- required environment variables and secret placeholders
- persistence / volume needs
- health check method
- license or distribution constraint when relevant

Use the concrete templates when the accepted requirement document does not already provide equivalent structure:

```text
templates/iac/software-inventory-template.md
templates/iac/communication-specification-template.md
```

If a required shared artifact or software inventory item is missing, stop the workflow and create:

```text
work/<receipt-id>/design-document/open-questions.md
```

The AI must not infer software components, port numbers, communication routes, public exposure, or ownership boundaries.

## Workflow

1. Run `/pre-development-preparation`.
2. Run the Context First Environment Gate and require `environment-selection.environment == docker`.
3. Determine repository mode from `Repository Control`:
   - `existing`: sync the target repository, create a GitHub Issue, then create `feature/issue-<issue-number>`.
   - `precreated-new`: use a GitHub repository that the human has already created, prepare `work/<receipt-id>/source/repository/` as the first content workspace, then push the initial branch before creating the issue branch.
4. Run `/rag-load` before design. Derive retrieval queries from the runtime platform, network/security area, deployment target, observability area, prior incidents, and known target repository or planned repository name.
5. Confirm the required shared artifacts and software inventory. If they are absent or contradictory, stop and write `open-questions.md`.
6. Run `/realtime-iac` only after relevant RAG context and shared artifacts are summarized.
7. Create the IaC design set before implementation:
   - `requirements.md`
   - `network-design.md`
   - `security-design.md`
   - `firewall-policy.md`
   - `runtime-design.md`
   - `docker-compose-design.md`
   - `observability-design.md`
   - `monitoring-policy.md`
8. Run the Boilerplate Template Selection Gate. If realtime gateway infrastructure matches `templates/boilerplates/realtime-gateway-infra-template/`, development / CI/CD / observability platform infrastructure matches `templates/boilerplates/platform-infra-template/`, or PostgreSQL / MySQL shared database infrastructure matches `templates/boilerplates/database-infra-template/`, copy the selected template to the target IaC destination and edit only the copy. If no template matches, record `decision: traditional-coding`.
9. Generate IaC artifacts only from approved designs and the approved boilerplate selection result.
10. For `precreated-new` repository mode, confirm the GitHub repository already exists, push the initial branch after human approval, create the GitHub Issue with `[IaC]` prefix, then create `feature/issue-<issue-number>` from the pushed initial branch.
11. Run security review before local runtime tests.
12. Validate in this order: Docker Desktop, Linux runtime, integration.
13. Create documentation and handoff artifacts.
14. Preserve artifacts under `work/<receipt-id>/` and target repository `docs/evidence/issue-<issue-number>/`.
15. Record decisions, QA, findings, test evidence, RAG context references, specialist review references, boilerplate selection result, and handoff context as JSON where schemas exist.

## Boilerplate Template Selection Gate

Run this gate after Network / Security Design, Runtime Design, Observability Design, and Test Strategy are approved, and before IaC Implementation starts.

Template candidate:

| Target | Template path | Instruction |
| --- | --- | --- |
| Realtime gateway IaC / infrastructure | `templates/boilerplates/realtime-gateway-infra-template/` | `realtime-gateway-infra-template_実装指示書.md` |
| Development / CI/CD / observability platform infrastructure | `templates/boilerplates/platform-infra-template/` | `Platform_Infrastructure_Boilerplate_追加実装指示書.md` |
| PostgreSQL / MySQL shared database infrastructure | `templates/boilerplates/database-infra-template/` | `Database_Infrastructure_Boilerplate_追加実装指示書.md` |

Rules:

- Inspect the infrastructure target and decide whether realtime gateway infrastructure, platform infrastructure, database infrastructure, multiple templates, or no template applies.
- Check that the mapped template directory exists and contains root files, environment directories, modules, scripts, and docs before using it.
- If the matching template exists, copy the template to the target IaC directory or `work/<receipt-id>/source/repository/` and edit only the copied destination.
- Do not edit the boilerplate template itself during product implementation.
- Preserve the template responsibility boundaries unless the approved design explicitly changes them.
- For platform infrastructure, record Terraform component selection, Docker Compose profile, admin CIDR, secret source, backup / restore, and product-specific validation evidence.
- For database infrastructure, record DB engine, DB version, database name, app user, connection source, persistence, backup / restore, migration, connection contract, secret redaction, and evidence.
- Do not generate `.env`, real secrets, production passwords, or private keys.
- Save the selection result under `work/<receipt-id>/process-report/boilerplate-template-selection.md`.

Required report template:

```text
templates/process-report/boilerplate-template-selection-report-template.md
```

## Repository Modes

### Existing Repository Mode

Use this mode when the IaC must be added to an existing GitHub repository.

Order:

1. Resolve repository and target branch from `Repository Control`.
2. Run repository preparation and requirement comparison.
3. Create the `[IaC]` GitHub Issue after human approval.
4. Create `feature/issue-<issue-number>` on GitHub first, then clone / check out that branch under `work/<receipt-id>/source/repository/`.
5. Implement, validate, commit, push, and create a Pull Request after human approval.

### Precreated New Repository Mode

Use this mode when the human has already created a new empty or near-empty GitHub repository, and the IaC workflow will finally push the generated contents to it.

Order:

1. Resolve the planned `owner/repository` and initial branch from `Repository Control`.
2. Confirm the GitHub repository already exists and is the intended destination.
3. Generate IaC and docs under `work/<receipt-id>/source/repository/`.
4. After human approval, initialize local git, commit, and push the initial branch to the precreated GitHub repository.
5. Create the `[IaC]` GitHub Issue in that repository.
6. Create `feature/issue-<issue-number>` from the pushed initial branch.
7. Continue normal implementation / validation on the issue branch.
8. Push the issue branch and create a Pull Request after human approval.

Runtime helpers:

```powershell
uv run --project runtime python runtime/scm/bootstrap_repository.py --work-id <receipt-id> --github-repo <owner>/<repo> --push --human-check approved
uv run --project runtime python runtime/github/issue_manager.py --work-id <receipt-id> --github-repo <owner>/<repo> --title "<title>" --flow-label iac --create
uv run --project runtime python runtime/scm/create_issue_branch.py --work-id <receipt-id> --issue-number <number> --github-repo <owner>/<repo> --base-branch <initial-branch> --link-to-issue
```

## IaC Artifact Scope

Allowed generated artifacts include:

- `docker-compose.yml`
- `.env.example`
- systemd unit files
- reverse proxy configuration
- TURN / STUN configuration
- firewall scripts or policy files
- logrotate configuration
- monitoring configuration
- README / setup / operation / troubleshooting docs

Never generate `.env` or real secrets. Use placeholders in `.env.example`.

## Responsibility Boundary

Keep software workflow and infrastructure workflow separate.

Shared artifacts such as communication specification, port definitions, network boundary definition, protocol definition, public/private network policy, architecture diagram, and ADRs are the single source of truth for both workflows.

The IaC workflow owns:

- runtime packaging and startup
- network exposure implementation
- firewall and route policy implementation
- reverse proxy / relay support
- observability plumbing
- host runtime integration
- infrastructure evidence and operator docs

The IaC workflow does not own:

- application protocol semantics
- control authority rules
- business/application behavior
- safety behavior definition
- generated secrets
- undocumented port or route decisions

## Stop Rules

Stop and request human review when any of these are unresolved:

- communication specification is missing
- port definition list is missing
- network boundary definition is missing
- software inventory is missing or omits software that IaC must install, package, start, supervise, proxy, monitor, or document
- public exposure scope is undefined
- system responsibility boundary is undefined
- repository mode, planned repository name, or initial branch is undefined
- TLS/auth model is unclear
- secret source and rotation are unclear
- firewall policy conflicts with runtime or application requirements
- `.env` or real secret generation would be required
- Docker Desktop validation cannot represent required Linux-only behavior
- Linux validation requires installation or host changes that have not been approved

## Test Case And Evidence Flow

Before implementation, Docker Desktop validation, Linux validation, or integration validation, create test case tables and an evidence plan.

Work artifacts:

```text
work/<receipt-id>/test-specifications/
work/<receipt-id>/test-evidence/
```

Target repository durable artifacts:

```text
work/<receipt-id>/source/repository/docs/evidence/issue-<issue-number>/test_specifications/iac-test-cases.md
work/<receipt-id>/source/repository/docs/evidence/issue-<issue-number>/integration/docker-desktop/
work/<receipt-id>/source/repository/docs/evidence/issue-<issue-number>/integration/linux-runtime/
work/<receipt-id>/source/repository/docs/evidence/issue-<issue-number>/integration/iac-integration/
work/<receipt-id>/source/repository/docs/evidence/issue-<issue-number>/human_check/
```

Evidence must include command output or logs for applicable checks:

- `docker compose config`
- container startup
- health check
- environment variable loading from `.env.example` or test env
- port binding
- log output
- restart policy
- network isolation
- UDP communication when applicable
- systemd validation on Linux
- firewall validation on Linux
- logrotate validation on Linux

## Agent Set

Use these agent roles in order. Existing repository agents may fulfill the role when their scope matches.

| Order | Role | Primary Output |
| --- | --- | --- |
| 1 | requirements organizer | `requirements.md`, `open-questions.md` |
| 2 | network/security designer | `network-design.md`, `security-design.md`, `firewall-policy.md` |
| 3 | runtime designer | `runtime-design.md`, `docker-compose-design.md` |
| 4 | observability designer | `observability-design.md`, `monitoring-policy.md` |
| 5 | IaC implementer | generated IaC artifacts |
| 6 | security reviewer | `security-review.md` |
| 7 | Docker Desktop tester | `docker-test-plan.md`, `docker-test-result.md`, `evidence/` |
| 8 | Linux runtime tester | `runtime-validation.md` |
| 9 | integration tester | `integration-test.md`, `evidence/` |
| 10 | documentation writer | README, setup, operation, troubleshooting, architecture notes |

## Issue Title

Use the IaC flow prefix for GitHub Issues:

```text
[IaC] <issue-title>
```

## Specialist Review Gate

Use Specialist Agent review when IaC depends on domain-specific knowledge such as realtime network protocols, remote access security, Linux/systemd behavior, Docker networking, TURN/STUN, reverse proxy, firewall, logrotate, monitoring, or evidence strategy.

Save review outputs under:

```text
work/<receipt-id>/process-report/specialist-review-<domain>.md
```

High or critical findings must return the workflow to shared artifact confirmation, design, or test strategy before implementation or validation continues.


## Workflow Feedback Output

During every AI workflow run, capture actionable workflow friction or improvement candidates in `work/feedback/`.
Create or update a Feedback report when you observe ambiguity, repeated checks, missing context/docs, runtime observation gaps, noisy handoffs, encoding issues, or a reusable workflow improvement.

Use the existing helper when creating a new report:

```powershell
python runtime/workflow/self_improvement.py create-feedback `
  --target-workflow "<slash-command>" `
  --reporter "AI workflow" `
  --situation "<what was happening>" `
  --friction "<observed friction>" `
  --impact "<impact on quality, speed, or safety>" `
  --proposed-improvement "<candidate improvement>"
```

Keep the initial `Review Status` as `Proposed`. Do not run `/self-improvement` automatically inside this workflow; `/self-improvement` is executed later when feedback has accumulated and a human is ready to review Accepted / Rejected / Deferred decisions.
