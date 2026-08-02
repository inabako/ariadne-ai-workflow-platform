# 実行環境選択

AI workflowを実行する前に、OS、shell、runtime、toolの違いによる失敗を避けるため、`aiwfctl env` で実行環境を選択します。

`aiwfctl env` は Environment Dispatcher です。Workflow開始前に最適なBackendを決定し、後続Workflowへ渡す環境情報を作ります。

## 基本方針

直接 PowerShell、Bash、Docker commandを推測で実行する前に、必ず `aiwfctl env select` でEnvironmentを確認します。

```powershell
aiwfctl env
aiwfctl env list
aiwfctl env show gui-mode
aiwfctl env select gui-mode
aiwfctl env select web-svg
aiwfctl env select docker
aiwfctl env select flutter
```

PATHが未反映の場合は、repo-local wrapperから直接呼びます。

```powershell
.\runtime\windows-script\aiwfctl.cmd env select gui-mode
```

## 利用者向けEnvironmentとBackend

利用者が指定するのは目的ベースのEnvironment名です。内部Backend名は表示情報として扱います。

| Environment | Backend | 主な用途 |
| --- | --- | --- |
| `gui-mode` | `windows-msys2-gui` | PyQt、Qt、QTest、MSYS2、GStreamer、Windows GUI |
| `web-svg` | `wsl-ubuntu-web` | Web SVG、Node.js、npm、Next.js、React、Playwright |
| `docker` | `docker-compose` | Docker / Docker Compose、本番相当、結合試験 |
| `vscode-environment` | `vscode-workspace` | VSCode Workspace-as-Code、terminal、task、aiwfctl導線 |
| `flutter` | `flutter-multiplatform` | Flutter、Dart、Android、iOS、Web、Windows/macOS/Linux desktop |

source of truthは次です。

```text
db/registries/registry.duckdb
```

schemaは次です。

```text
.ariadne/schemas/environment-selection.schema.json
.ariadne/schemas/workflow-environment-profiles.schema.json
```

## CLI

### 一覧

```powershell
aiwfctl env list
```

### Environment詳細

```powershell
aiwfctl env show web-svg
```

`env show` は `work/<work-id>/context/environment-selection.json` の出力例も表示します。

### Environmentを選択

```powershell
aiwfctl env select gui-mode
aiwfctl env select web-svg
aiwfctl env select docker
aiwfctl env select flutter
```

JSONで受け取る場合:

```powershell
aiwfctl env select web-svg --json
```

作業証跡として保存する場合:

```powershell
aiwfctl env select gui-mode --work-id issue-123
```

保存先:

```text
work/<work-id>/process-report/environment-selection-YYYYMMDD_HHMMSS.json
work/<work-id>/process-report/environment-selection-YYYYMMDD_HHMMSS.md
work/<work-id>/context/environment-selection.json
work/<work-id>/context/context-manifest.json
```

`context/environment-selection.json` は後続Workflowが読む固定名のWorkflow Contextです。
`context/context-manifest.json` はContext First Architectureの索引であり、後続Workflow / Agent はまずこのmanifestを確認します。

標準Contextは次の項目を持ちます。

```json
{
  "schema_version": "1.0",
  "artifact_type": "environment-selection-context",
  "selected_at": "2026-07-05T13:00:00+09:00",
  "selected_by": "dispatcher",
  "selection_mode": "manual",
  "environment": "gui-mode",
  "backend": "windows-msys2-gui",
  "reason": "PyQt / Qt / GStreamer / Windows GUI 開発",
  "work_id": "issue-123"
}
```

`selected_by` は `dispatcher` / `human` / `workflow` のいずれかです。`selection_mode` は `manual` / `auto` / `human-check` のいずれかです。

既存の `context/environment-selection.json` がある場合、`work_id`、`environment`、`backend` が異なれば警告を表示します。これにより、後続Workflowが古い環境認識を誤って使うことを防ぎます。

