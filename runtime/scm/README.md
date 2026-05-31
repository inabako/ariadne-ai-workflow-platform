# Runtime SCM

`runtime/scm/` は、target repository の取得、要件比較、Issue番号branch作成、semantic commit を扱います。

## Responsibilities

- GitHub / git repository から target branch を取得する
- `work/<採番ID>/source/repository/` を準備する
- 要件定義書と repository state の比較レポートを作成する
- Issue番号から `feature/issue-<issue-number>` branch を作成する
- semantic commit message を検証して commit する

## Environment

SCM連携に必要な値は repository root の `.env` から読み込みます。

主なキー:

- `GIT_USER_NAME`
- `GIT_USER_EMAIL`
- `DEFAULT_GIT_REMOTE_NAME`
- `DEFAULT_GIT_TARGET_BRANCH`
- `DEFAULT_FEATURE_BRANCH_PREFIX`

`commit_changes.py` は、`GIT_USER_NAME` / `GIT_USER_EMAIL` が設定されている場合、対象repositoryのlocal git configへ反映してからcommitします。

`create_issue_branch.py` は、`--branch-prefix` が未指定の場合、`DEFAULT_FEATURE_BRANCH_PREFIX` を使います。

`prepare_repository.py` は、`--remote` が未指定の場合、`DEFAULT_GIT_REMOTE_NAME` を使います。

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
runtime/scm/compare_requirements.py
runtime/scm/create_issue_branch.py
runtime/scm/commit_changes.py
```

## Example

```powershell
python runtime/scm/prepare_repository.py `
  --work-id WF-20260601-090000 `
  --repository https://github.com/example/robot.git `
  --target-branch main

python runtime/scm/compare_requirements.py `
  --work-id WF-20260601-090000

python runtime/scm/create_issue_branch.py `
  --work-id WF-20260601-090000 `
  --issue-number 123

python runtime/scm/commit_changes.py `
  --work-id WF-20260601-090000 `
  --all `
  --message "feat: add remote gateway skeleton"
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
