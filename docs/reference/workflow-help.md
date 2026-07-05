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
runtime/registries/workflow_help.json
```

構造定義は次に置きます。

```text
.github/schemas/workflow-help.schema.json
```

`runtime/registries/` はruntime横断で参照するregistry実体、`.github/schemas/` は構造定義専用です。

## 更新ルール

ヘルプの追加、修正、検索性改善は、必要に応じて `.github/agents/workflow-help-curator-agent.prompt.md` を使います。

workflow prompt commandを追加、削除、引数変更した場合は、次を更新します。

1. `runtime/registries/workflow_help.json`
2. `.github/schemas/workflow-help.schema.json` が必要なら更新
3. `docs/reference/workflow-help.md`
4. `runtime/tests/test_ctl_help.py`

特に、次の項目は省略しません。

- `command`
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