## 不明なEnvironment名

存在しないEnvironment名を指定した場合は、候補を表示してHuman Checkへ戻します。

例:

```powershell
aiwfctl env select pyqt
```

`pyqt` はtool名であり、利用者向けEnvironment名ではありません。この場合は `gui-mode` を候補として表示します。

## 選択ルール

### Windows PowerShell / MSYS2

次の場合に選択します。

- PyQt
- Qt
- MSYS2
- Windows API
- Windows上のGStreamer
- Windows service
- GUI application
- QTest候補

対応Backend:

```text
windows-msys2-gui
```

### WSL Ubuntu

次の場合に選択します。

- Bash
- Linux CLI
- Node.js
- Next.js
- React
- Playwright
- Linux向けbuild

対応Backend:

```text
wsl-ubuntu-web
```

### Docker

次の場合に選択します。

- container内でのみ動作確認が必要
- 本番相当環境で検証する
- Docker Composeによる結合試験を行う

対応Backend:

```text
docker-compose
```

### Flutter Multi-platform

次の場合に選択します。

- Flutter / Dart projectを扱う。
- Android / iOS / Web / Windows / macOS / Linux targetを選ぶ。
- platform別build、Integration Test、Evidence保存を計画する。

対応Backend:

```text
flutter-multiplatform
```

target別build環境:

| Target | Build environment |
| --- | --- |
| Android | Windows / macOS / Linux |
| iOS | macOS |
| Web | Windows / macOS / Linux |
| Windows | Windows |
| macOS | macOS |
| Linux | Linux |

対象platform未指定時は、全platform対応とは推測せずHuman Checkへ戻します。

## Human Check

次の場合は推測で進めず、Human Checkに戻します。

- 実行環境を特定できない。
- WindowsとWSLの両方で実行可能だが、推奨環境を判断できない。
- OS依存libraryの有無を確認できない。
- Docker Desktop起動、network公開、tool installなどローカル環境へ影響する。
- GUI、camera、GStreamer、field networkなど外部I/Oが絡む。
- iOS/macOS build、Flutter release build、署名、Store配布、Platform Channel、native code追加が絡む。

## Preflightとの関係

`aiwfctl env select` は、どの環境で実行すべきかを選ぶ前段です。repo-local初期化状態、PATH状態、`aiwfctl.cmd`、workflow doctor scriptの有無を軽量確認します。必要toolの詳細確認は `aiwfctl preflight ...` で確認します。

例:

```powershell
.\runtime\windows-script\aiwf.cmd ctl preflight `
  --profile gui-mode `
  --work-id issue-123 `
  --source-dir <target-system-repo-path>
```

Webの場合:

```powershell
.\runtime\windows-script\aiwf.cmd ctl preflight `
  --profile web-nextjs `
  --work-id issue-123 `
  --source-dir C:\github\some-next-app
```

Dockerの場合:

```powershell
.\runtime\windows-script\aiwf.cmd ctl preflight `
  --profile docker-compose `
  --work-id issue-123
```

Flutterの場合:

```powershell
.\runtime\windows-script\aiwf.cmd ctl preflight `
  --profile flutter `
  --work-id issue-123 `
  --source-dir C:\github\some-flutter-app
```

Flutter Web Integration Testまで実行する場合は、`flutter drive -d chrome` がWebDriverを要求します。`chromedriver` がPATHにない場合、preflightではoptional missingとして表示し、Flutter workflow側では `build-environment-required` として完了判定を止めます。

Flutter SDKを導入済みでもPATH未反映の場合:

```powershell
.\runtime\windows-script\register-flutter-path.cmd --check
.\runtime\windows-script\register-flutter-path.cmd --shell
```

標準配置は `C:\flutter` です。別pathにSDKを置いた場合は第2引数でSDK rootを渡します。

```powershell
.\runtime\windows-script\register-flutter-path.cmd --shell C:\tools\flutter
```
