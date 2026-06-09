# Operations

このページは、workflow運用で迷いやすい共通ルールをまとめます。

## Human Approval Gates

次の操作は、人間承認なしに進めません。

- GitHub Issue 作成
- Pull Request 作成
- GitHub branch 作成
- missing tool / package のinstall
- 実機または外部I/Oを伴うstartup / integration check
- push
- RAG登録 / rebuild
- archive移動
- base work削除

## Commit Rule

Branch:

```text
feature/issue-<issue-number>
```

Semantic commit examples:

```text
feat: add remote gateway skeleton
fix: correct telemetry timeout handling
docs: update robotics safety gate
test: add communication loss regression
chore: update workflow skill index
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

## Environment Preflight

必要tool、Python module、MSYS2 package、support repositoryが不足している場合は、install listを作って止まります。

installは人間承認後にだけ行います。

```powershell
python runtime/environment/preflight.py `
  --profile corrective-action-fix `
  --work-id "<work-id>"
```

## Encoding / Mojibake Gate

source fileにmojibakeが見える場合、workflow concernとして扱います。

例:

- `縺`
- `繧`
- `譁`
- `謗`
- `�`

base checkoutで見つけた場合は、base branchを編集せずreportまたはIssue bodyに記録します。

issue branch作成後に、target repositoryへ `.editorconfig` を追加し、editor / session reload後に再読込します。

`.bat` / `.cmd` がShift_JIS / CP932を意図している場合は、UTF-8へ一括変換しません。

## Archive

完了したissue work folderは、承認後に次へ移動します。

```text
work/issue-<issue-number>
  -> work/close/issue-<issue-number>
```

base work folderを削除する前に、base phaseのprocess reportを保存します。

```text
work/<base-work-id>/process-report
  -> work/close/<issue-id>/process-report/base-work-<base-work-id>
```

copy確認と人間承認後にだけ、base work folderを削除します。
## GitHub Title Rules

Issue title は、workflowに応じて次のprefixを付けます。

| Workflow | Prefix |
| --- | --- |
| 新規機能追加 / 保守開発 | `[新規機能フロー]` |
| 改善 / corrective action / docs sync | `[改善フロー]` |
| 新システム / 初期開発 | `[初期開発]` |

Pull Request title は、対応するGitHub Issue titleを使います。

Issue branchをpushした後、`develop` へPull Requestを送信します。

Pull Request bodyには、変更点のMermaid式sequence diagramを含めます。
