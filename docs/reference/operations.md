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
- close archive準備 / prune
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
docs: update target-system safety gate
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

必要tool、Python module、MSYS2 package、support repositoryが不足している場合は、install listを作って止まります。installは人間承認後にだけ行います。

```powershell
python runtime/environment/preflight.py `
  --profile corrective-action-fix `
  --work-id "<work-id>"
```

## Encoding / Mojibake Gate

source fileにmojibakeが見える場合は、workflow concernとして扱います。

例:

- `邵ｺ`
- `郢ｧ`
- `隴`
- `隰`
- `・ｽ`

base checkoutで見つけた場合は、base branchを直接編集せず、reportまたはIssue bodyへ記録します。issue branch作成後にtarget repositoryへ `.editorconfig` を追加し、editor / session reload後に再読み込みします。

`.bat` / `.cmd` がShift_JIS / CP932を意図している場合は、UTF-8へ一括変換しません。

## Report-only Close Archive

`work/close` は、完了作業のsource checkoutや一時ファイルを保持する場所ではありません。作業報告、判断履歴、検証結果、参照リンクだけを残すreport-only archiveです。
close archive作成時は、RAGに吸収した具体内容を自動で読み取り、標準レポートへ要約・参照リンクとして反映します。

今後は肥大化を避けるため、workflow種別ごとに棚を分けます。

| 種別 | 保存先 |
| --- | --- |
| 改善フロー / docs-sync / corrective action | `work/close/improvement/issue-<issue-number>/` |
| 新システム開発フロー | `work/close/new-system-dev/issue-<issue-number>/` |
| GitHub knowledge maintenance | `work/close/github/YYMMDDHHmmss_<random>/` |
| VSCode Environment | `work/close/vscode/YYMMDDHHmmss_<random>/` |

各archiveの目標構成は共通です。

```text
work/close/<category>/<archive-id>/
  00-summary.md
  01-work-report.md
  02-test-report.md
  03-review-report.md
  04-human-check.md
  05-retrospective.md
  links.md
  metadata.json
```

改善フローの作成・監査:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . close-archive prepare --issue issue-<issue-number>
uv run --project runtime python runtime/ctl.py --repo-root . close-archive audit --issue issue-<issue-number>
```

RAG sourceを必ず反映したい場合:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . close-archive prepare `
  --issue issue-<issue-number> `
  --source-rag rag/normalized/<rag-source>.md `
  --require-rag
```

`prepare` は既定でRAG sourceを自動検出します。重要なRAG sourceは `--source-rag` で明示し、抜け漏れを失敗として扱う場合は `--require-rag` を付けます。明示指定したRAGだけを使う場合は `--no-auto-rag` を付けます。

新システム開発フロー:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . close-archive prepare `
  --issue issue-<issue-number> `
  --category new-system-dev
```

GitHub knowledge maintenance:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . close-archive prepare `
  --work-id github-knowledge-localty-system-robot-recent `
  --category github
```

VSCode Environment:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . close-archive prepare `
  --work-id vscode-environment `
  --category vscode
```

`github` と `vscode` は `prepare` 時に `YYMMDDHHmmss_<random>` のarchive-idを生成します。以後のaudit / pruneでは、出力された `archive_id` または `archive_dir` を指定します。

削除対象になる重い成果物:

- `source/`
- `repository/`
- `.git/`
- `.venv/`
- `node_modules/`
- `dist/`
- `build/`
- `.pytest_cache/`
- `__pycache__/`
- 8つのreport-onlyファイル以外の旧作業ディレクトリ

削除は必ずdry-run確認後、人間承認付きで実行します。

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . close-archive prune --issue issue-<issue-number>
uv run --project runtime python runtime/ctl.py --repo-root . close-archive prune `
  --issue issue-<issue-number> `
  --execute `
  --human-check approved
```

base work folderを削除する前に、base phaseのprocess reportは `links.md` とsummary reportへ要約・リンク化します。確認と人間承認後にだけ、base work folderを削除します。

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

## Runtime Human Gate Registry

人間承認が必要な操作は `db/registries/registry.duckdb` にも機械可読形式で定義します。
構造定義は `.github/schemas/human-gates.schema.json` に置きます。
責任分離を明確にするため、`db/registries/` はruntime横断のregistry実体、`.github/schemas/` はschema定義専用とします。
`registry.duckdb` の `human_gates` registry payload には `$schema` と `schema_version` を置かず、registry自体の版は `registry_version` で表します。

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . human-gate list
uv run --project runtime python runtime/ctl.py --repo-root . human-gate check --gate close-prune --human-check approved
```

詳細は [Human Gate Registry](human-gates.md) を参照します。

## Local Workspace Tracking Policy

GitHubにはworkflow本体と、再現に必要なdocs / schema / prompt / testを上げます。

- `work/**/README.md` は追跡対象
- `work/**` の作業実体は追跡しない
- `work/db/**` はknowledge source cloneなのでAriadne本体では追跡しない
- `rag/**` はREADMEも含めてAriadne本体では追跡しない

RAG source of truthは、標準では `work/db/ariadne-knowledge-platform` にcloneした `ariadne-knowledge-platform` repository側へ置きます。Ariadne本体側の `rag/` はDuckDB、evidence、retrieval resultなどのlocal生成workspaceです。

確認は次で行います。

```powershell
python runtime/workflow/workflow_doctor.py
```
