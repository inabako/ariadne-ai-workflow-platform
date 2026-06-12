# Runtime SCM

`runtime/scm/` は、target repository の取得、要件比較、Issue番号branch作成、semantic commit を扱います。

## Responsibilities

- GitHub / git repository から target branch を取得する
- `work/<採番ID>/source/repository/` を準備する
- precreated-new repository modeで `work/<採番ID>/source/repository/` を初期git repository化し、作成済みGitHub repositoryへ初回branchをpushする
- RAGで判明したsupport repositoryを `work/<採番ID>/source/<name>/` に準備する
- 要件定義書と repository state の比較レポートを作成する
- Issue番号から GitHub 上に `feature/issue-<issue-number>` branch を作成し、そのbranchをwork配下へclone / checkoutする
- 必要に応じてIssue branchをGitHub linked branchとして作成する
- semantic commit message を検証して commit する

## Environment

SCM連携に必要な値は repository root の `.env` から読み込みます。

主なキー:

- `GIT_USER_NAME`
- `GIT_USER_EMAIL`
- `GITHUB_OWNER`
- `GITHUB_TOKEN`
- `DEFAULT_GIT_REMOTE_NAME`
- `DEFAULT_GIT_TARGET_BRANCH`
- `DEFAULT_FEATURE_BRANCH_PREFIX`

`commit_changes.py` は、`GIT_USER_NAME` / `GIT_USER_EMAIL` が設定されている場合、対象repositoryのlocal git configへ反映してからcommitします。

`push_branch.py` は、HTTPS remote へのpush時に `GITHUB_TOKEN` が設定されていれば一時的な `GIT_ASKPASS` 経由で認証に使います。token はremote URLやgit configには保存しません。SSH remote または既存のgit credentialがある場合は、それらも利用できます。

`GITHUB_OWNER` を設定すると、`localty-system-gui` のようなrepository名だけの指定を `<GITHUB_OWNER>/localty-system-gui` として解決し、clone URLやGitHub branch作成に使います。

`create_issue_branch.py` は、既定ではGitHub上にbranchを先に作成してから、`work/<id>/source/repository/` にそのbranchをclone / checkoutします。`--link-to-issue` を指定すると、GitHub GraphQL `createLinkedBranch` でIssueに紐づくbranchとして作成します。`--branch-prefix` が未指定の場合、`DEFAULT_FEATURE_BRANCH_PREFIX` を使います。従来のローカルbranch作成だけを行う場合は `--local-only` を指定します。

`prepare_repository.py` は、`--remote` が未指定の場合、`DEFAULT_GIT_REMOTE_NAME` を使います。

`prepare_support_repository.py` は、RAGやpreflightで必要と判明したsupport repositoryを `work/<id>/source/<name>/` にclone / checkoutします。実行結果は `work/<id>/context/support-repositories.json` と `work/<id>/process-report/support-repository-<name>.json` に残します。

## Requirement Repository Control

`prepare_repository.py` は、`--repository` / `--target-branch` が未指定の場合、受付済み要件定義書の `Repository Control` 欄を読み取ります。

Resolution priority:

```text
CLI argument
  -> requirement document Repository Control
```

Supported fields:

- `Target Repository`
- `GitHub Owner`
- `GitHub Repository`
- `GitHub Repository URL`
- `Target Branch`
- `Base Branch`
- `Git Remote`

## CLI

```text
runtime/scm/prepare_repository.py
runtime/scm/prepare_support_repository.py
runtime/scm/compare_requirements.py
runtime/scm/bootstrap_repository.py
runtime/scm/create_issue_branch.py
runtime/scm/commit_changes.py
runtime/scm/push_branch.py
```

## Example

```powershell
python runtime/scm/create_issue_branch.py `
  --work-id issue-123 `
  --issue-number 123 `
  --repository https://github.com/example/robot.git `
  --base-branch main `
  --link-to-issue

python runtime/scm/prepare_support_repository.py `
  --work-id issue-123 `
  --name localty-system-protocol `
  --repository inabako/localty-system-protocol `
  --branch develop

python runtime/scm/commit_changes.py `
  --work-id issue-123 `
  --all `
  --message "feat: add remote gateway skeleton"

python runtime/scm/bootstrap_repository.py `
  --work-id WF-20260601-090000 `
  --github-repo owner/new-iac-repository `
  --push `
  --human-check approved

python runtime/scm/push_branch.py `
  --work-id issue-123 `
  --human-check approved `
  --set-upstream
```

## Branch Rule

```text
feature/issue-<issue-number>
```

## Commit Rule

Semantic commit を必須にします。

Allowed examples:

- `feat: add remote gateway skeleton`
- `fix: correct telemetry timeout handling`
- `docs: update robotics safety gate`
- `test: add communication loss regression`
