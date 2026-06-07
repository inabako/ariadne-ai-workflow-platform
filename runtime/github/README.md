# Runtime GitHub

`runtime/github/` は、GitHub Issue のdraft作成または実作成を扱います。

## Responsibilities

- 要件比較レポートとartifact indexを元に Issue body を作る
- `work/<採番ID>/process-report/` にIssue draftを保存する
- `--create` 指定時のみ GitHub REST API でIssueを作成する
- Issue番号を `github-issue-*.json` に記録する
- Issue branch作成時のGitHub GraphQL linked branch登録を支援する

## Environment

GitHub連携に必要な値は repository root の `.env` から読み込みます。

必須キー:

- `GITHUB_TOKEN`

任意キー:

- `GH_HOST`
- `GITHUB_API_URL`
- `GITHUB_GRAPHQL_URL`
- `GITHUB_OWNER`
- `DEFAULT_GITHUB_ISSUE_LABELS`
- `DEFAULT_GITHUB_ISSUE_ASSIGNEES`

`GITHUB_TOKEN` には、対象repositoryのIssue作成権限を持つGitHub Personal Access Tokenまたはfine-grained tokenを設定します。互換キーとして `GH_TOKEN` / `GITHUB_API_TOKEN` / `GITHUB_API_KEY` も読み取れます。

`GH_HOST` / `GITHUB_API_URL` は通常不要です。未指定の場合、REST API endpoint は `https://api.github.com`、GraphQL endpoint は `https://api.github.com/graphql` です。GitHub Enterprise Server などで明示したい場合だけ `GITHUB_API_URL` に `https://<host>/api/v3` 形式で指定できます。GraphQL endpointだけを上書きする場合は `GITHUB_GRAPHQL_URL` を指定します。

`GITHUB_OWNER` を設定すると、`localty-system-gui` のようなrepository名だけの指定を `<GITHUB_OWNER>/localty-system-gui` として解決できます。

`--github-repo` が未指定の場合、`scm-state.json` の repository を使います。

repository は要件定義書の `Repository Control` から `runtime/scm/prepare_repository.py` が解決します。`.env` に repository fallback は置きません。

ただし、`runtime/scm/prepare_repository.py` 済みの案件では、`work/<採番ID>/context/scm-state.json` の repository から GitHub repository を解決できます。

`--label` / `--assignee` が未指定の場合、`DEFAULT_GITHUB_ISSUE_LABELS` / `DEFAULT_GITHUB_ISSUE_ASSIGNEES` をカンマ区切りで読みます。

## CLI

```text
runtime/github/issue_manager.py
runtime/scm/create_issue_branch.py --link-to-issue
```

## Example

Draft only:

```powershell
python runtime/github/issue_manager.py `
  --work-id WF-20260601-090000 `
  --github-repo owner/repository `
  --title "Add remote gateway skeleton"
```

Create GitHub Issue:

```powershell
python runtime/github/issue_manager.py `
  --work-id WF-20260601-090000 `
  --github-repo owner/repository `
  --title "Add remote gateway skeleton" `
  --label enhancement `
  --create
```

## Network Rule

Issue creation requires network access and GitHub API token authentication.

By default, this runtime creates a local draft only. It calls GitHub only when `--create` is explicitly specified.

Issue linked branch creation is handled during `runtime/scm/create_issue_branch.py --link-to-issue`. It uses GitHub GraphQL `createLinkedBranch` after the GitHub Issue number is available.
