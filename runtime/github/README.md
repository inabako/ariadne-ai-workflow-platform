# Runtime GitHub

`runtime/github/` は、GitHub Issue のdraft作成または実作成を扱います。

## Responsibilities

- 要件比較レポートとartifact indexを元に Issue body を作る
- `work/<採番ID>/process-report/` にIssue draftを保存する
- `--create` 指定時のみ GitHub CLI でIssueを作成する
- Issue番号を `github-issue-*.json` に記録する

## Environment

GitHub連携に必要な値は repository root の `.env` から読み込みます。

主なキー:

- `GITHUB_AUTH_METHOD`
- `GITHUB_TOKEN`
- `GH_HOST`
- `DEFAULT_GITHUB_ISSUE_LABELS`
- `DEFAULT_GITHUB_ISSUE_ASSIGNEES`

`--github-repo` が未指定の場合、`scm-state.json` の repository を使います。

repository は要件定義書の `Repository Control` から `runtime/scm/prepare_repository.py` が解決します。`.env` に repository fallback は置きません。

ただし、`runtime/scm/prepare_repository.py` 済みの案件では、`work/<採番ID>/context/scm-state.json` の repository から GitHub repository を解決できます。

`--label` / `--assignee` が未指定の場合、`DEFAULT_GITHUB_ISSUE_LABELS` / `DEFAULT_GITHUB_ISSUE_ASSIGNEES` をカンマ区切りで読みます。

## CLI

```text
runtime/github/issue_manager.py
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

Issue creation requires network access and GitHub CLI authentication.

By default, this runtime creates a local draft only. It calls GitHub only when `--create` is explicitly specified.
