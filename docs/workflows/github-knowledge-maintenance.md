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
- まずは additive repair を優先する。
- 既存 commit message の rewrite は high-risk path として扱い、人間の明示承認、before/after SHA mapping、rollback plan がある場合だけ行う。

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
