# Pre-development Preparation Flow

## Purpose

新規機能および保守開発の開始前に、対象repository、要件定義書、GitHub Issue、作業branchを揃えるための flow です。

このflowは、実装前に作業対象と責任範囲を固定し、成果物とsource差分を追跡できる状態にします。

## Entry Conditions

- 完成版の要件定義書が `work/requirements/` に配置されている
- 対象GitHub repository が要件定義書の `Repository Control` で決まっている
- target branch が要件定義書、CLI引数、または `.env` で決まっている
- 新規機能または保守開発として作業を開始する

`work/requirements/` に要件定義書が無い場合は、Skill からオーダーされても intake harness で受領拒否する。

`work/requirements/` に要件定義書が2件以上ある場合も、どの要件を処理するか曖昧なため受領拒否する。標準運用は `1 requirement file = 1 receipt ID` とする。

要件定義書に repository が記載されていない場合も受領拒否する。対象repositoryを `.env` のfallbackで補完してはいけない。

## Phase 0: Intake

`work/requirements/` の完成版要件定義書を受付ID単位の作業領域へ移動します。

Runtime:

```text
runtime/intake/intake_requirements.py
```

出力:

- `work/<採番ID>/design-document/<requirements>`
- `work/<採番ID>/context/agent-context.json`
- `work/<採番ID>/context/artifact-index.json`

## Phase 1: Repository Sync

GitHubから対象repository / target branch を取得します。

Runtime:

```text
runtime/scm/prepare_repository.py
```

出力:

- `work/<採番ID>/source/repository/`
- `work/<採番ID>/context/scm-state.json`

確認:

- 要件定義書の `Repository Control` が読み取れるか
- target branch が最新か
- source directory が正しいか
- current commit が記録されているか

Repository resolution priority:

```text
CLI argument
  -> requirement document Repository Control
```

## Phase 2: Requirement Comparison

要件定義書と対象repositoryの現在状態を比較し、Issue化するための材料を作ります。

Runtime:

```text
runtime/scm/compare_requirements.py
```

出力:

- `work/<採番ID>/process-report/requirement-comparison-*.md`
- `work/<採番ID>/process-report/requirement-comparison-*.json`

確認:

- 要件定義書がartifactとして登録されているか
- repository branch / commit が明示されているか
- 既存実装、docs、仕様との差分観点が記録されているか

## Phase 3: GitHub Issue Draft / Create

修正内容、目的、影響範囲、成果物予定を対象repositoryのGitHub Issueへ記載します。

Runtime:

```text
runtime/github/issue_manager.py
```

出力:

- `work/<採番ID>/process-report/github-issue-*.md`
- `work/<採番ID>/process-report/github-issue-*.json`
- GitHub Issue number when `--create` is used

確認:

- Issue本文に Intent、Repository State、Scope、Artifacts、Acceptance Criteria が含まれているか
- Issue番号が取得できているか
- 未作成の場合、draft status として残っているか

## Phase 4: Working Branch Create

Issue番号をもとに作業branchを作成します。

Runtime:

```text
runtime/scm/create_issue_branch.py
```

branch naming:

```text
feature/issue-<issue-number>
```

確認:

- working branch が `feature/issue-<issue-number>` であるか
- `scm-state.json` に issue number と working branch が記録されているか

## Phase 5: Development Workflow

新規機能または保守開発の本体flowへ進みます。

代表例:

- `/new-robotics-system-development`
- `/robotics-maintenance-development`
- `/robotics-safety-gates`
- `/robotics-test-strategy`

## Phase 6: Commit

成果物とsource差分を作業branchにcommitします。

Runtime:

```text
runtime/scm/commit_changes.py
```

Commit message rule:

```text
feat: add remote gateway skeleton
fix: correct telemetry timeout handling
docs: update robotics safety gate
test: add communication loss regression
```

許可するtype:

- feat
- fix
- docs
- style
- refactor
- test
- chore
- build
- ci
- perf
- revert

Quality Gate:

- semantic commit 形式でないcommit messageは不可
- Issue番号branchでない場合は理由を記録する
- safety-critical QA が未解決の場合は実装commitの前にblockerとして扱う
