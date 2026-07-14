# Flutter Multi-platform Workflow

Flutterアプリの新規作成、既存改修、platform追加、test/build計画を扱うworkflowです。

このworkflowの中心は「Flutterコードを作ったら完了」ではなく、対象platform、host OS、test、build、evidence、Human Checkを一続きで扱うことです。

## 起動条件

- 要件にFlutter利用が含まれる。
- Android / iOS / Web / Windows / macOS / Linux のいずれかを対象にする。
- `work/<work-id>/requirements/flutter-targets.yaml` または `--targets` で対象platformを指定する。

未指定時は全platform対応と推測しません。Human Checkで対象platformを確定します。

## aiwfctl

```powershell
aiwfctl env select flutter --work-id <work-id>
aiwfctl flutter analyze --work-id <work-id>
aiwfctl flutter init --work-id <work-id> --targets android,web,windows
aiwfctl flutter verify --work-id <work-id> --execute
aiwfctl flutter build --work-id <work-id> --targets web --mode debug --execute
aiwfctl flutter finalize --work-id <work-id>
```

Flutter SDKを `C:\flutter` に導入済みだが、PowerShellから `flutter` が見つからない場合は、repo-local helperでUser PATHへ登録します。

```powershell
.\runtime\tools\register-flutter-path.cmd --check
.\runtime\tools\register-flutter-path.cmd --shell
```

SDKを別pathへ置いた場合:

```powershell
.\runtime\tools\register-flutter-path.cmd --shell C:\tools\flutter
```

## target宣言

`work/<work-id>/requirements/flutter-targets.yaml` に保存します。

```yaml
framework: flutter

targets:
  android:
    enabled: true
  ios:
    enabled: false
  web:
    enabled: true
  windows:
    enabled: true
  macos:
    enabled: false
  linux:
    enabled: false

requirements:
  responsive_ui: true
  offline_support: false
  native_integration: false
```

## 環境選択

| Target | Build environment |
| --- | --- |
| Android | Windows / macOS / Linux |
| iOS | macOS |
| Web | Windows / macOS / Linux |
| Windows | Windows |
| macOS | macOS |
| Linux | Linux |

現在hostでbuildできないtargetは、`build_environment_required` または `remote_build_required` としてContextへ出力します。

## Boilerplate

templateは `templates/boilerplates/apps/flutter-app-template/` にあります。

初期実装では、対象カテゴリの判定は残しつつ、実体は `multi-platform` baseを展開します。これにより、lib、test、integration_test、assets、pubspec.yaml、analysis_options.yaml、READMEが必ず揃います。

展開先:

```text
work/<work-id>/implementation/flutter-project/
```

target sourceへ自動上書きしません。

## Evidence

```text
work/<work-id>/evidence/flutter/
├─ common/
│  ├─ verification-plan.md
│  ├─ flutter-analyze-summary.md
│  ├─ flutter-test-summary.md
│  └─ flutter-test-integration-test-summary.md
├─ android/
├─ ios/
├─ web/
├─ windows/
├─ macos/
└─ linux/
```

`--execute` を付けると、各commandの `stdout.txt`、`stderr.txt`、`summary.md` を保存します。`build` はtarget別directoryへ保存します。

## 実試験の自動実行

計画だけ作る場合:

```powershell
aiwfctl flutter verify --work-id <work-id>
aiwfctl flutter build --work-id <work-id> --targets web --mode debug
```

実行して証跡を回収する場合:

```powershell
aiwfctl flutter verify --work-id <work-id> --execute
aiwfctl flutter build --work-id <work-id> --targets web --mode debug --execute
```

Web targetで `flutter drive -d chrome` によるIntegration Testまで実行する場合は、Chromeに加えてWebDriverが必要です。

```text
chromedriver
```

未導入の場合、`verify --execute` は `build-environment-required` として分類し、`finalize` は完了扱いにしません。

release buildは署名や配布判断を伴うため、実行にはHuman Check承認を明示します。

```powershell
aiwfctl flutter build --work-id <work-id> --targets web --mode release --execute --human-check approved
```

完了判定:

```powershell
aiwfctl flutter finalize --work-id <work-id>
```

`finalize` は新しいcommandを実行せず、保存済みContextとEvidenceを読んで次を判定します。

- `flutter-verification`
- `flutter-build`
- `flutter-evidence`

判定結果は `work/<work-id>/evidence/flutter/finalization-summary.md` と `flutter-development-context.json` に保存します。

## Context First

出力:

```text
work/<work-id>/context/flutter-development-context.json
work/<work-id>/context/context-manifest.json
work/<work-id>/reports/flutter-multiplatform-report.md
```

manifestには `flutter-development` contextとして登録します。後続workflowは、target platform、build可否、test計画、Human Check、Knowledge化対象をここから読みます。

## Human Check

- 対象platform未指定
- iOS / macOS / Android signing
- Store配布
- release build
- Platform Channel追加
- native code追加
- 実機試験
- security上の判断

## Knowledge化対象

- target platform選択理由
- build環境判断
- platform差分
- test方法
- build error解決
- UI / permission / native dependency上の注意
