# Runtime GitHub

`runtime/github/` は、GitHub Issue / Pull Request のdraft作成または実作成を扱います。

## Responsibilities

- 要件比較レポートとartifact indexを元に Issue body を作る
- `work/<採番ID>/process-report/` にIssue draftを保存する
- `--create` 指定時のみ GitHub REST API でIssueを作成する
- Issue番号を `github-issue-*.json` に記録する
- Issue branch作成時のGitHub GraphQL linked branch登録を支援する
- Issue branch push後の Pull Request draft / create を扱う

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

`GITHUB_OWNER` を設定すると、`target-system` のようなrepository名だけの指定を `<GITHUB_OWNER>/target-system` として解決できます。

`--github-repo` が未指定の場合、`scm-state.json` の repository を使います。

repository は要件定義書の `Repository Control` から `aiwfctl scm prepare` が解決します。`.env` に repository fallback は置きません。

ただし、`aiwfctl scm prepare` 済みの案件では、`work/<採番ID>/context/scm-state.json` の repository から GitHub repository を解決できます。

`--label` / `--assignee` が未指定の場合、`DEFAULT_GITHUB_ISSUE_LABELS` / `DEFAULT_GITHUB_ISSUE_ASSIGNEES` をカンマ区切りで読みます。

## Issue Title Prefix

Issue title は workflow に応じてprefixを付けます。

| Flow | Prefix |
| --- | --- |
| New feature / maintenance | `[新規機能フロー]` |
| Corrective action / docs sync | `[改善フロー]` |
| New system / initial development | `[初期開発]` |
| Realtime IaC | `[IaC]` |

`aiwfctl github issue` は `--flow-label` または `--title-prefix` でprefixを付与できます。

## Issue Body Template

Issue body のsourceは次の優先順位で決定します。

1. `--body-file` で明示されたMarkdown
2. target repository の `.github/ISSUE_TEMPLATE.md`
3. `aiwfctl github issue` のruntime fallback本文

target repository templateを使う場合、`Report`、`Target branch`、`Target commit` の空欄は、利用可能なworkflow contextから自動補完します。

## CLI

```text
aiwfctl github issue
aiwfctl github pr
aiwfctl scm branch --link-to-issue
```

## Example

Draft only:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github issue `
  --work-id WF-20260601-090000 `
  --github-repo owner/repository `
  --title "Add remote gateway skeleton" `
  --flow-label initial-development
```

Create GitHub Issue:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github issue `
  --work-id WF-20260601-090000 `
  --github-repo owner/repository `
  --title "Add remote gateway skeleton" `
  --flow-label initial-development `
  --label enhancement `
  --create
```

Create Pull Request after the issue branch has been pushed:

```powershell
.\runtime\windows-script\aiwf.cmd ctl github pr `
  --work-id issue-11 `
  --base develop `
  --create `
  --human-check approved
```

## Network Rule

Issue creation requires network access and GitHub API token authentication.

By default, this runtime creates local drafts only. It calls GitHub only when `--create` is explicitly specified.

Pull Request creation also requires `--create --human-check approved`.

Issue linked branch creation is handled during `aiwfctl scm branch --link-to-issue`. It uses GitHub GraphQL `createLinkedBranch` after the GitHub Issue number is available.
