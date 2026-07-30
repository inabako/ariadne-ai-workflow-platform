# GitHub Actions公開前ローカル予行Evidence

## 概要

- date: 2026-07-31
- target: `.github/workflows`
- runner: `act`
- image: `catthehacker/ubuntu:act-22.04`
- artifact path: `.act-artifacts/workflow-public-readiness-20260731/`
- purpose: OSS公開前に、license / dependency audit workflowが本番相当のjob単位で動作するか確認する。

## 静的検証

- `yamllint`: pass
- `actionlint`: pass
- `git diff --check`: pass
- `act --list`: pass
- `aiwfctl release validate --json`: pass
  - errors: `0`
  - warnings: `28`

`dependency-review` の設定ファイルは `.github/workflows` 配下に置くと `act` がworkflowとして誤検出するため、`.github/config/dependency-review.yml` に配置する。

## ローカル予行結果

| Workflow | Job | Result | Notes |
| --- | --- | --- | --- |
| `.github/workflows/reuse-lint.yml` | `reuse-lint` | pass | artifact uploadまで成功 |
| `.github/workflows/scancode.yml` | `scancode` | pass | ScanCode JSON検証とartifact uploadまで成功 |
| `.github/workflows/dependency-review.yml` | `dependency-review` | expected local fail | GitHub Dependency graph / APIに依存するため、`act` ではDependency Review本体がfail |

## REUSE Lint結果

- status: `pass`
- tool: `reuse 6.2.0`
- used licenses: `AGPL-3.0-or-later`
- files with copyright information: `1591 / 1591`
- files with license information: `1591 / 1591`
- invalid SPDX license expressions: `0`

## ScanCode結果

- status: `pass`
- tool: `ScanCode Toolkit 32.5.0`
- scanned resources: `2146`
- license detections: `50`
- copyright detections: `5`
- package detections: `8`

追加確認では、`unknown` / `proprietary` 系の検出は、CLI引数名、テスト中のSPDX文字列、文書見出し、contribution policy文の誤検出として確認した。
明らかな第三者license / copyright上の懸念は見つかっていない。

## Dependency Review結果

ローカル予行では、GitHub Dependency Review Actionが次の理由でfailした。

```text
Dependency review is not supported on this repository.
Please ensure that Dependency graph is enabled.
```

このworkflowは設定読み込み、失敗時metadata生成、artifact uploadまでは確認済み。
最終確認はGitHub上でDependency graphを有効化した状態の `pull_request` または `workflow_dispatch` で行う。

GitHub CLIではrepositoryが現在 `private` であることは確認できた。
Dependency alerts / Dependency graph設定のAPI確認は、利用中のpersonal access tokenに `administration: read` 相当の権限がなく `403 Forbidden` となった。
Dependency graph有効化後に、ローカルtokenを `GITHUB_TOKEN` secretとして渡して `act` を再実行したが、Dependency Review Action本体は同じ理由でfailした。
そのため、残リスクはworkflow定義ではなく、GitHub上のrepository visibility、Dependency graph、Dependency Review Actionの対応条件、またはGitHub Advanced Security利用可否にある。

## 公開前判断

ローカルで再現可能な範囲では、`.github/workflows` の構文、参照パス、artifact生成、REUSE lint、ScanCodeは公開可能な状態。

公開前にGitHub上で確認が必要な残作業は、Dependency graphを有効化したうえで `.github/workflows/dependency-review.yml` を実行し、`ariadne-dependency-review-results` artifactを確認すること。
private repositoryのまま確認する場合は、GitHub Advanced Securityの利用可否も確認する。

`aiwfctl release validate` のwarningはrelease gate上の確認対象として残っている。
`.env` はgit管理外かつ `.gitignore` 対象だが、ローカルには実値入りのtoken設定が存在するため、公開前にpush対象へ含まれていないことを継続確認する。

このファイルはreview evidenceであり、法的助言ではありません。
