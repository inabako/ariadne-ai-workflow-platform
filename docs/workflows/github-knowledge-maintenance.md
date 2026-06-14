# GitHub Knowledge Maintenance

`/github-knowledge-maintenance` は、GitHub Repositoryを長期的な知識資産として保守するworkflowです。

Git履歴やsource codeは変更せず、Issue、Pull Request、comment、docs、Corrective Action Report、Knowledge DB候補、RAG候補を整えます。

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
uv run python runtime/workflow/github_knowledge_maintenance.py init `
  --repository "<target-repository>" `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output
```

Create the analysis scaffold:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py analysis-template `
  --work-id "<work-id>"
```

Create a human review repair plan:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py repair-plan `
  --work-id "<work-id>"
```

Create the GitHub sync plan:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py github-sync-plan `
  --work-id "<work-id>"
```

Create a RAG candidate:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
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

## GitHub Access Policy

GitHub CLI / API を優先します。

Clone は、GitHub APIでは取得できない解析が必要で、人間が理由を承認した場合だけ行います。

## Git History Policy

禁止:

- `git rebase`
- `git commit --amend`
- force push
- Commit SHA変更
- Git履歴変更
- source code改変

許可:

- Issue更新
- Issueコメント
- PR更新
- PRコメント
- CAR補足
- Documentation補足
- Knowledge DB候補生成
- RAG候補生成

## Human Review Gate

GitHubへ同期する前に、人間が以下を確認します。

- 修正理由
- 修正対象
- 修正前後
- Git履歴を変更しないこと
- 実行するGitHub CLI/API command

## Completion

- Repositoryを解析した
- Git履歴を変更していない
- 知識資産を抽出した
- Issue / PR / Docs の説明不足を検出した
- 修正案を生成した
- 人間レビューを実施した
- 承認済みの説明資産のみ更新した
- Knowledge DB候補を生成した
- RAG候補を生成した
