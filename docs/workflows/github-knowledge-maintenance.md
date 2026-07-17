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

Initialize:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py init `
  --repository "<target-repository>" `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output
```

Create the analysis scaffold:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py analysis-template `
  --work-id "<work-id>"
```

Create a human review repair plan:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py repair-plan `
  --work-id "<work-id>"
```

Detect 1-3 file commit leakage candidates from local Git history:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py detect-rebase-candidates `
  --work-id "<work-id>" `
  --base "HEAD~30" `
  --head "HEAD"
```

Create the GitHub sync plan:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py github-sync-plan `
  --work-id "<work-id>"
```

Execute one approved GitHub sync action:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py github-sync-apply `
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
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py rebase-plan `
  --work-id "<work-id>"
```

Execute an approved rebase candidate after Human Check:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py rebase-apply `
  --work-id "<work-id>" `
  --candidate-id "<candidate-id>" `
  --human-check approved
```

Create a RAG candidate:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
  --work-id "<work-id>"
```

## Main Artifact

```text
work/<work-id>/context/github-knowledge-analysis.json
```

Schema:

```text
.github/schemas/github-knowledge-analysis.schema.json
```

## Context First

`/github-knowledge-maintenance` は、GitHubを読み取る前に `context-manifest.json` へ次のContextを登録します。

- `tool-selection`: GitHub CLI / GitHub API をどう使うかを記録します。
- `github-operation-gate`: read-only / mutation / clone の許可状態とHuman Check要否を記録します。
- `github-knowledge-analysis`: Issue、Pull Request、docs、CAR、commit情報の調査結果を後続Workflowへ渡します。
- `agent-context` / `artifact-index` / `handoff-package`: 作業領域、成果物、引き継ぎ情報を標準Contextとして扱います。

`repair_mode: proposal` では mutation を許可しません。`repair_mode: apply` の場合も、GitHubへの書き込みは `github-operation-gate` とHuman Review Gateの確認後に行います。

`github-sync-plan` は、analysisが `repair_mode: apply` の場合に `github-operation-gate` と `tool-selection` を必須Contextとして確認します。
`github-sync-apply` は、`github_sync_actions` のうち `approval_status: approved` の1件だけを実行し、結果をanalysis JSONへ書き戻します。実行可能なcommandは `gh issue edit/comment`、`gh pr edit/comment`、`gh api repos/...` に限定します。
未解決の `history_rewrite_candidates` がある場合、`github-sync-apply` は停止します。rebase候補が検出されなかった場合、または全候補が `rejected` / `no-rewrite` / `keep-with-evidence` / `verified` として解決済みの場合だけ、sync系を実施します。
`detect-rebase-candidates` は、ローカルGit履歴から1-3 fileのcommit漏れ候補を検出し、`github-knowledge-analysis.json` の `history_rewrite_candidates` に `approval_status: pending` として記録します。
`rebase-plan` は、検出済み候補からHuman Review用の実行計画レポートを出力します。Git操作は実行しません。
`rebase-apply` は、`--human-check approved` と候補の `approval_status: approved` が両方そろった場合だけ、承認済みのGit commandを実行します。
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
- 1-3 fileのcommit漏れを既存commitへ整理するinteractive rebase

Small rebase整備の完了条件:

- 対象fileは1-3件。
- `detect-rebase-candidates` で候補が `history_rewrite_candidates` に記録されている。
- `rebase-plan` で実行計画レポートが出力されている。
- `rebase-plan` の凡例で、未完了扱い、rebase不要扱い、正当差分として残す扱いを確認する。
- `repair_goal` が `absorb-into-existing-commit`、`drop-empty-or-noise-commit`、`split-into-independent-commit`、`keep-with-evidence`、`no-rewrite` のいずれか。
- `keep-with-evidence` の場合は、独立した責務と既存証跡がある。
- `before_after_sha_mapping`、`rollback_plan`、`verification_commands` が記録されている。
- `rebase-apply` は、Human Check承認済み、かつ候補が `approval_status: approved` の場合だけ実行する。
- 新しいIssue名やcommit messageを作って、無駄なcommitを正当化するだけでは完了にしない。

Rebase候補の凡例:

| 状態 | 意味 | GitHub反映前の扱い |
| --- | --- | --- |
| `approval_status: pending` | 未判断 | 未完了。GitHub sync apply前に判断する |
| `approval_status: approved` + absorb/split/drop | rebase実行対象 | rebase適用と検証まで未完了 |
| `repair_goal: keep-with-evidence` | 正当な独立差分として残す | `independent_responsibility` と `evidence_refs` があれば完了 |
| `repair_goal: no-rewrite` | rebase不要 | reasonが記録されていれば完了 |
| `approval_status: rejected` | 候補棄却 | 完了。rebaseしない |

GitHub sync apply の順序:

- rebase候補が0件の場合は、Human Check後に `github-sync-apply` を実行できる。
- rebase候補がある場合は、先に `rebase-plan`、Human Check、`rebase-apply`、verificationを完了する。
- absorb/split/drop候補は `execution_status: verified` になるまでGitHub sync applyを止める。
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
