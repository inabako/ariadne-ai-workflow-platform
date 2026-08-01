# GitHub Knowledge Maintenance

`/github-knowledge-maintenance` は、GitHub Repositoryを長期的な知識資産として保守するworkflowです。

Git履歴を「なかったこと」にせず、Issue、Pull Request、comment、docs、commit source、commit message、Corrective Action Report、Knowledge DB候補、RAG候補を整えます。

commit message 補修では、GitHub の commit list に表示される semantic subject も品質対象にします。

## Inputs

```yaml
repository_url:
scan_mode:
  - repository
  - issue
  - pull-request
  - recent
  - full
repair_mode:
  - proposal
  - apply
rag_output:
  true
  false
```

## Workflow

```text
Repository URL
  -> GitHub Metadata Collection
  -> Commit Source / Message Gap Check
  -> Semantic Commit Subject Check
  -> Small Rebase Candidate Check
  -> Knowledge Asset Discovery
  -> Narrative Analysis
  -> Repair Planning
  -> Human Review
  -> GitHub Documentation Sync
  -> Knowledge DB Generation
  -> RAG Candidate Generation
```

## Runtime

Default work folders are:

```text
work/github/<target-branch>/<scan-mode>/
work/github/original/<scan-mode>/
```

For example, branch-scoped work for `dev-bk-01` goes under `work/github/dev-bk-01/recent/`.
If no `--target-branch` is provided, the original repository-level scan goes under `work/github/original/recent/`.

Initialize:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge init `
  --repository "<target-repository>" `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output
```

Create the analysis scaffold:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge analysis-template `
  --work-id "<work-id>"
```

Create a human review repair plan:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge repair-plan `
  --work-id "<work-id>"
```

Detect 1-3 file commit leakage candidates from local Git history:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge detect-rebase `
  --work-id "<work-id>" `
  --base "HEAD~30" `
  --head "HEAD"
```

Create the GitHub sync plan:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge sync-plan `
  --work-id "<work-id>"
```

Create the OK / NG review checklist for Issue / PR / comment repair actions:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge sync-review-plan `
  --work-id "<work-id>"
```

Ingest the checked review plan through ctl before execution:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge sync-review-intake `
  --work-id "<work-id>" `
  --human-check approved
```

Execute one reviewed and approved GitHub sync action:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge sync-apply `
  --work-id "<work-id>" `
  --action-id "<action-id>" `
  --human-check approved
```

The same operation is available through `aiwfctl`:

```powershell
aiwfctl github-knowledge sync-apply `
  --work-id "<work-id>" `
  --action-id "<action-id>" `
  --human-check approved
```

Create a high-risk rebase review plan for 1-3 file commit leakage:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-plan `
  --work-id "<work-id>"
```

Ingest the Human Review OK / NG checklist through ctl before package generation:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-review-intake `
  --work-id "<work-id>" `
  --human-check approved
```

`rebase-review-intake` reads the latest `github-history-rebase-plan-*.md` unless `--plan-path` is provided. It validates one checked value per candidate, records OK as `approval_status: approved` with a concrete `repair_goal`, and records NG as `approval_status: rejected`. The command updates `github-knowledge-analysis.json`; AI must not hand-edit that approval state.

Approved small-commit rebase packages should use the built-in replay runtime:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-package `
  --work-id "<work-id>" `
  --target-branch "<branch>" `
  --apply-mode direct
```

`rebase-replay-package` は、`approval_status: approved` の実行可能candidateだけから `work/<work-id>/context/rebase-replay-package.json` を生成します。AIはこのJSONを手書きしません。`--candidate-id` を指定した場合は、その承認済みcandidateだけをpackage化します。

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-apply `
  --work-id "<work-id>" `
  --package-path "work/<work-id>/context/rebase-replay-package.json" `
  --human-check approved
```

The replay runtime checks out the target branch under `work/<work-id>/git-worktree/<branch>/`, executes data-only actions from the JSON package, writes the SHA map and execution report, and optionally pushes with `--push` when the approved package includes the exact force-with-lease boundary. Do not generate ad hoc Python rebase scripts under `work/<work-id>/context/`.

Use `apply_mode: direct` by default. If direct patch replay cannot match context, use an approved `apply_mode: git-3way` package or pass `--apply-mode git-3way` so the runtime uses `git apply --3way --index`. Use `apply_mode: auto-3way` only when the approval package explicitly permits fallback from direct apply to Git 3-way apply.

If a replay package has already been executed and verified without `--push`, publish the verified tip through ctl instead of regenerating the package or editing JSON:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge publish-verified-replay `
  --work-id "<work-id>" `
  --target-branch "<branch>" `
  --expected-remote-sha "<approved-remote-sha>" `
  --human-check approved
