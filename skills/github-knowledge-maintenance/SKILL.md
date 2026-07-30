---
name: github-knowledge-maintenance
description: Maintain a GitHub repository as a long-lived knowledge asset without erasing Git history. Use when the user selects /github-knowledge-maintenance or asks to preserve GitHub Issues, PRs, docs, CARs, commit-source, commit-message, semantic-subject, Knowledge DB, or RAG candidates as reusable repository knowledge.
---

# GitHub Knowledge Maintenance Skill

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.ariadne/shared/output-language-policy.md`.

## Runtime Entrypoint Rule

Use `aiwfctl` / `runtime/ctl/ctl.py` as the official runtime entrypoint for this workflow.

- Follow `.ariadne/shared/runtime-entrypoint-policy.md`.
- On Windows 11, start runtime commands through `runtime/windows-script/aiwf.cmd` first, then delegate to `aiwfctl` from there.
- Do not directly invoke `runtime/workflow/github_knowledge_maintenance.py`, `runtime/workflow/context_first.py`, `runtime/workflow/human_gate_policy.py`, `runtime/workflow/self_improvement.py`, or `runtime/workflow/close_archive.py` during normal workflow execution.
- Treat `runtime/workflow/*.py` files as internal implementation modules unless a runtime developer is testing that module itself.
- Context First checks must go through `aiwfctl context ...`.
- Human Check registry checks must go through `aiwfctl human-gate ...`.
- GitHub knowledge analysis, sync, rebase package generation, approved replay, and RAG candidate generation must go through `aiwfctl github-knowledge ...`.
- Close archive preparation, audit, and prune must go through `aiwfctl close-archive ...`.
- Self-improvement feedback generated from this workflow must go through `aiwfctl self-improvement ...`.

If a needed operation is not exposed through `aiwfctl`, stop the current operation and create a self-improvement Feedback report first. Do not silently add `runtime/ctl/ctl.py` commands inside the active workflow; wait for Human Review / accepted self-improvement flow.

## Mechanical Artifact Integrity Rule

Do not judge JSON or Markdown corruption from PowerShell console rendering alone.

- After generating or updating `github-knowledge-analysis.json` or Human-facing reports, run the official artifact check:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge artifact-integrity `
  --work-id "<work-id>" `
  --fail-on-finding
```

- Treat the saved file bytes and strict UTF-8 / JSON parse result from `artifact-integrity` as the source of truth.
- Do not update `github-knowledge-analysis.json` with ad hoc PowerShell JSON fragments, text replacement, or temporary helper scripts.
- Use dedicated runtime commands such as `analysis-template`, `detect-rebase`, `rebase-review-intake`, `rebase-package`, `rebase-apply`, `publish-verified-replay`, `sync-review-intake`, `sync-apply`, and `rag-candidate` to write workflow JSON.
- If an update path is missing, create Feedback first instead of hand-editing the JSON during the active workflow.

## Purpose

GitHub Repositoryを、未来のAI workflowとRAGが再利用できるKnowledge Baseとして継続保守します。

This workflow does not erase Git history or make historical evidence disappear. If commit semantic subjects, commit bodies, PR titles, PR bodies, or source documentation are missing, vague, or misleading, record the gap, prepare a reviewed repair proposal, and route the learned content to RAG. Existing commit rewriting is a separate high-risk action and requires explicit item-level approval plus before/after SHA mapping.

Small rebase maintenance for 1-3 file commit leakage is also a high-risk repair path. Run it in four stages: detect commit leakage, calculate the rebase execution plan, output the plan report, and execute the approved Git CLI rewrite package only after one Human Check approval.

Do not complete a useless or accidental commit by inventing a strange Issue reference, PR story, or commit message after the fact. The rebase repair must either absorb the files into the proper semantic commit, split them into a real independent responsibility, drop an empty/noise commit, or explicitly keep it with existing evidence.

Semantic commit quality is part of the repair target. The commit subject shown in the GitHub commit list must carry useful meaning by itself, using `type(scope): responsibility/result`, and the body must preserve intent, scope, decision, impact, and reusable maintenance knowledge.

## GitHub API / Git CLI Responsibility Boundary

Keep these responsibilities separate:

- GitHub API / `gh`: collect and update GitHub-hosted metadata such as Issues, Pull Requests, comments, labels, releases, and remote branch refs. Authentication is usually required for private repositories and mutation.
- Git CLI local: read and create the local commit graph, perform rebase-equivalent non-interactive rewrite, generate before/after SHA mapping, and verify tree equality or intended tree delta. Authentication is not required for local-only operations.
- Git CLI remote: fetch, ls-remote, push, and force-with-lease the approved local graph to the approved remote branch. Authentication is required because this changes or reads GitHub remote state.
- GitHub API cannot perform `git rebase`, commit graph rewrite, or commit message rewrite. Do not explain local rebase/editor behavior as a GitHub token problem.
- Runtime automation must not depend on `git rebase -i` editor hooks. Use non-interactive Git CLI local commands, such as replay/cherry-pick/commit-tree/update-ref patterns, then use Git CLI remote commands only for the approved remote reflection step.
- One Human Check approval package is enough when it includes repository, target branch, rewrite action, rollback plan, local verification commands, and exact remote update command. Do not split the same approved rewrite into repeated approval prompts. After the package is approved, `--human-check approved` is a runtime execution guard, not a second human prompt.

## Required Inputs

- repository URL, slug, or repository name
- scan mode: `repository`, `issue`, `pull-request`, `recent`, or `full`
- repair mode: `proposal` or `apply`
- whether RAG output is required

Example:

```text
/github-knowledge-maintenance localty-system-gui recent proposal rag
```

## Directory Model

Primary work folder:

```text
work/github/<scope>/<mode>/
```

`<scope>` is the target branch name when `--target-branch` is provided. If no target branch is provided, use `original`.
Examples:

```text
work/github/dev-bk-01/recent/
work/github/original/recent/
```

Primary artifacts:

```text
work/<work-id>/context/github-knowledge-analysis.json
work/<work-id>/process-report/github-knowledge-repair-plan-*.md
work/<work-id>/process-report/github-history-rebase-plan-*.md
work/<work-id>/process-report/github-documentation-sync-plan-*.md
work/<work-id>/process-report/github-knowledge-rag-candidate-*.md
```

Reference guideline:

```text
docs/reference/semantic-commit-message-guideline.md
```

Approved RAG publication target:

```text
work/db/ariadne-knowledge-platform/rag/github-knowledge/
```

This target stores approved source Markdown reports named:

```text
YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

After publishing source Markdown, regenerate the RAG artifacts in this order:

1. normalize approved source Markdown into UUID JSON
2. chunk normalized JSON
3. rebuild indexes
4. rebuild embeddings

Normalize:

```powershell
uv run --project runtime python runtime/rag/normalize_documents.py `
  --source-dir work/db/ariadne-knowledge-platform/rag/github-knowledge `
  --output-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --document-type github-repository-knowledge
```

Chunk:

```powershell
uv run --project runtime python runtime/rag/chunk_documents.py `
  --input-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --output-dir work/db/ariadne-knowledge-platform/rag/chunks
```

Index:

```powershell
uv run --project runtime python runtime/rag/build_index.py `
  --normalized-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --chunks-dir work/db/ariadne-knowledge-platform/rag/chunks `
  --output-dir work/db/ariadne-knowledge-platform/rag/indexes
```

Embedding:

```powershell
uv run --project runtime python runtime/rag/embed_chunks.py `
  --chunks-index work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl `
  --output work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl
```

Final durable landing:

```text
work/db/ariadne-knowledge-platform/rag/normalized/<uuid>.json
```

## Workflow

Run from:

```powershell
cd C:\github\ariadne-ai-workflow-platform
```

On Windows 11, prefer:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge init `
  --repository "<target-repository>" `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output
```

### 1. Initialize Work Area

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge init `
  --repository "<target-repository>" `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output
```

If the work folder already exists, stop and ask whether to reuse it. After confirmation, rerun with `--reuse-existing`.

### 2. Create Analysis Scaffold

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge analysis-template `
  --work-id "<work-id>"
```

Generated:

```text
work/<work-id>/context/github-knowledge-analysis.json
```

Schema:

```text
.ariadne/schemas/github-knowledge-analysis.schema.json
```

### 3. Repository Discovery

Use:

```text
.ariadne/agents/repository-discovery-agent.prompt.md
```

Confirm repository identity, scan scope, and whether clone is forbidden or conditionally allowed.

### 4. GitHub Metadata Collection

Use:

```text
.ariadne/agents/github-metadata-collector-agent.prompt.md
```

Before metadata collection, run the repository runtime GitHub CLI preflight. This separates `gh --version`, `gh auth status`, and token availability so the AI does not decide these steps ad hoc:

```powershell
.\runtime\windows-script\aiwf.cmd preflight `
  --profile github-cli `
  --work-id "<work-id>"
```

If `gh --version` is missing, record the missing tool in the analysis JSON, ask for human approval, then install GitHub CLI with:

```powershell
winget install --id GitHub.cli
```

After installation, open a new terminal or refresh PATH, then rerun the preflight.

If `gh auth status` reports unauthenticated and repository `.env` or process ENV contains `GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_API_TOKEN`, or `GITHUB_API_KEY`, run the ENV login action through preflight. Do not print token values:

```powershell
.\runtime\windows-script\aiwf.cmd preflight `
  --profile github-cli `
  --gh-login-from-env `
  --human-check approved
```

The runtime performs `gh auth login --with-token` from stdin and then `gh auth setup-git`. Use token ENV, not GitHub password ENV. If the repository `.env` contains a token key, note that the token is available to repository runtime helpers via `load_env()`, even when `$env:GITHUB_TOKEN` is not set in the current PowerShell process. Do not print token values.

Prefer GitHub CLI/API:

```powershell
gh issue list --repo "<owner/repo>" --state all --limit 100
gh issue view "<number>" --repo "<owner/repo>" --comments
gh pr list --repo "<owner/repo>" --state all --limit 100
gh pr view "<number>" --repo "<owner/repo>" --comments
gh pr diff "<number>" --repo "<owner/repo>"
gh api repos/<owner>/<repo>/releases
```

Do not clone unless GitHub CLI/API evidence is insufficient and the human explicitly approves the clone reason.

### 5. Knowledge Asset Discovery

Use:

```text
.ariadne/agents/knowledge-asset-discovery-agent.prompt.md
```

Extract:

- Intent
- Scope
- Design Decision
- Corrective Action
- Maintenance Knowledge
- Shared Artifact
- Future RAG Candidate
- Commit Source / Message Gap
- Semantic Commit Subject Gap
- Pull Request Title Gap

Record findings in `github-knowledge-analysis.json`.
For 1-3 file commit leakage, run detection before planning:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge detect-rebase `
  --work-id "<work-id>" `
  --base "HEAD~30" `
  --head "HEAD"
```

If the human asks for all history, or if the branch was intentionally created for safe full-history maintenance, use the explicit full-history mode instead of increasing a recent-history number by hand:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge detect-rebase `
  --work-id "<work-id>" `
  --git-repo "." `
  --all-history `
  --head "origin/<target-branch>" `
  --max-commits 200
```

This writes candidates to `history_rewrite_candidates` with `approval_status: pending`. Candidate records include `file_paths`, `suspect_commits`, `expected_commit`, `repair_goal`, `independent_responsibility`, `evidence_refs`, `recommended_action`, `reason`, `approval_status`, `completion_criteria`, `before_after_sha_mapping`, `rollback_plan`, `draft_commands`, and `verification_commands`.
When commit subjects are thin, the runtime must inspect commit materials as well as the subject: changed paths, directories, extensions, repository domains, nearby commits, and related file sets. If a safe absorb target cannot be determined from that evidence, record `repair_goal: manual-review-required` and keep the candidate unresolved for Human Review. Do not use `no-rewrite` merely because automatic target detection failed.

### 6. Narrative Analysis

Use:

```text
.ariadne/agents/narrative-analyzer-agent.prompt.md
```

Check the chain:

```text
Issue -> Pull Request -> Review -> Comment -> Documentation
```

Record narrative gaps and open questions in `github-knowledge-analysis.json`.

### 7. Repair Planning

Use:

```text
.ariadne/agents/documentation-repair-agent.prompt.md
```

Create the human review plan:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge repair-plan `
  --work-id "<work-id>"
```

Create the high-risk rebase review plan for 1-3 file commit leakage:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-plan `
  --work-id "<work-id>"
```

This is a proposal. It does not mutate GitHub.

Immediately verify the saved artifacts before reporting mojibake, JSON corruption, or checklist readiness:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge artifact-integrity `
  --work-id "<work-id>" `
  --fail-on-finding
```

`status`, `next-action`, and `resume` include an `encoding_gate`. Treat `encoding_gate.status: block` as a hard stop: do not run rebase, replay, push, or GitHub sync apply commands until the returned repair/integrity command has been run and the saved artifacts are readable and consistent. Block conditions include UTF-8 decode failure, JSON parse failure, mojibake markers in resume artifacts, replay packages missing `target_branch` / `source_ref` / `apply_mode`, push-enabled packages missing `expected_remote_sha`, invalid approval/execution statuses, and verified/pushed candidates missing before/after SHA mapping.

After the single Human Check approval package is recorded in the generated OK / NG checklist, ingest that checklist through the official runtime entrypoint. Do not hand-edit `github-knowledge-analysis.json`:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-review-intake `
  --work-id "<work-id>" `
  --human-check approved
```

`rebase-review-intake` reads the latest `github-history-rebase-plan-*.md` unless `--plan-path` is provided. It validates that every candidate has exactly one OK or NG checkbox, writes OK rows as `approval_status: approved` plus a concrete `repair_goal`, writes NG rows as `approval_status: rejected`, and records the single review intake in `github-knowledge-analysis.json`. With `--ok-repair-goal auto`, OK rows keep an existing executable goal or become `absorb-into-existing-commit` when `expected_commit` exists. Use an explicit `--ok-repair-goal` only when the checklist package intentionally approved another disposition.

After the single Human Check approval package is ingested, execute only an approved candidate:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-package `
  --work-id "<work-id>" `
  --candidate-id "<candidate-id>" `
  --target-branch "<branch>" `
  --apply-mode direct

uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-apply `
  --work-id "<work-id>" `
  --human-check approved
```

`rebase-apply` requires `approval_status: approved` in `github-knowledge-analysis.json` and the `--human-check approved` runtime guard. Do not ask the human again for the CLI guard when the approval package already covers the repository, branch, rewrite action, rollback plan, verification commands, and exact remote update command.

For approved small-commit rebase packages, prefer the built-in non-interactive replay runtime instead of generating helper Python files under `work/<work-id>/context/`:

Generate the package from approved candidates; do not hand-write the JSON:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-package `
  --work-id "<work-id>" `
  --target-branch "<branch>" `
  --apply-mode direct
```

Use `--candidate-id "<candidate-id>"` to restrict the package to explicit approved candidates. Without `--candidate-id`, the runtime packages all approved executable candidates that are not already verified or pushed. `split-into-independent-commit` candidates require a concrete `message_override` or `proposed_commit_message`; the runtime must not invent one.

Then execute the generated package:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-apply `
  --work-id "<work-id>" `
  --package-path "work/<work-id>/context/rebase-replay-package.json" `
  --human-check approved
```

When remote reflection is part of the approved package, add `--push`. The package must include `target_branch`, `source_ref`, `expected_remote_sha`, `candidate_ids`, and data-only rewrite actions such as `absorb`, `drop`, `remove_after_apply`, and `message_overrides`.

If replay was already executed and verified without `--push`, do not regenerate the package or hand-edit JSON just to add `allow_push`. Publish the verified replay tip through the dedicated runtime entrypoint:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge publish-verified-replay `
  --work-id "<work-id>" `
  --target-branch "<branch>" `
  --expected-remote-sha "<approved-remote-sha>" `
  --human-check approved
```

`publish-verified-replay` consumes the latest `tree_equal: true` and unpublished `rebase_replay_executions[*].new_tip`, verifies that the remote branch still equals the approved expected SHA, then runs one `force-with-lease` push. Use `--new-tip "<sha>"` only when multiple verified unpublished replay executions exist and the approval package identifies the exact tip.

After approved small-commit rebase is verified, run commit message/body repair through the same high-risk replay runtime. Do not run `git commit --amend`, `git rebase -i`, or ad hoc scripts by hand:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge message-repair-plan `
  --work-id "<work-id>" `
  --source-ref "origin/<branch>"
```

The message repair plan writes one OK / NG checklist for weak semantic subjects or damaged commit messages. After the human checks the list, ingest it once:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge message-review-intake `
  --work-id "<work-id>" `
  --human-check approved
```

Generate the replay package from approved message repair candidates:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge message-repair-package `
  --work-id "<work-id>" `
  --target-branch "<branch>" `
  --source-ref "origin/<branch>" `
  --expected-remote-sha "<remote-sha>"
```

Then execute it with the existing replay apply runtime:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge rebase-apply `
  --work-id "<work-id>" `
  --package-path "work/<work-id>/context/message-repair-package.json" `
  --human-check approved `
  --push
```

Message repair packages must be tree-preserving and may contain only `message_overrides` for approved `message_repair_candidates`. The replay runtime must verify that the final tree still matches `source_ref`, record before/after SHA mapping, verify the GitHub-list-readable subject with `git log --format="%H %s"`, and return to GitHub sync only after `execution_status: verified` or `pushed`.

Patch apply mode must be explicit in the package or CLI when direct patch replay is not enough:

- `apply_mode: direct`: default strict `git apply --index`; use when commit patches match cleanly.
- `apply_mode: git-3way`: use Git's `git apply --3way --index` for approved packages where direct patch replay cannot match context.
- `apply_mode: auto-3way`: try direct apply first, then fall back to Git 3-way apply. Use only when the approval package explicitly permits fallback behavior.

The CLI can override the package mode with `--apply-mode direct`, `--apply-mode git-3way`, or `--apply-mode auto-3way`. Record the selected mode in the execution report and analysis JSON.

The replay runtime must create the verification checkout under:

```text
work/<work-id>/git-worktree/<target-branch>/
```

Do not use the main checkout as the rewrite workspace. Do not generate ad hoc `*.py` rebase scripts in `work/<work-id>/context/`; the runtime engine owns patch replay, byte-safe Git apply, SHA mapping, report creation, verification, and optional force-with-lease push.

The rebase plan includes a legend for candidate disposition:

- `approval_status: pending`: incomplete, do not run GitHub sync apply yet.
- approved absorb/split/drop repair goals: incomplete until rebase is applied and verified.
- `manual-review-required`: unresolved until the human chooses absorb, split, drop, keep-with-evidence, no-rewrite, or rejected from commit material evidence.
- `keep-with-evidence`: resolved only when independent responsibility and existing evidence are recorded.
- `no-rewrite`: resolved only when the human explicitly decides that no rewrite is needed.
- `rejected`: resolved, do not rebase.

Run order:

- If no rebase candidates are detected, continue to GitHub sync after the relevant Human Check.
- If any rebase candidate is unresolved, do not run GitHub sync apply.
- Resolve rebase candidates first with `rebase-plan`, one Human Check approval package, `rebase-apply`, and verification.
- Approved absorb/split/drop candidates remain unresolved until `execution_status: verified`.
- `manual-review-required` candidates remain unresolved. `keep-with-evidence`, explicit `no-rewrite`, and `rejected` candidates can unblock GitHub sync when the required evidence/reason is recorded.

### 8. Human Review Gate

Before any GitHub mutation, the human must confirm:

- repair reason
- repair target
- before / after summary
- for PR title repair, the current title, proposed title, and exact `gh pr edit --title` command
- whether the action is additive repair or approved commit-message/source correction
- whether the proposed semantic subject is meaningful in GitHub commit list view
- for any commit rewrite, the before/after SHA mapping and rollback plan
- for 1-3 file commit leakage rebase, the target file list, suspect commits, expected commit, exact rebase/amend commands, before/after SHA mapping, rollback plan, and verification commands
- exact Git / GitHub CLI/API command

### 9. GitHub Documentation Sync

Use:

```text
.ariadne/agents/github-documentation-sync-agent.prompt.md
```

Create the sync plan:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge sync-plan `
  --work-id "<work-id>"
```

Create the single OK / NG review checklist for Issue / PR / comment repair actions:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge sync-review-plan `
  --work-id "<work-id>"
```

After the human checks one OK or NG per action id, ingest the checklist through ctl. Do not hand-edit `github_sync_actions[*].approval_status`:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge sync-review-intake `
  --work-id "<work-id>" `
  --human-check approved
```

Execute one reviewed and approved GitHub sync action through ctl/runtime:

```powershell
aiwfctl github-knowledge sync-apply `
  --work-id "<work-id>" `
  --action-id "<action-id>" `
  --human-check approved
```

Allowed operations after item-level approval:

```text
gh issue edit
gh issue comment
gh pr edit
gh pr comment
gh api
```

Do not execute commands marked `pending` or `approved` without `human_review_decision: OK` and `human_review_source` from `sync-review-intake`. Do not execute GitHub sync commands manually; use `github-sync-apply` / `aiwfctl github-knowledge sync-apply` so approval status, command shape, and execution result are recorded.

### 10. Knowledge DB / RAG Candidate Generation

Use:

```text
.ariadne/agents/knowledge-db-registrar-agent.prompt.md
```

Create a candidate note:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rag-candidate `
  --work-id "<work-id>"
```

Publish to `work/db/ariadne-knowledge-platform/rag/github-knowledge/` only after explicit approval:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rag-candidate `
  --work-id "<work-id>" `
  --publish-rag `
  --human-check approved
```

Then normalize the approved published report to UUID JSON with `runtime/rag/normalize_documents.py`, and rebuild chunks, indexes, and embeddings. After long-lived Knowledge absorption is confirmed, use the generic work cleanup ctl returned by `rag-candidate` / `next-action` before removing temporary GitHub knowledge work:

```powershell
.\runtime\windows-script\aiwf.cmd ctl work cleanup-check --work-id github/original --recursive
.\runtime\windows-script\aiwf.cmd ctl work cleanup-apply --work-id github/original --recursive --human-check approved
```

## Workflow Feedback Output

During every AI workflow run, capture actionable workflow friction or improvement candidates in `work/feedback/`.
Create or update a Feedback report when you observe ambiguity, repeated checks, missing context/docs, runtime observation gaps, noisy handoffs, encoding issues, or a reusable workflow improvement.

Use the existing helper when creating a new report:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "<slash-command>" `
  --reporter "AI workflow" `
  --situation "<what was happening>" `
  --friction "<observed friction>" `
  --impact "<impact on quality, speed, or safety>" `
  --proposed-improvement "<candidate improvement>"
```

Keep the initial `Review Status` as `Proposed`. Do not run `/self-improvement` automatically inside this workflow; `/self-improvement` is executed later when feedback has accumulated and a human is ready to review Accepted / Rejected / Deferred decisions.

## Guardrails

- Do not erase Git history or hide historical evidence.
- Do not treat "no history erasure" as permission to leave weak commit messages or source explanations uncorrected.
- Do not leave semantic commit subjects vague. Avoid broad scopes and weak wording such as "対応", "修正", "更新", or repository-name-only scopes when a more precise responsibility scope exists.
- Do not leave PR titles vague. A merged PR title must be useful in the GitHub PR list without opening the body.
- For commit message repair, propose both a GitHub-list-readable subject and a body that records intent, scope, decision, impact, and reusable maintenance knowledge.
- Prefer additive repair first: PR body, follow-up documentation commit, README/docs supplement, CAR supplement, or RAG candidate.
- Existing commit-message/source correction with `git rebase`, `git commit --amend`, or force push is allowed only when the human explicitly approves that high-risk path and a before/after SHA mapping is recorded.
- 1-3 file commit leakage rebase is allowed only after `detect-rebase-candidates`, `rebase-plan`, item-level approval, before/after SHA mapping, rollback plan, and verification commands.
- Do not mark rebase maintenance complete by attaching a new Issue/message to a useless commit. Completion requires absorb/split/drop/no-rewrite/keep-with-evidence disposition and reviewed evidence.
- Do not change source code.
- Do not clone by default.
- Do not mutate GitHub without explicit human approval.
- Do not manually run approved GitHub sync actions outside ctl/runtime. Use `github-sync-apply` so the result is written back to `github-knowledge-analysis.json`.
- Do not install missing tools silently. For missing `gh`, record the install command `winget install --id GitHub.cli`, get human approval, then verify with `gh --version`.
- Do not convert a free-form observation into a GitHub update; write it to `github-knowledge-analysis.json` first.
- Do not run RAG publication without explicit human approval.
- Route the knowledge learned from commit-source/message repairs into RAG candidates after human review.
- If evidence is missing, record an open question instead of guessing.

## Output Summary

Use:

```text
=== GitHub Knowledge Maintenance Summary ===

Repository
  <owner/repo>

Analysis JSON
  work/<work-id>/context/github-knowledge-analysis.json

Knowledge Assets
  <count>

Narrative Gaps
  Critical: 0
  High: 0
  Medium: 0
  Low: 0

Repair Proposals
  <count>

GitHub Sync
  Pending Approval: <count>

RAG Candidates
  <count>

Next Action
  Human Review / GitHub Sync Approval / RAG Approval
```
