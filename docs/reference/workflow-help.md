# Workflow Help CLI

この文書は、AI workflow prompt command のヘルプをターミナルから確認するための `aiwfctl` 入口を説明します。

## 目的

AI workflow は command、Skill、prompt、runtime helper、docs が分かれています。
そのため、作業前に次を素早く確認できる入口を用意します。

- prompt command の正確なスペル
- 前提条件
- 必須引数
- 任意引数
- 引数に設定するべき内容
- 処理の概要
- 処理の詳細
- 関連するSkill、prompt、runtime、docs
- SVG GUI / Web SVG などの親workflow内拡張

## 入口

PowerShell:

```powershell
.\runtime\tools\aiwfctl.cmd help
```

cmd:

```cmd
runtime\tools\aiwfctl.cmd help
```

VSCode統合ターミナルでは `.vscode/settings.json` が `${workspaceFolder}\runtime\tools` を `PATH` に追加するため、次のように呼び出せます。

```powershell
aiwfctl help
```

既に開いているterminalにはPATH変更が反映されません。VSCodeのterminalを閉じて開き直してください。

現在のPowerShellだけ一時的にPATHを通す場合:

```powershell
$env:Path = "$PWD\runtime\tools;$env:Path"
aiwfctl help list
```

PATH未反映のterminalでは、次のように直接呼び出せます。

```powershell
.\runtime\tools\aiwfctl.cmd help list
```

通常のPowerShellやWindows Terminalからも `aiwfctl` とだけ呼びたい場合は、User Pathへ登録します。

```powershell
.\runtime\tools\register-aiwfctl-path.cmd
```

`aiwfctl.cmd` から呼ぶ場合:

```powershell
.\runtime\tools\aiwfctl.cmd path register
```

登録状態を確認する場合:

```powershell
.\runtime\tools\aiwfctl.cmd path check
```

登録後、新しいPowerShellを開いてから確認します。
Windows Terminal や VSCode 本体を登録前から開いていた場合は、そのアプリ自体を閉じて開き直してください。同じアプリ内の新規タブでは古い環境を継承する場合があります。

登録後、すぐに `aiwfctl` が使えるPowerShell sessionを開く場合:

```powershell
.\runtime\tools\register-aiwfctl-path.cmd --shell
```

`aiwfctl.cmd` から登録と更新済みsession起動をまとめて行う場合:

```powershell
.\runtime\tools\aiwfctl.cmd path shell
```

VSCode taskから実行する場合:

```text
workflow:aiwfctl-path-shell
```

```powershell
Get-Command aiwfctl
aiwfctl help list
```

User Path登録後に現在のPowerShellへ反映する場合は、現在のPATHを壊さないように `runtime\tools` だけを先頭追加します。

```powershell
$env:Path = "$PWD\runtime\tools;$env:Path"
```

repo root の `runtime/tools` がPATHに入っている場合も、`aiwfctl help` で呼び出せます。

PowerShell のExecutionPolicyに依存しないよう、標準入口は `.ps1` ではなく `.cmd` に統一します。

## Environment Selection

実行環境を選択する場合は `aiwfctl env` を使います。

```powershell
aiwfctl env
aiwfctl env list
aiwfctl env show gui-mode
aiwfctl env select gui-mode
aiwfctl env select web-svg
aiwfctl env select docker
```

`gui-mode` / `web-svg` / `docker` は利用者向けEnvironment名です。`windows-msys2-gui` などの内部Backend名は表示情報として扱います。

判断不能な場合は `human-check-required` を返します。作業証跡と後続Workflow用contextとして保存する場合は `--work-id` を指定します。

```powershell
aiwfctl env select gui-mode --work-id issue-123
```

この場合、詳細ログは `work/<work-id>/process-report/` に、標準Contextは `work/<work-id>/context/environment-selection.json` に保存されます。同時に `work/<work-id>/context/context-manifest.json` へ登録されます。

## よく使う操作

workflow command 一覧:

```powershell
aiwfctl help list
```

`help list` は slash command と workflow extension を分けて表示します。
SVG系は standalone command ではないため、`Workflow Extensions` に表示されます。
各項目では、`必須:` の下に該当する `docs:` の相対pathを表示します。

command詳細:

```powershell
aiwfctl help show /corrective-action-fix
aiwfctl help show gui-mode
aiwfctl help show web-svg
```

キーワード検索:

```powershell
aiwfctl help search svg gui
aiwfctl help search repository branch
aiwfctl help search rag dispatch
```

全文をターミナルに表示:

```powershell
aiwfctl help open
```

検索語で絞った全文を表示:

```powershell
aiwfctl help open --query safety --query stop
```

検索可能なMarkdownとして出力:

```powershell
aiwfctl help markdown --output work/help/ai-workflow-help.md
```

## Help Registry

ヘルプ本体は次のregistryに置きます。

```text
db/registries/registry.duckdb
```

DuckDB read modelのsource JSONは次です。

```text
work/db/ariadne-knowledge-platform/registries/workflow_help.json
work/db/ariadne-knowledge-platform/registries/search_terms.json
```

`workflow_help.json` はcommand / extension本体だけを持ちます。各項目の `id` は `/ariadne-new-system` なら `ariadne_new_system` のように、prompt commandやextension名をsnake_case化した機能IDにします。

検索語は `search_terms.json` に分離します。各検索語の `id` はUUID、`owner_id` は `workflow_help.json` 内のsnake_case機能IDにします。

構造定義は次に置きます。

```text
.github/schemas/workflow-help.schema.json
.github/schemas/search-terms.schema.json
```

`db/registries/` はruntime横断で参照するregistry実体、`.github/schemas/` は構造定義専用です。

## 更新ルール

ヘルプの追加、修正、検索性改善は、必要に応じて `.github/agents/workflow-help-curator-agent.prompt.md` を使います。

workflow prompt commandを追加、削除、引数変更した場合は、次を更新します。

1. `work/db/ariadne-knowledge-platform/registries/workflow_help.json`
2. `work/db/ariadne-knowledge-platform/registries/search_terms.json`
3. `db/registries/registry.duckdb`
4. `.github/schemas/workflow-help.schema.json` / `.github/schemas/search-terms.schema.json` が必要なら更新
5. `docs/reference/workflow-help.md`
6. `runtime/tests/test_ctl_help.py`

特に、次の項目は省略しません。

- `command`
- `id`。prompt commandやextension名をsnake_case化した機能ID。例: `ariadne_new_system`
- `overview`
- `prerequisites`
- `arguments`
- `details`
- `examples`
- `skill_path`
- `prompt_path`
- `docs`

## 検索の考え方

`aiwfctl help search` は、registry内の command、overview、argument説明、details、docs などを対象に検索します。
明示的なintent語、同義語、自然文検索語は `search_terms.json` に置きます。検索語自体の `id` はUUIDにし、help item本体とは `owner_id` のsnake_case機能IDで結びます。

例:

```powershell
aiwfctl help search vscode terminal
```

この場合、`/vscode-environment` のように、説明やdetailsに該当語を持つcommandが表示されます。

## 生成Markdownの扱い

`help markdown` の出力先既定値は次です。

```text
work/help/ai-workflow-help.md
```

`work/` 配下なので、生成物はGit追跡しません。
必要なときに生成して、エディタやターミナルの検索機能で探します。

## 境界

`aiwfctl help` はヘルプ表示専用です。
workflow実行、GitHub操作、RAG build、削除、pushなどの副作用は行いません。

副作用のある操作は、各workflow本体またはruntime helper側でHuman Gate Registryに従って判断します。