```

`publish-verified-replay` selects the latest unpublished `tree_equal: true` replay execution, checks that `source_tip..new_tip` has no tree diff, verifies the remote branch still equals the approved expected SHA, and pushes `new_tip` with `force-with-lease`. Use `--new-tip "<sha>"` when more than one verified unpublished replay exists.

### Resume Encoding Gate

`status` / `next-action` / `resume` run an encoding gate before returning a replay, push, or GitHub sync command. The gate checks saved artifact bytes, strict UTF-8 decode, JSON parse, mojibake markers, replay package fields, candidate status values, and before/after SHA mapping requirements.

If `encoding_gate.status` is `block`, do not continue rebase, replay, push, or GitHub sync apply. Run the returned `encoding_gate.repair_command` / `next_action.command` first and inspect the artifact integrity report. Console rendering alone is not evidence of saved-file corruption.

After the approved small-commit rebase is verified, run commit message/body repair before GitHub sync when weak semantic subjects remain:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge message-repair-plan `
  --work-id "<work-id>" `
  --source-ref "origin/<branch>"
```

The generated message repair checklist is the single Human Check for message rewrite candidates. Ingest it through ctl:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge message-review-intake `
  --work-id "<work-id>" `
  --human-check approved
```

Generate a tree-preserving replay package from approved message candidates:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge message-repair-package `
  --work-id "<work-id>" `
  --target-branch "<branch>" `
  --source-ref "origin/<branch>" `
  --expected-remote-sha "<remote-sha>"
```

Execute that package with the existing replay apply runtime:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github-knowledge rebase-apply `
  --work-id "<work-id>" `
  --package-path "work/<work-id>/context/message-repair-package.json" `
  --human-check approved `
  --push
```

`message-repair-package.json` must contain only approved `message_overrides`. The runtime verifies that the final tree still matches `source_ref`, records before/after SHA mapping, checks the repaired subjects with `git log --format="%H %s"`, and only then returns to GitHub sync.

Create a RAG candidate:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rag-candidate `
  --work-id "<work-id>"
```

After publishing a RAG candidate to the long-lived knowledge area, `rag-candidate` and `next-action` return a work cleanup hint. Confirm the temporary GitHub knowledge work scope through the generic cleanup ctl before removing it:

```powershell
.\runtime\windows-script\aiwf.cmd ctl work cleanup-check --work-id github/original --recursive
.\runtime\windows-script\aiwf.cmd ctl work cleanup-apply --work-id github/original --recursive --human-check approved
```

## Main Artifact

```text
work/<work-id>/context/github-knowledge-analysis.json
```

Schema:

```text
.ariadne/schemas/github-knowledge-analysis.schema.json
```

## Context First

`/github-knowledge-maintenance` は、GitHubを読み取る前に `context-manifest.json` へ次のContextを登録します。

- `tool-selection`: GitHub CLI / GitHub API をどう使うかを記録します。
- `github-operation-gate`: read-only / mutation / clone の許可状態とHuman Check要否を記録します。
- `github-knowledge-analysis`: Issue、Pull Request、docs、CAR、commit情報の調査結果を後続Workflowへ渡します。
- `agent-context` / `artifact-index` / `handoff-package`: 作業領域、成果物、引き継ぎ情報を標準Contextとして扱います。

`repair_mode: proposal` では mutation を許可しません。`repair_mode: apply` の場合も、GitHubへの書き込みは `github-operation-gate` とHuman Review Gateの確認後に行います。

`github-sync-plan` は、analysisが `repair_mode: apply` の場合に `github-operation-gate` と `tool-selection` を必須Contextとして確認します。
`github-sync-review-plan` は、Issue / PR / comment repair action を候補IDごとの OK / NG チェックリストとして出力します。
`github-sync-review-intake` は、チェック済みレポートを読み取り、`github_sync_actions` の `approval_status`、`human_review_decision`、`human_review_source` を更新します。
`github-sync-apply` は、`github_sync_actions` のうち `approval_status: approved` かつ `human_review_decision: OK` の1件だけを実行し、結果をanalysis JSONへ書き戻します。実行可能なcommandは `gh issue edit/comment`、`gh pr edit/comment`、`gh api repos/...` に限定します。
未解決の `history_rewrite_candidates` がある場合、`github-sync-apply` は停止します。rebase候補が検出されなかった場合、または全候補が `rejected` / 明示的な `no-rewrite` / `keep-with-evidence` / `verified` として解決済みの場合だけ、sync系を実施します。
`detect-rebase-candidates` は、ローカルGit履歴から1-3 fileのcommit漏れ候補を検出し、`github-knowledge-analysis.json` の `history_rewrite_candidates` に `approval_status: pending` として記録します。commit subjectが薄い場合は、subjectだけで判断せず、変更path、directory、extension、repository domain、近接commit、関連file setを複合的に確認します。安全な吸収先を自動特定できない場合は `no-rewrite` ではなく `manual-review-required` としてHuman Reviewへ残します。
`rebase-plan` は、検出済み候補からHuman Review用の実行計画レポートを出力します。Git操作は実行しません。
`rebase-apply` は、1つのHuman Check approval packageで承認されたGit CLI commandだけを非対話で実行し、local verification結果をanalysis JSONへ記録します。`--human-check approved` は承認済みパッケージをruntimeへ渡す実行ガードであり、追加の承認依頼ではありません。
`aiwfctl github-knowledge rebase-package` は、承認済みcandidateからschema準拠の `rebase-replay-package.json` を生成します。AIは `work/<work-id>/context/` にrebase用の一時 `*.py` や手書きJSONを作りません。
`aiwfctl github-knowledge rebase-apply` は、承認済みsmall-commit rebase packageをJSON dataとして読み込み、runtime内蔵の非対話replay engineで実行します。検証用checkoutは `work/<work-id>/git-worktree/<branch>/` に限定し、本体checkoutや `main` tree をrewrite検証場所として使いません。
`apply_mode` は `direct` / `git-3way` / `auto-3way` から選びます。通常は `direct` を使い、どうしてもpatch contextが合わない承認済みpackageだけ `git-3way` または明示許可された `auto-3way` を使います。
`rag-candidate --publish-rag` は、RAG publication前に `github-operation-gate` のHuman Check条件を確認します。

## GitHub Access Policy

GitHub CLI / API を優先します。

GitHub CLI が見つからない場合は、先に不足ツールとして記録し、人間承認後に以下を実行します。

```powershell
winget install --id GitHub.cli
```

導入後は新しい terminal を開くか PATH を更新して、以下を確認します。

```powershell
gh --version
gh auth status
```

`GITHUB_TOKEN` は repository root の `.env` に登録されていれば、runtime helper の `load_env()` 経由で利用できます。現在の PowerShell の `$env:GITHUB_TOKEN` に見えない場合でも、`.env` 側の有無を別途確認します。token 値は表示しません。

Clone は、GitHub APIでは取得できない解析が必要で、人間が理由を承認した場合だけ行います。

## GitHub API / Git CLI Responsibility Boundary

- GitHub API / `gh` は、Issue、PR、comment、label、release、remote branch refなどGitHub上のmetadataとcollaboration stateを扱います。private repositoryやmutationでは通常認証が必要です。
- Git CLI local は、commit graph作成、rebase相当の履歴rewrite、before/after SHA mapping、tree diff検証を扱います。local-only操作なので認証は不要です。
- Git CLI remote は、fetch、ls-remote、push、force-with-leaseで検証済みlocal graphをGitHub branchへ反映します。remote操作なので認証が必要です。
- GitHub APIでは `git rebase`、commit graph rewrite、commit message rewriteはできません。GitHub tokenの有無とlocal rebase editorの要否は別問題です。
- runtime自動化では `git rebase -i` のeditor hookに依存しません。非対話のGit CLI local commandで履歴を作り、local verification後にGit CLI remote commandで承認済みbranchへ反映します。
- 承認は1つのapproval packageにまとめます。対象repository、対象branch、rewrite action、rollback plan、local verification command、exact remote update commandを同じ承認単位に含めます。承認後のlocal rewrite、verification、approved remote updateでは、人間への再承認依頼を出しません。

## Git History Policy

基本方針:

- Git履歴そのものを消したり、なかったことにしたりしない。
- ただし、commit source / commit message の不記載・表現不足・内容不足は放置しない。
- GitHub commit list に表示される semantic subject が弱い場合も補修対象にする。
- 1-3 fileの不自然なコミット履歴やcommit漏れは、small rebase整備候補として記録できる。
- commit漏れ整備は、検出、rebase実行計画算出、レポート出力、人間承認後実行の4段に分ける。
- 無駄なcommitに後付けIssueやmessageを付けるだけのrepairは完了扱いにしない。
- small rebase候補は、吸収、分割、drop、または独立責務の根拠付き維持のどれかを `repair_goal` として明示する。
- まずは additive repair を優先する。
- 既存 commit message の rewrite やsmall rebase整備は high-risk path として扱い、人間の明示承認、before/after SHA mapping、rollback plan がある場合だけ行う。

## Semantic Commit Subject Policy

commit message 補修では、subject と body を分けて評価します。

subject は GitHub の commit list だけで意味が通ることを必須にします。

形式:

```text
type(scope): 変更の責務または成果
```

避ける例:

```text
feat(localty): 対応
feat(localty): 修正
feat(localty): README.mdを修正
feat(localty): protocol共通化に伴う対応
```

推奨例:

```text
docs(runtime): supervisor/worker運用契約とprotocol依存をREADMEへ反映
feat(supervisor): worker分離とcontrol安全境界を追加
feat(protocol): UDP port定義をlocalty-system-protocolへ集約
```

body では以下を補います。

- intent
- scope
- decision
- impact
- safety / deployment / protocol boundary
- future AI workflow が再利用すべき知識

詳細は `docs/reference/semantic-commit-message-guideline.md` を参照します。

通常の修復対象:

- PR body補足
- follow-up documentation commit
- README/docs補足
- CAR補足
- commit narrative repair note
- RAG候補生成

high-risk path:

- `git rebase`
- `git commit --amend`
- force push
- Commit SHA変更を伴う commit message rewrite
- 1-3 fileのcommit漏れを既存commitへ整理する非対話Git CLI rewrite

Small rebase整備の完了条件:

- 対象fileは1-3件。
- `detect-rebase-candidates` で候補が `history_rewrite_candidates` に記録されている。
- `rebase-plan` で実行計画レポートが出力されている。
- `rebase-plan` の凡例で、未完了扱い、rebase不要扱い、正当差分として残す扱いを確認する。
- `repair_goal` が `absorb-into-existing-commit`、`drop-empty-or-noise-commit`、`split-into-independent-commit`、`keep-with-evidence`、`manual-review-required`、`no-rewrite` のいずれか。
- `keep-with-evidence` の場合は、独立した責務と既存証跡がある。
- approval packageに `rollback_plan`、`verification_commands`、exact remote update command が記録されている。
- `before_after_sha_mapping` は、承認後のlocal rewrite検証でruntimeが生成して記録する。
- `rebase-apply` は、1つのHuman Check approval packageが承認済みで、候補が `approval_status: approved` の場合だけ非対話Git CLI commandを実行する。`--human-check approved` はその承認済み事実をruntimeに渡す実行ガードであり、追加承認ではない。
- 新しいIssue名やcommit messageを作って、無駄なcommitを正当化するだけでは完了にしない。

Rebase候補の凡例:

| 状態 | 意味 | GitHub反映前の扱い |
| --- | --- | --- |
| `approval_status: pending` | 未判断 | 未完了。GitHub sync apply前に判断する |
| `approval_status: approved` + absorb/split/drop | rebase実行対象 | rebase適用と検証まで未完了 |
| `repair_goal: manual-review-required` | commit資材の内容確認が必要 | 未完了。Human Reviewで吸収、分割、message補修、維持、却下、no-rewriteのいずれかに変更する |
| `repair_goal: keep-with-evidence` | 正当な独立差分として残す | `independent_responsibility` と `evidence_refs` があれば完了 |
| `repair_goal: no-rewrite` | rebase不要 | reasonが記録されていれば完了 |
| `approval_status: rejected` | 候補棄却 | 完了。rebaseしない |

GitHub sync apply の順序:

- rebase候補が0件の場合は、対象操作のHuman Check後に `github-sync-apply` を実行できる。
- rebase候補がある場合は、先に `rebase-plan`、1つのHuman Check approval package、`rebase-apply`、verificationを完了する。
- absorb/split/drop候補は `execution_status: verified` になるまでGitHub sync applyを止める。
- `manual-review-required` 候補は、Human Reviewで具体的な方針に変更されるまでGitHub sync applyを止める。
- `keep-with-evidence` / `no-rewrite` / `rejected` は、凡例の条件を満たせばGitHub sync applyを止めない。

許可:

- Issue更新
- Issueコメント
- PR更新
- PRコメント
- CAR補足
- Documentation補足
- Knowledge DB候補生成
- RAG候補生成
- commit source / message gap の調査と補足案生成

## Human Review Gate

GitHubへ同期する前に、人間が以下を確認します。

- 修正理由
- 修正対象
- 修正前後
- additive repair か、commit message/source correction か
- commit rewrite を伴う場合は before/after SHA mapping と rollback plan
- commit rewrite を伴う場合は GitHub commit list に表示される semantic subject を確認する
- 実行するGitHub CLI/API command

## Completion

- Repositoryを解析した
- Git履歴をなかったことにしていない
- commit rewrite を実行した場合は before/after SHA mapping、tree hash一致、rollback plan を記録した
- 知識資産を抽出した
- Issue / PR / Docs の説明不足を検出した
- commit source / commit message の不記載・表現・内容不足を検出した
- semantic commit subject の弱さを検出し、必要な場合は改善案を生成した
- 修正案を生成した
- 人間レビューを実施した
- 承認済みの説明資産のみ更新した
- Knowledge DB候補を生成した
- 修正で得た内容をRAG候補として生成した
